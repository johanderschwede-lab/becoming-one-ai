import os
import yaml
import json
import requests
from typing import Dict, Any, List
from datetime import datetime
import logging
from dotenv import load_dotenv

# Load environment variables
load_dotenv('../.env')

class SupabaseUploader:
    def __init__(self):
        # Initialize Supabase connection
        self.url = os.getenv("SUPABASE_URL")
        self.key = os.getenv("SUPABASE_ANON_KEY")
        
        if not self.url or not self.key:
            raise ValueError("SUPABASE_URL and SUPABASE_ANON_KEY environment variables are required")
            
        self.table_name = "internal_teaching_materials"
        self.headers = {
            "apikey": self.key,
            "Authorization": f"Bearer {self.key}",
            "Content-Type": "application/json"
        }
        
    def upload_document(self, file_path: str, analysis: Dict, categories: List[str], phase_folder: str) -> Dict[str, Any]:
        """Upload a processed document to Supabase"""
        try:
            # Read the document content
            with open(file_path, 'r', encoding='utf-8') as f:
                content = f.read()
            
            # Extract filename without extension
            filename = os.path.basename(file_path)
            title = os.path.splitext(filename)[0]
            
            # Simplified metadata structure to avoid JSON parsing issues
            metadata = {
                "original_filename": filename,
                "file_size": len(content),
                "word_count": len(content.split()),
                "categories": categories,
                "phase": phase_folder,
                "analysis_summary": analysis.get("analysis", "")[:500] if analysis else "",
                "processed_at": datetime.now().isoformat()
            }
            
            # Upload to Supabase using existing table structure
            data = {
                "title": title,
                "content": content,
                "material_type": "document",
                "source_type": "compass_processor",
                "source_creator": "AI_Compass_System",
                "source_url": file_path,
                "metadata": json.dumps(metadata, default=str, ensure_ascii=False),
                "content_hash": str(hash(content)),
                "upload_date": datetime.now().isoformat(),
                "status": "active",
                # "tags": json.dumps(categories).replace('"', '\\"'),  # Temporarily disabled due to array format issues
                "notes": f"Processed by Compass system. Categories: {', '.join(categories)}. Phase: {phase_folder}"
            }
            
            # Use REST API
            api_url = f"{self.url}/rest/v1/{self.table_name}"
            response = requests.post(api_url, headers=self.headers, json=data)
            
            if response.status_code == 201:
                # Supabase returns empty response on successful insert
                # Query for the inserted record
                try:
                    query_url = f"{self.url}/rest/v1/{self.table_name}?content_hash=eq.{str(hash(content))}&order=upload_date.desc&limit=1"
                    query_response = requests.get(query_url, headers=self.headers)
                    
                    if query_response.status_code == 200:
                        result = query_response.json()
                        if result and len(result) > 0:
                            logging.info(f"Successfully uploaded {filename} to Supabase")
                            return result[0]
                        else:
                            logging.warning(f"Upload successful but could not retrieve record for {filename}")
                            return {"uploaded": True, "filename": filename}
                    else:
                        logging.warning(f"Upload successful but query failed for {filename}")
                        return {"uploaded": True, "filename": filename}
                except Exception as e:
                    logging.warning(f"Upload successful but retrieval failed for {filename}: {str(e)}")
                    return {"uploaded": True, "filename": filename}
            else:
                logging.error(f"Failed to upload {filename} to Supabase: {response.status_code} - {response.text}")
                return None
                
        except Exception as e:
            logging.error(f"Error uploading {file_path} to Supabase: {str(e)}")
            return None
    
    def upload_batch(self, documents: List[Dict]) -> List[Dict]:
        """Upload multiple documents in batch"""
        results = []
        for doc in documents:
            result = self.upload_document(
                doc["file_path"],
                doc["analysis"],
                doc["categories"],
                doc["phase_folder"]
            )
            results.append(result)
        return results
    
    def test_connection(self) -> bool:
        """Test Supabase connection"""
        try:
            # Try to query the table
            api_url = f"{self.url}/rest/v1/{self.table_name}?select=material_id&limit=1"
            response = requests.get(api_url, headers=self.headers)
            
            if response.status_code == 200:
                logging.info("Supabase connection test successful")
                return True
            else:
                logging.error(f"Supabase connection test failed: {response.status_code} - {response.text}")
                return False
        except Exception as e:
            logging.error(f"Supabase connection test failed: {str(e)}")
            return False
