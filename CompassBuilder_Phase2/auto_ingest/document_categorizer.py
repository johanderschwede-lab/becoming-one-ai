# build this

import os
import yaml
import asyncio
import logging
from datetime import datetime
from typing import Dict, List
import openai

class DocumentCategorizer:
    def __init__(self, api_key: str):
        if not api_key:
            raise ValueError("OpenAI API key is required")
            
        self.openai = openai
        self.openai.api_key = api_key
        
        # Load categories from schema
        try:
            self.categories = self._load_categories()
        except Exception as e:
            logging.error(f"Failed to load category schema: {str(e)}")
            raise
    
    def _load_categories(self) -> Dict:
        """Load category schema"""
        schema_path = os.path.join(
            os.path.dirname(__file__),
            "category_schema.yaml"
        )
        
        if os.path.exists(schema_path):
            with open(schema_path, 'r') as f:
                return yaml.safe_load(f)
        else:
            # Default categories if schema not found
            return {
                "method_core": {
                    "name": "Method Core",
                    "keywords": ["Becoming One", "emotional anchor", "feeling-state"]
                },
                "technical": {
                    "name": "Technical",
                    "keywords": ["implementation", "code", "architecture"]
                },
                "documentation": {
                    "name": "Documentation",
                    "keywords": ["guide", "manual", "instructions"]
                }
            }
    
    async def analyze_document(self, file_path: str) -> Dict:
        """Analyze document content"""
        try:
            # Read file with proper encoding handling
            with open(file_path, 'r', encoding='utf-8') as f:
                content = f.read()
        except UnicodeDecodeError:
            # Try alternative encoding if UTF-8 fails
            with open(file_path, 'r', encoding='latin-1') as f:
                content = f.read()
        except Exception as e:
            logging.error(f"Failed to read file {file_path}: {str(e)}")
            raise
        
        # Prepare analysis prompt
        prompt = f"""
        Analyze this document and extract key characteristics:
        
        Document: {content[:1000]}... (truncated)
        
        Identify:
        1. Main topics and themes
        2. Document type and purpose
        3. Key concepts discussed
        4. Technical vs conceptual ratio
        5. Implementation details if any
        
        Format the response as:
        TOPICS: [comma-separated list]
        TYPE: [document type]
        CONCEPTS: [comma-separated list]
        RATIO: [technical/conceptual percentage]
        DETAILS: [key implementation details if any]
        """
        
        max_retries = 3
        retry_count = 0
        
        while retry_count < max_retries:
            try:
                response = await openai.AsyncOpenAI().chat.completions.create(
                    model="gpt-4",
                    messages=[
                        {"role": "system", "content": "You are an expert at analyzing documents and identifying their key characteristics."},
                        {"role": "user", "content": prompt}
                    ],
                    temperature=0.3  # Lower temperature for more consistent analysis
                )
                
                return {
                    "content": content,
                    "analysis": response.choices[0].message.content,
                    "analyzed_at": datetime.now().isoformat()
                }
                
            except Exception as e:
                retry_count += 1
                if retry_count == max_retries:
                    logging.error(f"Failed to analyze document after {max_retries} attempts: {str(e)}")
                    raise
                await asyncio.sleep(1)  # Wait before retrying
    
    def analyze_fluff(self, content: str) -> Dict:
        """Analyze content for fluff markers"""
        fluff_markers = [
            "revolutionary breakthrough",
            "game-changing innovation",
            "paradigm shift",
            "next-generation solution",
            "cutting-edge methodology"
        ]
        
        matches = []
        for marker in fluff_markers:
            if marker.lower() in content.lower():
                matches.append(marker)
        
        return {
            "score": len(matches) * 0.5,  # 0.5 points per match
            "matches": matches
        }
    
    def suggest_categories(self, analysis: Dict) -> List[str]:
        """Suggest categories based on analysis"""
        suggested = []
        
        for cat_id, cat_info in self.categories.items():
            # Check for category keywords in content
            matches = sum(1 for kw in cat_info["keywords"] 
                        if kw.lower() in analysis["content"].lower())
            
            if matches >= 2:  # Require at least 2 keyword matches
                suggested.append(cat_id)
        
        return suggested or ["documentation"]  # Default to documentation
    
    def track_document(self, file_path: str, analysis: Dict, categories: List[str]):
        """Track document processing"""
        from document_tracker import DocumentTracker
        tracker = DocumentTracker()
        tracker.track_document(file_path, analysis, categories)
