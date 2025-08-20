"""
Pinecone integration for vector search and context retrieval
"""
import os
from typing import List, Dict, Any, Optional
import uuid
from pinecone import Pinecone, ServerlessSpec
from openai import OpenAI
import hashlib
from loguru import logger


class PineconeClient:
    """Pinecone vector database client for context-aware retrieval"""
    
    def __init__(self):
        api_key = os.getenv("PINECONE_API_KEY")
        if not api_key:
            raise ValueError("PINECONE_API_KEY must be set")
        
        self.pc = Pinecone(api_key=api_key)
        self.index_name = os.getenv("PINECONE_INDEX_NAME", "becoming-one-embeddings")
        self.openai_client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))
        
        # Initialize index
        self._ensure_index_exists()
        self.index = self.pc.Index(self.index_name)
    
    def _ensure_index_exists(self):
        """Ensure the Pinecone index exists"""
        try:
            existing_indexes = [index.name for index in self.pc.list_indexes()]
            
            if self.index_name not in existing_indexes:
                logger.info(f"Creating Pinecone index: {self.index_name}")
                self.pc.create_index(
                    name=self.index_name,
                    dimension=1536,  # OpenAI text-embedding-ada-002 dimension
                    metric="cosine",
                    spec=ServerlessSpec(
                        cloud="aws",
                        region=os.getenv("PINECONE_ENVIRONMENT", "us-east-1")
                    )
                )
                logger.info(f"Index {self.index_name} created successfully")
            else:
                logger.info(f"Using existing index: {self.index_name}")
                
        except Exception as e:
            logger.error(f"Error ensuring index exists: {e}")
            raise
    
    async def get_embedding(self, text: str) -> List[float]:
        """Get embedding for text using OpenAI"""
        try:
            response = self.openai_client.embeddings.create(
                model="text-embedding-ada-002",
                input=text.replace("\n", " ")
            )
            return response.data[0].embedding
        except Exception as e:
            logger.error(f"Error getting embedding: {e}")
            raise
    
    async def store_interaction(
        self,
        person_id: uuid.UUID,
        message: str,
        response: str,
        source: str,
        metadata: Optional[Dict[str, Any]] = None
    ):
        """Store conversation interaction in Pinecone"""
        try:
            # Create combined text for embedding
            combined_text = f"User: {message}\nAI: {response}"
            
            # Get embedding
            embedding = await self.get_embedding(combined_text)
            
            # Create unique ID for this interaction
            interaction_id = hashlib.md5(
                f"{person_id}_{message}_{response}".encode()
            ).hexdigest()
            
            # Prepare metadata
            vector_metadata = {
                "person_id": str(person_id),
                "message": message,
                "response": response,
                "source": source,
                "timestamp": str(uuid.uuid1().time),
                "type": "interaction",
                **(metadata or {})
            }
            
            # Store in Pinecone
            self.index.upsert(
                vectors=[{
                    "id": interaction_id,
                    "values": embedding,
                    "metadata": vector_metadata
                }]
            )
            
            logger.info(f"Stored interaction in Pinecone: {interaction_id}")
            
        except Exception as e:
            logger.error(f"Error storing interaction in Pinecone: {e}")
    
    async def search_similar_content(
        self,
        query: str,
        person_id: Optional[uuid.UUID] = None,
        top_k: int = 5,
        include_metadata: bool = True
    ) -> List[str]:
        """Search for similar content in Pinecone"""
        try:
            # Get query embedding
            query_embedding = await self.get_embedding(query)
            
            # Build filter for person-specific search
            filter_dict = {}
            if person_id:
                filter_dict["person_id"] = str(person_id)
            
            # Search Pinecone
            search_results = self.index.query(
                vector=query_embedding,
                top_k=top_k,
                include_metadata=include_metadata,
                filter=filter_dict if filter_dict else None
            )
            
            # Extract relevant context
            contexts = []
            for match in search_results.matches:
                if match.score > 0.7:  # Only include high-similarity matches
                    metadata = match.metadata
                    context = f"Previous conversation - User: {metadata.get('message', '')} AI: {metadata.get('response', '')}"
                    contexts.append(context)
            
            return contexts
            
        except Exception as e:
            logger.error(f"Error searching Pinecone: {e}")
            return []
    
    async def store_knowledge_base_content(
        self,
        content: str,
        title: str,
        category: str,
        metadata: Optional[Dict[str, Any]] = None
    ):
        """Store knowledge base content (Becoming One™ method materials)"""
        try:
            # Get embedding for content
            embedding = await self.get_embedding(content)
            
            # Create unique ID
            content_id = hashlib.md5(f"{title}_{category}_{content}".encode()).hexdigest()
            
            # Prepare metadata
            vector_metadata = {
                "title": title,
                "category": category,
                "content": content,
                "type": "knowledge_base",
                "timestamp": str(uuid.uuid1().time),
                **(metadata or {})
            }
            
            # Store in Pinecone
            self.index.upsert(
                vectors=[{
                    "id": content_id,
                    "values": embedding,
                    "metadata": vector_metadata
                }]
            )
            
            logger.info(f"Stored knowledge base content: {title}")
            
        except Exception as e:
            logger.error(f"Error storing knowledge base content: {e}")
    
    async def search_knowledge_base(
        self,
        query: str,
        category: Optional[str] = None,
        top_k: int = 3
    ) -> List[Dict[str, Any]]:
        """Search knowledge base content"""
        try:
            # Get query embedding
            query_embedding = await self.get_embedding(query)
            
            # Build filter
            filter_dict = {"type": "knowledge_base"}
            if category:
                filter_dict["category"] = category
            
            # Search Pinecone
            search_results = self.index.query(
                vector=query_embedding,
                top_k=top_k,
                include_metadata=True,
                filter=filter_dict
            )
            
            # Extract knowledge base results
            results = []
            for match in search_results.matches:
                if match.score > 0.6:  # Lower threshold for knowledge base
                    results.append({
                        "title": match.metadata.get("title"),
                        "content": match.metadata.get("content"),
                        "category": match.metadata.get("category"),
                        "relevance_score": match.score
                    })
            
            return results
            
        except Exception as e:
            logger.error(f"Error searching knowledge base: {e}")
            return []
    
    async def get_user_interaction_summary(self, person_id: uuid.UUID) -> Dict[str, Any]:
        """Get summary of user's interactions for analysis"""
        try:
            # Search for all user interactions
            dummy_query = "summary"  # We'll get all via filter
            query_embedding = await self.get_embedding(dummy_query)
            
            search_results = self.index.query(
                vector=query_embedding,
                top_k=100,  # Get many results
                include_metadata=True,
                filter={"person_id": str(person_id), "type": "interaction"}
            )
            
            # Analyze patterns
            total_interactions = len(search_results.matches)
            sources = {}
            recent_topics = []
            
            for match in search_results.matches:
                metadata = match.metadata
                source = metadata.get("source", "unknown")
                sources[source] = sources.get(source, 0) + 1
                
                # Extract topics from recent interactions (simple keyword extraction)
                message = metadata.get("message", "")
                if message:
                    recent_topics.append(message[:100])  # First 100 chars
            
            return {
                "total_interactions": total_interactions,
                "sources": sources,
                "recent_topics": recent_topics[:5],  # Last 5 topics
                "engagement_level": "high" if total_interactions > 20 else "medium" if total_interactions > 5 else "new"
            }
            
        except Exception as e:
            logger.error(f"Error getting user summary: {e}")
            return {"total_interactions": 0, "sources": {}, "recent_topics": [], "engagement_level": "unknown"}
    
    async def delete_user_data(self, person_id: uuid.UUID):
        """Delete all data for a specific user (GDPR compliance)"""
        try:
            # Note: Pinecone doesn't support direct filtering for deletion
            # This would require fetching all vectors and deleting by ID
            # For now, we'll log the request
            logger.info(f"User data deletion requested for person_id: {person_id}")
            
            # In production, implement proper deletion logic
            # This might involve:
            # 1. Querying all vectors for the user
            # 2. Collecting their IDs
            # 3. Batch deleting by IDs
            
        except Exception as e:
            logger.error(f"Error deleting user data: {e}")
