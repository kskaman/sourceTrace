---
title: "Database Operations Runbook"
category: "Engineering"
doc_type: "runbook"
last_updated: "2024-12-01"
owner: "Engineering"
classification: "Internal"
---

# Database Operations Runbook

**Effective Date:** December 1, 2024
**Owner:** Database Engineering team
**Applies to:** All PostgreSQL production clusters managed by Acme Corp

---

## 1. Database Architecture

Acme Corp runs PostgreSQL 16 as its primary relational database. The production environment consists of:

| Component | Configuration | Purpose |
|---|---|---|
| Primary instance | db.r6g.4xlarge, 1 TB SSD | Handles all write operations |
| Read replica 1 | db.r6g.2xlarge, 1 TB SSD | Serves read traffic from the application layer |
| Read replica 2 | db.r6g.2xlarge, 1 TB SSD | Serves read traffic from analytics and reporting workloads |
| pgvector replica | db.r6g.4xlarge, 1 TB SSD | Dedicated to semantic search (HNSW vector index) |

All instances run in the US-East region with synchronous replication to the primary read replica and asynchronous replication to the others.

---

## 2. Backups

### 2.1 Backup Schedule

| Backup Type | Frequency | Retention | Storage |
|---|---|---|---|
| Continuous WAL archiving | Real-time | 30 days of point-in-time recovery | S3 (same region) |
| Full snapshot | Daily at 2:00 AM UTC | 90 days | S3 (same region + cross-region replica) |

### 2.2 Point-in-Time Recovery (PITR)

PITR allows restoring the database to any point within the 30-day WAL retention window. To perform a PITR:

1. Create a new instance from the most recent daily snapshot that precedes the target recovery point.
2. Apply WAL records up to the desired timestamp.
3. Verify data integrity (row counts, application-level checksums).
4. Promote the new instance to primary if replacing the current production instance, or use it for data extraction.

Recovery Point Objective (RPO): 1 hour. Recovery Time Objective (RTO): 4 hours.

### 2.3 Backup Verification

The database engineering team tests backup restoration quarterly per the Backup and Recovery Policy. Each test restores a full snapshot plus WAL replay to a temporary instance and runs the application smoke test suite against it.

---

## 3. Failover

### 3.1 Automated Failover

If the primary instance becomes unresponsive:

1. The monitoring system (Datadog) detects the failure within 30 seconds.
2. The connection proxy (PgBouncer) stops sending new connections to the primary.
3. Read replica 1 (synchronous) is promoted to primary automatically. Promotion takes 15–60 seconds.
4. The application reconnects through the proxy with no configuration change required.
5. An alert is sent to the DBA on-call and the #database-ops Slack channel.

### 3.2 Manual Failover

For planned maintenance (major version upgrades, hardware changes):

1. Announce the maintenance window at least 72 hours in advance per the Enterprise SLA.
2. Stop write traffic by setting the primary to read-only mode.
3. Wait for all replicas to catch up (replication lag = 0).
4. Promote the target replica to primary.
5. Update the proxy configuration to point to the new primary.
6. Verify application health. Resume write traffic.

Planned failover typically causes < 30 seconds of write unavailability. Reads continue without interruption.

---

## 4. Query Tuning

### 4.1 Identifying Slow Queries

The `pg_stat_statements` extension tracks query execution statistics. Use the following query to find the slowest queries by total time:

```sql
SELECT query,
       calls,
       mean_exec_time,
       total_exec_time,
       rows
FROM pg_stat_statements
ORDER BY total_exec_time DESC
LIMIT 20;
```

Queries with `mean_exec_time` above 100ms or `total_exec_time` in the top 20 are candidates for optimization.

The Datadog PostgreSQL integration provides a real-time dashboard of query performance, including p50, p95, and p99 latency by query fingerprint.

### 4.2 Reading Execution Plans

Use `EXPLAIN (ANALYZE, BUFFERS, FORMAT TEXT)` to examine how PostgreSQL executes a query:

```sql
EXPLAIN (ANALYZE, BUFFERS, FORMAT TEXT)
SELECT * FROM records WHERE account_id = 'acct_a1b2c3' AND status = 'active';
```

Key things to look for:

- **Seq Scan on a large table:** Indicates a missing index. The database is reading every row instead of using an index to jump directly to matching rows.
- **Nested Loop with high row estimates:** May indicate a missing join index or a statistics issue.
- **Sort with high memory usage:** Consider adding an index on the sort column, or increasing `work_mem` for the session.
- **Bitmap Heap Scan with many recheck conditions:** The index is filtering some rows but PostgreSQL still needs to verify each one against the heap — common with low-selectivity conditions.

### 4.3 Ways to Make Database Lookups Faster

When a query is slow, work through the following checklist in order:

