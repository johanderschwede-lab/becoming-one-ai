#!/usr/bin/env python3
"""
Becoming One™ Enhanced Personality Analysis Demo
===============================================

This demo showcases the enhanced personality analysis system that integrates
your specific methodology including:
- Feeling-states vs. external objects
- Emotional anchors and The Pearl
- Avoidance patterns as portals
- Anti-bypass approach (turn 180°)
- Procrastination archetypes
- Manifestation through feeling-state generation
"""

import asyncio
import json
import uuid
from datetime import datetime
from dotenv import load_dotenv

# Load environment variables
load_dotenv('config/live.env')

from src.core.personality_analyzer import BecomingOnePersonalityAnalyzer
from src.core.becoming_one_method_enhanced import (
    FeelingPrimitive, EmotionalAnchor, AvoidancePattern, 
    ProcrastinationArchetype, BecomingOneMetrics, Pearl
)


class BecomingOneEnhancedDemo:
    """
    Demo showcasing the enhanced Becoming One™ analysis system
    """
    
    def __init__(self):
        self.analyzer = BecomingOnePersonalityAnalyzer()
    
    async def run_demo(self):
        """Run comprehensive Becoming One™ enhanced analysis demo"""
        print("\n" + "="*80)
        print("🌟 BECOMING ONE™ ENHANCED PERSONALITY ANALYSIS DEMO")
        print("="*80)
        print("Now featuring your specific methodology:")
        print("• Feeling-states as the true desire (not external objects)")
        print("• Emotional anchors as 'stored emotional matter'")
        print("• The Pearl: transformational insights from anchor digestion")
        print("• Anti-bypass approach: turn 180° toward feeling")
        print("• Procrastination as portal, not problem")
        print("• Manifestation through feeling-state generation")
        print("• Loyalty debts and secondary gains")
        print("• Bridge-of-incidents (tiny decisive acts)")
        print()
        
        # Test messages that reveal Becoming One™ patterns
        test_messages = [
            {
                "message": "I keep procrastinating on my business idea. Every time I sit down to work on it, I get this heavy feeling in my chest and suddenly I'm cleaning the house or scrolling social media. I know I want success, but maybe I'm just not ready yet.",
                "description": "Procrastination with somatic awareness + avoidance patterns",
                "expected_insights": ["fog_walker archetype", "fear_of_visibility anchor", "success = significance feeling"]
            },
            {
                "message": "I dream of having my own home, but every time I look at houses I feel overwhelmed and think 'who am I to deserve this?' My family always struggled financially and I don't want to abandon them by having more than they did.",
                "description": "Manifestation desire with loyalty debt + unworthiness anchor",
                "expected_insights": ["home = safety feeling", "loyalty debt to family", "unworthiness anchor"]
            },
            {
                "message": "I had this moment yesterday where I was angry at my partner, and instead of shutting down like usual, I just stayed with the anger. I felt it in my whole body - the heat, the energy. And suddenly I wasn't angry anymore, I was just... powerful. Like I could handle anything.",
                "description": "Pearl extraction - anchor digestion leading to quality gain",
                "expected_insights": ["Pearl: anger → power", "quality gained: potency", "anti-bypass success"]
            },
            {
                "message": "I want to find my soulmate, but I keep dating people who are unavailable. I tell myself 'when I lose 10 pounds, then I'll be worthy of real love' or 'after I get my career sorted, then I'll focus on relationships.' But nothing ever feels ready enough.",
                "description": "Manifestation through external conditions vs. feeling-state",
                "expected_insights": ["love = belonging feeling", "delay factors", "unworthiness anchor"]
            },
            {
                "message": "Every time I'm about to publish something or share my work, I find another thing that needs to be perfect. I spent 3 hours yesterday editing a simple email. I know it's ridiculous but I can't help myself. What if people judge me? What if I'm not good enough?",
                "description": "Perfectionist archetype with fear of visibility",
                "expected_insights": ["perfectionist archetype", "fear_of_visibility anchor", "turn 180° opportunity"]
            }
        ]
        
        for i, test_case in enumerate(test_messages, 1):
            await self.analyze_message_demo(i, test_case)
            print("\n" + "-"*80 + "\n")
        
        # Show how the system builds a comprehensive map over time
        await self.demonstrate_becoming_one_mapping()
        
        print("\n" + "="*80)
        print("🎯 BECOMING ONE™ ENHANCED SYSTEM READY")
        print("="*80)
        print("The system now understands and analyzes:")
        print("✅ Feeling-states as true desires (not external objects)")
        print("✅ Emotional anchors and their age epochs")
        print("✅ The Pearl: transformational insights from digestion")
        print("✅ Procrastination archetypes and avoidance patterns")
        print("✅ Loyalty debts preventing growth")
        print("✅ Secondary gains from keeping blocks")
        print("✅ Anti-bypass opportunities (turn 180°)")
        print("✅ Bridge-of-incidents for manifestation")
        print("✅ Synchronicity patterns as navigation beacons")
        print("✅ Time compression through feeling-state generation")
        print()
    
    async def analyze_message_demo(self, demo_number: int, test_case: dict):
        """Demonstrate enhanced Becoming One™ analysis"""
        message = test_case["message"]
        description = test_case["description"]
        expected = test_case.get("expected_insights", [])
        
        print(f"📝 DEMO {demo_number}: {description}")
        print(f"Message: \"{message}\"")
        print(f"Expected insights: {', '.join(expected)}")
        print()
        
        # Generate a test person_id
        person_id = uuid.uuid4()
        
        # Run enhanced analysis
        print("🔍 Running enhanced Becoming One™ analysis...")
        analysis = await self.analyzer.analyze_message(
            person_id=person_id,
            message=message,
            context={"source": "demo", "method": "becoming_one_enhanced"}
        )
        
        # Display enhanced results
        self.display_becoming_one_analysis(analysis)
        
        # Generate Becoming One™ response
        print("💬 Generating Becoming One™ anti-bypass response...")
        try:
            profile = await self.analyzer.update_personality_profile(
                person_id=person_id,
                analysis_results=analysis
            )
            
            response = self.analyzer.generate_personalized_response(
                profile=profile,
                current_message=message
            )
            
            print(f"Response: {response.get('personalized_response', 'Error generating response')}")
            print(f"Anti-bypass level: {response.get('personalization_level', 'unknown')}")
        except Exception as e:
            print(f"Response generation error: {e}")
    
    def display_becoming_one_analysis(self, analysis: dict):
        """Display enhanced Becoming One™ analysis results"""
        print("📊 BECOMING ONE™ ENHANCED ANALYSIS:")
        
        # Emotional Anchor Analysis
        anchors = analysis.get("emotional_anchor_analysis", {})
        if anchors and not anchors.get("error"):
            print("  ⚓ Emotional Anchors (Stored Emotional Matter):")
            for activation in anchors.get("anchor_activations", []):
                intensity = activation.get("intensity", 0) * 100
                epoch = activation.get("age_epoch", "unknown")
                print(f"    {activation.get('anchor', 'unknown').title()}: {intensity:.1f}% intensity (epoch: {epoch})")
            
            if anchors.get("loyalty_debts"):
                print("  🔗 Loyalty Debts:")
                for debt in anchors.get("loyalty_debts", []):
                    print(f"    To {debt.get('to_whom', 'unknown')}: {debt.get('vow', 'unspecified vow')}")
            
            if anchors.get("pearls_detected"):
                print("  💎 Pearls Detected:")
                for pearl in anchors.get("pearls_detected", []):
                    print(f"    Insight: {pearl.get('insight', 'unknown')}")
                    print(f"    Quality gained: {pearl.get('quality_gained', 'unknown')}")
        
        # Avoidance Pattern Analysis
        avoidance = analysis.get("avoidance_pattern_analysis", {})
        if avoidance and not avoidance.get("error"):
            print("  🚫 Avoidance Patterns (Anti-Bypass Opportunities):")
            archetype = avoidance.get("procrastination_archetype", "unknown")
            print(f"    Procrastination Archetype: {archetype.title()}")
            
            if avoidance.get("hedging_language"):
                print(f"    Hedging Language: {', '.join(avoidance.get('hedging_language', []))}")
            
            if avoidance.get("turn_180_opportunities"):
                print("    Turn 180° Opportunities:")
                for opp in avoidance.get("turn_180_opportunities", []):
                    print(f"      → {opp}")
        
        # Feeling-State Manifestation Analysis
        manifestation = analysis.get("feeling_state_manifestation_analysis", {})
        if manifestation and not manifestation.get("error"):
            print("  ✨ Manifestation & Feeling-State Analysis:")
            
            target_feelings = manifestation.get("target_feelings", [])
            if target_feelings:
                print("    Target Feeling-States:")
                for feeling in target_feelings:
                    confidence = feeling.get("confidence", 0) * 100
                    print(f"      {feeling.get('feeling', 'unknown').title()}: {confidence:.1f}% confidence")
            
            underlying = manifestation.get("underlying_feeling_desire", "unknown")
            print(f"    Core Feeling Desire: {underlying.title()}")
            
            external = manifestation.get("external_desires", [])
            if external:
                print(f"    External Desires: {', '.join(external)}")
            
            bridges = manifestation.get("bridge_opportunities", [])
            if bridges:
                print("    Bridge Opportunities:")
                for bridge in bridges:
                    print(f"      → {bridge}")
            
            compression = manifestation.get("time_compression_potential", 0) * 100
            print(f"    Time Compression Potential: {compression:.1f}%")
        
        print()
    
    async def demonstrate_becoming_one_mapping(self):
        """Show how the system builds a living map of the individual"""
        print("🗺️  BECOMING ONE™ LIVING MAP DEMONSTRATION")
        print("Showing how personality insights build into a comprehensive map...")
        print()
        
        person_id = uuid.uuid4()
        
        # Sequence showing progression through Becoming One™ work
        progression_messages = [
            "I always put everyone else's needs before mine. I feel guilty when I try to focus on myself.",
            "I noticed when I think about my own needs, I get this tightness in my throat. Like I'm not allowed to want things.",
            "Yesterday I practiced just feeling that throat tightness instead of pushing it away. It was scary but I stayed with it.",
            "The tightness turned into sadness, and I realized I've been afraid of disappointing my mother my whole life.",
            "Today I asked for what I needed at work - just a small thing - and it felt terrifying but also powerful.",
            "I'm starting to see this pattern everywhere. I can feel the 'loyalty to mom' pulling me back from my own life."
        ]
        
        cumulative_insights = {
            "anchors_identified": [],
            "pearls_discovered": [],
            "feeling_states_accessed": [],
            "bridges_crossed": [],
            "patterns_recognized": []
        }
        
        for i, message in enumerate(progression_messages, 1):
            print(f"Session {i}: \"{message[:60]}...\"")
            
            # Analyze message
            analysis = await self.analyzer.analyze_message(
                person_id=person_id,
                message=message,
                context={"source": "demo", "session": i}
            )
            
            # Extract key insights
            anchors = analysis.get("emotional_anchor_analysis", {})
            if anchors.get("anchor_activations"):
                for anchor in anchors["anchor_activations"]:
                    if anchor["anchor"] not in cumulative_insights["anchors_identified"]:
                        cumulative_insights["anchors_identified"].append(anchor["anchor"])
            
            if anchors.get("pearls_detected"):
                for pearl in anchors["pearls_detected"]:
                    cumulative_insights["pearls_discovered"].append(pearl["insight"])
            
            manifestation = analysis.get("feeling_state_manifestation_analysis", {})
            if manifestation.get("target_feelings"):
                for feeling in manifestation["target_feelings"]:
                    if feeling["feeling"] not in cumulative_insights["feeling_states_accessed"]:
                        cumulative_insights["feeling_states_accessed"].append(feeling["feeling"])
            
            if manifestation.get("bridge_opportunities"):
                cumulative_insights["bridges_crossed"].extend(manifestation["bridge_opportunities"])
            
            print(f"  → New insights: Session {i} progression")
            print()
        
        print("📈 CUMULATIVE BECOMING ONE™ MAP:")
        print(f"  Anchors Identified: {', '.join(cumulative_insights['anchors_identified'])}")
        print(f"  Pearls Discovered: {len(cumulative_insights['pearls_discovered'])} transformational insights")
        print(f"  Feeling-States Accessed: {', '.join(cumulative_insights['feeling_states_accessed'])}")
        print(f"  Bridges Available: {len(cumulative_insights['bridges_crossed'])} actionable steps")
        print()
        print("💡 This living map enables:")
        print("  • Targeted anchor work based on individual pattern")
        print("  • Progressive capacity building (no bypass)")
        print("  • Feeling-state manifestation aligned with essence")
        print("  • Bridge-of-incidents for real-world integration")


async def main():
    """Run the enhanced Becoming One™ demo"""
    demo = BecomingOneEnhancedDemo()
    await demo.run_demo()


if __name__ == "__main__":
    asyncio.run(main())
