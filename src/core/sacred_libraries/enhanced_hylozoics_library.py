"""
Enhanced Hylozoics Sacred Library - Dual-Mode System
===================================================

Combines exact quotes (sacred) with AI-powered synthesis (vector insights).
Supports multi-language sources with Swedish originals as authoritative.

Features:
- Sacred Mode: Exact quotes only, zero hallucination
- Vector Mode: AI synthesis and cross-references
- Multi-language support (Swedish, English, German)
- Cross-library concept mapping
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


class Language(Enum):
    """Supported languages"""
    SWEDISH = "sv"      # Original/Authoritative
    ENGLISH = "en"      # Primary translation
    GERMAN = "de"       # Secondary translation


class ResponseMode(Enum):
    """Response modes for the library"""
    SACRED_ONLY = "sacred_only"           # Only exact quotes
    VECTOR_ONLY = "vector_only"           # Only AI synthesis
    DUAL_MODE = "dual_mode"               # Both sacred + vector
    CROSS_LIBRARY = "cross_library"       # Multiple libraries


@dataclass
class MultiLanguageQuote:
    """Quote with multi-language support"""
    quote_id: str
    original_text: str              # Swedish original
    original_language: Language
    translations: Dict[Language, str] # Translations by language
    source_book: str
    page_number: Optional[int]
    chapter: str
    section: Optional[str]
    hylozoics_terms: List[str]
    key_untranslatable_terms: List[str]  # Terms that don't translate well
    translation_notes: Dict[Language, str]  # Translation context notes
    
    def get_text(self, language: Language = Language.ENGLISH) -> str:
        """Get text in specified language"""
        if language == self.original_language:
            return self.original_text
        return self.translations.get(language, self.original_text)
    
    def get_citation(self, language: Language = Language.ENGLISH) -> str:
        """Get formatted citation"""
        lang_flag = {"sv": "🇸🇪", "en": "🇬🇧", "de": "🇩🇪"}.get(language.value, "")
        
        citation = f"{lang_flag} {self.source_book}"
        if self.page_number:
            citation += f", p. {self.page_number}"
        citation += f"\n■ Chapter: {self.chapter}"
        
        if language != self.original_language:
            citation += f"\n■ Original: Swedish (Authoritative)"
            
        return citation


@dataclass
class VectorInsight:
    """AI-generated insights from vector analysis"""
    concept_connections: List[str]      # Related concepts found
    cross_references: List[str]         # Other relevant quotes
    synthesis_summary: str              # AI synthesis of the concept
    study_suggestions: List[str]        # Recommended follow-up reading
    confidence_score: float             # AI confidence in analysis
    
    def format_for_display(self) -> str:
        """Format insights for user display"""
        text = "▲ VECTOR INSIGHTS ▲\n\n"
        
        if self.concept_connections:
            text += f"● Related Concepts:\n"
            for concept in self.concept_connections[:3]:  # Limit to top 3
                text += f"  • {concept}\n"
            text += "\n"
        
        if self.synthesis_summary:
            text += f"● AI Synthesis:\n{self.synthesis_summary}\n\n"
        
        if self.study_suggestions:
            text += f"● Further Study:\n"
            for suggestion in self.study_suggestions[:2]:  # Limit to top 2
                text += f"  • {suggestion}\n"
        
        if self.confidence_score < 0.7:
            text += f"\n⚠️ Note: Analysis confidence {self.confidence_score:.1%}"
        
        return text


@dataclass
class DualModeResponse:
    """Combined sacred quote + vector insights"""
    sacred_quote: MultiLanguageQuote
    vector_insights: Optional[VectorInsight]
    related_quotes: List[MultiLanguageQuote]
    response_mode: ResponseMode
    language: Language = Language.ENGLISH
    
    def format_for_telegram(self) -> str:
        """Format complete response for Telegram"""
        response = "◆ HYLOZOICS TEACHING ◆\n\n"
        
        # Sacred quote section
        if self.language != Language.SWEDISH:
            # Show Swedish original first for authenticity
            response += f"🇸🇪 **Original (Swedish):**\n\"{self.sacred_quote.original_text}\"\n\n"
        
        # Main quote in requested language
        lang_flag = {"sv": "🇸🇪", "en": "🇬🇧", "de": "🇩🇪"}.get(self.language.value, "🇬🇧")
        response += f"{lang_flag} **Translation:**\n\"{self.sacred_quote.get_text(self.language)}\"\n\n"
        
        # Citation
        response += self.sacred_quote.get_citation(self.language) + "\n\n"
        
        # Untranslatable terms note
        if self.sacred_quote.key_untranslatable_terms and self.language != Language.SWEDISH:
            response += f"📝 **Key Terms**: {', '.join(self.sacred_quote.key_untranslatable_terms)}\n"
            response += "(Some Hylozoics terms have no direct translation)\n\n"
        
        # Vector insights section
        if self.vector_insights and self.response_mode in [ResponseMode.DUAL_MODE, ResponseMode.VECTOR_ONLY]:
            response += self.vector_insights.format_for_display()
        
        # Related quotes indicator
        if self.related_quotes:
            response += f"\n● {len(self.related_quotes)} related passages available"
        
        return response


class EnhancedHylozoicsLibrary:
    """Enhanced Sacred Library with dual-mode responses and multi-language support"""
    
    def __init__(self):
        """Initialize the enhanced library"""
        self.supabase_client: Client = create_client(
            os.getenv("SUPABASE_URL"), 
            os.getenv("SUPABASE_ANON_KEY")
        )
        
        self.pinecone_client = PineconeClient()
        self.openai_client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))
        
        # Namespace for sacred quotes (exact)
        self.sacred_namespace = "hylozoics_sacred"
        # Namespace for vector synthesis (AI analysis)
        self.vector_namespace = "hylozoics_vector"
        
        # Load term mappings and translation data
        self.term_mappings = self._load_term_mappings()
        self.untranslatable_terms = self._load_untranslatable_terms()
        
        logger.info("Enhanced Hylozoics Library initialized with dual-mode support")
    
    def _load_term_mappings(self) -> Dict[str, Dict[str, str]]:
        """Load cross-language term mappings"""
        return {
            "medvetenhet": {
                "en": "consciousness",
                "de": "Bewusstsein",
                "concept": "fundamental property of all existence"
            },
            "monad": {
                "en": "monad", 
                "de": "Monade",
                "concept": "ultimate unit of consciousness"
            },
            "hölje": {
                "en": "envelope",
                "de": "Hülle", 
                "concept": "temporary vehicle of consciousness"
            },
            "rike": {
                "en": "kingdom",
                "de": "Reich",
                "concept": "stage of evolutionary development"
            }
        }
    
    def _load_untranslatable_terms(self) -> List[str]:
        """Terms that lose meaning in translation"""
        return [
            "hylozoik",      # The system itself
            "monad",         # Preserved across languages
            "kausalvärld",   # Causal world - concept doesn't translate well
            "mentalvärld",   # Mental world - similar issue
        ]
    
    async def get_teaching_response(
        self, 
        user_question: str,
        response_mode: ResponseMode = ResponseMode.DUAL_MODE,
        language: Language = Language.ENGLISH
    ) -> DualModeResponse:
        """
        Get teaching response with dual-mode capability
        
        Args:
            user_question: User's question
            response_mode: SACRED_ONLY, VECTOR_ONLY, or DUAL_MODE
            language: Preferred response language
        """
        try:
            # Step 1: Find relevant sacred quote
            sacred_quotes = await self._search_sacred_quotes(user_question, limit=3)
            
            if not sacred_quotes:
                return self._no_quote_response(language)
            
            primary_quote = sacred_quotes[0]
            related_quotes = sacred_quotes[1:] if len(sacred_quotes) > 1 else []
            
            # Step 2: Generate vector insights if requested
            vector_insights = None
            if response_mode in [ResponseMode.DUAL_MODE, ResponseMode.VECTOR_ONLY]:
                vector_insights = await self._generate_vector_insights(
                    primary_quote, user_question, related_quotes
                )
            
            return DualModeResponse(
                sacred_quote=primary_quote,
                vector_insights=vector_insights,
                related_quotes=related_quotes,
                response_mode=response_mode,
                language=language
            )
            
        except Exception as e:
            logger.error(f"Error generating dual-mode response: {e}")
            return self._error_response(language)
    
    async def _search_sacred_quotes(
        self, 
        query: str, 
        limit: int = 3
    ) -> List[MultiLanguageQuote]:
        """Search for exact quotes in sacred namespace"""
        try:
            # Generate query embedding
            query_embedding = await self.pinecone_client.get_embedding(query)
            
            # Search in sacred namespace only
            search_results = await self.pinecone_client.search_similar(
                query_embedding=query_embedding,
                namespace=self.sacred_namespace,
                filter_dict={"is_sacred": True},
                top_k=limit
            )
            
            # Retrieve full quote data from Supabase
            quotes = []
            for result in search_results:
                quote_id = result["metadata"]["quote_id"]
                
                quote_data = self.supabase_client.table("hylozoics_multilang_quotes").select("*").eq(
                    "quote_id", quote_id
                ).execute()
                
                if quote_data.data:
                    data = quote_data.data[0]
                    quote = MultiLanguageQuote(
                        quote_id=data["quote_id"],
                        original_text=data["original_text"],
                        original_language=Language.SWEDISH,
                        translations={
                            Language.ENGLISH: data.get("english_translation", ""),
                            Language.GERMAN: data.get("german_translation", "")
                        },
                        source_book=data["source_book"],
                        page_number=data.get("page_number"),
                        chapter=data["chapter"],
                        section=data.get("section"),
                        hylozoics_terms=data["hylozoics_terms"],
                        key_untranslatable_terms=data.get("untranslatable_terms", []),
                        translation_notes={
                            Language.ENGLISH: data.get("english_notes", ""),
                            Language.GERMAN: data.get("german_notes", "")
                        }
                    )
                    quotes.append(quote)
            
            return quotes
            
        except Exception as e:
            logger.error(f"Error searching sacred quotes: {e}")
            return []
    
    async def _generate_vector_insights(
        self,
        primary_quote: MultiLanguageQuote,
        user_question: str,
        related_quotes: List[MultiLanguageQuote]
    ) -> VectorInsight:
        """Generate AI insights using vector analysis"""
        try:
            # Search vector namespace for broader context
            query_embedding = await self.pinecone_client.get_embedding(user_question)
            
            vector_results = await self.pinecone_client.search_similar(
                query_embedding=query_embedding,
                namespace=self.vector_namespace,
                top_k=10
            )
            
            # Create context for AI synthesis
            context_texts = [primary_quote.original_text, primary_quote.get_text(Language.ENGLISH)]
            context_texts.extend([q.get_text(Language.ENGLISH) for q in related_quotes])
            
            # Add vector search results for broader context
            for result in vector_results[:5]:  # Top 5 for context
                if "text" in result["metadata"]:
                    context_texts.append(result["metadata"]["text"])
            
            # Generate synthesis using OpenAI
            synthesis_prompt = f"""You are analyzing Hylozoics teachings by Henry T. Laurency.

