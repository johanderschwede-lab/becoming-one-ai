import streamlit as st
import json
from datetime import datetime
from consider_list_manager import ConsiderListManager

def main():
    st.set_page_config(
        page_title="Consider List Manager",
        page_icon="📋",
        layout="wide"
    )
    
    st.title("📋 Consider List Manager")
    st.markdown("Manage what to implement vs. what to save for later consideration")
    
    # Initialize consider list manager
    consider_manager = ConsiderListManager()
    
    # Sidebar navigation
    st.sidebar.title("Navigation")
    page = st.sidebar.selectbox(
        "Choose a page",
        ["📋 Consider List", "➕ Add New Item", "📊 Statistics", "✅ Implemented Items", "❌ Rejected Items"]
    )
    
    if page == "📋 Consider List":
        show_consider_list(consider_manager)
    elif page == "➕ Add New Item":
        add_new_item(consider_manager)
    elif page == "📊 Statistics":
        show_statistics(consider_manager)
    elif page == "✅ Implemented Items":
        show_implemented_items(consider_manager)
    elif page == "❌ Rejected Items":
        show_rejected_items(consider_manager)

def show_consider_list(consider_manager):
    st.header("📋 Consider List")
    
    # Filter options
    col1, col2 = st.columns(2)
    with col1:
        priority_filter = st.selectbox("Filter by Priority", ["All", "high", "medium", "low"])
    with col2:
        category_filter = st.selectbox("Filter by Category", ["All", "method_core", "technical", "ai_agents", "documentation", "other"])
    
    # Get consider list
    priority = priority_filter if priority_filter != "All" else None
    consider_items = consider_manager.get_consider_list(status="consider", priority=priority)
    
    if not consider_items:
        st.info("No items in the consider list.")
        return
    
    # Filter by category if needed
    if category_filter != "All":
        consider_items = [item for item in consider_items if item['category'] == category_filter]
    
    if not consider_items:
        st.info(f"No items found with the selected filters.")
        return
    
    # Display items
    for item in consider_items:
        with st.expander(f"📋 {item['title']} - {item['priority'].upper()} Priority"):
            col1, col2 = st.columns([3, 1])
            
            with col1:
                st.write(f"**Category:** {item['category']}")
                st.write(f"**Added by:** {item['added_by']}")
                st.write(f"**Date:** {item['added_date']}")
                
                if item['notes']:
                    st.write(f"**Notes:** {item['notes']}")
                
                st.write("**Content:**")
                st.text_area("Content", value=item['content'], height=150, disabled=True, key=f"content_{item['consider_id']}")
            
            with col2:
                st.write("**Actions:**")
                
                # Implement button
                if st.button(f"✅ Implement", key=f"implement_{item['consider_id']}"):
                    st.session_state[f"implement_{item['consider_id']}"] = True
                
                if st.session_state.get(f"implement_{item['consider_id']}", False):
                    implementation_notes = st.text_area("Implementation notes:", key=f"impl_notes_{item['consider_id']}")
                    if st.button("Confirm Implementation", key=f"confirm_impl_{item['consider_id']}"):
                        result = consider_manager.update_consider_item(
                            item['consider_id'], 
                            "implement", 
                            "Approved for implementation", 
                            implementation_notes
                        )
                        if result['success']:
                            st.success("Item implemented!")
                            st.rerun()
                        else:
                            st.error(f"Error: {result['error']}")
                
                # Reject button
                if st.button(f"❌ Reject", key=f"reject_{item['consider_id']}"):
                    st.session_state[f"reject_{item['consider_id']}"] = True
                
                if st.session_state.get(f"reject_{item['consider_id']}", False):
                    reject_reason = st.text_area("Rejection reason:", key=f"reject_reason_{item['consider_id']}")
                    if st.button("Confirm Rejection", key=f"confirm_reject_{item['consider_id']}"):
                        result = consider_manager.update_consider_item(
                            item['consider_id'], 
                            "reject", 
                            reject_reason
                        )
                        if result['success']:
                            st.success("Item rejected!")
                            st.rerun()
                        else:
                            st.error(f"Error: {result['error']}")
                
                # Archive button
                if st.button(f"📁 Archive", key=f"archive_{item['consider_id']}"):
                    result = consider_manager.update_consider_item(
                        item['consider_id'], 
                        "archive", 
                        "Archived for future reference"
                    )
                    if result['success']:
                        st.success("Item archived!")
                        st.rerun()
                    else:
                        st.error(f"Error: {result['error']}")

