# build this

import streamlit as st
import yaml
import os
from datetime import datetime
from typing import Dict, List, Optional

class PromptDashboard:
    def __init__(self):
        st.set_page_config(
            page_title="Compass Module Dashboard",
            layout="wide"
        )
        
    def render_header(self):
        """Render dashboard header"""
        st.title("🧭 Compass Module Dashboard")
        st.markdown("---")
        
        # Quick stats in columns
        col1, col2, col3, col4 = st.columns(4)
        with col1:
            st.metric("Total Modules", "42")
        with col2:
            st.metric("Active Agents", "7")
        with col3:
            st.metric("Recent Changes", "3")
        with col4:
            st.metric("Pending Reviews", "2")
    
    def render_module_table(self, modules: List[Dict]):
        """Render interactive module table"""
        st.subheader("📚 Module Overview")
        
        # Filters
        col1, col2 = st.columns(2)
        with col1:
            selected_type = st.selectbox(
                "Filter by Type",
                ["All", "Core", "Agent", "Integration", "Legal"]
            )
        with col2:
            search = st.text_input("Search Modules")
            
        # Module table
        st.dataframe(
            modules,
            column_config={
                "title": "Module",
                "type": "Type",
                "version": "Version",
                "last_updated": "Updated",
                "status": "Status",
                "actions": st.column_config.Column(
                    "Actions",
                    help="Available actions",
                    width="small"
                )
            }
        )
    
    def render_diff_viewer(self, module_id: Optional[str] = None):
        """Render version diff viewer"""
        st.subheader("📊 Version Comparison")
        
        if module_id:
            # Show diff
            col1, col2 = st.columns(2)
            with col1:
                st.code("Old Version", language="yaml")
            with col2:
                st.code("New Version", language="yaml")
                
            # Diff summary
            st.info("🔄 Changes Summary")
            st.markdown("""
            - Added: New configuration options
            - Modified: Response templates
            - Removed: Deprecated settings
            """)
    
    def render_agent_mappings(self):
        """Render agent relationship diagram"""
        st.subheader("🤖 Agent Mappings")
        
        # Mermaid diagram
        st.markdown("""
        ```mermaid
        graph TD
            A[Core Agent] --> B[Content Processor]
            A --> C[User Manager]
            B --> D[Knowledge Base]
            C --> E[Auth Service]
        ```
        """)
    
    def render_tag_cloud(self):
        """Render interactive tag cloud"""
        st.subheader("🏷️ Tag Overview")
        
        # Tag buttons
        cols = st.columns(4)
        tags = ["#core", "#agent", "#integration", "#legal", "#active", "#review", "#deprecated"]
        for i, tag in enumerate(tags):
            with cols[i % 4]:
                st.button(tag)
    
    def main(self):
        """Main dashboard render"""
        self.render_header()
        
        # Tabs for different views
        tab1, tab2, tab3 = st.tabs(["Modules", "Versions", "Agents"])
        
        with tab1:
            self.render_module_table([])
            self.render_tag_cloud()
            
        with tab2:
            self.render_diff_viewer()
            
        with tab3:
            self.render_agent_mappings()

if __name__ == "__main__":
    dashboard = PromptDashboard()
    dashboard.main()