Primary Quote: "{primary_quote.get_text(Language.ENGLISH)}"
User Question: "{user_question}"

Context from Hylozoics corpus:
{chr(10).join(context_texts[:8])}  # Limit context

Provide insights in this JSON format:
{{
    "concept_connections": ["related concept 1", "related concept 2", "related concept 3"],
    "synthesis_summary": "Brief synthesis of how this concept fits in Hylozoics system (max 100 words)",
    "study_suggestions": ["suggestion 1", "suggestion 2"],
    "confidence_score": 0.85
}}

Use ONLY Hylozoics terminology. Be concise and accurate."""

            response = self.openai_client.chat.completions.create(
                model="gpt-4",
                messages=[
                    {"role": "system", "content": "You are a Hylozoics analysis assistant. Provide structured insights using only Laurency's terminology."},
                    {"role": "user", "content": synthesis_prompt}
                ],
                max_tokens=300,
                temperature=0.2  # Low temperature for consistency
            )
            
            # Parse JSON response
            try:
                insights_data = json.loads(response.choices[0].message.content)
                
                return VectorInsight(
                    concept_connections=insights_data.get("concept_connections", []),
                    cross_references=[],  # Could be populated from vector results
                    synthesis_summary=insights_data.get("synthesis_summary", ""),
                    study_suggestions=insights_data.get("study_suggestions", []),
                    confidence_score=insights_data.get("confidence_score", 0.5)
                )
                
            except json.JSONDecodeError:
                # Fallback if JSON parsing fails
                return VectorInsight(
                    concept_connections=[],
                    cross_references=[],
                    synthesis_summary="Analysis temporarily unavailable",
                    study_suggestions=[],
                    confidence_score=0.3
                )
            
        except Exception as e:
            logger.error(f"Error generating vector insights: {e}")
            return VectorInsight(
                concept_connections=[],
                cross_references=[],
                synthesis_summary="Insights temporarily unavailable",
                study_suggestions=[],
                confidence_score=0.0
            )
    
    async def add_multilang_quote(self, quote: MultiLanguageQuote) -> bool:
        """Add a multi-language quote to both sacred and vector stores"""
        try:
            # Store in Supabase
            quote_data = {
                "quote_id": quote.quote_id,
                "original_text": quote.original_text,
                "original_language": quote.original_language.value,
                "english_translation": quote.translations.get(Language.ENGLISH, ""),
                "german_translation": quote.translations.get(Language.GERMAN, ""),
                "source_book": quote.source_book,
                "page_number": quote.page_number,
                "chapter": quote.chapter,
                "section": quote.section,
                "hylozoics_terms": quote.hylozoics_terms,
                "untranslatable_terms": quote.key_untranslatable_terms,
                "english_notes": quote.translation_notes.get(Language.ENGLISH, ""),
                "german_notes": quote.translation_notes.get(Language.GERMAN, ""),
                "created_at": datetime.now().isoformat(),
                "verified": True
            }
            
            result = self.supabase_client.table("hylozoics_multilang_quotes").insert(quote_data).execute()
            
            # Store in both Pinecone namespaces
            # Sacred namespace: exact quote for retrieval
            sacred_embedding = await self.pinecone_client.get_embedding(quote.original_text)
            await self.pinecone_client.store_vector(
                vector_id=f"{quote.quote_id}_sacred",
                embedding=sacred_embedding,
                metadata={
                    "quote_id": quote.quote_id,
                    "source_book": quote.source_book,
                    "is_sacred": True,
                    "language": "swedish"
                },
                namespace=self.sacred_namespace
            )
            
            # Vector namespace: for AI analysis and synthesis
            english_text = quote.get_text(Language.ENGLISH)
            vector_embedding = await self.pinecone_client.get_embedding(english_text)
            await self.pinecone_client.store_vector(
                vector_id=f"{quote.quote_id}_vector",
                embedding=vector_embedding,
                metadata={
                    "quote_id": quote.quote_id,
                    "text": english_text,
                    "concepts": ",".join(quote.hylozoics_terms),
                    "is_vector": True,
                    "language": "english"
                },
                namespace=self.vector_namespace
            )
            
            logger.info(f"Added multilingual quote: {quote.quote_id}")
            return True
            
        except Exception as e:
            logger.error(f"Error adding multilingual quote: {e}")
            return False
    
    def _no_quote_response(self, language: Language) -> DualModeResponse:
        """Response when no quotes found"""
        no_quote = MultiLanguageQuote(
            quote_id="no_quote",
            original_text="Ingen relevant passage hittades i Laurencys verk för denna fråga.",
            original_language=Language.SWEDISH,
            translations={
                Language.ENGLISH: "No relevant passage found in Laurency's works for this question.",
                Language.GERMAN: "Keine relevante Passage in Laurencys Werken für diese Frage gefunden."
            },
            source_book="Hylozoics Sacred Library",
            page_number=None,
            chapter="System Response",
            section=None,
            hylozoics_terms=[],
            key_untranslatable_terms=[],
            translation_notes={}
        )
        
        return DualModeResponse(
            sacred_quote=no_quote,
            vector_insights=None,
            related_quotes=[],
            response_mode=ResponseMode.SACRED_ONLY,
            language=language
        )
    
    def _error_response(self, language: Language) -> DualModeResponse:
        """Response when system error occurs"""
        error_quote = MultiLanguageQuote(
            quote_id="error",
            original_text="Hylozoiska biblioteket är tillfälligt otillgängligt.",
            original_language=Language.SWEDISH,
            translations={
                Language.ENGLISH: "Hylozoics library temporarily unavailable.",
                Language.GERMAN: "Hylozoische Bibliothek vorübergehend nicht verfügbar."
            },
            source_book="Hylozoics Sacred Library",
            page_number=None,
            chapter="System Status",
            section=None,
            hylozoics_terms=[],
            key_untranslatable_terms=[],
            translation_notes={}
        )
        
        return DualModeResponse(
            sacred_quote=error_quote,
            vector_insights=None,
            related_quotes=[],
            response_mode=ResponseMode.SACRED_ONLY,
            language=language
        )


# Global instance for easy access
enhanced_hylozoics_library = EnhancedHylozoicsLibrary()