def add_new_item(consider_manager):
    st.header("➕ Add New Item to Consider List")
    
    # Form for adding new item
    content = st.text_area("Content/Description:", height=200, placeholder="Describe what you want to consider...")
    
    col1, col2 = st.columns(2)
    with col1:
        category = st.selectbox("Category:", ["method_core", "technical", "ai_agents", "documentation", "personality_systems", "sacred_library", "content_processing", "other"])
        priority = st.selectbox("Priority:", ["low", "medium", "high"])
    
    with col2:
        source = st.text_input("Your name:", placeholder="Enter your name...")
        notes = st.text_area("Additional notes:", height=100, placeholder="Any additional context...")
    
    if st.button("📋 Add to Consider List"):
        if content and source:
            result = consider_manager.add_to_consider_list(
                content, source, category, priority, notes
            )
            
            if result['success']:
                st.success(f"✅ {result['message']}")
                st.info("The item has been added to the consider list for review.")
            else:
                st.error(f"❌ Error: {result['error']}")
        else:
            st.warning("Please fill in both the content and your name.")

def show_statistics(consider_manager):
    st.header("📊 Consider List Statistics")
    
    stats = consider_manager.get_consider_stats()
    
    if not stats:
        st.info("No statistics available.")
        return
    
    # Display statistics
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        st.metric("Pending Consider", stats.get('total_consider', 0))
    
    with col2:
        st.metric("Implemented", stats.get('total_implement', 0))
    
    with col3:
        st.metric("Rejected", stats.get('total_reject', 0))
    
    with col4:
        st.metric("Archived", stats.get('total_archive', 0))
    
    # Priority breakdown
    st.subheader("By Priority")
    priority_stats = stats.get('by_priority', {})
    
    col1, col2, col3 = st.columns(3)
    with col1:
        st.metric("High Priority", priority_stats.get('high', 0))
    with col2:
        st.metric("Medium Priority", priority_stats.get('medium', 0))
    with col3:
        st.metric("Low Priority", priority_stats.get('low', 0))
    
    # Category breakdown
    st.subheader("By Category")
    category_stats = stats.get('by_category', {})
    
    if category_stats:
        for category, count in category_stats.items():
            st.write(f"**{category}:** {count} items")

def show_implemented_items(consider_manager):
    st.header("✅ Implemented Items")
    
    implemented_items = consider_manager.get_consider_list(status="implement")
    
    if not implemented_items:
        st.info("No implemented items found.")
        return
    
    for item in implemented_items:
        with st.expander(f"✅ {item['title']}"):
            st.write(f"**Category:** {item['category']}")
            st.write(f"**Priority:** {item['priority']}")
            st.write(f"**Added by:** {item['added_by']}")
            st.write(f"**Added date:** {item['added_date']}")
            
            if item['notes']:
                st.write(f"**Notes:** {item['notes']}")
            
            st.write("**Content:**")
            st.text_area("Content", value=item['content'], height=150, disabled=True, key=f"impl_content_{item['consider_id']}")

def show_rejected_items(consider_manager):
    st.header("❌ Rejected Items")
    
    rejected_items = consider_manager.get_consider_list(status="reject")
    
    if not rejected_items:
        st.info("No rejected items found.")
        return
    
    for item in rejected_items:
        with st.expander(f"❌ {item['title']}"):
            st.write(f"**Category:** {item['category']}")
            st.write(f"**Priority:** {item['priority']}")
            st.write(f"**Added by:** {item['added_by']}")
            st.write(f"**Added date:** {item['added_date']}")
            
            if item['notes']:
                st.write(f"**Notes:** {item['notes']}")
            
            st.write("**Content:**")
            st.text_area("Content", value=item['content'], height=150, disabled=True, key=f"reject_content_{item['consider_id']}")

if __name__ == "__main__":
    main()
