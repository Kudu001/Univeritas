def chunk_text(pages, chunk_size=500, overlap=50):
    """
    Split PDF page text into overlapping chunks.
    pages: list of (page_number, text) from extraction.extract_text_from_pdf
    Returns list of {'content', 'page_number', 'chunk_index'}
    """
    chunks = []
    idx = 0
    buffer = ''
    current_page = 1

    for page_number, text in pages:
        words = text.split()
        for word in words:
            buffer += word + ' '
            if len(buffer.split()) >= chunk_size:
                chunks.append({
                    'content': buffer.strip(),
                    'page_number': current_page,
                    'chunk_index': idx,
                })
                idx += 1
                buffer_words = buffer.split()
                buffer = ' '.join(buffer_words[-overlap:]) + ' '
        current_page = page_number

    if buffer.strip():
        chunks.append({
            'content': buffer.strip(),
            'page_number': current_page,
            'chunk_index': idx,
        })
    return chunks


def chunk_code(code_files, max_lines=50):
    """
    Split source code files into chunks of max_lines lines.
    code_files: list of {'filename', 'language', 'content'} from extraction.extract_code_from_zip
    Returns list of {'content', 'source_file', 'language', 'chunk_index'}
    """
    chunks = []
    idx = 0
    for file_info in code_files:
        lines = file_info['content'].splitlines()
        for start in range(0, len(lines), max_lines):
            segment = '\n'.join(lines[start:start + max_lines])
            if segment.strip():
                chunks.append({
                    'content': segment,
                    'source_file': file_info['filename'],
                    'language': file_info['language'],
                    'chunk_index': idx,
                })
                idx += 1
    return chunks
