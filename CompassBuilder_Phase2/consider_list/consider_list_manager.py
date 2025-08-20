import os
import json
from datetime import datetime
from typing import Dict, List, Optional
import logging
from dotenv import load_dotenv
import requests

# Load environment variables
load_dotenv('../.env')

class ConsiderListManager:
    def __init__(self):
        self.supabase_url = os.getenv("SUPABASE_URL")
        self.supabase_key = os.getenv("SUPABASE_ANON_KEY")
        
        self.headers = {
            "apikey": self.supabase_key,
            "Authorization": f"Bearer {self.supabase_key}",
            "Content-Type": "application/json"
        }
        
        # Consider list states
        self.STATES = {
            "CONSIDER": "consider",
            "IMPLEMENT": "implement",
            "REJECT": "reject",
            "ARCHIVE": "archive"
        }
    
    def add_to_consider_list(self, content: str, source: str, category: str, 
                           priority: str = "medium", notes: str = "") -> Dict:
        """Add an item to the consider list"""
        
        consider_data = {
            "title": f"Consider Item - {datetime.now().strftime('%Y-%m-%d %H:%M')}",
            "content": content,
            "material_type": "consider_item",
            "source_type": "compass_consider_list",
            "source_creator": source,
            "source_url": "consider_list",
            "metadata": json.dumps({
                "consider_id": f"consider_{datetime.now().strftime('%Y%m%d_%H%M%S')}",
                "added_by": source,
                "added_date": datetime.now().isoformat(),
                "category": category,
                "priority": priority,
                "notes": notes,
                "status": self.STATES["CONSIDER"],
                "reviewed": False,
                "review_date": None,
                "decision": None,
                "decision_reason": None,
                "implementation_notes": None
            }, default=str),
            "content_hash": str(hash(content)),
            "upload_date": datetime.now().isoformat(),
            "status": "consider",
            "notes": f"Added to consider list by {source}. Category: {category}. Priority: {priority}"
        }
        
        try:
            api_url = f"{self.supabase_url}/rest/v1/internal_teaching_materials"
            response = requests.post(api_url, headers=self.headers, json=consider_data)
            
            if response.status_code == 201:
                # Query for the inserted record
                query_url = f"{self.supabase_url}/rest/v1/internal_teaching_materials?content_hash=eq.{str(hash(content))}&order=upload_date.desc&limit=1"
                query_response = requests.get(query_url, headers=self.headers)
                
                if query_response.status_code == 200:
                    result = query_response.json()
                    if result and len(result) > 0:
                        logging.info(f"Added to consider list: {result[0]['material_id']}")
                        return {
                            "success": True,
                            "consider_id": result[0]['material_id'],
                            "message": f"Added to consider list with priority: {priority}"
                        }
                
                return {
                    "success": True,
                    "message": "Added to consider list"
                }
            else:
                logging.error(f"Failed to add to consider list: {response.status_code} - {response.text}")
                return {
                    "success": False,
                    "error": f"Database error: {response.status_code}"
                }
                
        except Exception as e:
            logging.error(f"Error adding to consider list: {str(e)}")
            return {
                "success": False,
                "error": str(e)
            }
    
    def get_consider_list(self, status: str = "consider", priority: str = None) -> List[Dict]:
        """Get items from the consider list"""
        try:
            # Build query
            query_params = f"material_type=eq.consider_item&status=eq.{status}"
            if priority:
                query_params += f"&metadata->>'priority'=eq.{priority}"
            
            api_url = f"{self.supabase_url}/rest/v1/internal_teaching_materials?{query_params}&order=upload_date.desc"
            response = requests.get(api_url, headers=self.headers)
            
            if response.status_code == 200:
                items = response.json()
                return [
                    {
                        "consider_id": item['material_id'],
                        "title": item['title'],
                        "content": item['content'],
                        "added_by": json.loads(item['metadata']).get('added_by', 'Unknown'),
                        "added_date": json.loads(item['metadata']).get('added_date', 'Unknown'),
                        "category": json.loads(item['metadata']).get('category', 'Unknown'),
                        "priority": json.loads(item['metadata']).get('priority', 'Unknown'),
                        "notes": json.loads(item['metadata']).get('notes', ''),
                        "status": json.loads(item['metadata']).get('status', 'Unknown'),
                        "reviewed": json.loads(item['metadata']).get('reviewed', False)
                    }
                    for item in items
                ]
            else:
                return []
                
        except Exception as e:
            logging.error(f"Error getting consider list: {str(e)}")
            return []
    
    def update_consider_item(self, consider_id: str, action: str, 
                           decision_reason: str = "", implementation_notes: str = "") -> Dict:
        """Update a consider list item (implement, reject, archive)"""
        
        if action not in self.STATES.values():
            return {"success": False, "error": f"Invalid action: {action}"}
        
        try:
            # Get current item
            api_url = f"{self.supabase_url}/rest/v1/internal_teaching_materials?material_id=eq.{consider_id}"
            response = requests.get(api_url, headers=self.headers)
            
            if response.status_code != 200:
                return {"success": False, "error": "Item not found"}
            
            item_data = response.json()[0]
            metadata = json.loads(item_data['metadata'])
            
            # Update metadata
            metadata['status'] = action
            metadata['reviewed'] = True
            metadata['review_date'] = datetime.now().isoformat()
            metadata['decision'] = action
            metadata['decision_reason'] = decision_reason
            metadata['implementation_notes'] = implementation_notes
            
            # Update the record
            update_data = {
                "metadata": json.dumps(metadata, default=str),
                "status": action,
                "notes": f"Status updated to {action}. Reason: {decision_reason}"
            }
            
            update_url = f"{self.supabase_url}/rest/v1/internal_teaching_materials?material_id=eq.{consider_id}"
            update_response = requests.patch(update_url, headers=self.headers, json=update_data)
            
            if update_response.status_code == 204:
                # If implementing, create implementation record
                if action == self.STATES["IMPLEMENT"]:
                    self._create_implementation_record(item_data, implementation_notes)
                
                return {"success": True, "status": action}
            else:
                return {"success": False, "error": f"Update failed: {update_response.status_code}"}
                
        except Exception as e:
            return {"success": False, "error": str(e)}
    
    def _create_implementation_record(self, item_data: Dict, implementation_notes: str):
        """Create an implementation record when an item is approved"""
        try:
            impl_data = {
                "title": f"Implementation - {item_data['title']}",
                "content": item_data['content'],
                "material_type": "implementation",
                "source_type": "compass_consider_list",
                "source_creator": "Consider_List_Manager",
                "source_url": "implementation",
                "metadata": json.dumps({
                    "implementation_id": f"impl_{datetime.now().strftime('%Y%m%d_%H%M%S')}",
                    "original_consider_id": item_data['material_id'],
                    "implemented_date": datetime.now().isoformat(),
                    "implementation_notes": implementation_notes,
                    "status": "active"
                }, default=str),
                "content_hash": str(hash(item_data['content'])),
                "upload_date": datetime.now().isoformat(),
                "status": "active",
                "notes": f"Implemented from consider list. Notes: {implementation_notes}"
            }
            
            api_url = f"{self.supabase_url}/rest/v1/internal_teaching_materials"
            response = requests.post(api_url, headers=self.headers, json=impl_data)
            
            if response.status_code == 201:
                logging.info("Implementation record created successfully")
            else:
                logging.error(f"Failed to create implementation record: {response.status_code}")
                
        except Exception as e:
            logging.error(f"Error creating implementation record: {str(e)}")
    
    def get_consider_stats(self) -> Dict:
        """Get statistics about the consider list"""
        try:
            stats = {
                "total_consider": 0,
                "total_implement": 0,
                "total_reject": 0,
                "total_archive": 0,
                "by_priority": {"high": 0, "medium": 0, "low": 0},
                "by_category": {}
            }
            
            # Get all consider items
            api_url = f"{self.supabase_url}/rest/v1/internal_teaching_materials?material_type=eq.consider_item"
            response = requests.get(api_url, headers=self.headers)
            
            if response.status_code == 200:
                items = response.json()
                
                for item in items:
                    metadata = json.loads(item['metadata'])
                    status = metadata.get('status', 'consider')
                    priority = metadata.get('priority', 'medium')
                    category = metadata.get('category', 'unknown')
                    
                    # Count by status
                    if status == 'consider':
                        stats['total_consider'] += 1
                    elif status == 'implement':
                        stats['total_implement'] += 1
                    elif status == 'reject':
                        stats['total_reject'] += 1
                    elif status == 'archive':
                        stats['total_archive'] += 1
                    
                    # Count by priority
                    if priority in stats['by_priority']:
                        stats['by_priority'][priority] += 1
                    
                    # Count by category
                    if category not in stats['by_category']:
                        stats['by_category'][category] = 0
                    stats['by_category'][category] += 1
            
            return stats
            
        except Exception as e:
            logging.error(f"Error getting consider stats: {str(e)}")
            return {}
