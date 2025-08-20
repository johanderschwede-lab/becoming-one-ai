"""
Becoming One™ Knowledge Management System
========================================

This system manages the upload, storage, retrieval, and expansion of your core IP:
- Schaubilder (20+ wisdom models)
- Master prompts and AI instructions
- Teaching materials and methods
- Human-generated answers for continuous learning

Architecture:
- Pinecone: Vector embeddings for semantic search
- Supabase: Structured metadata, relationships, and source tracking
- Content pipeline: Processing, chunking, and quality control
"""

import os
import uuid
import json
import hashlib
from typing import Dict, List, Optional, Any, Tuple
from datetime import datetime
from dataclasses import dataclass, field
from enum import Enum

import pinecone
from supabase import create_client, Client
from openai import OpenAI
import tiktoken


class ContentType(Enum):
    """Types of content in the knowledge base"""
    SCHAUBILD = "schaubild"
    MASTER_PROMPT = "master_prompt"
    TEACHING_MATERIAL = "teaching_material"
    METHOD_DESCRIPTION = "method_description"
    HUMAN_GENERATED_ANSWER = "human_generated_answer"
    AI_INSTRUCTION = "ai_instruction"
    PROTOCOL = "protocol"
    CASE_STUDY = "case_study"


class ContentSource(Enum):
    """Where content originated"""
    JOHAN_ORIGINAL = "johan_original"
    MARIANNE_ORIGINAL = "marianne_original"
    WORKSHOP_RECORDING = "workshop_recording"
    PRESENTATION_TRANSCRIPT = "presentation_transcript"
    HUMAN_INTERACTION = "human_interaction"
    AI_GENERATED = "ai_generated"


@dataclass
class ContentChunk:
    """A processed chunk of content ready for embedding"""
    chunk_id: str
    content: str
    content_type: ContentType
    source: ContentSource
    metadata: Dict[str, Any]
    embedding: Optional[List[float]] = None
    token_count: int = 0
    created_at: datetime = field(default_factory=datetime.now)


@dataclass
class SchaubildMeta:
    """Metadata for a Schaubild"""
    schaubild_id: str
    title: str
    description: str
    concepts: List[str]
    feeling_states: List[str]
    anchor_types: List[str]
    difficulty_level: int  # 1-10
    prerequisites: List[str]
    related_schaubilder: List[str]


