"""
Tiered Wisdom Synthesis Engine
=============================

Core engine for multi-library truth synthesis with subscription-based access control.
Generates responses based on user tier: Sacred Source, Cross-Library, or Synthesis Master.
"""

import os
import json
import hashlib
from typing import Dict, List, Optional, Any, Tuple
from datetime import datetime, timedelta
from dataclasses import dataclass
from enum import Enum

from supabase import create_client, Client
from ..integrations.pinecone_client import PineconeClient
from openai import OpenAI
from loguru import logger


class UserTier(Enum):
    """User subscription tiers"""
    SACRED_SOURCE = 1       # Basic: Single library access
    CROSS_LIBRARY = 2       # Premium: Multi-library comparison
    SYNTHESIS_MASTER = 3    # Elite: Complete synthesis + personality integration


class ResponseType(Enum):
    """Types of responses based on tier"""
    SINGLE_LIBRARY = "single_library"
    CROSS_LIBRARY_COMPARISON = "cross_library_comparison"
    COMPLETE_SYNTHESIS = "complete_synthesis"


@dataclass
class UserSubscription:
    """User subscription information"""
    person_id: str
    tier_level: int
    tier_name: str
    monthly_query_limit: int
    queries_used_this_month: int
    cross_library_access: bool
    synthesis_access: bool
    personality_integration: bool
    subscription_active: bool


@dataclass
class SacredQuote:
    """Individual quote from a sacred library"""
    quote_id: str
    text: str
    source_book: str
    chapter: str
    page_number: Optional[int]
    paragraph_number: Optional[int]
    library_name: str
    tradition: str
    language: str = "english"
    citation: str = ""
    
    def get_formatted_citation(self) -> str:
        """Get properly formatted citation"""
        if self.citation:
            return self.citation
        
        citation = f"{self.source_book}"
        if self.chapter:
            citation += f", {self.chapter}"
        if self.page_number:
            citation += f", p. {self.page_number}"
        if self.paragraph_number:
            citation += f", para. {self.paragraph_number}"
        
        return citation


@dataclass
class CrossLibraryAnalysis:
    """Analysis comparing multiple traditions"""
    common_themes: List[str]
    key_differences: Dict[str, str]
    apparent_contradictions: List[str]
    contradiction_explanations: List[str]
    complementary_aspects: List[str]


