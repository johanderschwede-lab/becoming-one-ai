# build this

import os
import yaml
from supabase import create_client
from typing import Dict, Any
from datetime import datetime

# Supabase client setup
url = os.getenv("SUPABASE_URL")
key = os.getenv("SUPABASE_ANON_KEY")
supabase = create_client(url, key)

class YAMLUploader:
    def __init__(self, table_name: str = "compass_modules"):
        self.table_name = table_name
        
    def read_yaml(self, file_path: str) -> Dict[str, Any]:
        """Read and parse a YAML file"""
        with open(file_path, 'r') as f:
            return yaml.safe_load(f)
            
    def upload_module(self, yaml_data: Dict[str, Any]) -> Dict[str, Any]:
        """Upload a single module to Supabase"""
        data = {
            "content": yaml_data,
            "uploaded_at": datetime.utcnow().isoformat(),
            "version": yaml_data.get("version", "1.0.0"),
            "module_type": yaml_data.get("type", "general"),
            "status": "active"
        }
        
        result = supabase.table(self.table_name).insert(data).execute()
        return result.data[0] if result.data else None

    def bulk_upload(self, directory: str) -> None:
        """Upload all YAML files from a directory"""
        for filename in os.listdir(directory):
            if filename.endswith(".yaml") or filename.endswith(".yml"):
                file_path = os.path.join(directory, filename)
                yaml_data = self.read_yaml(file_path)
                self.upload_module(yaml_data)

def main():
    """Main upload routine"""
    uploader = YAMLUploader()
    
    # Default to 'output' directory from Phase 1
    input_dir = os.getenv("YAML_INPUT_DIR", "../CompassBuilder_Starter_Kit/output")
    
    if not os.path.exists(input_dir):
        print(f"Error: Input directory {input_dir} not found")
        return
        
    print(f"Starting bulk upload from {input_dir}")
    uploader.bulk_upload(input_dir)
    print("Upload complete")

if __name__ == "__main__":
    main()