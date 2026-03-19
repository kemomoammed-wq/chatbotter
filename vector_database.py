# vector_database.py: Vector Database for Semantic Search and RAG
import logging
import os
import json
import numpy as np
from typing import List, Dict, Any, Optional, Tuple
from pathlib import Path
import pickle

# Setup logger first
logger = logging.getLogger(__name__)

# Vector databases
try:
    import faiss
    FAISS_AVAILABLE = True
except ImportError:
    FAISS_AVAILABLE = False
    logger.warning("FAISS not available. Using simple vector search.")

try:
    import chromadb
    from chromadb.config import Settings
    CHROMA_AVAILABLE = True
except ImportError:
    CHROMA_AVAILABLE = False
    logger.warning("ChromaDB not available. Using FAISS fallback.")

# Embeddings
try:
    from sentence_transformers import SentenceTransformer
    SENTENCE_TRANSFORMERS_AVAILABLE = True
except (ImportError, RuntimeError) as e:
    SENTENCE_TRANSFORMERS_AVAILABLE = False
    logger.warning(f"Sentence Transformers not available: {e}. Using simple embeddings.")

class VectorDatabase:
    """Advanced vector database for semantic search and RAG"""
    
    def __init__(
        self,
        embedding_model: str = 'paraphrase-multilingual-MiniLM-L12-v2',
        database_type: str = 'faiss',  # 'faiss', 'chroma', 'simple'
        persist_dir: str = 'data/vector_db'
    ):
        self.embedding_model_name = embedding_model
        self.database_type = database_type
        self.persist_dir = Path(persist_dir)
        self.persist_dir.mkdir(parents=True, exist_ok=True)
        
        # Initialize embedding model
        if SENTENCE_TRANSFORMERS_AVAILABLE:
            try:
                self.embedder = SentenceTransformer(embedding_model)
                self.embedding_dim = self.embedder.get_sentence_embedding_dimension()
            except Exception as e:
                logger.error(f"Error loading embedding model: {e}")
                self.embedder = None
                self.embedding_dim = 384  # Default dimension
        else:
            self.embedder = None
            self.embedding_dim = 384
        
        # Initialize vector database
        self.index = None
        self.documents = []
        self.metadata = []
        
        if database_type == 'faiss' and FAISS_AVAILABLE:
            self._init_faiss()
        elif database_type == 'chroma' and CHROMA_AVAILABLE:
            self._init_chroma()
        else:
            self._init_simple()
    
    def _init_faiss(self):
        """Initialize FAISS index"""
        self.index = None  # Will be created on first add
        logger.info("FAISS vector database initialized")
    
    def _init_chroma(self):
        """Initialize ChromaDB"""
        try:
            self.chroma_client = chromadb.Client(Settings(
                persist_directory=str(self.persist_dir / 'chroma'),
                anonymized_telemetry=False
            ))
            self.collection = self.chroma_client.get_or_create_collection(
                name="chatbot_documents",
                metadata={"hnsw:space": "cosine"}
            )
            logger.info("ChromaDB vector database initialized")
        except Exception as e:
            logger.error(f"Error initializing ChromaDB: {e}")
            self._init_simple()
    
    def _init_simple(self):
        """Initialize simple in-memory vector storage"""
        self.vectors = []
        logger.info("Simple vector database initialized")
    
    def add_documents(
        self,
        texts: List[str],
        metadatas: Optional[List[Dict]] = None,
        ids: Optional[List[str]] = None
    ) -> None:
        """Add documents to vector database"""
        try:
            if not texts:
                return
            
            # Generate embeddings
            if self.embedder:
                embeddings = self.embedder.encode(
                    texts,
                    show_progress_bar=len(texts) > 100,
                    convert_to_numpy=True
                )
            else:
                # Simple TF-IDF fallback
                embeddings = self._simple_embedding(texts)
            
            # Generate IDs if not provided
            if ids is None:
                ids = [f"doc_{i}_{hash(text)}" for i, text in enumerate(texts)]
            
            # Default metadata
            if metadatas is None:
                metadatas = [{}] * len(texts)
            
            # Add to database
            if self.database_type == 'faiss' and FAISS_AVAILABLE:
                self._add_to_faiss(embeddings, texts, metadatas, ids)
            elif self.database_type == 'chroma' and CHROMA_AVAILABLE:
                self._add_to_chroma(texts, embeddings, metadatas, ids)
            else:
                self._add_to_simple(embeddings, texts, metadatas, ids)
            
            logger.info(f"Added {len(texts)} documents to vector database")
            
        except Exception as e:
            logger.error(f"Error adding documents: {e}")
            raise
    
    def _add_to_faiss(self, embeddings: np.ndarray, texts: List[str], metadatas: List[Dict], ids: List[str]):
        """Add documents to FAISS index"""
        embeddings = np.array(embeddings).astype('float32')
        
        # Normalize for cosine similarity
        faiss.normalize_L2(embeddings)
        
        if self.index is None:
            # Create index
            self.embedding_dim = embeddings.shape[1]
            self.index = faiss.IndexFlatIP(self.embedding_dim)  # Inner product for cosine similarity
        
        # Add vectors
        self.index.add(embeddings)
        
        # Store documents and metadata
        self.documents.extend(texts)
        self.metadata.extend(metadatas)
        
        # Save index
        self._save_faiss_index()
    
    def _add_to_chroma(self, texts: List[str], embeddings: np.ndarray, metadatas: List[Dict], ids: List[str]):
        """Add documents to ChromaDB"""
        # Convert embeddings to list
        embeddings_list = embeddings.tolist()
        
        # Add to collection
        self.collection.add(
            embeddings=embeddings_list,
            documents=texts,
            metadatas=metadatas,
            ids=ids
        )
    
    def _add_to_simple(self, embeddings: np.ndarray, texts: List[str], metadatas: List[Dict], ids: List[str]):
        """Add documents to simple storage"""
        for emb, text, meta, doc_id in zip(embeddings, texts, metadatas, ids):
            self.vectors.append({
                'embedding': emb,
                'text': text,
                'metadata': meta,
                'id': doc_id
            })
    
    def search(
        self,
        query: str,
        k: int = 5,
        filter_metadata: Optional[Dict] = None
    ) -> List[Dict[str, Any]]:
        """Search for similar documents"""
        try:
            # Generate query embedding
            if self.embedder:
                query_embedding = self.embedder.encode(
                    query,
                    convert_to_numpy=True
                ).reshape(1, -1)
            else:
                query_embedding = self._simple_embedding([query])
            
            query_embedding = np.array(query_embedding).astype('float32')
            faiss.normalize_L2(query_embedding)
            
            results = []
            
            if self.database_type == 'faiss' and FAISS_AVAILABLE and self.index:
                # FAISS search
                distances, indices = self.index.search(query_embedding, k)
                
                for dist, idx in zip(distances[0], indices[0]):
                    if idx < len(self.documents):
                        results.append({
                            'text': self.documents[idx],
                            'metadata': self.metadata[idx],
                            'score': float(dist),
                            'distance': float(dist)
                        })
            
            elif self.database_type == 'chroma' and CHROMA_AVAILABLE:
                # ChromaDB search
                query_embeddings = query_embedding.tolist()
                search_results = self.collection.query(
                    query_embeddings=query_embeddings,
                    n_results=k,
                    where=filter_metadata
                )
                
                for i in range(len(search_results['documents'][0])):
                    results.append({
                        'text': search_results['documents'][0][i],
                        'metadata': search_results['metadatas'][0][i],
                        'id': search_results['ids'][0][i],
                        'distance': search_results['distances'][0][i] if 'distances' in search_results else 0.0
                    })
            
            else:
                # Simple search
                query_emb = query_embedding[0]
                
                # Calculate cosine similarity
                similarities = []
                for vec in self.vectors:
                    sim = np.dot(query_emb, vec['embedding']) / (
                        np.linalg.norm(query_emb) * np.linalg.norm(vec['embedding'])
                    )
                    similarities.append((sim, vec))
                
                # Sort by similarity
                similarities.sort(key=lambda x: x[0], reverse=True)
                
                for sim, vec in similarities[:k]:
                    results.append({
                        'text': vec['text'],
                        'metadata': vec['metadata'],
                        'id': vec['id'],
                        'score': float(sim),
                        'distance': float(1 - sim)
                    })
            
            return results
            
        except Exception as e:
            logger.error(f"Error searching vector database: {e}")
            return []
    
    def _simple_embedding(self, texts: List[str]) -> np.ndarray:
        """Simple embedding fallback using TF-IDF"""
        from sklearn.feature_extraction.text import TfidfVectorizer
        
        vectorizer = TfidfVectorizer(max_features=self.embedding_dim)
        embeddings = vectorizer.fit_transform(texts).toarray()
        
        return embeddings
    
    def _save_faiss_index(self):
        """Save FAISS index to disk"""
        try:
            if self.index:
                index_path = self.persist_dir / 'faiss.index'
                faiss.write_index(self.index, str(index_path))
                
                # Save documents and metadata
                data_path = self.persist_dir / 'faiss_data.pkl'
                with open(data_path, 'wb') as f:
                    pickle.dump({
                        'documents': self.documents,
                        'metadata': self.metadata
                    }, f)
        except Exception as e:
            logger.error(f"Error saving FAISS index: {e}")
    
    def load_faiss_index(self):
        """Load FAISS index from disk"""
        try:
            index_path = self.persist_dir / 'faiss.index'
            data_path = self.persist_dir / 'faiss_data.pkl'
            
            if index_path.exists():
                self.index = faiss.read_index(str(index_path))
                
                if data_path.exists():
                    with open(data_path, 'rb') as f:
                        data = pickle.load(f)
                        self.documents = data['documents']
                        self.metadata = data['metadata']
                
                logger.info("FAISS index loaded successfully")
        except Exception as e:
            logger.error(f"Error loading FAISS index: {e}")
    
    def get_stats(self) -> Dict[str, Any]:
        """Get database statistics"""
        stats = {
            'database_type': self.database_type,
            'embedding_model': self.embedding_model_name,
            'embedding_dim': self.embedding_dim
        }
        
        if self.database_type == 'faiss' and self.index:
            stats['num_vectors'] = self.index.ntotal
            stats['documents_count'] = len(self.documents)
        elif self.database_type == 'chroma' and CHROMA_AVAILABLE:
            stats['num_vectors'] = self.collection.count()
        else:
            stats['num_vectors'] = len(self.vectors)
        
        return stats

# Global instance
_vector_db = None

def get_vector_database() -> VectorDatabase:
    """Get global vector database instance"""
    global _vector_db
    if _vector_db is None:
        _vector_db = VectorDatabase()
    return _vector_db

