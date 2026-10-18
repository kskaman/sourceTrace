"""Expand precise child-chunk hits into neighboring parent context."""

from src.database import get_connection


def _merged_parent_ranges(
	children: list[dict], radius: int
) -> list[tuple[str, int, int]]:
	"""Return merged chunk-index ranges grouped by document relevance order."""
	ranges_by_path: dict[str, list[tuple[int, int]]] = {}
	for child in children:
		chunk_index = child["chunk_index"]
		ranges_by_path.setdefault(child["file_path"], []).append(
			(max(0, chunk_index - radius), chunk_index + radius)
		)

	merged: list[tuple[str, int, int]] = []
	for file_path, ranges in ranges_by_path.items():
		ordered_ranges = sorted(ranges)
		start, end = ordered_ranges[0]
		for next_start, next_end in ordered_ranges[1:]:
			if next_start <= end + 1:
				end = max(end, next_end)
				continue
			merged.append((file_path, start, end))
			start, end = next_start, next_end
		merged.append((file_path, start, end))
	return merged


def expand_to_parent_context(
	children: list[dict],
	data_folder: str,
	radius: int = 2,
	conn=None,
) -> list[dict]:
	"""Return each child and its neighboring chunks from the same document."""
	if radius < 0:
		raise ValueError("radius must be non-negative")
	if not data_folder.strip():
		raise ValueError("data_folder must not be empty")
	if not children:
		return []

	owns_connection = conn is None
	connection = conn or get_connection()
	expanded: list[dict] = []
	seen_chunk_ids: set[int] = set()

	try:
		with connection.cursor() as cur:
			for file_path, start, end in _merged_parent_ranges(children, radius):
				cur.execute(
					"""
					SELECT id, content, source_file, file_path, doc_type, category,
						   chunk_index, page_number
					FROM chunks
					WHERE data_folder = %s
					  AND file_path = %s
					  AND chunk_index BETWEEN %s AND %s
					ORDER BY chunk_index
					""",
					(
						data_folder,
						file_path,
						start,
						end,
					),
				)
				for row in cur.fetchall():
					if row[0] in seen_chunk_ids:
						continue
					seen_chunk_ids.add(row[0])
					expanded.append(
						{
							"chunk_id": row[0],
							"content": row[1],
							"source_file": row[2],
							"file_path": row[3],
							"doc_type": row[4],
							"category": row[5],
							"chunk_index": row[6],
							"page_number": row[7],
						}
					)
	finally:
		if owns_connection:
			connection.close()

	return expanded
