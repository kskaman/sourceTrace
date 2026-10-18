"""Tests for expanding precise child hits into larger parent context windows."""
import pytest

from src.retrieve import parent


class FakeCursor:
	def __init__(self, rows_by_path):
		self.rows_by_path = rows_by_path
		self.calls = []
		self._rows = []

	def __enter__(self):
		return self

	def __exit__(self, exc_type, exc, traceback):
		return False

	def execute(self, sql, params):
		self.calls.append((sql, params))
		_, file_path, start, end = params
		self._rows = [
			row
			for row in self.rows_by_path[file_path]
			if start <= row[6] <= end
		]

	def fetchall(self):
		return self._rows


class FakeConnection:
	def __init__(self, rows_by_path):
		self.cursor_instance = FakeCursor(rows_by_path)
		self.closed = False

	def cursor(self):
		return self.cursor_instance

	def close(self):
		self.closed = True


def _row(chunk_id, chunk_index, file_path="docs/policy.md"):
	return (
		chunk_id,
		f"content {chunk_index}",
		"policy.md",
		file_path,
		"md",
		"Policy",
		chunk_index,
		None,
	)


def _child(chunk_id, chunk_index):
	return {
		"chunk_id": chunk_id,
		"source_file": "policy.md",
		"file_path": "docs/policy.md",
		"chunk_index": chunk_index,
	}


def test_expand_to_parent_context_scopes_neighbors_and_deduplicates_overlap():
	conn = FakeConnection(
		{"docs/policy.md": [_row(index + 10, index) for index in range(5)]}
	)

	expanded = parent.expand_to_parent_context(
		[_child(13, 3), _child(11, 1)],
		data_folder="policies",
		radius=1,
		conn=conn,
	)

	assert [chunk["chunk_index"] for chunk in expanded] == [0, 1, 2, 3, 4]
	assert len({chunk["chunk_id"] for chunk in expanded}) == 5
	assert [call[1] for call in conn.cursor_instance.calls] == [
		("policies", "docs/policy.md", 0, 4),
	]
	assert all("data_folder = %s" in call[0] for call in conn.cursor_instance.calls)
	assert all("file_path = %s" in call[0] for call in conn.cursor_instance.calls)
	assert conn.closed is False


def test_expand_to_parent_context_closes_connection_it_opens(monkeypatch):
	conn = FakeConnection({"docs/policy.md": [_row(12, 2)]})
	monkeypatch.setattr(parent, "get_connection", lambda: conn)

	assert parent.expand_to_parent_context(
		[_child(12, 2)], data_folder="policies", radius=0
	)[0]["content"] == "content 2"
	assert conn.closed is True


def test_expand_to_parent_context_isolates_data_folders(db_conn):
	with db_conn.cursor() as cur:
		for data_folder, prefix in (("policies", "policy"), ("archive", "archive")):
			for chunk_index in range(3):
				cur.execute(
					"""
					INSERT INTO chunks (
						embedding, content, source_file, file_path, doc_type,
						chunk_index, total_chunks, doc_hash, data_folder
					) VALUES (
						array_fill(0, ARRAY[384])::vector, %s, 'policy.md',
						'docs/policy.md', 'md', %s, 3, %s, %s
					)
					""",
					(
						f"{prefix} {chunk_index}",
						chunk_index,
						f"{prefix}-hash",
						data_folder,
					),
				)
		cur.execute(
			"""
			SELECT id FROM chunks
			WHERE data_folder = 'policies' AND chunk_index = 1
			"""
		)
		child_id = cur.fetchone()[0]
	db_conn.commit()

	expanded = parent.expand_to_parent_context(
		[_child(child_id, 1)],
		data_folder="policies",
		radius=1,
		conn=db_conn,
	)

	assert [chunk["content"] for chunk in expanded] == [
		"policy 0",
		"policy 1",
		"policy 2",
	]


@pytest.mark.parametrize("radius", [-1, -2])
def test_expand_to_parent_context_rejects_negative_radius(radius):
	with pytest.raises(ValueError, match="non-negative"):
		parent.expand_to_parent_context([], data_folder="policies", radius=radius)
