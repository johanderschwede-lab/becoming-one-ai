# build this

import streamlit as st
import yaml
import os
from datetime import datetime
from typing import Dict, Any, Optional
from pathlib import Path

class PromptEditor:
    def __init__(self):
        st.set_page_config(
            page_title="Prompt Editor",
            layout="wide",
            initial_sidebar_state="expanded"
        )
        self.load_state()
        
    def load_state(self):
        """Initialize or load session state"""
        if 'current_prompt' not in st.session_state:
            st.session_state.current_prompt = None
        if 'yaml_content' not in st.session_state:
            st.session_state.yaml_content = None
            
    def render_sidebar(self):
        """Render sidebar with file operations"""
        with st.sidebar:
            st.title("📝 Prompt Editor")
            
            # File operations
            st.header("File Operations")
            
            # Load existing prompt
            uploaded_file = st.file_uploader("Load YAML", type=['yaml', 'yml'])
            if uploaded_file:
                content = yaml.safe_load(uploaded_file)
                st.session_state.yaml_content = content
                st.session_state.current_prompt = uploaded_file.name
            
            # Create new prompt
            if st.button("Create New Prompt"):
                st.session_state.yaml_content = {
                    "title": "New Prompt",
                    "version": "1.0.0",
                    "type": "general",
                    "description": "",
                    "parameters": {},
                    "content": "",
                    "examples": [],
                    "metadata": {
                        "created_at": datetime.now().isoformat(),
                        "created_by": "Prompt Editor"
                    }
                }
                st.session_state.current_prompt = "new_prompt.yaml"
            
            # Save prompt
            if st.session_state.yaml_content:
                if st.button("Save YAML"):
                    yaml_str = yaml.dump(
                        st.session_state.yaml_content,
                        sort_keys=False,
                        allow_unicode=True
                    )
                    st.download_button(
                        "Download YAML",
                        yaml_str,
                        file_name=st.session_state.current_prompt,
                        mime="application/x-yaml"
                    )
    
    def render_metadata_editor(self):
        """Render metadata editing section"""
        st.header("📋 Basic Information")
        
        col1, col2 = st.columns(2)
        with col1:
            st.session_state.yaml_content["title"] = st.text_input(
                "Title",
                value=st.session_state.yaml_content.get("title", "")
            )
            st.session_state.yaml_content["version"] = st.text_input(
                "Version",
                value=st.session_state.yaml_content.get("version", "1.0.0")
            )
            
        with col2:
            st.session_state.yaml_content["type"] = st.selectbox(
                "Type",
                ["general", "system", "user", "assistant", "function"],
                index=0 if "type" not in st.session_state.yaml_content else 
                      ["general", "system", "user", "assistant", "function"].index(
                          st.session_state.yaml_content["type"]
                      )
            )
            
        st.session_state.yaml_content["description"] = st.text_area(
            "Description",
            value=st.session_state.yaml_content.get("description", ""),
            height=100
        )
    
    def render_content_editor(self):
        """Render main content editing section"""
        st.header("📝 Prompt Content")
        
        # Main content
        st.session_state.yaml_content["content"] = st.text_area(
            "Content",
            value=st.session_state.yaml_content.get("content", ""),
            height=200
        )
        
        # Parameters
        st.subheader("Parameters")
        params = st.session_state.yaml_content.get("parameters", {})
        
        col1, col2, col3 = st.columns(3)
        with col1:
            new_param_name = st.text_input("New Parameter Name")
        with col2:
            new_param_type = st.selectbox(
                "Parameter Type",
                ["string", "number", "boolean", "array", "object"]
            )
        with col3:
            if st.button("Add Parameter"):
                params[new_param_name] = {"type": new_param_type}
                st.session_state.yaml_content["parameters"] = params
        
        # Show existing parameters
        for param_name, param_info in params.items():
            col1, col2, col3 = st.columns(3)
            with col1:
                st.text(param_name)
            with col2:
                st.text(param_info["type"])
            with col3:
                if st.button(f"Remove {param_name}"):
                    del params[param_name]
                    st.session_state.yaml_content["parameters"] = params
    
    def render_examples_editor(self):
        """Render examples editing section"""
        st.header("📚 Examples")
        
        examples = st.session_state.yaml_content.get("examples", [])
        
        # Add new example
        new_example = st.text_area("New Example")
        if st.button("Add Example"):
            examples.append(new_example)
            st.session_state.yaml_content["examples"] = examples
        
        # Show existing examples
        for i, example in enumerate(examples):
            col1, col2 = st.columns([4, 1])
            with col1:
                examples[i] = st.text_area(f"Example {i+1}", value=example)
            with col2:
                if st.button(f"Remove Example {i+1}"):
                    examples.pop(i)
                    st.session_state.yaml_content["examples"] = examples
    
    def render_preview(self):
        """Render YAML preview"""
        st.header("👁️ Preview")
        
        yaml_str = yaml.dump(
            st.session_state.yaml_content,
            sort_keys=False,
            allow_unicode=True
        )
        st.code(yaml_str, language="yaml")
    
    def main(self):
        """Main UI render"""
        self.render_sidebar()
        
        if st.session_state.yaml_content:
            tab1, tab2, tab3, tab4 = st.tabs([
                "Basic Info",
                "Content",
                "Examples",
                "Preview"
            ])
            
            with tab1:
                self.render_metadata_editor()
            with tab2:
                self.render_content_editor()
            with tab3:
                self.render_examples_editor()
            with tab4:
                self.render_preview()
        else:
            st.info("👈 Load a YAML file or create a new prompt to begin")

if __name__ == "__main__":
    editor = PromptEditor()
    editor.main()
