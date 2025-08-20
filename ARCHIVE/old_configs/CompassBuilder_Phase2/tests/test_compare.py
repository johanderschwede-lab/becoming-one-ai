# write test for this

import pytest
from datetime import datetime
from ..versioning.compare import PromptVersioner, Version

@pytest.fixture
def old_version():
    """Create an old version for testing"""
    return Version(
        content={
            "title": "Test Prompt",
            "version": "1.0.0",
            "content": "Original content"
        },
        timestamp=datetime.now(),
        version_id="1.0.0"
    )

@pytest.fixture
def new_version():
    """Create a new version for testing"""
    return Version(
        content={
            "title": "Test Prompt",
            "version": "1.0.1",
            "content": "Updated content"
        },
        timestamp=datetime.now(),
        version_id="1.0.1"
    )

def test_compare_yaml(old_version, new_version):
    """Test YAML comparison"""
    versioner = PromptVersioner()
    diff = versioner.compare_yaml(old_version, new_version)
    
    assert len(diff) > 0
    assert any(line.startswith('-') for line in diff)
    assert any(line.startswith('+') for line in diff)

def test_extract_changes(old_version, new_version):
    """Test change extraction"""
    versioner = PromptVersioner()
    diff = versioner.compare_yaml(old_version, new_version)
    changes = versioner.extract_changes(diff)
    
    assert len(changes) > 0
    assert any(change[0] == 'addition' for change in changes)
    assert any(change[0] == 'deletion' for change in changes)

def test_summarize_changes(old_version, new_version):
    """Test change summarization"""
    versioner = PromptVersioner()
    diff = versioner.compare_yaml(old_version, new_version)
    changes = versioner.extract_changes(diff)
    summary = versioner.summarize_changes(changes)
    
    assert "Added" in summary or "Removed" in summary
    assert isinstance(summary, str)