@dataclass
class SynthesisResponse:
    """Complete synthesis response with all components"""
    query_topic: str
    response_type: ResponseType
    user_tier: UserTier
    
    # Sacred quotes from all relevant libraries
    sacred_quotes: Dict[str, List[SacredQuote]]  # library_name -> quotes
    
    # Cross-library analysis (Tier 2+)
    cross_library_analysis: Optional[CrossLibraryAnalysis] = None
    
    # Complete synthesis (Tier 3 only)
    universal_principle: Optional[str] = None
    synthesis_text: Optional[str] = None
    personality_applications: Optional[Dict[str, str]] = None
    study_path_suggestions: Optional[List[str]] = None
    
    # Metadata
    confidence_score: float = 0.0
    generation_time_ms: int = 0
    libraries_searched: List[str] = None
    
    def format_for_telegram(self) -> str:
        """Format response for Telegram based on user tier"""
        if self.user_tier == UserTier.SACRED_SOURCE:
            return self._format_single_library()
        elif self.user_tier == UserTier.CROSS_LIBRARY:
            return self._format_cross_library()
        else:  # SYNTHESIS_MASTER
            return self._format_complete_synthesis()
    
    def _format_single_library(self) -> str:
        """Format for Tier 1: Single library response"""
        if not self.sacred_quotes:
            return "◆ No relevant quotes found ◆"
        
        # Get first library with quotes
        library_name = next(iter(self.sacred_quotes.keys()))
        quotes = self.sacred_quotes[library_name]
        
        if not quotes:
            return "◆ No relevant quotes found ◆"
        
        primary_quote = quotes[0]
        
        response = f"""◆ {library_name.upper()} TEACHING ◆

"{primary_quote.text}"

■ Source: {primary_quote.get_formatted_citation()}"""
        
        if len(quotes) > 1:
            response += f"\n\n● {len(quotes) - 1} additional passages available"
        
        return response
    
    def _format_cross_library(self) -> str:
        """Format for Tier 2: Cross-library comparison"""
        response = f"◆ {self.query_topic.upper()} ACROSS TRADITIONS ◆\n\n"
        
        # Show quotes from each tradition
        tradition_symbols = {
            "neville": "🔮",
            "scovel_shinn": "✨", 
            "hylozoics": "🌌",
            "fourth_way": "🎭"
        }
        
        for library_name, quotes in self.sacred_quotes.items():
            if quotes:
                symbol = tradition_symbols.get(library_name, "📖")
                primary_quote = quotes[0]
                
                response += f"{symbol} {library_name.upper().replace('_', ' ')}:\n"
                response += f'"{primary_quote.text}"\n'
                response += f"■ Source: {primary_quote.get_formatted_citation()}\n\n"
        
        # Add cross-library analysis
        if self.cross_library_analysis:
            response += "▲ CROSS-TRADITION ANALYSIS ▲\n"
            
            if self.cross_library_analysis.common_themes:
                response += "● Common Themes:\n"
                for theme in self.cross_library_analysis.common_themes[:3]:
                    response += f"  • {theme}\n"
                response += "\n"
            
            if self.cross_library_analysis.key_differences:
                response += "● Key Differences:\n"
                for tradition, difference in list(self.cross_library_analysis.key_differences.items())[:3]:
                    response += f"  • {tradition}: {difference}\n"
                response += "\n"
            
            if self.cross_library_analysis.complementary_aspects:
                response += "● Complementary Aspects:\n"
                for aspect in self.cross_library_analysis.complementary_aspects[:2]:
                    response += f"  • {aspect}\n"
        
        return response
    
    def _format_complete_synthesis(self) -> str:
        """Format for Tier 3: Complete synthesis"""
        response = f"◆ {self.query_topic.upper()}: COMPLETE SYNTHESIS ◆\n\n"
        
        # Sacred sources section
        response += "🏛️ SACRED SOURCES (All Traditions):\n\n"
        
        tradition_symbols = {
            "neville": "🔮",
            "scovel_shinn": "✨",
            "hylozoics": "🌌", 
            "fourth_way": "🎭"
        }
        
        total_quotes = 0
        for library_name, quotes in self.sacred_quotes.items():
            if quotes:
                symbol = tradition_symbols.get(library_name, "📖")
                response += f"{symbol} {library_name.upper().replace('_', ' ')} ({len(quotes)} passages):\n"
                
                # Show first quote, indicate more available
                primary_quote = quotes[0]
                response += f'"{primary_quote.text[:200]}..."\n'
                if len(quotes) > 1:
                    response += f"[+{len(quotes)-1} more passages]\n"
                response += "\n"
                total_quotes += len(quotes)
        
        # Synthesis section
        if self.universal_principle or self.synthesis_text:
            response += "▲ SYNTHESIS: THE UNIFIED TRUTH ▲\n\n"
            
            if self.universal_principle:
                response += f"● Universal Principle: {self.universal_principle}\n\n"
            
            if self.synthesis_text:
                response += f"● Complete Analysis:\n{self.synthesis_text}\n\n"
        
        # Cross-library analysis
        if self.cross_library_analysis:
            if self.cross_library_analysis.apparent_contradictions:
                response += "● Resolution of Apparent Contradictions:\n"
                for i, (contradiction, explanation) in enumerate(zip(
                    self.cross_library_analysis.apparent_contradictions,
                    self.cross_library_analysis.contradiction_explanations
                )):
                    if i < 2:  # Limit to 2 for readability
                        response += f"  • {contradiction}\n"
                        response += f"    Resolution: {explanation}\n"
                response += "\n"
        
        # Personality applications
        if self.personality_applications:
            response += "● Personality-Specific Applications:\n"
            for personality_type, application in list(self.personality_applications.items())[:3]:
                response += f"  • {personality_type}: {application}\n"
            response += "\n"
        
        # Study path
        if self.study_path_suggestions:
            response += "● Progressive Study Path:\n"
            for i, suggestion in enumerate(self.study_path_suggestions[:4], 1):
                response += f"  {i}. {suggestion}\n"
            response += "\n"
        
        # Synthesis summary
        if self.synthesis_text:
            response += f"● Truth Synthesis:\n\"{self.synthesis_text[-200:]}\""
        
        return response


