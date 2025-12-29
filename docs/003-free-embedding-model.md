# Extended Document Type Support

## Summary
Added support for additional document formats beyond the original PDF, Markdown, and text files.

## Implemented File Types

### Fully Supported
- **Word Documents**: `.docx` (extracts paragraphs and tables)
- **Excel Spreadsheets**: `.xlsx`, `.xls` (extracts all sheets with headers and data)
- **PowerPoint Presentations**: `.pptx` (extracts text from all slides)
- **HTML Files**: `.html`, `.htm` (extracts text content, removes boilerplate)
- **CSV Files**: `.csv` (auto-detects delimiter, extracts all rows)

### Legacy Formats (with helpful errors)
- `.doc` - Old Word format (requires conversion to .docx)
- `.ppt` - Old PowerPoint format (requires conversion to .pptx)

## Implementation Details

### New Loaders
- `docx_loader.py` - Word document extraction
- `excel_loader.py` - Excel spreadsheet extraction
- `pptx_loader.py` - PowerPoint presentation extraction
- `html_loader.py` - HTML file extraction
- `csv_loader.py` - CSV file extraction
- `doc_loader.py` - Legacy .doc handler (with helpful error)
- `ppt_loader.py` - Legacy .ppt handler (with helpful error)

### Updated Components
- `file_loader.py` - Dispatcher updated to route to new loaders
- `admin.py` - Upload endpoint accepts all new file types
- `upload-form.tsx` - Frontend file picker updated with new accept types

### Dependencies Added
- `python-docx>=1.1.0` - Word document support
- `openpyxl>=3.1.0` - Excel .xlsx support
- `pandas>=2.0.0` - Excel and data processing
- `python-pptx>=0.6.0` - PowerPoint support
- `xlrd>=2.0.0` - Legacy Excel .xls support

## Usage
All new file types can be uploaded via the `/admin` page upload form and will be processed through the same ingestion pipeline (normalization, chunking, deduplication, embedding, storage).

