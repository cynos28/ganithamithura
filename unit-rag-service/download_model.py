import chromadb
from chromadb.utils import embedding_functions

def main():
    print("Pre-downloading ChromaDB default ONNX embedding model...")
    # This will trigger the download if it's not already complete
    ef = embedding_functions.DefaultEmbeddingFunction()
    # Test the model
    res = ef(["Test document"])
    print("Download and test complete. Vector size:", len(res[0]))

if __name__ == "__main__":
    main()