1. **Add a missing index.** The most common fix. If the query filters on a column that is not indexed, creating a B-tree index on that column typically reduces lookup time from seconds to milliseconds. For composite filters (e.g., `WHERE account_id = ? AND status = ?`), create a multi-column index with the most selective column first.

2. **Use a covering index.** If the query selects only a few columns, an `INCLUDE` index that covers all selected columns allows PostgreSQL to answer the query entirely from the index without reading the table heap. This eliminates random I/O and can speed up lookups by 2–5x for read-heavy workloads.

3. **Partition large tables.** Tables with more than 100 million rows benefit from range partitioning (typically by date). Partitioning allows PostgreSQL to skip entire partitions during query planning, making lookups faster by reducing the search space.

4. **Tune connection pooling.** If lookup latency is high but the execution plan is fast, the bottleneck may be connection acquisition. PgBouncer is configured for transaction-level pooling with a maximum of 200 connections to the primary. If the pool is saturated, queries queue. Monitor `pgbouncer_pool_waiting_clients` in Datadog.

5. **Increase shared_buffers and effective_cache_size.** If the working set does not fit in memory, PostgreSQL reads from disk. Our production configuration: `shared_buffers = 16GB` (25% of instance RAM), `effective_cache_size = 48GB` (75% of instance RAM). These values are reviewed during quarterly capacity planning.

6. **Use read replicas for analytics queries.** Heavy analytical queries (aggregations, full-table scans for reporting) should run against read replica 2, not the primary. This prevents analytics workloads from competing with transactional queries for CPU and I/O. Application code routes queries based on the `read_only=true` connection parameter.

7. **Consider materialized views.** For complex queries that aggregate data across multiple tables and are run frequently with the same parameters, a materialized view pre-computes the result. Refresh the view on a schedule (e.g., every 6 hours) rather than computing it on every query. Trade-off: data freshness vs. query speed.

### 4.4 Index Maintenance

- **Reindex bloated indexes** quarterly or when index bloat exceeds 30% (measured by `pgstattuple`). Use `REINDEX CONCURRENTLY` to avoid blocking writes.
- **Remove unused indexes.** Indexes that are never scanned (check `pg_stat_user_indexes.idx_scan = 0` over a 30-day period) waste storage and slow down writes. Drop them after confirming with the application team.
- **Monitor index usage** in the Datadog PostgreSQL dashboard. Alert when a new query introduces a sequential scan on a table with more than 1 million rows.

---

## 5. Indexing Strategies

### 5.1 B-Tree Indexes

The default index type. Optimal for equality and range queries. Use for:

- Primary keys and foreign keys (created automatically).
- Columns used in WHERE clauses with `=`, `<`, `>`, `BETWEEN`, `IN`.
- Columns used in ORDER BY and GROUP BY.

### 5.2 GIN Indexes

Generalized Inverted Indexes. Optimal for full-text search, JSONB containment queries, and array operations. Used in Acme Corp for:

- Full-text search on record content (`to_tsvector` / `to_tsquery`).
- JSONB metadata field queries (`metadata @> '{"department": "Engineering"}'`).

### 5.3 HNSW Indexes (pgvector)

Hierarchical Navigable Small World indexes for approximate nearest neighbor search on vector columns. Used by the semantic search feature. See the ML Platform Architecture document for HNSW parameter tuning (`ef_construction`, `M`, `ef_search`) and performance benchmarks.

### 5.4 BRIN Indexes

Block Range Indexes. Effective for large tables where the indexed column is naturally correlated with the physical order of the rows (e.g., timestamps on append-only tables). BRIN indexes are much smaller than B-tree indexes and are used on the audit log table (`created_at` column).

---

## 6. Common Operational Tasks

| Task | Command / Procedure | Frequency |
|---|---|---|
| Check replication lag | `SELECT now() - pg_last_xact_replay_timestamp() AS lag;` on each replica | Continuous (Datadog monitor) |
| Kill a long-running query | `SELECT pg_terminate_backend(pid);` after identifying the PID from `pg_stat_activity` | As needed |
| Vacuum a table | `VACUUM (ANALYZE) table_name;` — updates statistics and reclaims dead tuples | Autovacuum handles most cases; manual vacuum for bulk-delete operations |
| Check table bloat | `SELECT * FROM pgstattuple('table_name');` | Monthly |
| Rotate database credentials | Rotate via HashiCorp Vault; application picks up new credentials automatically via Vault agent | Every 180 days per IT Security Policy |

---

## 7. Escalation

| Situation | Escalate To |
|---|---|
| Replication lag > 30 seconds | DBA on-call |
| Primary instance unresponsive | DBA on-call + Platform on-call (automated alert) |
| Data corruption suspected | DBA on-call + VP of Engineering |
| Query performance degradation affecting SLO | DBA on-call + service owner |

See the Incident Response Runbook for the full escalation process.

---

*Version 3.0 — Last revised December 1, 2024. Questions: database-eng@acmecorp.com.*
