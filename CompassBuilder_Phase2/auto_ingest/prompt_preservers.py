# build this

import re
from pathlib import Path
from typing import List, Dict, Optional, Tuple
import json
from datetime import datetime

class PromptPreserver:
    def __init__(self):
        # Markers for user prompts in chat files
        self.prompt_markers = [
            r"Human:|User:|Johan:|<user>|<user_message>|<user_query>",
            r"system message:|system:|<system>|<system_message>"
        ]
        
        # Track extracted prompts
        self.extracted_prompts = {}
        
    def extract_prompts(self, content: str, file_path: str) -> List[Dict]:
        """Extract original prompts from chat content"""
        prompts = []
        current_prompt = None
        
        # Split content into lines
        lines = content.split('\n')
        
        for i, line in enumerate(lines):
            # Check if line starts a prompt
            for marker in self.prompt_markers:
                if re.match(marker, line):
                    # If we were collecting a previous prompt, save it
                    if current_prompt:
                        prompts.append(current_prompt)
                    
                    # Start new prompt
                    current_prompt = {
                        "type": "user" if "Human:|User:|Johan:" in marker else "system",
                        "source_file": str(file_path),
                        "line_number": i + 1,
                        "content": [],
                        "context_before": lines[max(0, i-5):i],  # Preserve 5 lines of context
                        "extracted_at": datetime.now().isoformat()
                    }
                    continue
            
            # If we're collecting a prompt, add the line
            if current_prompt:
                current_prompt["content"].append(line)
                
                # Check if prompt ends (next marker or significant whitespace)
                next_line = lines[i+1] if i+1 < len(lines) else ""
                if any(re.match(marker, next_line) for marker in self.prompt_markers) or \
                   (not next_line.strip() and not lines[i+2].strip() if i+2 < len(lines) else False):
                    current_prompt["content"] = "\n".join(current_prompt["content"])
                    prompts.append(current_prompt)
                    current_prompt = None
        
        # Save last prompt if exists
        if current_prompt:
            current_prompt["content"] = "\n".join(current_prompt["content"])
            prompts.append(current_prompt)
        
        return prompts
    
    def preserve_chat_file(self, file_path: str, output_dir: str) -> Tuple[Path, List[Dict]]:
        """Preserve chat file with all prompts intact"""
        # Read original content
        with open(file_path, 'r') as f:
            content = f.read()
        
        # Extract prompts
        prompts = self.extract_prompts(content, file_path)
        
        # Create preservation directory
        preserve_dir = Path(output_dir) / "preserved_chats"
        preserve_dir.mkdir(parents=True, exist_ok=True)
        
        # Save original file
        original_path = preserve_dir / Path(file_path).name
        with open(original_path, 'w') as f:
            f.write(content)
        
        # Save extracted prompts with metadata
        prompts_path = preserve_dir / f"{Path(file_path).stem}_prompts.json"
        with open(prompts_path, 'w') as f:
            json.dump({
                "source_file": str(file_path),
                "extracted_at": datetime.now().isoformat(),
                "prompts": prompts
            }, f, indent=2)
        
        # Track these prompts
        self.extracted_prompts[str(file_path)] = prompts
        
        return original_path, prompts
    
    def is_chat_file(self, file_path: str) -> bool:
        """Determine if file is a chat export"""
        # Check file content for chat markers
        try:
            with open(file_path, 'r') as f:
                content = f.read(1000)  # Read first 1000 chars
                return any(re.search(marker, content) for marker in self.prompt_markers)
        except:
            return False
    
    def create_prompt_index(self, output_dir: str):
        """Create an index of all preserved prompts"""
        if not self.extracted_prompts:
            return
        
        index_path = Path(output_dir) / "preserved_chats" / "prompt_index.md"
        
        with open(index_path, 'w') as f:
            f.write("# Preserved Original Prompts Index\n\n")
            
            for source_file, prompts in self.extracted_prompts.items():
                f.write(f"## {Path(source_file).name}\n\n")
                
                for i, prompt in enumerate(prompts, 1):
                    f.write(f"### Prompt {i} ({prompt['type']})\n")
                    f.write(f"Line: {prompt['line_number']}\n\n")
                    f.write("Context:\n```\n")
                    f.write("\n".join(prompt['context_before']))
                    f.write("\n```\n\n")
                    f.write("Content:\n```\n")
                    f.write(prompt['content'])
                    f.write("\n```\n\n")
                
                f.write("---\n\n")

class PromptValidator:
    def __init__(self):
        self.required_elements = {
            "user": ["intent", "context", "request"],
            "system": ["constraints", "behavior", "response_format"]
        }
    
    def validate_prompt(self, prompt: Dict) -> Dict:
        """Validate a prompt's completeness"""
        validation = {
            "is_valid": True,
            "missing_elements": [],
            "recommendations": []
        }
        
        # Check for required elements based on type
        if prompt["type"] in self.required_elements:
            for element in self.required_elements[prompt["type"]]:
                if element.lower() not in prompt["content"].lower():
                    validation["missing_elements"].append(element)
                    validation["is_valid"] = False
        
        # Add recommendations if needed
        if not validation["is_valid"]:
            validation["recommendations"].append(
                f"Add missing elements: {', '.join(validation['missing_elements'])}"
            )
        
        return validation
