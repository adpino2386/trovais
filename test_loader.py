from ingestion.loader import load_document
from ingestion.chunker import chunk_document

doc = load_document('data/sample_manuals/impractical_python_projects.pdf')
print('Filename:', doc['filename'])
print('Pages found:', doc['total_pages'])

chunks = chunk_document(doc)
print(f'Total chunks: {len(chunks)}')
print(f'\nFirst chunk text:\n{chunks[0]["text"][:300]}')
print(f'\nFirst chunk metadata: {chunks[0]["metadata"]}')