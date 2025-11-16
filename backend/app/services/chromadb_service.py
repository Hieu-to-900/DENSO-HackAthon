"""
ChromaDB Service - Connection and query layer for external news/market data.
Provides vector search capabilities for risk intelligence.
"""

from __future__ import annotations

import os
from datetime import datetime
from typing import Any, Dict, List, Optional

import chromadb
from chromadb.config import Settings


class ChromaDBService:
    """Service for interacting with ChromaDB vector database."""

    def __init__(
        self,
        host: str = "localhost",
        port: int = 8000,
        collection_name: str = "external_market_data",
    ):
        """Initialize ChromaDB client.
        
        Args:
            host: ChromaDB server host
            port: ChromaDB server port
            collection_name: Name of the collection to use
        """
        self.host = host
        self.port = port
        self.collection_name = collection_name
        
        # Initialize client (will connect to server or use local)
        try:
            self.client = chromadb.HttpClient(
                host=host,
                port=port,
                settings=Settings(anonymized_telemetry=False),
            )
            print(f"✅ Connected to ChromaDB server at {host}:{port}")
        except Exception as e:
            print(f"⚠️ ChromaDB server not available, using local client: {str(e)}")
            # Fallback to local persistent client
            persist_directory = os.getenv("CHROMADB_PATH", "./data/chromadb")
            self.client = chromadb.PersistentClient(
                path=persist_directory,
                settings=Settings(anonymized_telemetry=False),
            )
        
        self.collection = None

    def get_collection(self):
        """Get or create the collection."""
        if self.collection is None:
            try:
                self.collection = self.client.get_collection(self.collection_name)
                print(f"✅ Using existing collection: {self.collection_name}")
            except Exception:
                # Collection doesn't exist, create it
                self.collection = self.client.create_collection(
                    name=self.collection_name,
                    metadata={"description": "External market news and risk data"},
                )
                print(f"✅ Created new collection: {self.collection_name}")
        
        return self.collection

    async def query_recent_news(
        self,
        query_text: Optional[str] = None,
        n_results: int = 20,
        where_filter: Optional[Dict[str, Any]] = None,
    ) -> List[Dict[str, Any]]:
        """Query recent news from ChromaDB.
        
        Args:
            query_text: Text to search for (semantic search)
            n_results: Number of results to return
            where_filter: Metadata filter (e.g., {"category": "supply_chain"})
            
        Returns:
            List of documents with metadata
        """
        collection = self.get_collection()
        
        try:
            if query_text:
                # Semantic search
                results = collection.query(
                    query_texts=[query_text],
                    n_results=n_results,
                    where=where_filter,
                    include=["documents", "metadatas", "distances"],
                )
            else:
                # Get all recent documents
                results = collection.get(
                    where=where_filter,
                    limit=n_results,
                    include=["documents", "metadatas"],
                )
            
            # Format results
            documents = []
            if query_text:
                # Query results format
                for i, doc_id in enumerate(results["ids"][0]):
                    documents.append({
                        "id": doc_id,
                        "text": results["documents"][0][i],
                        "metadata": results["metadatas"][0][i],
                        "similarity": 1 - results["distances"][0][i] if "distances" in results else None,
                    })
            else:
                # Get results format
                for i, doc_id in enumerate(results["ids"]):
                    documents.append({
                        "id": doc_id,
                        "text": results["documents"][i],
                        "metadata": results["metadatas"][i],
                    })
            
            return documents
            
        except Exception as e:
            print(f"❌ ChromaDB query failed: {str(e)}")
            return []

    async def add_news_documents(
        self, documents: List[Dict[str, Any]]
    ) -> int:
        """Add news documents to ChromaDB.
        
        Args:
            documents: List of documents to add with format:
                {
                    "id": "unique_id",
                    "text": "document text",
                    "metadata": {...}
                }
        
        Returns:
            Number of documents added
        """
        collection = self.get_collection()
        
        try:
            ids = [doc["id"] for doc in documents]
            texts = [doc["text"] for doc in documents]
            metadatas = [doc.get("metadata", {}) for doc in documents]
            
            collection.add(
                ids=ids,
                documents=texts,
                metadatas=metadatas,
            )
            
            print(f"✅ Added {len(documents)} documents to ChromaDB")
            return len(documents)
            
        except Exception as e:
            print(f"❌ Failed to add documents to ChromaDB: {str(e)}")
            return 0

    async def get_news_by_category(
        self, category: str, limit: int = 10
    ) -> List[Dict[str, Any]]:
        """Get news filtered by category.
        
        Args:
            category: News category (e.g., "supply_chain", "competition")
            limit: Maximum number of results
            
        Returns:
            List of documents
        """
        return await self.query_recent_news(
            n_results=limit,
            where_filter={"category": category},
        )

    async def search_by_products(
        self, product_codes: List[str], limit: int = 10
    ) -> List[Dict[str, Any]]:
        """Search news related to specific products.
        
        Args:
            product_codes: List of product codes to search for
            limit: Maximum number of results
            
        Returns:
            List of documents mentioning the products
        """
        # Query with product codes as search terms
        query_text = " OR ".join(product_codes)
        return await self.query_recent_news(
            query_text=query_text,
            n_results=limit,
        )

    async def get_high_risk_news(
        self, risk_threshold: float = 0.7, limit: int = 10
    ) -> List[Dict[str, Any]]:
        """Get news with high risk scores.
        
        Args:
            risk_threshold: Minimum risk score (0-1)
            limit: Maximum number of results
            
        Returns:
            List of high-risk documents
        """
        return await self.query_recent_news(
            n_results=limit,
            where_filter={"risk_score": {"$gte": risk_threshold}},
        )

    def get_collection_stats(self) -> Dict[str, Any]:
        """Get statistics about the ChromaDB collection."""
        collection = self.get_collection()
        
        try:
            count = collection.count()
            return {
                "collection_name": self.collection_name,
                "total_documents": count,
                "host": self.host,
                "port": self.port,
            }
        except Exception as e:
            print(f"❌ Failed to get collection stats: {str(e)}")
            return {}


# Global ChromaDB service instance
chromadb_service = ChromaDBService(
    host=os.getenv("CHROMADB_HOST", "localhost"),
    port=int(os.getenv("CHROMADB_PORT", "8000")),
    collection_name=os.getenv("CHROMADB_COLLECTION", "external_market_data"),
)


async def get_chromadb_service() -> ChromaDBService:
    """Dependency for FastAPI routes."""
    return chromadb_service
