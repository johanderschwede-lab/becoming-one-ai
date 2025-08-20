#!/usr/bin/env python3
"""
Becoming One™ Personality Synthesis System Demo
===============================================

This script demonstrates the comprehensive personality analysis and synthesis
system that combines established frameworks (Enneagram, Human Design, Astrology,
Maya Calendar) with the unique Becoming One™ Essence and vertical development dimensions.
"""

import asyncio
import json
import uuid
from datetime import datetime
from dotenv import load_dotenv

# Load environment variables
load_dotenv('config/live.env')

from src.core.personality_analyzer import BecomingOnePersonalityAnalyzer
from src.core.personality_synthesis_model import (
    SynthesisPersonalityProfile,
    EnneagramType,
    EssenceLevel,
    VerticalStage,
    EmotionalAnchorPattern,
    AvoidanceSignature
)


class PersonalitySynthesisDemo:
    """
    Demo class showing the personality synthesis system in action
    """
    
    def __init__(self):
        self.analyzer = BecomingOnePersonalityAnalyzer()
    
    async def run_demo(self):
        """Run comprehensive personality analysis demo"""
        print("\n" + "="*80)
        print("🌟 BECOMING ONE™ PERSONALITY SYNTHESIS SYSTEM DEMO")
        print("="*80)
        print("Demonstrating AI-powered personality analysis across multiple frameworks:")
        print("• Enneagram (9 types + wings + instincts)")
        print("• Human Design (Types, Strategy, Authority)")
        print("• Astrology (Sun/Moon/Rising, Elements)")
        print("• Maya Calendar (Kin, Tone, Seal)")
        print("• Myers-Briggs/Jung (Cognitive Functions)")
        print("• Becoming One™ (Essence Level, Vertical Stage, Anchor Patterns)")
        print()
        
        # Test different personality expressions
        test_messages = [
            {
                "message": "I keep procrastinating on my important goals. I know what I should do but I just can't seem to get started. There's this heavy feeling in my chest whenever I think about it.",
                "description": "Procrastination with somatic awareness"
            },
            {
                "message": "I'm always helping everyone else but I never seem to have time for myself. I feel guilty when I try to focus on my own needs. Maybe I'm just being selfish?",
                "description": "Helper pattern with self-sacrifice"
            },
            {
                "message": "I have this vision of what I want to create but I get so frustrated when things don't go according to my plan. I need everything to be perfect or I just shut down.",
                "description": "Perfectionism with control issues"
            },
            {
                "message": "Sometimes I feel like I don't belong anywhere. I see all these people living their normal lives and I just feel... different. Like I'm missing something everyone else has.",
                "description": "Identity seeking with belonging issues"
            },
            {
                "message": "I love starting new projects and I have so many ideas! But then I get bored and move on to the next thing. People say I should focus more but variety is what makes me feel alive.",
                "description": "Enthusiast pattern with variety seeking"
            }
        ]
        
        for i, test_case in enumerate(test_messages, 1):
            await self.analyze_message_demo(i, test_case["message"], test_case["description"])
            print("\n" + "-"*80 + "\n")
        
        # Show synthesis across multiple messages
        await self.demonstrate_profile_building()
        
        print("\n" + "="*80)
        print("🎯 DEMO COMPLETE - PERSONALITY SYNTHESIS SYSTEM READY")
        print("="*80)
        print("The system can now:")
        print("✅ Analyze any message for personality patterns across all frameworks")
        print("✅ Build comprehensive user profiles over time") 
        print("✅ Generate personalized Becoming One™ responses")
        print("✅ Track emotional anchors and avoidance patterns")
        print("✅ Identify essence levels and vertical development stages")
        print("✅ Synthesize insights across multiple personality systems")
        print()
    
    async def analyze_message_demo(self, demo_number: int, message: str, description: str):
        """Demonstrate analysis of a single message"""
        print(f"📝 DEMO {demo_number}: {description}")
        print(f"Message: \"{message}\"")
        print()
        
        # Generate a test person_id
        person_id = uuid.uuid4()
        
        # Analyze the message
        print("🔍 Running AI personality analysis...")
        analysis = await self.analyzer.analyze_message(
            person_id=person_id,
            message=message,
            context={"source": "demo"}
        )
        
        # Display results
        self.display_analysis_results(analysis)
        
        # Create/update personality profile
        print("🧠 Building personality synthesis profile...")
        profile = await self.analyzer.update_personality_profile(
            person_id=person_id,
            analysis_results=analysis
        )
        
        # Display profile insights
        self.display_profile_insights(profile)
        
        # Generate personalized response
        print("💬 Generating personalized Becoming One™ response...")
        personalized_response = self.analyzer.generate_personalized_response(
            profile=profile,
            current_message=message
        )
        
        print(f"Response: {personalized_response.get('personalized_response', 'Error generating response')}")
        print(f"Personalization Level: {personalized_response.get('personalization_level', 'unknown')}")
        print(f"Systems Used: {personalized_response.get('systems_used', [])}")
    
    def display_analysis_results(self, analysis: dict):
        """Display the personality analysis results"""
        print("📊 ANALYSIS RESULTS:")
        
        # Enneagram Analysis
        enneagram = analysis.get("enneagram_analysis", {})
        if enneagram and not enneagram.get("error"):
            print("  🔢 Enneagram Indicators:")
            for indicator in enneagram.get("primary_type_indicators", []):
                confidence = indicator.get("confidence", 0) * 100
                print(f"    Type {indicator.get('type')}: {confidence:.1f}% confidence")
        
        # Human Design Analysis
        hd = analysis.get("human_design_analysis", {})
        if hd and not hd.get("error"):
            print("  ⚡ Human Design Indicators:")
            for indicator in hd.get("type_indicators", []):
                confidence = indicator.get("confidence", 0) * 100
                print(f"    {indicator.get('type').title()}: {confidence:.1f}% confidence")
        
        # Emotional Anchor Analysis
        anchors = analysis.get("emotional_anchor_analysis", {})
        if anchors and not anchors.get("error"):
            print("  ⚓ Emotional Anchor Activations:")
            for activation in anchors.get("anchor_activations", []):
                intensity = activation.get("intensity", 0) * 100
                print(f"    {activation.get('anchor').title()}: {intensity:.1f}% intensity")
        
        # Avoidance Pattern Analysis
        avoidance = analysis.get("avoidance_pattern_analysis", {})
        if avoidance and not avoidance.get("error"):
            print("  🚫 Avoidance Patterns:")
            for pattern in avoidance.get("avoidance_signatures", []):
                confidence = pattern.get("confidence", 0) * 100
                print(f"    {pattern.get('pattern').title()}: {confidence:.1f}% confidence")
        
        # Essence Level Analysis
        essence = analysis.get("essence_level_analysis", {})
        if essence and not essence.get("error"):
            print("  ✨ Becoming One™ Dimensions:")
            print(f"    Primary Level: {essence.get('primary_level', 'unknown').title()}")
            print(f"    Vertical Stage: {essence.get('vertical_stage', 'unknown').title()}")
            print(f"    Manifestation Style: {essence.get('manifestation_style', 'unknown').replace('_', ' ').title()}")
        
        print()
    
    def display_profile_insights(self, profile: SynthesisPersonalityProfile):
        """Display the synthesis profile insights"""
        print("🎯 SYNTHESIS PROFILE INSIGHTS:")
        
        if profile.core_patterns:
            print(f"  Core Patterns: {', '.join(profile.core_patterns)}")
        
        if profile.growth_edges:
            print(f"  Growth Edges: {', '.join(profile.growth_edges)}")
        
        if profile.recommended_practices:
            print(f"  Recommended Practices: {', '.join(profile.recommended_practices[:3])}")
        
        if profile.becoming_one:
            print(f"  Essence Level: {profile.becoming_one.primary_essence_level.value.title()}")
            print(f"  Vertical Stage: {profile.becoming_one.current_vertical_stage.value.title()}")
            print(f"  Journey Stage: {profile.becoming_one.journey_stage.title()}")
            
            if profile.becoming_one.dominant_anchor_patterns:
                anchors = [a.value.replace('_', ' ').title() for a in profile.becoming_one.dominant_anchor_patterns]
                print(f"  Dominant Anchors: {', '.join(anchors)}")
            
            if profile.becoming_one.avoidance_signatures:
                patterns = [a.value.replace('_', ' ').title() for a in profile.becoming_one.avoidance_signatures]
                print(f"  Avoidance Patterns: {', '.join(patterns)}")
        
        print()
    
    async def demonstrate_profile_building(self):
        """Demonstrate how profiles build over multiple interactions"""
        print("🏗️  PROFILE BUILDING DEMONSTRATION")
        print("Showing how personality insights accumulate over multiple interactions...")
        print()
        
        person_id = uuid.uuid4()
        profile = None
        
        # Sequence of messages showing personality evolution
        message_sequence = [
            "I'm feeling stuck in my career. I know I should be more ambitious but I just feel overwhelmed.",
            "Actually, I realized I keep waiting for permission from others before making decisions.",
            "There's this pattern where I abandon my own needs to keep everyone else happy.",
            "I notice I hold my breath when I think about disappointing people.",
            "Maybe the real issue is that I don't trust my own inner knowing?"
        ]
        
        for i, message in enumerate(message_sequence, 1):
            print(f"Message {i}: \"{message}\"")
            
            # Analyze message
            analysis = await self.analyzer.analyze_message(
                person_id=person_id,
                message=message,
                context={"source": "demo", "sequence": i}
            )
            
            # Update profile
            profile = await self.analyzer.update_personality_profile(
                person_id=person_id,
                analysis_results=analysis,
                existing_profile=profile
            )
            
            # Show evolving insights
            if profile.becoming_one:
                print(f"  → Essence Level: {profile.becoming_one.primary_essence_level.value}")
                if profile.becoming_one.dominant_anchor_patterns:
                    anchors = [a.value for a in profile.becoming_one.dominant_anchor_patterns]
                    print(f"  → Detected Anchors: {anchors}")
            
            print()
        
        print("📈 FINAL SYNTHESIS PROFILE:")
        self.display_profile_insights(profile)


async def main():
    """Run the personality synthesis demo"""
    demo = PersonalitySynthesisDemo()
    await demo.run_demo()


if __name__ == "__main__":
    asyncio.run(main())
