# Batch Folder Upload

This project supports folder-based batch uploads from the Admin Content tab.

## Behavior

- A folder picker in the frontend can submit multiple files in one batch request.
- Nested sub-folders are preserved as relative document URIs.
- Each file is processed independently so one failure does not stop the rest of the batch.
- Re-uploading the same file path replaces the previous indexed chunks for that URI.
- Re-uploading an updated Markdown file at the same path updates the indexed content instead of duplicating stale chunks.

## Failure Handling

- The batch endpoint returns per-file results, including success or failure and the ingested chunk count.
- If one file fails, successful files still finish and are retained.
- To resume after a failure, upload the same folder again or retry only the failed paths.
- Because document URIs are path-based, unchanged files are safe to re-upload without creating duplicate document entries.

## Implementation Summary

- Frontend: folder-capable batch upload UI in `frontend/components/admin/upload-form.tsx`.
- Frontend API: batch upload client in `frontend/lib/api/admin.ts`.
- Backend: batch route in `backend/src/api/routes/admin.py`.
- Backend ingestion: duplicate URI cleanup before upsert in `backend/src/ingest/pipeline.py`.

## Notes

- Folder selection uses browser support for `webkitdirectory`.
- The backend still accepts single-file uploads for compatibility.