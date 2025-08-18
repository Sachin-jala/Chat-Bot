import asyncio
from pathlib import Path
from app.openai_client import embed_text
from app.rag import RAG
from app.utils import chunk_text

async def main():
    docs_dir = Path('data/docs')
    files = list(docs_dir.glob('**/*.txt'))
    for f in files:
        text = f.read_text(encoding='utf-8')
        chunks = chunk_text(text)
        embeddings = await embed_text(chunks, model='text-embedding-3-small')
        metadatas = [{'source': str(f), 'text': c}for c in chunks]
        RAG.add(embeddings, metadatas)
    print ('Indexing complete.')

if __name__ == '__main__':
    asyncio.run(main())