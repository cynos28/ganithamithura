try:
    import chromadb
    from chromadb.config import Settings as ChromaSettings
    CHROMADB_AVAILABLE = True
except ImportError:
    CHROMADB_AVAILABLE = False
    print("⚠️  ChromaDB not available - vector search will be disabled")

from typing import List, Dict, Any
from app.config import settings
from app.utils.llm_client import llm_client


class EmbeddingsService:
    """Service for managing document embeddings and vector search"""
    
    def __init__(self):
        if not CHROMADB_AVAILABLE:
            self.client = None
            self.collection = None
            return
            
        # Initialize ChromaDB client
        self.client = chromadb.Client(ChromaSettings(
            persist_directory=settings.chroma_persist_directory,
            anonymized_telemetry=False
        ))
        
        # Get or create collection
        self.collection = self.client.get_or_create_collection(
            name=settings.chroma_collection_name,
            metadata={"description": "Ganithamithura educational documents"}
        )
    
    async def add_document_chunks(
        self,
        document_id: str,
        chunks: List[str],
        metadata: Dict[str, Any]
    ) -> str:
        """Add document chunks to vector database with embeddings"""
        if not CHROMADB_AVAILABLE:
            print(f"⚠️  ChromaDB not available - skipping embedding for document {document_id}")
            return document_id
            
        try:
            # Use ChromaDB default embeddings (no OpenAI API needed)
            # This uses sentence-transformers locally - free but less accurate
            print(f"🔄 Storing {len(chunks)} chunks using default embeddings...")
            
            # Sanitize metadata for ChromaDB (only str, int, float, bool allowed)
            clean_metadata = {}
            for key, value in metadata.items():
                if isinstance(value, (list, tuple)):
                    # Convert lists to comma-separated strings
                    clean_metadata[key] = ",".join(str(v) for v in value)
                elif isinstance(value, dict):
                    # Convert dicts to JSON strings
                    import json
                    clean_metadata[key] = json.dumps(value)
                elif isinstance(value, (str, int, float, bool)):
                    clean_metadata[key] = value
                else:
                    # Convert other types to string
                    clean_metadata[key] = str(value)
            
            # Create IDs and metadata for each chunk
            ids = [f"{document_id}_chunk_{i}" for i in range(len(chunks))]
            metadatas = [
                {
                    **clean_metadata,
                    "chunk_index": i,
                    "chunk_text": chunks[i][:200]  # Preview
                }
                for i in range(len(chunks))
            ]
            
            # Add to collection (ChromaDB will auto-generate embeddings)
            self.collection.add(
                documents=chunks,
                metadatas=metadatas,
                ids=ids
            )
            
            print(f"✅ Stored {len(chunks)} chunks with default embeddings for document {document_id}")
            return document_id
        except Exception as e:
            raise Exception(f"Error adding document chunks: {str(e)}")
    
    async def search_similar_chunks(
        self,
        query: str,
        n_results: int = 5,
        filter_metadata: Dict[str, Any] = None
    ) -> List[Dict[str, Any]]:
        """Search for similar document chunks using semantic similarity"""
        if not CHROMADB_AVAILABLE:
            return []
            
        try:
            # Use ChromaDB default search (no OpenAI API needed)
            results = self.collection.query(
                query_texts=[query],
                n_results=n_results,
                where=filter_metadata
            )
            
            # Format results
            similar_chunks = []
            if results['documents']:
                for i in range(len(results['documents'][0])):
                    similar_chunks.append({
                        'text': results['documents'][0][i],
                        'metadata': results['metadatas'][0][i] if results['metadatas'] else {},
                        'distance': results['distances'][0][i] if results['distances'] else 0,
                    })
            
            return similar_chunks
        except Exception as e:
            raise Exception(f"Error searching chunks: {str(e)}")
    
    def delete_document(self, document_id: str):
        """Delete all chunks of a document"""
        if not CHROMADB_AVAILABLE:
            return
            
        try:
            # Get all chunk IDs for this document
            results = self.collection.get(
                where={"document_id": document_id}
            )
            
            if results['ids']:
                self.collection.delete(ids=results['ids'])
        except Exception as e:
            raise Exception(f"Error deleting document: {str(e)}")
    
    def get_collection_stats(self) -> Dict[str, Any]:
        """Get statistics about the collection"""
        if not CHROMADB_AVAILABLE:
            return {
                "status": "disabled",
                "message": "ChromaDB not installed"
            }
            
        try:
            count = self.collection.count()
            return {
                "total_chunks": count,
                "collection_name": settings.chroma_collection_name
            }
        except Exception as e:
            return {"error": str(e)}


# Singleton instance
embeddings_service = EmbeddingsService()
