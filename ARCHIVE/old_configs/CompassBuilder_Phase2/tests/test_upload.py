# write test for this

import pytest
import yaml
import os
from datetime import datetime
from ..supabase_sync.upload import YAMLUploader

@pytest.fixture
def test_yaml_file(tmp_path):
    """Create a test YAML file"""
    content = {
        "title": "Test Prompt",
        "version": "1.0.0",
        "type": "test",
        "content": "This is a test prompt"
    }
    
    file_path = tmp_path / "test.yaml"
    with open(file_path, 'w') as f:
        yaml.dump(content, f)
    
    return file_path

@pytest.fixture
def mock_supabase(mocker):
    """Mock Supabase client"""
    mock = mocker.Mock()
    mock.table().insert().execute.return_value.data = [{"id": "test-id"}]
    return mock

def test_yaml_reading(test_yaml_file):
    """Test YAML file reading"""
    uploader = YAMLUploader()
    data = uploader.read_yaml(str(test_yaml_file))
    
    assert data["title"] == "Test Prompt"
    assert data["version"] == "1.0.0"
    assert data["type"] == "test"

def test_upload_module(mock_supabase, test_yaml_file):
    """Test module upload to Supabase"""
    uploader = YAMLUploader()
    uploader.supabase = mock_supabase
    
    data = uploader.read_yaml(str(test_yaml_file))
    result = uploader.upload_module(data)
    
    assert result["id"] == "test-id"
    mock_supabase.table().insert().execute.assert_called_once()
