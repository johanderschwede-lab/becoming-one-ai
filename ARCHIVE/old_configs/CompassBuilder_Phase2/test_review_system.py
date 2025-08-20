#!/usr/bin/env python3
"""
Test script for the Master Prompt Review System
"""

import sys
import os
sys.path.append(os.path.join(os.path.dirname(__file__), 'master_prompt_review'))
from review_system import MasterPromptReviewSystem

def test_review_system():
    print("🔍 Testing Master Prompt Review System...")
    
    # Initialize the review system
    review_system = MasterPromptReviewSystem()
    
    # Test 1: Get current master prompt
    print("\n1. Testing current master prompt retrieval...")
    current_prompt = review_system.get_current_master_prompt()
    print(f"Current prompt length: {len(current_prompt)} characters")
    print(f"Current prompt preview: {current_prompt[:100]}...")
    
    # Test 2: Analyze a sample change
    print("\n2. Testing change analysis...")
    sample_new_prompt = """
    # Updated Master Prompt for Becoming One™ AI System
    
    This is a test update to the master prompt that includes:
    - Enhanced personality analysis capabilities
    - Improved emotional anchor detection
    - Better integration with the WillB.one community
    
    The system should now provide more accurate guidance for personal development.
    """
    
    analysis = review_system.analyze_master_prompt_change(sample_new_prompt, current_prompt)
    print(f"Analysis result: {analysis.get('recommendation', 'No recommendation')}")
    print(f"Impact level: {analysis.get('impact_level', 'Unknown')}")
    
    # Test 3: Create a review request
    print("\n3. Testing review request creation...")
    review_result = review_system.create_review_request(
        sample_new_prompt,
        "Test_User",
        "This is a test review request to verify the system works correctly."
    )
    
    if review_result['success']:
        print(f"✅ Review request created successfully!")
        print(f"Review ID: {review_result['review_id']}")
        
        # Test 4: Get pending reviews
        print("\n4. Testing pending reviews retrieval...")
        pending_reviews = review_system.get_pending_reviews()
        print(f"Found {len(pending_reviews)} pending reviews")
        
        if pending_reviews:
            print(f"Latest review: {pending_reviews[0]['title']}")
            print(f"Impact level: {pending_reviews[0]['impact_level']}")
            print(f"AI recommendation: {pending_reviews[0]['recommendation']}")
        
        print("\n✅ All tests completed successfully!")
        print("\nTo review and approve/reject changes, run:")
        print("python launch_review_dashboard.py")
        
    else:
        print(f"❌ Review request failed: {review_result['error']}")

if __name__ == "__main__":
    test_review_system()