class BecomingOneKnowledgeSystem:
    """
    Complete knowledge management system for Becoming One™ IP
    """
    
    def __init__(self):
        self.openai_client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))
        self.supabase_client: Client = create_client(
            os.getenv("SUPABASE_URL"), 
            os.getenv("SUPABASE_ANON_KEY")
        )
        
        # Initialize Pinecone
        pinecone.init(
            api_key=os.getenv("PINECONE_API_KEY"),
            environment=os.getenv("PINECONE_ENVIRONMENT")
        )
        self.pinecone_index = pinecone.Index(os.getenv("PINECONE_INDEX_NAME"))
        
        # Token counter for chunking
        self.tokenizer = tiktoken.get_encoding("cl100k_base")
        
        # Chunk size for embeddings (optimal for retrieval)
        self.chunk_size = 500  # tokens
        self.chunk_overlap = 50  # tokens
    
    async def upload_schaubild(
        self, 
        title: str, 
        content: str, 
        metadata: Dict[str, Any]
    ) -> str:
        """
        Upload a Schaubild to the knowledge system
        
        Returns:
            schaubild_id: Unique identifier for the uploaded Schaubild
        """
        schaubild_id = str(uuid.uuid4())
        
        # 1. Store master record in Supabase
        schaubild_record = {
            "schaubild_id": schaubild_id,
            "title": title,
            "content_hash": hashlib.sha256(content.encode()).hexdigest(),
            "metadata": metadata,
            "upload_date": datetime.now().isoformat(),
            "status": "processing"
        }
        
        await self._store_in_supabase("schaubilder", schaubild_record)
        
        # 2. Process content into chunks
        chunks = await self._process_content_into_chunks(
            content=content,
            content_type=ContentType.SCHAUBILD,
            source=ContentSource.JOHAN_ORIGINAL,
            parent_id=schaubild_id,
            metadata=metadata
        )
        
        # 3. Generate embeddings and store in Pinecone
        await self._store_chunks_in_pinecone(chunks)
        
        # 4. Update status
        await self._update_supabase_status(schaubild_id, "active")
        
        print(f"✅ Schaubild '{title}' uploaded successfully: {schaubild_id}")
        return schaubild_id
    
    async def upload_master_prompt(
        self, 
        prompt_name: str, 
        prompt_content: str, 
        context: Dict[str, Any]
    ) -> str:
        """Upload master prompts and AI instructions"""
        prompt_id = str(uuid.uuid4())
        
        # Store in both structured (Supabase) and vector (Pinecone) format
        prompt_record = {
            "prompt_id": prompt_id,
            "name": prompt_name,
            "content": prompt_content,
            "context": context,
            "upload_date": datetime.now().isoformat(),
            "version": 1
        }
        
        await self._store_in_supabase("master_prompts", prompt_record)
        
        # Create embedding for semantic retrieval
        chunks = await self._process_content_into_chunks(
            content=prompt_content,
            content_type=ContentType.MASTER_PROMPT,
            source=ContentSource.JOHAN_ORIGINAL,
            parent_id=prompt_id,
            metadata={"name": prompt_name, **context}
        )
        
        await self._store_chunks_in_pinecone(chunks)
        
        print(f"✅ Master prompt '{prompt_name}' uploaded: {prompt_id}")
        return prompt_id
    
    async def add_human_generated_answer(
        self,
        question: str,
        answer: str,
        context: Dict[str, Any],
        source_person: str = "johan"
    ) -> str:
        """
        Add human-generated answers to expand the knowledge base
        This creates a feedback loop for continuous learning
        """
        answer_id = str(uuid.uuid4())
        
        # Store the Q&A pair
        qa_record = {
            "answer_id": answer_id,
            "question": question,
            "answer": answer,
            "source_person": source_person,
            "context": context,
            "created_date": datetime.now().isoformat(),
            "validation_status": "pending"  # Human review before activation
        }
        
        await self._store_in_supabase("human_generated_answers", qa_record)
        
        # Create embeddings for both question and answer
        qa_content = f"Question: {question}\n\nAnswer: {answer}"
        
        chunks = await self._process_content_into_chunks(
            content=qa_content,
            content_type=ContentType.HUMAN_GENERATED_ANSWER,
            source=ContentSource.HUMAN_INTERACTION,
            parent_id=answer_id,
            metadata={
                "source_person": source_person,
                "question": question,
                **context
            }
        )
        
        await self._store_chunks_in_pinecone(chunks)
        
        print(f"✅ Human answer added for review: {answer_id}")
        return answer_id
    
    async def query_knowledge_base(
        self,
        query: str,
        content_types: Optional[List[ContentType]] = None,
        top_k: int = 5
    ) -> List[Dict[str, Any]]:
        """
        Query the knowledge base for relevant content
        This is what the AI uses to generate responses
        """
        # 1. Generate query embedding
        query_embedding = await self._generate_embedding(query)
        
        # 2. Build filter for content types
        filter_dict = {}
        if content_types:
            filter_dict["content_type"] = {"$in": [ct.value for ct in content_types]}
        
        # 3. Search Pinecone
        search_results = self.pinecone_index.query(
            vector=query_embedding,
            top_k=top_k,
            include_metadata=True,
            filter=filter_dict
        )
        
        # 4. Enrich with Supabase data
        enriched_results = []
        for match in search_results.matches:
            chunk_data = {
                "content": match.metadata.get("content", ""),
                "score": match.score,
                "content_type": match.metadata.get("content_type"),
                "source": match.metadata.get("source"),
                "parent_id": match.metadata.get("parent_id"),
                "metadata": match.metadata
            }
            
            # Get additional context from Supabase if needed
            if match.metadata.get("parent_id"):
                parent_context = await self._get_parent_context(
                    match.metadata["parent_id"],
                    match.metadata["content_type"]
                )
                chunk_data["parent_context"] = parent_context
            
            enriched_results.append(chunk_data)
        
        return enriched_results
    
    async def generate_becoming_one_response(
        self,
        user_query: str,
        user_context: Dict[str, Any]
    ) -> Dict[str, Any]:
        """
        Generate response using ONLY Becoming One™ knowledge base
        No hallucinations - only sourced content
        """
        # 1. Search knowledge base
        relevant_chunks = await self.query_knowledge_base(
            query=user_query,
            content_types=[
                ContentType.SCHAUBILD,
                ContentType.TEACHING_MATERIAL,
                ContentType.METHOD_DESCRIPTION,
                ContentType.HUMAN_GENERATED_ANSWER
            ],
            top_k=8
        )
        
        if not relevant_chunks:
            return {
                "response": "I don't have specific Becoming One™ knowledge to answer that question yet. This is an opportunity to add to our knowledge base.",
                "sources": [],
                "confidence": 0.0,
                "needs_human_input": True
            }
        
        # 2. Get master prompt for response generation
        master_prompts = await self.query_knowledge_base(
            query="becoming one response generation",
            content_types=[ContentType.MASTER_PROMPT],
            top_k=2
        )
        
        # 3. Construct prompt with sources
        source_content = "\n\n".join([
            f"Source {i+1} (Score: {chunk['score']:.3f}):\n{chunk['content']}"
            for i, chunk in enumerate(relevant_chunks)
        ])
        
        system_prompt = self._get_system_prompt(master_prompts)
        
        user_prompt = f"""
        User Query: {user_query}
        
        User Context: {json.dumps(user_context, indent=2)}
        
        Relevant Becoming One™ Knowledge:
        {source_content}
        
        Instructions:
        1. Answer ONLY using the provided Becoming One™ knowledge
        2. If the knowledge doesn't fully answer the question, say so
        3. Apply the anti-bypass framework - no spiritual bypassing
        4. Focus on feeling-states, anchors, and practical application
        5. Cite which sources you're drawing from
        """
        
        # 4. Generate response
        response = await self.openai_client.chat.completions.create(
            model="gpt-4-turbo-preview",
            messages=[
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": user_prompt}
            ],
            temperature=0.7,
            max_tokens=1000
        )
        
        # 5. Extract sources used
        sources_used = [
            {
                "content_type": chunk["content_type"],
                "source": chunk["source"],
                "score": chunk["score"],
                "parent_id": chunk.get("parent_id")
            }
            for chunk in relevant_chunks
        ]
        
        return {
            "response": response.choices[0].message.content,
            "sources": sources_used,
            "confidence": min([chunk["score"] for chunk in relevant_chunks]),
            "needs_human_input": False,
            "query_id": str(uuid.uuid4())  # For tracking and learning
        }
    
    # ========================================================================
    # INTERNAL METHODS
    # ========================================================================
    
    async def _process_content_into_chunks(
        self,
        content: str,
        content_type: ContentType,
        source: ContentSource,
        parent_id: str,
        metadata: Dict[str, Any]
    ) -> List[ContentChunk]:
        """Break content into optimal chunks for embedding"""
        
        # Tokenize content
        tokens = self.tokenizer.encode(content)
        chunks = []
        
        # Split into overlapping chunks
        for i in range(0, len(tokens), self.chunk_size - self.chunk_overlap):
            chunk_tokens = tokens[i:i + self.chunk_size]
            chunk_text = self.tokenizer.decode(chunk_tokens)
            
            chunk_id = f"{parent_id}_{i // (self.chunk_size - self.chunk_overlap)}"
            
            chunk = ContentChunk(
                chunk_id=chunk_id,
                content=chunk_text,
                content_type=content_type,
                source=source,
                metadata={
                    **metadata,
                    "parent_id": parent_id,
                    "chunk_index": i // (self.chunk_size - self.chunk_overlap),
                    "token_count": len(chunk_tokens)
                },
                token_count=len(chunk_tokens)
            )
            
            chunks.append(chunk)
        
        return chunks
    
    async def _generate_embedding(self, text: str) -> List[float]:
        """Generate embedding for text"""
        response = await self.openai_client.embeddings.create(
            model="text-embedding-ada-002",
            input=text
        )
        return response.data[0].embedding
    
    async def _store_chunks_in_pinecone(self, chunks: List[ContentChunk]):
        """Store chunks with embeddings in Pinecone"""
        vectors_to_upsert = []
        
        for chunk in chunks:
            # Generate embedding
            chunk.embedding = await self._generate_embedding(chunk.content)
            
            # Prepare for Pinecone
            vector_data = {
                "id": chunk.chunk_id,
                "values": chunk.embedding,
                "metadata": {
                    "content": chunk.content,
                    "content_type": chunk.content_type.value,
                    "source": chunk.source.value,
                    **chunk.metadata
                }
            }
            vectors_to_upsert.append(vector_data)
        
        # Batch upsert to Pinecone
        self.pinecone_index.upsert(vectors=vectors_to_upsert)
    
    async def _store_in_supabase(self, table: str, record: Dict[str, Any]):
        """Store record in Supabase"""
        result = self.supabase_client.table(table).insert(record).execute()
        return result
    
    async def _update_supabase_status(self, record_id: str, status: str):
        """Update record status in Supabase"""
        # This would update based on the specific table structure
        pass
    
    async def _get_parent_context(self, parent_id: str, content_type: str) -> Dict[str, Any]:
        """Get parent context from Supabase"""
        # Implementation depends on content type
        return {}
    
    def _get_system_prompt(self, master_prompts: List[Dict[str, Any]]) -> str:
        """Construct system prompt from master prompts"""
        if master_prompts:
            return master_prompts[0]["content"]
        
        # Fallback system prompt
        return """
        You are the Becoming One™ AI, embodying Johan and Marianne's methodology.
        
        Core principles:
        - Answer only from provided Becoming One™ knowledge
        - No spiritual bypassing - turn 180° toward feeling
        - Focus on feeling-states as true desires (not external objects)
        - Treat blocks as anchors containing stored energy
        - Use procrastination as portals to transformation
        - Apply anti-bypass framework consistently
        
        If you don't have specific knowledge to answer, say so clearly.
        """


