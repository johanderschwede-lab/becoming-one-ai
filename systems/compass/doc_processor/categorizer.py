# build this

import os
import yaml
import json
from pathlib import Path
from typing import Dict, List, Optional
import openai
from datetime import datetime
import re

class DocumentCategorizer:
    def __init__(self, api_key: str):
        self.openai = openai
        self.openai.api_key = api_key
        
        # Load category schema
        with open("category_schema.yaml", 'r') as f:
            self.categories = yaml.safe_load(f)
        
        # Initialize tracking database
        self.tracking_db = "document_tracking.json"
        self.load_tracking()
    
    def load_tracking(self):
        """Load or initialize tracking database"""
        if os.path.exists(self.tracking_db):
            with open(self.tracking_db, 'r') as f:
                self.documents = json.load(f)
        else:
            self.documents = {
                "processed": {},
                "pending": {},
                "categories": {}
            }
    
    def save_tracking(self):
        """Save tracking database"""
        with open(self.tracking_db, 'w') as f:
            json.dump(self.documents, f, indent=2)
    
    async def analyze_document(self, file_path: str) -> Dict:
        """Analyze a document using GPT-4"""
        with open(file_path, 'r') as f:
            content = f.read()
            
        # Prepare content sample (first 1000 chars + last 1000 chars)
        content_sample = content[:1000] + "..." + content[-1000:]
        
        # Create category overview for GPT
        category_overview = "\n".join([
            f"- {cat_id}: {info['name']}"
            for cat_id, info in self.categories.items()
        ])
        
        analysis_prompt = f"""
        Analyze this document and categorize it according to our system:

        Document Name: {Path(file_path).name}
        Content Sample: {content_sample}

        Available Categories:
        {category_overview}

        For each category that applies, explain why it fits and which aspects of the document match that category.
        Also identify:
        1. Key concepts and terminology used
        2. Document purpose and type
        3. Related systems or components
        4. Implementation vs. conceptual focus
        5. Suggested subcategories
        """
        
        response = await openai.ChatCompletion.acreate(
            model="gpt-4",
            messages=[
                {"role": "system", "content": "You are an expert at analyzing documents and identifying their categories in the Becoming One™ system."},
                {"role": "user", "content": analysis_prompt}
            ]
        )
        
        return {
            "analysis": response.choices[0].message.content,
            "analyzed_at": datetime.now().isoformat()
        }
    
    def suggest_categories(self, analysis: Dict) -> List[str]:
        """Suggest categories based on analysis and file patterns"""
        suggested = set()
        
        for cat_id, cat_info in self.categories.items():
            # Check for category keywords
            keyword_matches = sum(1 for kw in cat_info["keywords"] 
                                if kw.lower() in analysis["analysis"].lower())
            
            # Check for file patterns
            pattern_matches = sum(1 for pattern in cat_info["file_patterns"] 
                                if any(re.search(pattern, line, re.IGNORECASE) 
                                      for line in analysis["analysis"].split('\n')))
            
            # Require either strong keyword presence or file pattern match
            if keyword_matches >= 2 or pattern_matches >= 1:
                suggested.add(cat_id)
        
        return list(suggested)
    
    def suggest_subcategories(self, category: str, analysis: Dict) -> List[str]:
        """Suggest subcategories for a given category"""
        subcats = []
        
        if category in self.categories:
            for subcat in self.categories[category]["subcategories"]:
                # Convert subcategory to searchable terms
                terms = subcat.replace('_', ' ').split()
                if any(term.lower() in analysis["analysis"].lower() for term in terms):
                    subcats.append(subcat)
        
        return subcats
    
    def track_document(self, file_path: str, analysis: Dict, categories: List[str]):
        """Track document in the database"""
        doc_id = Path(file_path).name
        
        # Get subcategories for each category
        subcategories = {
            cat: self.suggest_subcategories(cat, analysis)
            for cat in categories
        }
        
        doc_info = {
            "path": str(file_path),
            "analyzed_at": analysis["analyzed_at"],
            "categories": categories,
            "subcategories": subcategories,
            "analysis": analysis["analysis"],
            "status": "pending",
            "priority": self._calculate_priority(categories)
        }
        
        self.documents["pending"][doc_id] = doc_info
        
        # Update category indexes
        for cat in categories:
            if cat not in self.documents["categories"]:
                self.documents["categories"][cat] = []
            self.documents["categories"][cat].append(doc_id)
        
        self.save_tracking()
    
    def _calculate_priority(self, categories: List[str]) -> int:
        """Calculate document priority based on categories"""
        priority = 1
        
        # Method and master prompt documents get highest priority
        if "becoming_one_method" in categories or "master_prompt" in categories:
            priority += 3
            
        # Technical and strategic documents get medium priority
        if any(cat in categories for cat in ["technical_implementation", "omnichannel", "products_and_offers"]):
            priority += 2
            
        # More categories = higher priority
        priority += min(len(categories) - 1, 2)  # Cap category bonus at 2
        
        return min(priority, 5)  # Cap at priority 5
    
    def generate_processing_plan(self) -> str:
        """Generate a processing plan based on tracked documents"""
        plan = "# Document Processing Plan\n\n"
        
        # Group by priority
        priority_groups = {i: [] for i in range(5, 0, -1)}
        for doc_id, info in self.documents["pending"].items():
            priority_groups[info["priority"]].append((doc_id, info))
        
        # Generate plan
        for priority in range(5, 0, -1):
            docs = priority_groups[priority]
            if not docs:
                continue
                
            plan += f"\n## Priority {priority} Documents\n\n"
            for doc_id, info in sorted(docs, key=lambda x: len(x[1]["categories"]), reverse=True):
                categories = ", ".join(info["categories"])
                subcats = ", ".join(sum(info["subcategories"].values(), []))
                plan += f"- {doc_id}\n  - Categories: {categories}\n  - Subcategories: {subcats}\n\n"
        
        return plan

async def main():
    """Main categorization routine"""
    categorizer = DocumentCategorizer(os.getenv("OPENAI_API_KEY"))
    
    # Process a directory of documents
    doc_dir = "documents_to_process"
    for file in os.listdir(doc_dir):
        if file.endswith(('.md', '.txt', '.doc', '.docx')):
            file_path = os.path.join(doc_dir, file)
            
            # Analyze document
            analysis = await categorizer.analyze_document(file_path)
            
            # Suggest categories
            categories = categorizer.suggest_categories(analysis)
            
            # Track document
            categorizer.track_document(file_path, analysis, categories)
    
    # Generate processing plan
    plan = categorizer.generate_processing_plan()
    print(plan)

if __name__ == "__main__":
    import asyncio
    asyncio.run(main())