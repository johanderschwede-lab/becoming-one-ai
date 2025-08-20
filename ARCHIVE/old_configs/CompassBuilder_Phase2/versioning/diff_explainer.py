# build this

import yaml
import difflib
from typing import Dict, List, Tuple
import openai
from datetime import datetime

class DiffExplainer:
    def __init__(self, api_key: str):
        self.openai = openai
        self.openai.api_key = api_key
        
    def extract_diff(self, old_yaml: str, new_yaml: str) -> List[str]:
        """Generate a diff between two YAML strings"""
        old_lines = old_yaml.splitlines()
        new_lines = new_yaml.splitlines()
        
        diff = list(difflib.unified_diff(
            old_lines,
            new_lines,
            fromfile='old',
            tofile='new',
            lineterm=''
        ))
        return diff
    
    def categorize_changes(self, diff_lines: List[str]) -> Dict[str, List[str]]:
        """Categorize changes into additions, deletions, and modifications"""
        changes = {
            "additions": [],
            "deletions": [],
            "modifications": []
        }
        
        current_section = None
        for line in diff_lines:
            if line.startswith('+') and not line.startswith('+++'):
                changes["additions"].append(line[1:].strip())
            elif line.startswith('-') and not line.startswith('---'):
                changes["deletions"].append(line[1:].strip())
            elif line.startswith('@'):
                current_section = line
                
        # Identify modifications (pairs of additions/deletions)
        for del_line in changes["deletions"][:]:
            for add_line in changes["additions"][:]:
                if self._similarity_score(del_line, add_line) > 0.5:
                    changes["modifications"].append((del_line, add_line))
                    changes["deletions"].remove(del_line)
                    changes["additions"].remove(add_line)
                    break
                    
        return changes
    
    def _similarity_score(self, str1: str, str2: str) -> float:
        """Calculate similarity between two strings"""
        matcher = difflib.SequenceMatcher(None, str1, str2)
        return matcher.ratio()
    
    async def explain_changes(self, old_yaml: str, new_yaml: str) -> str:
        """Generate a human-readable explanation of changes"""
        diff = self.extract_diff(old_yaml, new_yaml)
        changes = self.categorize_changes(diff)
        
        # Prepare context for GPT
        context = f"""
        Analyze these YAML changes and explain what changed and why it matters:
        
        Additions:
        {chr(10).join(changes['additions'])}
        
        Deletions:
        {chr(10).join(changes['deletions'])}
        
        Modifications:
        {chr(10).join([f'{old} → {new}' for old, new in changes['modifications']])}
        """
        
        response = await openai.ChatCompletion.acreate(
            model="gpt-4",
            messages=[
                {"role": "system", "content": "You are an expert at analyzing YAML changes and explaining their impact in clear, human terms."},
                {"role": "user", "content": context}
            ]
        )
        
        return response.choices[0].message.content
    
    def generate_summary_report(self, old_yaml: str, new_yaml: str, explanation: str) -> str:
        """Generate a complete summary report"""
        changes = self.categorize_changes(self.extract_diff(old_yaml, new_yaml))
        
        report = f"""
        # 📊 YAML Change Analysis
        Generated: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}
        
        ## 🤖 AI Explanation
        {explanation}
        
        ## 📈 Change Statistics
        - Additions: {len(changes['additions'])}
        - Deletions: {len(changes['deletions'])}
        - Modifications: {len(changes['modifications'])}
        
        ## 🔍 Detailed Changes
        
        ### ➕ Additions
        {''.join([f'- {item}\\n' for item in changes['additions']])}
        
        ### ➖ Deletions
        {''.join([f'- {item}\\n' for item in changes['deletions']])}
        
        ### 🔄 Modifications
        {''.join([f'- {old} → {new}\\n' for old, new in changes['modifications']])}
        """
        
        return report

async def main():
    """Main diff explanation routine"""
    explainer = DiffExplainer(os.getenv("OPENAI_API_KEY"))
    
    # Example usage
    old_yaml = """
    title: Test Prompt
    version: 1.0.0
    content: Original content
    """
    
    new_yaml = """
    title: Test Prompt
    version: 1.0.1
    content: Updated content with new features
    settings:
      advanced: true
    """
    
    explanation = await explainer.explain_changes(old_yaml, new_yaml)
    report = explainer.generate_summary_report(old_yaml, new_yaml, explanation)
    print(report)

if __name__ == "__main__":
    import asyncio
    asyncio.run(main())