# ========================================================================
# UPLOAD UTILITIES
# ========================================================================

class ContentUploader:
    """Utilities for uploading different types of content"""
    
    def __init__(self, knowledge_system: BecomingOneKnowledgeSystem):
        self.ks = knowledge_system
    
    async def upload_schaubild_from_file(self, file_path: str, metadata: Dict[str, Any]) -> str:
        """Upload a Schaubild from a file"""
        with open(file_path, 'r', encoding='utf-8') as f:
            content = f.read()
        
        title = metadata.get('title', os.path.basename(file_path))
        return await self.ks.upload_schaubild(title, content, metadata)
    
    async def upload_multiple_schaubilder(self, directory_path: str) -> List[str]:
        """Upload all Schaubilder from a directory"""
        uploaded_ids = []
        
        for filename in os.listdir(directory_path):
            if filename.endswith(('.md', '.txt', '.docx')):
                file_path = os.path.join(directory_path, filename)
                
                metadata = {
                    'title': filename.replace('.md', '').replace('.txt', '').replace('.docx', ''),
                    'filename': filename,
                    'upload_batch': datetime.now().isoformat()
                }
                
                schaubild_id = await self.upload_schaubild_from_file(file_path, metadata)
                uploaded_ids.append(schaubild_id)
        
        return uploaded_ids
    
    async def upload_master_prompts_from_config(self, config_file: str) -> List[str]:
        """Upload master prompts from a configuration file"""
        with open(config_file, 'r') as f:
            prompts_config = json.load(f)
        
        uploaded_ids = []
        for prompt_name, prompt_data in prompts_config.items():
            prompt_id = await self.ks.upload_master_prompt(
                prompt_name=prompt_name,
                prompt_content=prompt_data['content'],
                context=prompt_data.get('context', {})
            )
            uploaded_ids.append(prompt_id)
        
        return uploaded_ids