class SynthesisEngine:
    """Core engine for tiered wisdom synthesis"""
    
    def __init__(self):
        """Initialize the synthesis engine"""
        self.supabase_client: Client = create_client(
            os.getenv("SUPABASE_URL"),
            os.getenv("SUPABASE_ANON_KEY")
        )
        
        self.pinecone_client = PineconeClient()
        self.openai_client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))
        
        # Available libraries
        self.available_libraries = {
            "hylozoics": "hylozoics_sacred",
            "neville": "neville_sacred", 
            "scovel_shinn": "scovel_shinn_sacred",
            "fourth_way": "fourth_way_sacred"
        }
        
        logger.info("Synthesis Engine initialized with tiered access control")
    
    async def get_user_subscription(self, person_id: str) -> Optional[UserSubscription]:
        """Get user's subscription information"""
        try:
            result = self.supabase_client.table("user_subscriptions").select("*").eq(
                "person_id", person_id
            ).execute()
            
            if result.data:
                data = result.data[0]
                return UserSubscription(
                    person_id=data["person_id"],
                    tier_level=data["tier_level"],
                    tier_name=data["tier_name"],
                    monthly_query_limit=data["monthly_query_limit"],
                    queries_used_this_month=data["queries_used_this_month"],
                    cross_library_access=data["cross_library_access"],
                    synthesis_access=data["synthesis_access"],
                    personality_integration=data["personality_integration"],
                    subscription_active=data["payment_status"] == "active"
                )
            
            # Create default subscription for new users
            return await self._create_default_subscription(person_id)
            
        except Exception as e:
            logger.error(f"Error getting user subscription: {e}")
            return None
    
    async def _create_default_subscription(self, person_id: str) -> UserSubscription:
        """Create default Tier 1 subscription for new users"""
        try:
            subscription_data = {
                "person_id": person_id,
                "tier_level": 1,
                "tier_name": "Sacred Source",
                "features_enabled": ["single_library_access", "basic_search", "quote_bookmarking"],
                "monthly_query_limit": 100,
                "cross_library_access": False,
                "synthesis_access": False,
                "personality_integration": False
            }
            
            result = self.supabase_client.table("user_subscriptions").insert(subscription_data).execute()
            
            return UserSubscription(
                person_id=person_id,
                tier_level=1,
                tier_name="Sacred Source",
                monthly_query_limit=100,
                queries_used_this_month=0,
                cross_library_access=False,
                synthesis_access=False,
                personality_integration=False,
                subscription_active=True
            )
            
        except Exception as e:
            logger.error(f"Error creating default subscription: {e}")
            return None
    
    async def check_query_limits(self, person_id: str) -> bool:
        """Check if user can make another query"""
        try:
            # Call the database function
            result = self.supabase_client.rpc("check_query_limit", {"p_person_id": person_id}).execute()
            return result.data if result.data is not None else False
            
        except Exception as e:
            logger.error(f"Error checking query limits: {e}")
            return False
    
    async def generate_synthesis_response(
        self, 
        person_id: str, 
        query: str,
        requested_libraries: Optional[List[str]] = None
    ) -> SynthesisResponse:
        """Generate synthesis response based on user tier"""
        start_time = datetime.now()
        
        try:
            # Get user subscription
            subscription = await self.get_user_subscription(person_id)
            if not subscription or not subscription.subscription_active:
                return self._create_error_response("Subscription required", UserTier.SACRED_SOURCE)
            
            # Check query limits
            if not await self.check_query_limits(person_id):
                return self._create_error_response("Monthly query limit exceeded", UserTier(subscription.tier_level))
            
            # Determine response type based on tier
            user_tier = UserTier(subscription.tier_level)
            
            if user_tier == UserTier.SACRED_SOURCE:
                response_type = ResponseType.SINGLE_LIBRARY
                libraries_to_search = [requested_libraries[0] if requested_libraries else "hylozoics"]
            elif user_tier == UserTier.CROSS_LIBRARY:
                response_type = ResponseType.CROSS_LIBRARY_COMPARISON
                libraries_to_search = requested_libraries or ["hylozoics", "neville", "scovel_shinn"]
            else:  # SYNTHESIS_MASTER
                response_type = ResponseType.COMPLETE_SYNTHESIS
                libraries_to_search = requested_libraries or list(self.available_libraries.keys())
            
            # Check cache first (for Tier 2 and 3)
            if user_tier != UserTier.SACRED_SOURCE:
                cached_response = await self._get_cached_synthesis(query, libraries_to_search, user_tier)
                if cached_response:
                    await self._increment_query_usage(person_id)
                    return cached_response
            
            # Generate new response
            sacred_quotes = await self._search_all_libraries(query, libraries_to_search)
            
            synthesis_response = SynthesisResponse(
                query_topic=query,
                response_type=response_type,
                user_tier=user_tier,
                sacred_quotes=sacred_quotes,
                libraries_searched=libraries_to_search
            )
            
            # Add cross-library analysis for Tier 2+
            if user_tier != UserTier.SACRED_SOURCE and sacred_quotes:
                synthesis_response.cross_library_analysis = await self._generate_cross_library_analysis(
                    query, sacred_quotes
                )
            
            # Add complete synthesis for Tier 3
            if user_tier == UserTier.SYNTHESIS_MASTER and sacred_quotes:
                await self._add_complete_synthesis(synthesis_response, subscription.personality_integration)
            
            # Calculate performance metrics
            end_time = datetime.now()
            synthesis_response.generation_time_ms = int((end_time - start_time).total_seconds() * 1000)
            
            # Cache the response (for Tier 2 and 3)
            if user_tier != UserTier.SACRED_SOURCE:
                await self._cache_synthesis_response(synthesis_response)
            
            # Increment user's query usage
            await self._increment_query_usage(person_id)
            
            # Log the query
            await self._log_user_query(person_id, query, synthesis_response)
            
            return synthesis_response
            
        except Exception as e:
            logger.error(f"Error generating synthesis response: {e}")
            return self._create_error_response("System error", UserTier.SACRED_SOURCE)
    
    async def _search_all_libraries(self, query: str, libraries: List[str]) -> Dict[str, List[SacredQuote]]:
        """Search for quotes across specified libraries"""
        all_quotes = {}
        
        for library_name in libraries:
            if library_name not in self.available_libraries:
                continue
            
            namespace = self.available_libraries[library_name]
            quotes = await self._search_library(query, library_name, namespace)
            all_quotes[library_name] = quotes
        
        return all_quotes
    
    async def _search_library(self, query: str, library_name: str, namespace: str) -> List[SacredQuote]:
        """Search a specific library for relevant quotes"""
        try:
            # Generate query embedding
            query_embedding = await self.pinecone_client.get_embedding(query)
            
            # Search in library namespace
            search_results = await self.pinecone_client.search_similar(
                query_embedding=query_embedding,
                namespace=namespace,
                filter_dict={"is_sacred": True},
                top_k=5
            )
            
            quotes = []
            for result in search_results:
                # This would retrieve full quote data from the appropriate table
                # For now, creating mock quotes based on metadata
                quote = SacredQuote(
                    quote_id=result["metadata"].get("quote_id", "unknown"),
                    text=result["metadata"].get("text", "Quote text would be retrieved from database"),
                    source_book=result["metadata"].get("source_book", "Unknown Book"),
                    chapter=result["metadata"].get("chapter", "Unknown Chapter"),
                    page_number=result["metadata"].get("page_number"),
                    paragraph_number=result["metadata"].get("paragraph_number"),
                    library_name=library_name,
                    tradition=library_name.replace("_", " ").title()
                )
                quotes.append(quote)
            
            return quotes
            
        except Exception as e:
            logger.error(f"Error searching {library_name} library: {e}")
            return []
    
    async def _generate_cross_library_analysis(
        self, 
        query: str, 
        sacred_quotes: Dict[str, List[SacredQuote]]
    ) -> CrossLibraryAnalysis:
        """Generate cross-library comparative analysis"""
        try:
            # Prepare context from all quotes
            quote_contexts = []
            for library_name, quotes in sacred_quotes.items():
                for quote in quotes[:2]:  # Limit to top 2 quotes per library
                    quote_contexts.append(f"{library_name.upper()}: \"{quote.text}\"")
            
            analysis_prompt = f"""Analyze these quotes from different wisdom traditions on the topic: {query}

Quotes:
{chr(10).join(quote_contexts)}

Provide analysis in JSON format:
{{
    "common_themes": ["theme1", "theme2", "theme3"],
    "key_differences": {{
        "tradition1": "how this tradition differs",
        "tradition2": "how this tradition differs"
    }},
    "apparent_contradictions": ["contradiction1", "contradiction2"],
    "contradiction_explanations": ["explanation1", "explanation2"],
    "complementary_aspects": ["aspect1", "aspect2"]
}}

Focus on finding universal truths while respecting each tradition's unique perspective."""

            response = self.openai_client.chat.completions.create(
                model="gpt-4",
                messages=[
                    {"role": "system", "content": "You are a comparative wisdom analyst. Analyze traditions respectfully while finding universal truths."},
                    {"role": "user", "content": analysis_prompt}
                ],
                max_tokens=500,
                temperature=0.3
            )
            
            try:
                analysis_data = json.loads(response.choices[0].message.content)
                return CrossLibraryAnalysis(
                    common_themes=analysis_data.get("common_themes", []),
                    key_differences=analysis_data.get("key_differences", {}),
                    apparent_contradictions=analysis_data.get("apparent_contradictions", []),
                    contradiction_explanations=analysis_data.get("contradiction_explanations", []),
                    complementary_aspects=analysis_data.get("complementary_aspects", [])
                )
            except json.JSONDecodeError:
                # Fallback analysis
                return CrossLibraryAnalysis(
                    common_themes=["Universal consciousness principles"],
                    key_differences={"approach": "Different methodological approaches"},
                    apparent_contradictions=[],
                    contradiction_explanations=[],
                    complementary_aspects=["Traditions complement rather than contradict"]
                )
                
        except Exception as e:
            logger.error(f"Error generating cross-library analysis: {e}")
            return CrossLibraryAnalysis([], {}, [], [], [])
    
    async def _add_complete_synthesis(self, response: SynthesisResponse, include_personality: bool):
        """Add complete synthesis for Tier 3 users"""
        try:
            # Prepare comprehensive context
            all_quote_texts = []
            for quotes in response.sacred_quotes.values():
                all_quote_texts.extend([quote.text for quote in quotes])
            
            synthesis_prompt = f"""Generate complete synthesis for the topic: {response.query_topic}

Source quotes from multiple wisdom traditions:
{chr(10).join(all_quote_texts[:10])}  # Limit context

Generate comprehensive synthesis including:
1. Universal principle that all traditions point toward
2. Complete analysis of how traditions complement each other
3. Resolution of any apparent contradictions
4. Study progression recommendations

Respond in JSON format:
{{
    "universal_principle": "The core truth all traditions agree on",
    "synthesis_text": "Complete analysis and synthesis (200 words max)",
    "study_path_suggestions": ["step1", "step2", "step3", "step4"]
}}"""

            if include_personality:
                synthesis_prompt += """
5. Personality-specific applications

Add to JSON:
    "personality_applications": {
        "Enneagram Type 4": "How this applies to Type 4",
        "Human Design Manifestor": "How this applies to Manifestors",
        "Gene Keys Profile": "General application guidance"
    }
"""

            response_data = self.openai_client.chat.completions.create(
                model="gpt-4",
                messages=[
                    {"role": "system", "content": "You are a master synthesist of wisdom traditions. Create unified understanding while respecting each tradition."},
                    {"role": "user", "content": synthesis_prompt}
                ],
                max_tokens=800,
                temperature=0.2
            )
            
            try:
                synthesis_data = json.loads(response_data.choices[0].message.content)
                
                response.universal_principle = synthesis_data.get("universal_principle", "")
                response.synthesis_text = synthesis_data.get("synthesis_text", "")
                response.study_path_suggestions = synthesis_data.get("study_path_suggestions", [])
                
                if include_personality:
                    response.personality_applications = synthesis_data.get("personality_applications", {})
                
                response.confidence_score = 0.85  # High confidence for complete synthesis
                
            except json.JSONDecodeError:
                response.synthesis_text = "Complete synthesis temporarily unavailable"
                response.confidence_score = 0.3
                
        except Exception as e:
            logger.error(f"Error generating complete synthesis: {e}")
            response.synthesis_text = "Synthesis generation error"
            response.confidence_score = 0.1
    
    async def _get_cached_synthesis(
        self, 
        query: str, 
        libraries: List[str], 
        user_tier: UserTier
    ) -> Optional[SynthesisResponse]:
        """Check for cached synthesis response"""
        try:
            # Create query hash for deduplication
            query_hash = hashlib.sha256(f"{query}_{sorted(libraries)}".encode()).hexdigest()
            
            result = self.supabase_client.table("synthesis_responses").select("*").eq(
                "query_hash", query_hash
            ).eq(
                "tier_required", user_tier.value
            ).gt(
                "expires_at", datetime.now().isoformat()
            ).execute()
            
            if result.data:
                # Convert cached data back to SynthesisResponse
                # This would be implemented based on the cached data structure
                logger.info(f"Using cached synthesis for query: {query}")
                return None  # Placeholder - would return actual cached response
            
            return None
            
        except Exception as e:
            logger.error(f"Error checking synthesis cache: {e}")
            return None
    
    async def _cache_synthesis_response(self, response: SynthesisResponse):
        """Cache synthesis response for future use"""
        try:
            query_hash = hashlib.sha256(f"{response.query_topic}_{sorted(response.libraries_searched)}".encode()).hexdigest()
            
            cache_data = {
                "query_topic": response.query_topic,
                "query_hash": query_hash,
                "libraries_included": response.libraries_searched,
                "sacred_quotes": json.dumps({k: [quote.__dict__ for quote in v] for k, v in response.sacred_quotes.items()}),
                "synthesis_text": response.synthesis_text or "",
                "universal_principle": response.universal_principle or "",
                "confidence_score": response.confidence_score,
                "tier_required": response.user_tier.value,
                "generation_time_ms": response.generation_time_ms
            }
            
            self.supabase_client.table("synthesis_responses").insert(cache_data).execute()
            logger.info(f"Cached synthesis response for: {response.query_topic}")
            
        except Exception as e:
            logger.error(f"Error caching synthesis response: {e}")
    
    async def _increment_query_usage(self, person_id: str):
        """Increment user's query usage count"""
        try:
            self.supabase_client.rpc("increment_query_usage", {"p_person_id": person_id}).execute()
        except Exception as e:
            logger.error(f"Error incrementing query usage: {e}")
    
    async def _log_user_query(self, person_id: str, query: str, response: SynthesisResponse):
        """Log user query for analytics"""
        try:
            log_data = {
                "person_id": person_id,
                "query_text": query,
                "query_category": "synthesis",  # Could be determined by AI
                "libraries_requested": response.libraries_searched,
                "response_mode": response.response_type.value,
                "response_type": "synthesis" if response.synthesis_text else "comparison",
                "quotes_returned": sum(len(quotes) for quotes in response.sacred_quotes.values()),
                "libraries_searched": response.libraries_searched,
                "response_time_ms": response.generation_time_ms,
                "tier_at_query_time": response.user_tier.value
            }
            
            self.supabase_client.table("user_query_history").insert(log_data).execute()
            
        except Exception as e:
            logger.error(f"Error logging user query: {e}")
    
    def _create_error_response(self, error_message: str, user_tier: UserTier) -> SynthesisResponse:
        """Create error response"""
        return SynthesisResponse(
            query_topic="Error",
            response_type=ResponseType.SINGLE_LIBRARY,
            user_tier=user_tier,
            sacred_quotes={"error": [SacredQuote(
                quote_id="error",
                text=error_message,
                source_book="System",
                chapter="Error",
                library_name="system",
                tradition="System"
            )]},
            libraries_searched=[]
        )


# Global instance
synthesis_engine = SynthesisEngine()
