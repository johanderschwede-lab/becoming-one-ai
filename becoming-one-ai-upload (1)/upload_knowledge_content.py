#!/usr/bin/env python3
"""
Becoming One™ Knowledge Upload Utility
=====================================

This script helps you upload your core IP to the knowledge management system:
- Schaubilder (your 20+ wisdom models)
- Master prompts and AI instructions  
- Teaching materials and method descriptions
- Human-generated answers for continuous learning

Usage:
    python upload_knowledge_content.py --help
    python upload_knowledge_content.py upload-schaubild "path/to/schaubild.md" --title "Emotional Anchors"
    python upload_knowledge_content.py upload-directory "schaubilder/" --type schaubild
    python upload_knowledge_content.py upload-prompts "prompts.json"
"""

import os
import sys
import json
import asyncio
import argparse
from pathlib import Path
from typing import Dict, List, Any
from dotenv import load_dotenv

# Load environment variables
load_dotenv('config/live.env')

# Add src to path
sys.path.append(os.path.join(os.path.dirname(__file__), 'src'))

from src.core.knowledge_management_system import BecomingOneKnowledgeSystem, ContentUploader


async def upload_single_schaubild(file_path: str, title: str = None, metadata: Dict[str, Any] = None):
    """Upload a single Schaubild file"""
    ks = BecomingOneKnowledgeSystem()
    uploader = ContentUploader(ks)
    
    if not os.path.exists(file_path):
        print(f"❌ File not found: {file_path}")
        return
    
    # Auto-generate title if not provided
    if not title:
        title = Path(file_path).stem.replace('_', ' ').replace('-', ' ').title()
    
    # Default metadata
    if not metadata:
        metadata = {
            'filename': os.path.basename(file_path),
            'upload_source': 'manual_upload',
            'concepts': [],
            'feeling_states': [],
            'difficulty_level': 1
        }
    
    try:
        schaubild_id = await uploader.upload_schaubild_from_file(file_path, {
            'title': title,
            **metadata
        })
        print(f"✅ Successfully uploaded Schaubild: {title}")
        print(f"   ID: {schaubild_id}")
        print(f"   File: {file_path}")
    except Exception as e:
        print(f"❌ Error uploading {file_path}: {e}")


async def upload_directory(directory_path: str, content_type: str = "schaubild"):
    """Upload all files from a directory"""
    ks = BecomingOneKnowledgeSystem()
    uploader = ContentUploader(ks)
    
    if not os.path.exists(directory_path):
        print(f"❌ Directory not found: {directory_path}")
        return
    
    print(f"📁 Uploading all files from: {directory_path}")
    print(f"   Content type: {content_type}")
    
    supported_extensions = ['.md', '.txt', '.docx']
    files_found = []
    
    for file_path in Path(directory_path).rglob('*'):
        if file_path.suffix.lower() in supported_extensions:
            files_found.append(file_path)
    
    if not files_found:
        print(f"❌ No supported files found in {directory_path}")
        print(f"   Looking for: {', '.join(supported_extensions)}")
        return
    
    print(f"📋 Found {len(files_found)} files to upload:")
    for file_path in files_found:
        print(f"   - {file_path}")
    
    confirm = input(f"\n🤔 Upload all {len(files_found)} files? (y/N): ")
    if confirm.lower() != 'y':
        print("❌ Upload cancelled")
        return
    
    successful_uploads = 0
    failed_uploads = 0
    
    for file_path in files_found:
        try:
            title = file_path.stem.replace('_', ' ').replace('-', ' ').title()
            metadata = {
                'filename': file_path.name,
                'relative_path': str(file_path.relative_to(directory_path)),
                'upload_batch': 'directory_upload',
                'concepts': [],
                'feeling_states': [],
                'difficulty_level': 1
            }
            
            if content_type == "schaubild":
                schaubild_id = await uploader.upload_schaubild_from_file(str(file_path), {
                    'title': title,
                    **metadata
                })
                print(f"✅ Uploaded: {title} (ID: {schaubild_id})")
                successful_uploads += 1
            else:
                print(f"⚠️  Content type '{content_type}' not yet supported for batch upload")
                
        except Exception as e:
            print(f"❌ Failed to upload {file_path}: {e}")
            failed_uploads += 1
    
    print(f"\n📊 Upload Summary:")
    print(f"   ✅ Successful: {successful_uploads}")
    print(f"   ❌ Failed: {failed_uploads}")
    print(f"   📈 Success rate: {(successful_uploads / len(files_found)) * 100:.1f}%")


