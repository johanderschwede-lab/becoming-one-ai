import os
import json
import yaml
from datetime import datetime
from typing import Dict, List, Optional, Tuple
import logging
from dotenv import load_dotenv
import requests

# Load environment variables
load_dotenv('../.env')

class MasterPromptReviewSystem:
    def __init__(self):
        self.supabase_url = os.getenv("SUPABASE_URL")
        self.supabase_key = os.getenv("SUPABASE_ANON_KEY")
        self.openai_api_key = os.getenv("OPENAI_API_KEY")
        
        self.headers = {
            "apikey": self.supabase_key,
            "Authorization": f"Bearer {self.supabase_key}",
            "Content-Type": "application/json"
        }
        
        # Review states
        self.STATES = {
            "PENDING": "pending_review",
            "APPROVED": "approved",
            "REJECTED": "rejected",
            "NEEDS_REVISION": "needs_revision"
        }
    
    def analyze_master_prompt_change(self, new_content: str, current_content: str = None) -> Dict:
        """Analyze the impact of a proposed master prompt change"""
        
        # Get current master prompt if not provided
        if not current_content:
            current_content = self.get_current_master_prompt()
        
        analysis_prompt = f"""
        You are an expert at analyzing changes to master prompts and their system-wide impact.
        
        CURRENT MASTER PROMPT:
        {current_content[:2000]}...
        
        PROPOSED NEW MASTER PROMPT:
        {new_content[:2000]}...
        
        Analyze this change and provide:
        
        1. **CHANGE_SUMMARY**: Brief description of what changed
        2. **IMPACT_LEVEL**: Low/Medium/High/Critical
        3. **AFFECTED_AREAS**: List of system components that might be affected
        4. **RISK_ASSESSMENT**: Potential risks or unintended consequences
        5. **BENEFITS**: Expected improvements or benefits
        6. **RECOMMENDATION**: Approve/Reject/Needs Revision
        7. **REASONING**: Detailed explanation of the recommendation
        8. **SUGGESTED_REVISIONS**: If needed, specific suggestions for improvement
        
        Format as JSON:
        {{
            "change_summary": "...",
            "impact_level": "...",
            "affected_areas": ["area1", "area2"],
            "risk_assessment": "...",
            "benefits": "...",
            "recommendation": "...",
            "reasoning": "...",
            "suggested_revisions": "..."
        }}
        """
        
        try:
            # Use OpenAI to analyze the change
            response = requests.post(
                "https://api.openai.com/v1/chat/completions",
                headers={
                    "Authorization": f"Bearer {self.openai_api_key}",
                    "Content-Type": "application/json"
                },
                json={
                    "model": "gpt-4",
                    "messages": [
                        {"role": "system", "content": "You are an expert at analyzing master prompt changes and their system-wide impact."},
                        {"role": "user", "content": analysis_prompt}
                    ],
                    "temperature": 0.3
                }
            )
            
            if response.status_code == 200:
                result = response.json()
                analysis_text = result['choices'][0]['message']['content']
                
                # Try to parse JSON from the response
                try:
                    analysis = json.loads(analysis_text)
                except json.JSONDecodeError:
                    # If JSON parsing fails, create a structured response
                    analysis = {
                        "change_summary": "Analysis completed but parsing failed",
                        "impact_level": "Unknown",
                        "affected_areas": [],
                        "risk_assessment": "Unable to assess",
                        "benefits": "Unable to assess",
                        "recommendation": "Needs Revision",
                        "reasoning": analysis_text,
                        "suggested_revisions": "Please review manually"
                    }
                
                return analysis
            else:
                return {
                    "error": f"OpenAI API error: {response.status_code}",
                    "recommendation": "Needs Revision"
                }
                
        except Exception as e:
            return {
                "error": f"Analysis failed: {str(e)}",
                "recommendation": "Needs Revision"
            }
    
    def create_review_request(self, new_content: str, submitted_by: str, description: str = "") -> Dict:
        """Create a new review request for master prompt changes"""
        
        # Analyze the change
        analysis = self.analyze_master_prompt_change(new_content)
        
        # Get current master prompt
        current_content = self.get_current_master_prompt()
        
        # Create review record
        review_data = {
            "title": f"Master Prompt Review - {datetime.now().strftime('%Y-%m-%d %H:%M')}",
            "content": new_content,
            "material_type": "master_prompt_review",
            "source_type": "compass_review_system",
            "source_creator": submitted_by,
            "source_url": "master_prompt_review",
            "metadata": json.dumps({
                "review_id": f"review_{datetime.now().strftime('%Y%m%d_%H%M%S')}",
                "submitted_by": submitted_by,
                "submission_date": datetime.now().isoformat(),
                "description": description,
                "status": self.STATES["PENDING"]
            }, default=str),
            "content_hash": str(hash(new_content)),
            "upload_date": datetime.now().isoformat(),
            "status": "pending_review",
            # "tags": '["master_prompt", "review", "pending"]',  # Temporarily disabled due to array format issues
            "notes": f"Review request by {submitted_by}. Impact: {analysis.get('impact_level', 'Unknown')}. Recommendation: {analysis.get('recommendation', 'Unknown')}"
        }
        
        # Upload to Supabase
        try:
            api_url = f"{self.supabase_url}/rest/v1/internal_teaching_materials"
            response = requests.post(api_url, headers=self.headers, json=review_data)
            
            if response.status_code == 201:
                # Supabase returns empty response on successful insert
                # We need to query for the inserted record
                try:
                    # Get the inserted record by content hash
                    query_url = f"{self.supabase_url}/rest/v1/internal_teaching_materials?content_hash=eq.{str(hash(new_content))}&order=upload_date.desc&limit=1"
                    query_response = requests.get(query_url, headers=self.headers)
                    
                    if query_response.status_code == 200:
                        result = query_response.json()
                        if result and len(result) > 0:
                            logging.info(f"Review request created successfully: {result[0]['material_id']}")
                            return {
                                "success": True,
                                "review_id": result[0]['material_id'],
                                "analysis": analysis
                            }
                        else:
                            logging.error("Could not retrieve inserted record")
                            return {
                                "success": False,
                                "error": "Could not retrieve inserted record"
                            }
                    else:
                        logging.error(f"Failed to query inserted record: {query_response.status_code}")
                        return {
                            "success": False,
                            "error": f"Query failed: {query_response.status_code}"
                        }
                except Exception as e:
                    logging.error(f"Error retrieving inserted record: {str(e)}")
                    return {
                        "success": False,
                        "error": f"Retrieval error: {str(e)}"
                    }
            else:
                logging.error(f"Failed to create review request: {response.status_code} - {response.text}")
                return {
                    "success": False,
                    "error": f"Database error: {response.status_code}"
                }
                
        except Exception as e:
            logging.error(f"Error creating review request: {str(e)}")
            logging.error(f"Review data: {review_data}")
            return {
                "success": False,
                "error": str(e)
            }
    
    def get_current_master_prompt(self) -> str:
        """Get the current canonical master prompt"""
        try:
            # Query for the current master prompt
            api_url = f"{self.supabase_url}/rest/v1/internal_teaching_materials?material_type=eq.master_prompt&status=eq.active&order=upload_date.desc&limit=1"
            response = requests.get(api_url, headers=self.headers)
            
            if response.status_code == 200:
                results = response.json()
                if results:
                    return results[0]['content']
                else:
                    return "No current master prompt found"
            else:
                return f"Error retrieving master prompt: {response.status_code}"
                
        except Exception as e:
            return f"Error: {str(e)}"
    
    def approve_review(self, review_id: str, approver: str, reason: str = "") -> Dict:
        """Approve a master prompt review"""
        return self._update_review_status(review_id, self.STATES["APPROVED"], approver, reason)
    
    def reject_review(self, review_id: str, rejector: str, reason: str = "") -> Dict:
        """Reject a master prompt review"""
        return self._update_review_status(review_id, self.STATES["REJECTED"], rejector, reason)
    
    def request_revision(self, review_id: str, reviewer: str, reason: str = "") -> Dict:
        """Request revision of a master prompt review"""
        return self._update_review_status(review_id, self.STATES["NEEDS_REVISION"], reviewer, reason)
    
    def _update_review_status(self, review_id: str, status: str, reviewer: str, reason: str = "") -> Dict:
        """Update the status of a review"""
        try:
            # Get current review data
            api_url = f"{self.supabase_url}/rest/v1/internal_teaching_materials?material_id=eq.{review_id}"
            response = requests.get(api_url, headers=self.headers)
            
            if response.status_code != 200:
                return {"success": False, "error": "Review not found"}
            
            review_data = response.json()[0]
            metadata = json.loads(review_data['metadata'])
            
            # Update metadata
            if status == self.STATES["APPROVED"]:
                metadata['approvals'].append({
                    "reviewer": reviewer,
                    "date": datetime.now().isoformat(),
                    "reason": reason
                })
            elif status == self.STATES["REJECTED"]:
                metadata['rejections'].append({
                    "reviewer": reviewer,
                    "date": datetime.now().isoformat(),
                    "reason": reason
                })
            
            metadata['status'] = status
            metadata['final_decision'] = status
            metadata['decision_date'] = datetime.now().isoformat()
            metadata['decision_reason'] = reason
            
            # Update the record
            update_data = {
                "metadata": json.dumps(metadata),
                "status": status,
                "notes": f"Status updated to {status} by {reviewer}. Reason: {reason}"
            }
            
            update_url = f"{self.supabase_url}/rest/v1/internal_teaching_materials?material_id=eq.{review_id}"
            update_response = requests.patch(update_url, headers=self.headers, json=update_data)
            
            if update_response.status_code == 204:
                # If approved, update the master prompt
                if status == self.STATES["APPROVED"]:
                    self._apply_master_prompt_change(review_data['content'])
                
                return {"success": True, "status": status}
            else:
                return {"success": False, "error": f"Update failed: {update_response.status_code}"}
                
        except Exception as e:
            return {"success": False, "error": str(e)}
    
    def _apply_master_prompt_change(self, new_content: str):
        """Apply the approved master prompt change"""
        try:
            # Deactivate current master prompt
            current_url = f"{self.supabase_url}/rest/v1/internal_teaching_materials?material_type=eq.master_prompt&status=eq.active"
            deactivate_data = {"status": "inactive"}
            requests.patch(current_url, headers=self.headers, json=deactivate_data)
            
            # Create new active master prompt
            new_master_data = {
                "title": f"Master Prompt - {datetime.now().strftime('%Y-%m-%d %H:%M')}",
                "content": new_content,
                "material_type": "master_prompt",
                "source_type": "compass_system",
                "source_creator": "Master_Prompt_Review_System",
                "source_url": "approved_review",
                "metadata": json.dumps({
                    "version": datetime.now().strftime('%Y%m%d_%H%M%S'),
                    "approved_date": datetime.now().isoformat(),
                    "previous_version": "deactivated"
                }),
                "content_hash": str(hash(new_content)),
                "upload_date": datetime.now().isoformat(),
                "status": "active",
                "tags": json.dumps(["master_prompt", "canonical", "active"]),
                "notes": "Canonical master prompt - approved through review system"
            }
            
            api_url = f"{self.supabase_url}/rest/v1/internal_teaching_materials"
            response = requests.post(api_url, headers=self.headers, json=new_master_data)
            
            if response.status_code == 201:
                logging.info("Master prompt successfully updated")
            else:
                logging.error(f"Failed to update master prompt: {response.status_code}")
                
        except Exception as e:
            logging.error(f"Error applying master prompt change: {str(e)}")
    
    def get_pending_reviews(self) -> List[Dict]:
        """Get all pending review requests"""
        try:
            api_url = f"{self.supabase_url}/rest/v1/internal_teaching_materials?material_type=eq.master_prompt_review&status=eq.pending_review&order=upload_date.desc"
            response = requests.get(api_url, headers=self.headers)
            
            if response.status_code == 200:
                reviews = response.json()
                return [
                    {
                        "review_id": review['material_id'],
                        "title": review['title'],
                        "submitted_by": json.loads(review['metadata']).get('submitted_by', 'Unknown'),
                        "submission_date": json.loads(review['metadata']).get('submission_date', 'Unknown'),
                        "impact_level": json.loads(review['metadata']).get('analysis', {}).get('impact_level', 'Unknown'),
                        "recommendation": json.loads(review['metadata']).get('analysis', {}).get('recommendation', 'Unknown'),
                        "description": json.loads(review['metadata']).get('description', '')
                    }
                    for review in reviews
                ]
            else:
                return []
                
        except Exception as e:
            logging.error(f"Error getting pending reviews: {str(e)}")
            return []
