# write test for this

import pytest
import yaml
import os
from datetime import datetime
from ..auto_docs.generator import PromptAnalyzer, DocumentationGenerator

@pytest.fixture
def test_yaml_content():
    """Create test YAML content"""
    return {
        "title": "Test Prompt",
        "description": "A test prompt module",
        "version": "1.0.0",
        "type": "test",
        "examples": {
            "basic": "Example usage"
        },
        "related_modules": ["module1", "module2"]
    }

@pytest.fixture
def test_analysis():
    """Create test analysis result"""
    return {
        "analysis": """
        1. Primary Purpose: Testing
        2. Intended Usage: Examples
        3. Tone and Style: Technical
        4. Key Parameters: None
        5. Expected Outputs: Test results
        6. Important Constraints: None
        7. Related Modules: module1, module2
        """,
        "analyzed_at": datetime.now().isoformat()
    }

@pytest.fixture
def mock_analyzer(mocker, test_analysis):
    """Create mock analyzer"""
    mock = mocker.Mock()
    mock.analyze_prompt.return_value = test_analysis
    return mock

async def test_prompt_analysis(test_yaml_content):
    """Test prompt analysis"""
    analyzer = PromptAnalyzer("test-key")
    analysis = await analyzer.analyze_prompt(test_yaml_content)
    
    assert "analysis" in analysis
    assert "analyzed_at" in analysis

def test_markdown_generation(mock_analyzer, test_yaml_content, tmp_path):
    """Test markdown documentation generation"""
    generator = DocumentationGenerator(mock_analyzer)
    
    # Create test YAML file
    yaml_path = tmp_path / "test.yaml"
    with open(yaml_path, 'w') as f:
        yaml.dump(test_yaml_content, f)
    
    # Generate docs
    doc = generator._create_markdown_doc(str(yaml_path), mock_analyzer.analyze_prompt())
    
    assert test_yaml_content["title"] in doc
    assert test_yaml_content["description"] in doc
    assert test_yaml_content["version"] in doc

@pytest.mark.asyncio
async def test_full_generation(mock_analyzer, test_yaml_content, tmp_path):
    """Test full documentation generation process"""
    generator = DocumentationGenerator(mock_analyzer)
    
    # Setup test directories
    input_dir = tmp_path / "input"
    output_dir = tmp_path / "output"
    input_dir.mkdir()
    
    # Create test YAML file
    yaml_path = input_dir / "test.yaml"
    with open(yaml_path, 'w') as f:
        yaml.dump(test_yaml_content, f)
    
    # Generate documentation
    await generator.generate_docs(str(input_dir), str(output_dir))
    
    # Verify output
    assert (output_dir / "test.md").exists()
    assert (output_dir / "index.md").exists()
