from src.core import search_vector_store

# Test queries
queries = [
    "How to test login API?",
    "Database connection issues",
    "API rate limiting"
]

print("Testing vector store search")
print("="*60)

for query in queries:
    print(f"\nQuery: '{query}'")
    print("-"*60)

    results = search_vector_store(query, top_k=3)

    for i, (doc, score) in enumerate(results, 1):
        source = doc.metadata.get('source', 'Unknown').split('/')[-1]
        print(f"[{i}] {source} (similarity: {1-score:.2f})")
        print(f"    {doc.page_content[:120]}...")

print("="*60)
print("Vector search working!")