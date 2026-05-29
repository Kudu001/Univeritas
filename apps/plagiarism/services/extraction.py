import zipfile
import io


def extract_text_from_pdf(file_field):
    """Extract plain text from an uploaded PDF using PyMuPDF."""
    import fitz  # PyMuPDF
    content = file_field.read()
    doc = fitz.open(stream=content, filetype='pdf')
    pages = []
    for page in doc:
        pages.append((page.number + 1, page.get_text()))
    doc.close()
    return pages  # list of (page_number, text)


def extract_code_from_zip(file_field):
    """Extract source files from a zip archive. Returns list of dicts."""
    _TEXT_EXTENSIONS = {'.py', '.java', '.js', '.ts', '.c', '.cpp', '.cs', '.go', '.rb', '.php'}
    _LANG_MAP = {
        '.py': 'python', '.java': 'java', '.js': 'javascript', '.ts': 'typescript',
        '.c': 'c', '.cpp': 'cpp', '.cs': 'csharp', '.go': 'go', '.rb': 'ruby', '.php': 'php',
    }
    content = file_field.read()
    results = []
    with zipfile.ZipFile(io.BytesIO(content)) as zf:
        for name in zf.namelist():
            if name.endswith('/'):
                continue
            ext = '.' + name.rsplit('.', 1)[-1].lower() if '.' in name else ''
            if ext not in _TEXT_EXTENSIONS:
                continue
            try:
                code = zf.read(name).decode('utf-8', errors='replace')
                results.append({
                    'filename': name,
                    'language': _LANG_MAP.get(ext, 'unknown'),
                    'content': code,
                })
            except Exception:
                continue
    return results