# ========================================================================
# EXAMPLE USAGE
# ========================================================================

async def example_usage():
    """Example of how to use the knowledge management system"""
    
    # Initialize system
    ks = BecomingOneKnowledgeSystem()
    uploader = ContentUploader(ks)
    
    # Upload a Schaubild
    schaubild_id = await ks.upload_schaubild(
        title="The Emotional Anchor Model",
        content="""
        Emotional anchors are stored emotional matter from different life epochs.
        They create energy bonds that must be felt and digested to release their power.
        
        Key concepts:
        - Anchors form in conception, infancy, childhood, school-age, adolescence
        - Each anchor locks up life energy until processed
        - The nervous system protects us from feeling them
        - Processing requires turning 180° toward the feeling
        - Digestion releases energy and creates "pearls" of wisdom
        """,
        metadata={
            "concepts": ["emotional_anchors", "energy_bonds", "life_epochs"],
            "feeling_states": ["safety", "power", "freedom"],
            "difficulty_level": 3
        }
    )
    
    # Query the knowledge base
    results = await ks.query_knowledge_base("How do emotional anchors work?")
    
    # Generate a response
    response = await ks.generate_becoming_one_response(
        user_query="I keep procrastinating on my business. What should I do?",
        user_context={"procrastination_type": "business", "emotional_state": "stuck"}
    )
    
    print("Response:", response["response"])
    print("Sources used:", len(response["sources"]))


    async def upload_teaching_material(
        self,
        title: str,
        content: str,
        material_type: str,
        source_type: str,
        metadata: Dict[str, Any]
    ) -> str:
        """Upload teaching material to knowledge base"""
        material_id = str(uuid.uuid4())
        
        # Store in Supabase
        material_record = {
            "material_id": material_id,
            "title": title,
            "content": content,
            "material_type": material_type,
            "source_type": source_type,
            "metadata": metadata,
            "content_hash": hashlib.sha256(content.encode()).hexdigest(),
            "upload_date": datetime.now().isoformat(),
            "status": "active"
        }
        
        await self._store_in_supabase("teaching_materials", material_record)
        
        # Process into chunks and store in Pinecone
        chunks = await self._process_content_into_chunks(
            content=content,
            content_type=ContentType.TEACHING_MATERIAL,
            source=ContentSource(source_type),
            parent_id=material_id,
            metadata=metadata
        )
        
        await self._store_chunks_in_pinecone(chunks)
        
        return material_id

    async def add_community_content(
        self,
        content: str,
        category: str,
        themes: List[str],
        metadata: Dict[str, Any]
    ) -> str:
        """Add community content (questions, feedback, insights)"""
        content_id = str(uuid.uuid4())
        
        # Store community content
        community_record = {
            "content_id": content_id,
            "content": content,
            "category": category,
            "themes": themes,
            "metadata": metadata,
            "created_date": datetime.now().isoformat()
        }
        
        # Store in community table
        await self._store_in_supabase("community_content", community_record)
        
        return content_id


if __name__ == "__main__":
    import asyncio
    asyncio.run(example_usage())
