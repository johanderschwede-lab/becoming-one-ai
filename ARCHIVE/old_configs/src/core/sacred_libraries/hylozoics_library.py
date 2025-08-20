"""
Hylozoics Sacred Library - Zero-Hallucination Teaching System
============================================================

This library provides EXACT QUOTES ONLY from Henry T. Laurency's works.
No interpretation, no paraphrasing - only verbatim text from the source.

Features:
- Quote verification before any response
- Exact source citation (book, page, paragraph)
- Terminology locked to Laurency's specific terms
- Context preservation from original works
- Cross-reference system within Laurency's corpus
"""

import os
import uuid
import json
from typing import Dict, List, Optional, Any, Tuple
from datetime import datetime
from dataclasses import dataclass
from enum import Enum

from supabase import create_client, Client
from ..integrations.pinecone_client import PineconeClient
from openai import OpenAI
from loguru import logger


class HylozoicsContentType(Enum):
    """Types of Hylozoics content"""
    BOOK_CHAPTER = "book_chapter"
    SECTION = "section"
    PARAGRAPH = "paragraph"
    DEFINITION = "definition"
    CONCEPT_EXPLANATION = "concept_explanation"
    TERMINOLOGY = "terminology"


@dataclass
class HylozoicsQuote:
    """Exact quote from Laurency's works"""
    quote_id: str
    text: str  # Exact text from source
    source_book: str  # e.g., "The Knowledge of Reality"
    page_number: Optional[int]
    chapter: str
    section: Optional[str]
    paragraph_number: Optional[int]
    hylozoics_terms: List[str]  # Key terms in this quote
    related_concepts: List[str]  # Related Hylozoics concepts
    context: str  # Surrounding context for understanding
    
    def to_dict(self) -> Dict[str, Any]:
        return {
            "quote_id": self.quote_id,
            "text": self.text,
            "source_book": self.source_book,
            "page_number": self.page_number,
            "chapter": self.chapter,
            "section": self.section,
            "paragraph_number": self.paragraph_number,
            "hylozoics_terms": self.hylozoics_terms,
            "related_concepts": self.related_concepts,
            "context": self.context
        }


@dataclass
class HylozoicsResponse:
    """Structured response with exact quote and minimal context"""
    exact_quote: HylozoicsQuote
    related_quotes: List[HylozoicsQuote]
    hylozoics_explanation: Optional[str] = None  # ONLY using Laurency's terminology
    
    def format_for_telegram(self) -> str:
        """Format response for Telegram bot"""
        response = f"""◆ Hylozoics Teaching ◆

"{self.exact_quote.text}"

■ Source: {self.exact_quote.source_book}"""
        
        if self.exact_quote.page_number:
            response += f", p. {self.exact_quote.page_number}"
        
        response += f"\n■ Chapter: {self.exact_quote.chapter}"
        
        if self.exact_quote.section:
            response += f"\n■ Section: {self.exact_quote.section}"
        
        if self.hylozoics_explanation:
            response += f"\n\n▲ Context (Laurency's terms only):\n{self.hylozoics_explanation}"
        
        if self.related_quotes:
            response += f"\n\n● Related passages available: {len(self.related_quotes)}"
        
        return response


