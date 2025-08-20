#!/usr/bin/env python3
"""
Test the Expandable Personality Framework
"""

import sys
import os
from pathlib import Path

# Add src to path
sys.path.append(os.path.join(os.path.dirname(__file__), 'src'))

try:
    from src.core.expandable_personality_framework import ExpandablePersonalityFramework
    
    print("🧪 Testing Expandable Personality Framework...")
    
    # Initialize framework
    framework = ExpandablePersonalityFramework()
    
    # Prepare for new integrations
    print("\n🔄 Preparing Fourth Way integration...")
    fourth_way_prep = framework.prepare_for_fourth_way()
    
    print("\n🌌 Preparing Hylozoics integration...")
    hylozoics_prep = framework.prepare_for_hylozoics()
    
    # Show system status
    print("\n📊 System Status:")
    status = framework.get_system_status()
    for key, value in status.items():
        print(f"   {key}: {value}")
    
    print(f"\n✅ Framework successfully initialized!")
    print(f"📁 Data stored in: {framework.data_path}")
    print(f"🔄 Fourth Way concepts ready: {len(fourth_way_prep['planned_concepts'])}")
    print(f"🌌 Hylozoics concepts ready: {len(hylozoics_prep['planned_concepts'])}")
    
    print(f"\n🎯 Ready to receive your Fourth Way and Hylozoics content!")

except Exception as e:
    print(f"❌ Error testing framework: {e}")
    import traceback
    traceback.print_exc()
