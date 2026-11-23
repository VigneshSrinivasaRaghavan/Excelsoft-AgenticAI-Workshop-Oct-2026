from src.core import build_vector_store

if __name__ == "__main__":
    print("Building vector store...")

    try:
        vector_store = build_vector_store()
        print("Vector store built successfully")
    except Exception as e:
        print(f"Error building vector store: {e}")
        exit(1)