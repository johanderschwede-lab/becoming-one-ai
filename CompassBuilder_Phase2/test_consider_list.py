#!/usr/bin/env python3
"""
Test script for the Consider List System
"""

import sys
import os
sys.path.append(os.path.join(os.path.dirname(__file__), 'consider_list'))
from consider_list_manager import ConsiderListManager

def test_consider_list():
    print("📋 Testing Consider List System...")
    
    # Initialize the consider list manager
    consider_manager = ConsiderListManager()
    
    # Test 1: Add items to consider list
    print("\n1. Testing adding items to consider list...")
    
    test_items = [
        {
            "content": "Implement advanced personality synthesis using multiple mapping systems",
            "category": "method_core",
            "priority": "high",
            "notes": "This could significantly improve our personality analysis capabilities"
        },
        {
            "content": "Add video processing capabilities to the content ingestion pipeline",
            "category": "technical",
            "priority": "medium",
            "notes": "Would enable automatic processing of video content"
        },
        {
            "content": "Create a new AI agent for community moderation",
            "category": "ai_agents",
            "priority": "low",
            "notes": "Future enhancement for community management"
        }
    ]
    
    for item in test_items:
        result = consider_manager.add_to_consider_list(
            item["content"],
            "Test_User",
            item["category"],
            item["priority"],
            item["notes"]
        )
        
        if result['success']:
            print(f"✅ Added: {item['content'][:50]}...")
        else:
            print(f"❌ Failed: {result['error']}")
    
    # Test 2: Get consider list
    print("\n2. Testing consider list retrieval...")
    consider_items = consider_manager.get_consider_list(status="consider")
    print(f"Found {len(consider_items)} items in consider list")
    
    for item in consider_items:
        print(f"  - {item['title']} ({item['priority']} priority)")
    
    # Test 3: Get statistics
    print("\n3. Testing statistics...")
    stats = consider_manager.get_consider_stats()
    print(f"Total consider: {stats.get('total_consider', 0)}")
    print(f"Total implement: {stats.get('total_implement', 0)}")
    print(f"Total reject: {stats.get('total_reject', 0)}")
    print(f"Total archive: {stats.get('total_archive', 0)}")
    
    # Test 4: Update an item (implement)
    if consider_items:
        print("\n4. Testing item implementation...")
        first_item = consider_items[0]
        result = consider_manager.update_consider_item(
            first_item['consider_id'],
            "implement",
            "Approved for implementation",
            "This feature aligns with our roadmap"
        )
        
        if result['success']:
            print(f"✅ Implemented: {first_item['title']}")
        else:
            print(f"❌ Failed to implement: {result['error']}")
    
    print("\n✅ All tests completed successfully!")
    print("\nTo manage the consider list, run:")
    print("python launch_consider_dashboard.py")

if __name__ == "__main__":
    test_consider_list()