async def upload_master_prompts(config_file: str):
    """Upload master prompts from JSON configuration"""
    ks = BecomingOneKnowledgeSystem()
    uploader = ContentUploader(ks)
    
    if not os.path.exists(config_file):
        print(f"❌ Configuration file not found: {config_file}")
        return
    
    try:
        with open(config_file, 'r', encoding='utf-8') as f:
            prompts_config = json.load(f)
        
        print(f"📋 Found {len(prompts_config)} prompts to upload:")
        for prompt_name in prompts_config.keys():
            print(f"   - {prompt_name}")
        
        confirm = input(f"\n🤔 Upload all {len(prompts_config)} prompts? (y/N): ")
        if confirm.lower() != 'y':
            print("❌ Upload cancelled")
            return
        
        uploaded_ids = await uploader.upload_master_prompts_from_config(config_file)
        
        print(f"✅ Successfully uploaded {len(uploaded_ids)} master prompts")
        for i, prompt_id in enumerate(uploaded_ids, 1):
            print(f"   {i}. ID: {prompt_id}")
            
    except Exception as e:
        print(f"❌ Error uploading prompts: {e}")


async def add_human_answer(question: str, answer: str, context: Dict[str, Any] = None):
    """Add a human-generated answer to the knowledge base"""
    ks = BecomingOneKnowledgeSystem()
    
    if not context:
        context = {'source': 'manual_entry'}
    
    try:
        answer_id = await ks.add_human_generated_answer(
            question=question,
            answer=answer,
            context=context,
            source_person="johan"  # Default, could be made configurable
        )
        
        print(f"✅ Human answer added successfully")
        print(f"   ID: {answer_id}")
        print(f"   Question: {question[:100]}...")
        print(f"   Status: Pending validation")
        
    except Exception as e:
        print(f"❌ Error adding human answer: {e}")


async def test_knowledge_query(query: str):
    """Test querying the knowledge base"""
    ks = BecomingOneKnowledgeSystem()
    
    print(f"🔍 Testing query: '{query}'")
    
    try:
        # Query knowledge base
        results = await ks.query_knowledge_base(query, top_k=3)
        
        print(f"📊 Found {len(results)} relevant results:")
        for i, result in enumerate(results, 1):
            print(f"\n   {i}. Score: {result['score']:.3f}")
            print(f"      Type: {result['content_type']}")
            print(f"      Content: {result['content'][:200]}...")
        
        # Generate full response
        print(f"\n🤖 Generating Becoming One™ response...")
        response = await ks.generate_becoming_one_response(
            user_query=query,
            user_context={'source': 'test_query'}
        )
        
        print(f"\n💬 Response:")
        print(f"   {response['response']}")
        print(f"\n📈 Confidence: {response['confidence']:.3f}")
        print(f"🔗 Sources used: {len(response['sources'])}")
        
    except Exception as e:
        print(f"❌ Error testing query: {e}")