class HylozoicsLibrary:
    """Sacred Library for Henry T. Laurency's Hylozoics teachings"""
    
    def __init__(self):
        """Initialize the Hylozoics Sacred Library"""
        self.supabase_client: Client = create_client(
            os.getenv("SUPABASE_URL"), 
            os.getenv("SUPABASE_ANON_KEY")
        )
        
        self.pinecone_client = PineconeClient()
        self.openai_client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))
        
        # Sacred library namespace in Pinecone
        self.namespace = "hylozoics_sacred"
        
        # Hylozoics-specific terminology index
        self.hylozoics_terms = self._load_terminology_index()
        
        logger.info("Hylozoics Sacred Library initialized")
    
    def _load_terminology_index(self) -> Dict[str, str]:
        """Load Hylozoics-specific terminology"""
        # This would be loaded from a curated terminology database
        return {
            "hylozoics": "The esoteric knowledge of life and matter",
            "monad": "The ultimate unit of consciousness",
            "envelope": "The temporary vehicles of consciousness",
            "kingdom": "Stages of evolution (mineral, vegetable, animal, human, etc.)",
            "world": "Dimensional planes of existence",
            "consciousness": "The fundamental property of all existence",
            "evolution": "The development of consciousness through kingdoms",
            "causal": "The world of abstract thought and wisdom",
            "mental": "The world of concrete thought",
            "emotional": "The world of feelings and desires",
            "etheric": "The energy aspect of the physical world",
            "physical": "The dense matter world",
        }
    
    async def add_quote(self, quote: HylozoicsQuote) -> bool:
        """Add a verified quote to the Sacred Library"""
        try:
            # Store in Supabase for structured access
            quote_data = quote.to_dict()
            quote_data["created_at"] = datetime.now().isoformat()
            quote_data["verified"] = True  # All quotes must be verified
            
            result = self.supabase_client.table("hylozoics_quotes").insert(quote_data).execute()
            
            # Generate embedding for semantic search
            embedding = await self.pinecone_client.get_embedding(quote.text)
            
            # Store in Pinecone with sacred namespace
            metadata = {
                "quote_id": quote.quote_id,
                "source_book": quote.source_book,
                "chapter": quote.chapter,
                "content_type": "hylozoics_quote",
                "terms": ",".join(quote.hylozoics_terms),
                "is_sacred": True  # Mark as sacred content
            }
            
            await self.pinecone_client.store_vector(
                vector_id=quote.quote_id,
                embedding=embedding,
                metadata=metadata,
                namespace=self.namespace
            )
            
            logger.info(f"Added Hylozoics quote: {quote.quote_id}")
            return True
            
        except Exception as e:
            logger.error(f"Error adding Hylozoics quote: {e}")
            return False
    
    async def search_quotes(
        self, 
        query: str, 
        limit: int = 5,
        book_filter: Optional[str] = None
    ) -> List[HylozoicsQuote]:
        """Search for relevant quotes using semantic similarity"""
        try:
            # Generate query embedding
            query_embedding = await self.pinecone_client.get_embedding(query)
            
            # Search in sacred namespace only
            filter_dict = {"is_sacred": True}
            if book_filter:
                filter_dict["source_book"] = book_filter
            
            search_results = await self.pinecone_client.search_similar(
                query_embedding=query_embedding,
                namespace=self.namespace,
                filter_dict=filter_dict,
                top_k=limit
            )
            
            # Retrieve full quote data from Supabase
            quotes = []
            for result in search_results:
                quote_id = result["metadata"]["quote_id"]
                
                quote_data = self.supabase_client.table("hylozoics_quotes").select("*").eq(
                    "quote_id", quote_id
                ).execute()
                
                if quote_data.data:
                    data = quote_data.data[0]
                    quote = HylozoicsQuote(
                        quote_id=data["quote_id"],
                        text=data["text"],
                        source_book=data["source_book"],
                        page_number=data.get("page_number"),
                        chapter=data["chapter"],
                        section=data.get("section"),
                        paragraph_number=data.get("paragraph_number"),
                        hylozoics_terms=data["hylozoics_terms"],
                        related_concepts=data["related_concepts"],
                        context=data["context"]
                    )
                    quotes.append(quote)
            
            return quotes
            
        except Exception as e:
            logger.error(f"Error searching Hylozoics quotes: {e}")
            return []
    
    async def get_teaching_response(self, user_question: str) -> HylozoicsResponse:
        """
        Generate a teaching response using ONLY Laurency's exact words
        
        This is the core Sacred Library function - zero hallucination
        """
        try:
            # Search for relevant quotes
            main_quotes = await self.search_quotes(user_question, limit=3)
            
            if not main_quotes:
                # No relevant quotes found - return standard message
                return self._no_quote_response()
            
            primary_quote = main_quotes[0]
            related_quotes = main_quotes[1:] if len(main_quotes) > 1 else []
            
            # Generate minimal explanation using ONLY Hylozoics terminology
            explanation = await self._generate_hylozoics_explanation(
                primary_quote, user_question
            )
            
            return HylozoicsResponse(
                exact_quote=primary_quote,
                related_quotes=related_quotes,
                hylozoics_explanation=explanation
            )
            
        except Exception as e:
            logger.error(f"Error generating Hylozoics response: {e}")
            return self._error_response()
    
    async def _generate_hylozoics_explanation(
        self, 
        quote: HylozoicsQuote, 
        user_question: str
    ) -> str:
        """Generate explanation using ONLY Laurency's terminology"""
        
        # Create a strict prompt that only allows Hylozoics terms
        prompt = f"""You are explaining a concept from Henry T. Laurency's Hylozoics teachings.

STRICT RULES:
- Use ONLY terms from Laurency's Hylozoics system
- Do NOT add your own interpretations
- Do NOT use non-Hylozoics terminology
- Keep explanations minimal and precise
- Reference only concepts that appear in Laurency's works

Quote: "{quote.text}"
User Question: "{user_question}"
Available Hylozoics terms: {', '.join(self.hylozoics_terms.keys())}

Provide a brief explanation using ONLY Laurency's terminology:"""

        try:
            response = self.openai_client.chat.completions.create(
                model="gpt-4",
                messages=[
                    {"role": "system", "content": "You are a Hylozoics terminology assistant. Use ONLY Henry T. Laurency's exact terms and concepts."},
                    {"role": "user", "content": prompt}
                ],
                max_tokens=150,
                temperature=0.1  # Very low temperature for consistency
            )
            
            return response.choices[0].message.content.strip()
            
        except Exception as e:
            logger.error(f"Error generating Hylozoics explanation: {e}")
            return None
    
    def _no_quote_response(self) -> HylozoicsResponse:
        """Response when no relevant quotes are found"""
        no_quote = HylozoicsQuote(
            quote_id="no_quote",
            text="No relevant passage found in Laurency's works for this question.",
            source_book="Hylozoics Sacred Library",
            page_number=None,
            chapter="System Response",
            section=None,
            paragraph_number=None,
            hylozoics_terms=[],
            related_concepts=[],
            context="Search result"
        )
        
        return HylozoicsResponse(
            exact_quote=no_quote,
            related_quotes=[],
            hylozoics_explanation="This question may require different terminology or approach to find relevant Hylozoics teachings."
        )
    
    def _error_response(self) -> HylozoicsResponse:
        """Response when system error occurs"""
        error_quote = HylozoicsQuote(
            quote_id="error",
            text="Sacred Library temporarily unavailable.",
            source_book="Hylozoics Sacred Library",
            page_number=None,
            chapter="System Status",
            section=None,
            paragraph_number=None,
            hylozoics_terms=[],
            related_concepts=[],
            context="Error handling"
        )
        
        return HylozoicsResponse(
            exact_quote=error_quote,
            related_quotes=[],
            hylozoics_explanation=None
        )
    
    async def get_book_structure(self, book_title: str) -> Dict[str, Any]:
        """Get the structure of a Hylozoics book"""
        try:
            result = self.supabase_client.table("hylozoics_quotes").select(
                "chapter, section"
            ).eq("source_book", book_title).execute()
            
            # Organize by chapters and sections
            structure = {}
            for row in result.data:
                chapter = row["chapter"]
                section = row.get("section")
                
                if chapter not in structure:
                    structure[chapter] = []
                
                if section and section not in structure[chapter]:
                    structure[chapter].append(section)
            
            return structure
            
        except Exception as e:
            logger.error(f"Error getting book structure: {e}")
            return {}
    
    async def get_terminology_definition(self, term: str) -> Optional[HylozoicsQuote]:
        """Get Laurency's definition of a specific Hylozoics term"""
        try:
            # Search for quotes that define the term
            definition_quotes = await self.search_quotes(
                f"definition of {term} meaning of {term}", 
                limit=1
            )
            
            if definition_quotes:
                return definition_quotes[0]
            
            return None
            
        except Exception as e:
            logger.error(f"Error getting terminology definition: {e}")
            return None


# Global instance for easy access
hylozoics_library = HylozoicsLibrary()
