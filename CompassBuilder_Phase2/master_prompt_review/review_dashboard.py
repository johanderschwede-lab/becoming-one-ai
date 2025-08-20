import streamlit as st
import json
from datetime import datetime
from review_system import MasterPromptReviewSystem
import requests

def main():
    st.set_page_config(
        page_title="Master Prompt Review System",
        page_icon="🔍",
        layout="wide"
    )
    
    st.title("🔍 Master Prompt Review System")
    st.markdown("Review and approve changes to the canonical master prompt")
    
    # Initialize review system
    review_system = MasterPromptReviewSystem()
    
    # Sidebar navigation
    st.sidebar.title("Navigation")
    page = st.sidebar.selectbox(
        "Choose a page",
        ["📋 Pending Reviews", "📝 Submit New Review", "📊 Review History", "⚙️ Current Master Prompt"]
    )
    
    if page == "📋 Pending Reviews":
        show_pending_reviews(review_system)
    elif page == "📝 Submit New Review":
        submit_new_review(review_system)
    elif page == "📊 Review History":
        show_review_history(review_system)
    elif page == "⚙️ Current Master Prompt":
        show_current_master_prompt(review_system)

def show_pending_reviews(review_system):
    st.header("📋 Pending Reviews")
    
    # Get pending reviews
    pending_reviews = review_system.get_pending_reviews()
    
    if not pending_reviews:
        st.info("No pending reviews found.")
        return
    
    for review in pending_reviews:
        with st.expander(f"🔍 {review['title']} - {review['impact_level']} Impact"):
            col1, col2 = st.columns([2, 1])
            
            with col1:
                st.write(f"**Submitted by:** {review['submitted_by']}")
                st.write(f"**Date:** {review['submission_date']}")
                st.write(f"**Impact Level:** {review['impact_level']}")
                st.write(f"**AI Recommendation:** {review['recommendation']}")
                
                if review['description']:
                    st.write(f"**Description:** {review['description']}")
            
            with col2:
                st.write("**Actions:**")
                
                if st.button(f"✅ Approve", key=f"approve_{review['review_id']}"):
                    reason = st.text_input("Reason for approval:", key=f"approve_reason_{review['review_id']}")
                    if st.button("Confirm Approval", key=f"confirm_approve_{review['review_id']}"):
                        result = review_system.approve_review(review['review_id'], "Dashboard_User", reason)
                        if result['success']:
                            st.success("Review approved!")
                            st.rerun()
                        else:
                            st.error(f"Error: {result['error']}")
                
                if st.button(f"❌ Reject", key=f"reject_{review['review_id']}"):
                    reason = st.text_input("Reason for rejection:", key=f"reject_reason_{review['review_id']}")
                    if st.button("Confirm Rejection", key=f"confirm_reject_{review['review_id']}"):
                        result = review_system.reject_review(review['review_id'], "Dashboard_User", reason)
                        if result['success']:
                            st.success("Review rejected!")
                            st.rerun()
                        else:
                            st.error(f"Error: {result['error']}")
                
                if st.button(f"🔄 Request Revision", key=f"revision_{review['review_id']}"):
                    reason = st.text_input("Revision request:", key=f"revision_reason_{review['review_id']}")
                    if st.button("Confirm Revision Request", key=f"confirm_revision_{review['review_id']}"):
                        result = review_system.request_revision(review['review_id'], "Dashboard_User", reason)
                        if result['success']:
                            st.success("Revision requested!")
                            st.rerun()
                        else:
                            st.error(f"Error: {result['error']}")

def submit_new_review(review_system):
    st.header("📝 Submit New Master Prompt Review")
    
    # Get current master prompt
    current_prompt = review_system.get_current_master_prompt()
    
    st.subheader("Current Master Prompt")
    st.text_area("Current:", value=current_prompt, height=200, disabled=True)
    
    st.subheader("Proposed New Master Prompt")
    new_prompt = st.text_area("New Master Prompt:", height=300, placeholder="Enter your proposed new master prompt here...")
    
    description = st.text_input("Description of changes:", placeholder="Briefly describe what you're changing and why...")
    
    submitted_by = st.text_input("Your name:", placeholder="Enter your name for the review record...")
    
    if st.button("🔍 Analyze Changes"):
        if new_prompt and submitted_by:
            with st.spinner("Analyzing changes..."):
                analysis = review_system.analyze_master_prompt_change(new_prompt, current_prompt)
            
            st.subheader("📊 Impact Analysis")
            
            col1, col2 = st.columns(2)
            
            with col1:
                st.metric("Impact Level", analysis.get('impact_level', 'Unknown'))
                st.metric("Recommendation", analysis.get('recommendation', 'Unknown'))
                
                if analysis.get('affected_areas'):
                    st.write("**Affected Areas:**")
                    for area in analysis['affected_areas']:
                        st.write(f"• {area}")
            
            with col2:
                st.write("**Change Summary:**")
                st.write(analysis.get('change_summary', 'No summary available'))
                
                st.write("**Risk Assessment:**")
                st.write(analysis.get('risk_assessment', 'No risk assessment available'))
                
                st.write("**Expected Benefits:**")
                st.write(analysis.get('benefits', 'No benefits listed'))
            
            st.write("**Detailed Reasoning:**")
            st.write(analysis.get('reasoning', 'No reasoning provided'))
            
            if analysis.get('suggested_revisions'):
                st.write("**Suggested Revisions:**")
                st.write(analysis.get('suggested_revisions'))
            
            # Submit button
            if st.button("📤 Submit for Review"):
                with st.spinner("Submitting review request..."):
                    result = review_system.create_review_request(new_prompt, submitted_by, description)
                
                if result['success']:
                    st.success(f"✅ Review request submitted successfully! Review ID: {result['review_id']}")
                    st.info("The review is now pending approval. You can track its status in the Pending Reviews section.")
                else:
                    st.error(f"❌ Error submitting review: {result['error']}")
        else:
            st.warning("Please fill in both the new master prompt and your name.")

def show_review_history(review_system):
    st.header("📊 Review History")
    st.info("This feature will show the history of all master prompt reviews and their outcomes.")
    st.write("Coming soon...")

def show_current_master_prompt(review_system):
    st.header("⚙️ Current Master Prompt")
    
    current_prompt = review_system.get_current_master_prompt()
    
    if current_prompt and not current_prompt.startswith("Error"):
        st.subheader("Active Master Prompt")
        st.text_area("Current Canonical Master Prompt:", value=current_prompt, height=400, disabled=True)
        
        st.info("This is the current canonical master prompt that all AI systems are using.")
        
        # Show metadata if available
        try:
            api_url = f"{review_system.supabase_url}/rest/v1/internal_teaching_materials?material_type=eq.master_prompt&status=eq.active&order=upload_date.desc&limit=1"
            response = requests.get(api_url, headers=review_system.headers)
            
            if response.status_code == 200:
                results = response.json()
                if results:
                    metadata = json.loads(results[0]['metadata'])
                    st.write(f"**Version:** {metadata.get('version', 'Unknown')}")
                    st.write(f"**Approved Date:** {metadata.get('approved_date', 'Unknown')}")
                    st.write(f"**Upload Date:** {results[0]['upload_date']}")
        except:
            pass
    else:
        st.warning("No active master prompt found.")
        st.write("You may need to create an initial master prompt or approve a pending review.")

if __name__ == "__main__":
    main()