def create_sample_prompts_config():
    """Create a sample prompts configuration file"""
    sample_config = {
        "becoming_one_system_prompt": {
            "content": """You are the Becoming One™ AI, embodying Johan and Marianne's revolutionary methodology.

Core Principles:
- All human desire is feeling-state seeking, not object seeking
- Emotional anchors are stored emotional matter that must be felt and digested
- Turn 180° toward what you're avoiding - no spiritual bypassing
- Procrastination and avoidance are portals to transformation
- The nervous system protects us from exactly what we need to feel to grow
- Every block contains stored energy waiting to be released

Response Guidelines:
1. Answer ONLY from provided Becoming One™ knowledge
2. If knowledge is insufficient, say so clearly
3. Apply anti-bypass framework consistently
4. Focus on feeling-states, anchors, and practical steps
5. Offer specific protocols when appropriate
6. Track sources and maintain authenticity

Remember: We don't help people avoid feeling. We build their capacity to feel everything.""",
            "context": {
                "type": "system_prompt",
                "version": "1.0",
                "scope": "general_responses"
            }
        },
        "anchor_analysis_prompt": {
            "content": """Analyze this text for Becoming One™ emotional anchor patterns.

Look for:
- Stored emotional matter from different age epochs
- Loyalty debts to family/tribe/old self
- Secondary gains from keeping blocks
- Somatic markers indicating anchor activation
- The Pearl - transformational insights when digested
- Avoidance patterns and escape moves

Return specific, actionable insights about:
1. Which anchors are most active
2. What secondary gains they provide
3. What feeling-states are being avoided
4. What turn-180° opportunities exist
5. What bridge acts could be taken""",
            "context": {
                "type": "analysis_prompt",
                "version": "1.0",
                "scope": "anchor_detection"
            }
        }
    }
    
    config_file = "sample_master_prompts.json"
    with open(config_file, 'w', encoding='utf-8') as f:
        json.dump(sample_config, f, indent=2)
    
    print(f"✅ Created sample prompts configuration: {config_file}")
    print("   Edit this file to add your actual master prompts")


async def main():
    """Main CLI interface"""
    parser = argparse.ArgumentParser(
        description="Upload content to Becoming One™ Knowledge Management System"
    )
    
    subparsers = parser.add_subparsers(dest='command', help='Available commands')
    
    # Upload single Schaubild
    upload_schaubild_parser = subparsers.add_parser('upload-schaubild', help='Upload a single Schaubild')
    upload_schaubild_parser.add_argument('file_path', help='Path to the Schaubild file')
    upload_schaubild_parser.add_argument('--title', help='Title for the Schaubild')
    upload_schaubild_parser.add_argument('--concepts', nargs='*', help='Concepts covered')
    upload_schaubild_parser.add_argument('--feeling-states', nargs='*', help='Feeling states addressed')
    upload_schaubild_parser.add_argument('--difficulty', type=int, default=1, help='Difficulty level (1-10)')
    
    # Upload directory
    upload_dir_parser = subparsers.add_parser('upload-directory', help='Upload all files from directory')
    upload_dir_parser.add_argument('directory_path', help='Path to directory containing files')
    upload_dir_parser.add_argument('--type', default='schaubild', help='Content type')
    
    # Upload prompts
    upload_prompts_parser = subparsers.add_parser('upload-prompts', help='Upload master prompts from JSON')
    upload_prompts_parser.add_argument('config_file', help='Path to prompts configuration JSON')
    
    # Add human answer
    add_answer_parser = subparsers.add_parser('add-answer', help='Add human-generated answer')
    add_answer_parser.add_argument('question', help='The question being answered')
    add_answer_parser.add_argument('answer', help='Your answer')
    
    # Test query
    test_parser = subparsers.add_parser('test-query', help='Test querying the knowledge base')
    test_parser.add_argument('query', help='Query to test')
    
    # Create sample config
    subparsers.add_parser('create-sample-prompts', help='Create sample prompts configuration')
    
    args = parser.parse_args()
    
    if not args.command:
        parser.print_help()
        return
    
    try:
        if args.command == 'upload-schaubild':
            metadata = {}
            if args.concepts:
                metadata['concepts'] = args.concepts
            if args.feeling_states:
                metadata['feeling_states'] = args.feeling_states
            if args.difficulty:
                metadata['difficulty_level'] = args.difficulty
            
            await upload_single_schaubild(args.file_path, args.title, metadata)
            
        elif args.command == 'upload-directory':
            await upload_directory(args.directory_path, args.type)
            
        elif args.command == 'upload-prompts':
            await upload_master_prompts(args.config_file)
            
        elif args.command == 'add-answer':
            await add_human_answer(args.question, args.answer)
            
        elif args.command == 'test-query':
            await test_knowledge_query(args.query)
            
        elif args.command == 'create-sample-prompts':
            create_sample_prompts_config()
            
    except KeyboardInterrupt:
        print("\n❌ Operation cancelled by user")
    except Exception as e:
        print(f"❌ Unexpected error: {e}")
        import traceback
        traceback.print_exc()


if __name__ == "__main__":
    asyncio.run(main())
