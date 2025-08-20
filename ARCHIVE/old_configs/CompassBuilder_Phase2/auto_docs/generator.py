# build this

import yaml
import os
from typing import Dict, List, Optional
import openai
from datetime import datetime
from pathlib import Path

class PromptAnalyzer:
    def __init__(self, api_key: str):
        self.openai = openai
        self.openai.api_key = api_key
        
    async def analyze_prompt(self, yaml_content: Dict) -> Dict:
        """Analyze a prompt module and extract key characteristics"""
        
        analysis_prompt = f"""
        Analyze this AI prompt module and extract key characteristics:
        
        {yaml.dump(yaml_content, sort_keys=False)}
        
        Provide a structured analysis covering:
        1. Primary Purpose
        2. Intended Usage
        3. Tone and Style
        4. Key Parameters
        5. Expected Outputs
        6. Important Constraints
        7. Related Modules/Dependencies
        """
        
        response = await openai.ChatCompletion.acreate(
            model="gpt-4",
            messages=[
                {"role": "system", "content": "You are an expert at analyzing AI prompts and extracting their key characteristics."},
                {"role": "user", "content": analysis_prompt}
            ]
        )
        
        return {
            "analysis": response.choices[0].message.content,
            "analyzed_at": datetime.now().isoformat()
        }

class DocumentationGenerator:
    def __init__(self, analyzer: PromptAnalyzer):
        self.analyzer = analyzer
        
    def _create_markdown_doc(self, yaml_path: str, analysis: Dict) -> str:
        """Create markdown documentation for a prompt module"""
        
        with open(yaml_path, 'r') as f:
            yaml_content = yaml.safe_load(f)
            
        doc = f"""
        # {yaml_content.get('title', 'Untitled Prompt')}
        
        *Generated on: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}*
        
        ## Overview
        {yaml_content.get('description', 'No description provided.')}
        
        ## Analysis
        {analysis['analysis']}
        
        ## Technical Details
        - **Version:** {yaml_content.get('version', 'N/A')}
        - **Type:** {yaml_content.get('type', 'N/A')}
        - **Last Updated:** {yaml_content.get('last_updated', 'N/A')}
        
        ## Usage Examples
        ```yaml
        {yaml.dump(yaml_content.get('examples', {}), sort_keys=False)}
        ```
        
        ## Related Modules
        {chr(10).join(['- ' + mod for mod in yaml_content.get('related_modules', [])])}
        
        ## Notes
        {yaml_content.get('notes', 'No additional notes.')}
        """
        
        return doc
        
    def _create_html_doc(self, markdown_content: str) -> str:
        """Convert markdown to HTML with styling"""
        # TODO: Implement markdown to HTML conversion
        pass
        
    async def generate_docs(self, input_dir: str, output_dir: str):
        """Generate documentation for all YAML files in directory"""
        os.makedirs(output_dir, exist_ok=True)
        
        for file in os.listdir(input_dir):
            if file.endswith(('.yaml', '.yml')):
                yaml_path = os.path.join(input_dir, file)
                
                # Analyze prompt
                with open(yaml_path, 'r') as f:
                    yaml_content = yaml.safe_load(f)
                analysis = await self.analyzer.analyze_prompt(yaml_content)
                
                # Generate markdown
                doc = self._create_markdown_doc(yaml_path, analysis)
                
                # Save documentation
                doc_path = os.path.join(output_dir, f"{Path(file).stem}.md")
                with open(doc_path, 'w') as f:
                    f.write(doc)
                    
                print(f"Generated documentation for {file}")
                
    def generate_index(self, output_dir: str):
        """Generate index page for all documentation"""
        index = """
        # Prompt Module Documentation
        
        ## Available Modules
        
        """
        
        for file in sorted(os.listdir(output_dir)):
            if file.endswith('.md') and file != 'index.md':
                with open(os.path.join(output_dir, file), 'r') as f:
                    content = f.read()
                    title = content.split('\n')[1].strip('# ')
                    index += f"- [{title}]({file})\n"
                    
        with open(os.path.join(output_dir, 'index.md'), 'w') as f:
            f.write(index)

async def main():
    """Main documentation generation routine"""
    analyzer = PromptAnalyzer(os.getenv("OPENAI_API_KEY"))
    generator = DocumentationGenerator(analyzer)
    
    input_dir = os.getenv("YAML_INPUT_DIR", "../CompassBuilder_Starter_Kit/output")
    output_dir = "docs"
    
    await generator.generate_docs(input_dir, output_dir)
    generator.generate_index(output_dir)
    
if __name__ == "__main__":
    import asyncio
    asyncio.run(main())
