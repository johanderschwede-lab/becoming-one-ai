# build this

import streamlit as st
import json
import os
from datetime import datetime
from pathlib import Path
import pandas as pd

class TrackingDashboard:
    def __init__(self):
        st.set_page_config(
            page_title="Document Processing Dashboard",
            layout="wide"
        )
        self.load_data()
        
    def load_data(self):
        """Load tracking database"""
        with open("document_tracking.json", 'r') as f:
            self.data = json.load(f)
    
    def render_header(self):
        """Render dashboard header"""
        st.title("📚 Document Processing Dashboard")
        
        # Quick stats
        col1, col2, col3, col4 = st.columns(4)
        
        with col1:
            st.metric(
                "Total Documents",
                len(self.data["pending"]) + len(self.data["processed"])
            )
        with col2:
            st.metric(
                "Processed",
                len(self.data["processed"])
            )
        with col3:
            st.metric(
                "Pending",
                len(self.data["pending"])
            )
        with col4:
            st.metric(
                "Categories",
                len(self.data["categories"])
            )
    
    def render_document_table(self):
        """Render interactive document table"""
        st.header("📋 Document Overview")
        
        # Convert data to DataFrame
        docs = []
        for status, items in [("pending", self.data["pending"]), ("processed", self.data["processed"])]:
            for doc_id, info in items.items():
                docs.append({
                    "Document": doc_id,
                    "Status": status,
                    "Priority": info["priority"],
                    "Categories": ", ".join(info["categories"]),
                    "Analyzed": info["analyzed_at"]
                })
        
        df = pd.DataFrame(docs)
        
        # Filters
        col1, col2 = st.columns(2)
        with col1:
            status_filter = st.multiselect(
                "Filter by Status",
                ["pending", "processed"],
                default=["pending", "processed"]
            )
        with col2:
            priority_filter = st.multiselect(
                "Filter by Priority",
                range(1, 6),
                default=range(1, 6)
            )
        
        # Apply filters
        mask = (
            df["Status"].isin(status_filter) &
            df["Priority"].isin(priority_filter)
        )
        filtered_df = df[mask]
        
        # Display table
        st.dataframe(
            filtered_df,
            column_config={
                "Document": st.column_config.TextColumn("Document"),
                "Status": st.column_config.TextColumn("Status"),
                "Priority": st.column_config.NumberColumn("Priority"),
                "Categories": st.column_config.TextColumn("Categories"),
                "Analyzed": st.column_config.DatetimeColumn("Analyzed")
            }
        )
    
    def render_category_overview(self):
        """Render category statistics and distribution"""
        st.header("📊 Category Distribution")
        
        # Calculate category stats
        cat_stats = {}
        for cat, docs in self.data["categories"].items():
            cat_stats[cat] = {
                "total": len(docs),
                "processed": sum(1 for doc in docs if doc in self.data["processed"]),
                "pending": sum(1 for doc in docs if doc in self.data["pending"])
            }
        
        # Convert to DataFrame
        df = pd.DataFrame.from_dict(cat_stats, orient='index')
        
        # Display as chart
        st.bar_chart(df)
        
        # Show category details
        st.subheader("Category Details")
        st.dataframe(df)
    
    def render_processing_plan(self):
        """Render processing plan and progress"""
        st.header("📈 Processing Plan")
        
        # Group by priority
        priority_groups = {i: [] for i in range(5, 0, -1)}
        for doc_id, info in self.data["pending"].items():
            priority_groups[info["priority"]].append((doc_id, info))
        
        # Show plan
        for priority in range(5, 0, -1):
            docs = priority_groups[priority]
            if not docs:
                continue
            
            st.subheader(f"Priority {priority}")
            
            for doc_id, info in docs:
                col1, col2 = st.columns([4, 1])
                with col1:
                    st.write(f"📄 {doc_id}")
                    st.write(f"Categories: {', '.join(info['categories'])}")
                with col2:
                    if st.button(f"Mark Processed {doc_id}"):
                        self.mark_processed(doc_id)
                        st.rerun()
    
    def mark_processed(self, doc_id: str):
        """Mark a document as processed"""
        if doc_id in self.data["pending"]:
            doc_info = self.data["pending"].pop(doc_id)
            doc_info["processed_at"] = datetime.now().isoformat()
            self.data["processed"][doc_id] = doc_info
            
            with open("document_tracking.json", 'w') as f:
                json.dump(self.data, f, indent=2)
    
    def main(self):
        """Main dashboard render"""
        self.render_header()
        
        tab1, tab2, tab3 = st.tabs([
            "Documents",
            "Categories",
            "Processing Plan"
        ])
        
        with tab1:
            self.render_document_table()
        with tab2:
            self.render_category_overview()
        with tab3:
            self.render_processing_plan()

if __name__ == "__main__":
    dashboard = TrackingDashboard()
    dashboard.main()
