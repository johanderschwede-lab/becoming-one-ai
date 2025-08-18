"""
Enhanced Sacred Library with Vector Search + Exact Quote Retrieval
================================================================
Two-stage search: Vector understanding → Exact quote retrieval
"""

import json
import os
from pathlib import Path
from typing import List, Dict, Any, Optional
from loguru import logger
from openai import OpenAI

try:
    from integrations.pinecone_client import PineconeClient
    PINECONE_AVAILABLE = True
except ImportError:
    PINECONE_AVAILABLE = False
    logger.warning("Pinecone not available, using local search only")

from core.sacred_library_local import local_sacred_library

class EnhancedSacredLibrary:
    """Enhanced Sacred Library with vector search + exact quotes"""
    
    def __init__(self):
        self.openai_client = OpenAI(api_key=os.getenv("OPENAI_API_KEY")) if os.getenv("OPENAI_API_KEY") else None
        
        # Only initialize Pinecone if available and API key is set
        self.pinecone_client = None
        if PINECONE_AVAILABLE and os.getenv("PINECONE_API_KEY"):
            try:
                self.pinecone_client = PineconeClient()
            except Exception as e:
                logger.warning(f"Failed to initialize Pinecone client: {e}")
                
        # Use absolute path from project root
        project_root = Path(__file__).parent.parent.parent
        self.sacred_dir = project_root / "sacred_library_files"
        
    async def enhanced_search(self, query: str, limit: int = 3, target_language: str = "en") -> List[Dict[str, Any]]:
        """
        Enhanced search with vector understanding + exact quote retrieval
        
        Args:
            query: User's question
            limit: Number of quotes to return
            target_language: Preferred response language (en, sv, de)
        """
        try:
            logger.info(f"Enhanced Sacred Library search: '{query}' (target: {target_language})")
            
            # Stage 1: Understand the query semantically
            search_strategy = await self._analyze_query(query)
            logger.info(f"Search strategy: {search_strategy}")
            
            # Stage 2: Vector search (if available)
            vector_results = []
            if self.pinecone_client:
                try:
                    vector_results = await self._vector_search(query, search_strategy, limit * 2)
                    logger.info(f"Vector search found {len(vector_results)} results")
                except Exception as e:
                    logger.warning(f"Vector search failed: {e}")
            
            # Stage 3: Enhanced local search with better keywords
            enhanced_keywords = search_strategy.get('keywords', [])
            local_results = await self._enhanced_local_search(query, enhanced_keywords, limit * 2)
            logger.info(f"Enhanced local search found {len(local_results)} results")
            
            # Stage 4: Combine and rank results
            combined_results = self._combine_and_rank_results(vector_results, local_results, search_strategy)
            
            # Stage 5: Filter by language preference and limit
            final_results = self._filter_and_format_results(combined_results, target_language, limit)
            
            logger.info(f"Final results: {len(final_results)} quotes")
            return final_results
            
        except Exception as e:
            logger.error(f"Enhanced search error: {e}")
            # Fallback to basic local search
            return local_sacred_library.search_quotes(query, limit=limit)
    
    async def _analyze_query(self, query: str) -> Dict[str, Any]:
        """Analyze the query to understand search intent and generate better keywords"""
        if not self.openai_client:
            return {"type": "general", "keywords": query.lower().split()}
        
        try:
            analysis_prompt = f"""Analyze this question about Hylozoics/Henry T. Laurency and provide search strategy:

Question: "{query}"

Provide JSON response with:
1. "type": "biographical", "teaching", or "general"
2. "keywords": array of search terms in multiple languages (English, Swedish, German)
3. "focus": what the user is really asking about

Examples:
- "How does Laurency describe himself?" → biographical, keywords about personal descriptions
- "What does Hylozoics teach about consciousness?" → teaching, keywords about consciousness concepts

Respond only with valid JSON:"""

            response = self.openai_client.chat.completions.create(
                model="gpt-4-turbo-preview",
                messages=[{"role": "user", "content": analysis_prompt}],
                temperature=0.3,
                max_tokens=200
            )
            
            result = json.loads(response.choices[0].message.content.strip())
            return result
            
        except Exception as e:
            logger.warning(f"Query analysis failed: {e}")
            return {"type": "general", "keywords": query.lower().split(), "focus": query}
    
    async def _vector_search(self, query: str, strategy: Dict[str, Any], limit: int) -> List[Dict[str, Any]]:
        """Use Pinecone vector search to find semantically similar content"""
        if not self.pinecone_client:
            return []
        
        try:
            # Search in Pinecone for sacred library content
            results = await self.pinecone_client.search(
                query=query,
                namespace="sacred_library",
                top_k=limit,
                filter={"content_type": "hylozoics_quote"}
            )
            
            # Convert Pinecone results to our format
            formatted_results = []
            for result in results:
                if result.get('metadata'):
                    formatted_results.append({
                        'title': result['metadata'].get('title', 'Unknown'),
                        'content': result['metadata'].get('content', ''),
                        'metadata': {
                            'quote_id': result['metadata'].get('quote_id'),
                            'chapter': result['metadata'].get('chapter', 'Unknown'),
                            'language': result['metadata'].get('language', 'unknown'),
                            'author': result['metadata'].get('author', 'Henry T. Laurency'),
                            'source_book': result['metadata'].get('source_book', 'Hylozoics'),
                            'similarity_score': result.get('score', 0.0)
                        }
                    })
            
            return formatted_results
            
        except Exception as e:
            logger.error(f"Vector search error: {e}")
            return []
    
    async def _enhanced_local_search(self, query: str, keywords: List[str], limit: int) -> List[Dict[str, Any]]:
        """Enhanced local search using better keywords from query analysis"""
        try:
            # Use both original query and enhanced keywords
            all_terms = [query] + keywords
            results = []
            
            for term in all_terms:
                term_results = local_sacred_library.search_quotes(term, limit=limit//len(all_terms) + 1)
                results.extend(term_results)
                if len(results) >= limit:
                    break
            
            # Remove duplicates
            seen = set()
            unique_results = []
            for result in results:
                quote_id = result.get('metadata', {}).get('quote_id', result.get('title', ''))
                if quote_id not in seen:
                    seen.add(quote_id)
                    unique_results.append(result)
            
            return unique_results[:limit]
            
        except Exception as e:
            logger.error(f"Enhanced local search error: {e}")
            return []
    
    def _combine_and_rank_results(self, vector_results: List[Dict], local_results: List[Dict], strategy: Dict) -> List[Dict]:
        """Combine vector and local results, ranking by relevance"""
        all_results = []
        
        # Add vector results with high priority
        for result in vector_results:
            result['source'] = 'vector'
            result['priority'] = 2.0  # High priority for vector matches
            all_results.append(result)
        
        # Add local results
        for result in local_results:
            result['source'] = 'local'
            result['priority'] = 1.0  # Normal priority for keyword matches
            all_results.append(result)
        
        # Remove duplicates (prefer vector results)
        seen = set()
        unique_results = []
        for result in sorted(all_results, key=lambda x: x['priority'], reverse=True):
            quote_id = result.get('metadata', {}).get('quote_id', result.get('title', ''))
            if quote_id not in seen:
                seen.add(quote_id)
                unique_results.append(result)
        
        return unique_results
    
    def _filter_and_format_results(self, results: List[Dict], target_language: str, limit: int) -> List[Dict]:
        """Filter by language preference and format for consistent output"""
        # Language priority: exact match > English > any
        language_priority = {
            target_language: 3,
            'en': 2,
            'english': 2,
        }
        
        # Sort by language preference, then by priority
        def sort_key(result):
            lang = result.get('metadata', {}).get('language', '').lower()
            lang_score = language_priority.get(lang, 1)
            priority_score = result.get('priority', 1.0)
            return (lang_score, priority_score)
        
        sorted_results = sorted(results, key=sort_key, reverse=True)
        
        # Format results consistently
        formatted_results = []
        for result in sorted_results[:limit]:
            formatted_result = {
                'title': result.get('title', 'Unknown Quote'),
                'content': result.get('content', ''),
                'metadata': {
                    'quote_id': result.get('metadata', {}).get('quote_id', 'unknown'),
                    'chapter': result.get('metadata', {}).get('chapter', 'Unknown'),
                    'language': result.get('metadata', {}).get('language', 'unknown'),
                    'author': result.get('metadata', {}).get('author', 'Henry T. Laurency'),
                    'source_book': result.get('metadata', {}).get('source_book', 'Hylozoics'),
                    'search_source': result.get('source', 'local'),
                    'similarity_score': result.get('metadata', {}).get('similarity_score', 0.0)
                }
            }
            formatted_results.append(formatted_result)
        
        return formatted_results

# Global instance
enhanced_sacred_library = EnhancedSacredLibrary()
