from fastapi import UploadFile
from pathlib import Path

DATA_DIR = Path('data')
DOCS_DIR = DATA_DIR / 'docs'
DOCS_DIR.mkdir(parents=True, exist_ok=True)

async def save_upload_file(upload_file: UploadFile, dest: Path) -> Path:
    dest.parent.mkdir(parents=True, exist_ok=True)
    with open(dest, 'wb') as f:
        content = await upload_file.read()
        f.write(content)
    return dest
def chunk_text(text: str, chunk_size: int = 800, overlap: int = 100):
    tokens = text.split()
    chunks, i = [], 0
    while i < len(tokens):
        chunks.append(' '.join(tokens[i:i+chunk_size]))
        i += chunk_size - overlap
    return chunks