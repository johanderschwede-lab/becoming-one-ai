"""
Becoming One™ Content Generation Workflow System
==============================================

This system automatically generates new content from your existing IP:
- Short-form videos (TikTok, YouTube Shorts, Instagram Reels)
- Social media posts and threads
- Email newsletter content
- Workshop material variations
- Quote graphics and carousels
- Podcast episode outlines
"""

import os
import json
import asyncio
from typing import Dict, List, Optional, Any, Tuple
from datetime import datetime, timedelta
from dataclasses import dataclass, field
from enum import Enum
import uuid

from openai import OpenAI
from .knowledge_management_system import BecomingOneKnowledgeSystem


class ContentType(Enum):
    """Types of content we can generate"""
    SHORT_FORM_VIDEO = "short_form_video"
    SOCIAL_MEDIA_POST = "social_media_post"
    TWITTER_THREAD = "twitter_thread"
    INSTAGRAM_CAROUSEL = "instagram_carousel"
    EMAIL_NEWSLETTER = "email_newsletter"
    QUOTE_GRAPHIC = "quote_graphic"
    PODCAST_OUTLINE = "podcast_outline"
    WORKSHOP_VARIATION = "workshop_variation"
    BLOG_POST = "blog_post"


class Platform(Enum):
    """Target platforms"""
    TIKTOK = "tiktok"
    YOUTUBE_SHORTS = "youtube_shorts"
    INSTAGRAM_REELS = "instagram_reels"
    INSTAGRAM_POST = "instagram_post"
    TWITTER = "twitter"
    LINKEDIN = "linkedin"
    FACEBOOK = "facebook"
    EMAIL = "email"
    BLOG = "blog"
    PODCAST = "podcast"


@dataclass
class ContentTemplate:
    """Template for generating specific content types"""
    template_id: str
    name: str
    content_type: ContentType
    platforms: List[Platform]
    structure: Dict[str, str]  # e.g., {"hook": "...", "body": "...", "cta": "..."}
    duration_seconds: Optional[int] = None  # For video content
    word_count_range: Tuple[int, int] = (50, 300)  # Min, max words
    hashtag_count: int = 5
    requires_visuals: bool = False
    prompt_template: str = ""


@dataclass
class GeneratedContent:
    """A piece of generated content"""
    content_id: str
    content_type: ContentType
    platform: Platform
    title: str
    content_body: str
    hook: Optional[str] = None
    call_to_action: Optional[str] = None
    hashtags: List[str] = field(default_factory=list)
    visual_suggestions: List[str] = field(default_factory=list)
    source_segments: List[str] = field(default_factory=list)  # Source segment IDs
    engagement_score: float = 0.0  # Predicted engagement
    created_at: datetime = field(default_factory=datetime.now)
    metadata: Dict[str, Any] = field(default_factory=dict)


@dataclass
class ContentCalendar:
    """Content calendar entry"""
    calendar_id: str
    scheduled_date: datetime
    content: GeneratedContent
    status: str = "draft"  # draft, approved, scheduled, published
    notes: str = ""


class ContentGenerationEngine:
    """AI engine that generates content from your IP"""
    
    def __init__(self):
        self.openai_client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))
        self.knowledge_system = BecomingOneKnowledgeSystem()
        
        # Load content templates
        self.templates = self._load_content_templates()
    
    def _load_content_templates(self) -> Dict[str, ContentTemplate]:
        """Load predefined content templates"""
        templates = {}
        
        # Short-form video template
        templates["short_form_video"] = ContentTemplate(
            template_id="short_form_video",
            name="Short-form Teaching Video",
            content_type=ContentType.SHORT_FORM_VIDEO,
            platforms=[Platform.TIKTOK, Platform.YOUTUBE_SHORTS, Platform.INSTAGRAM_REELS],
            structure={
                "hook": "Attention-grabbing first 3 seconds",
                "teaching_point": "Main Becoming One™ insight (15-30 seconds)",
                "example": "Relatable example or story (10-15 seconds)",
                "call_to_action": "Clear next step (5 seconds)"
            },
            duration_seconds=60,
            word_count_range=(100, 200),
            hashtag_count=8,
            requires_visuals=True,
            prompt_template="""
            Create a 60-second video script based on this Becoming One™ teaching:
            
            Source Content: {source_content}
            Key Concepts: {concepts}
            Target Platform: {platform}
            
            Structure:
            - Hook (0-3s): Start with a question or surprising statement
            - Teaching Point (3-35s): Explain the core insight clearly
            - Example (35-50s): Give a relatable example
            - CTA (50-60s): Tell them what to do next
            
            Make it conversational, authentic, and true to Johan/Marianne's voice.
            Include visual cues in [brackets] for the video editor.
            """
        )
        
        # Social media post template
        templates["social_post"] = ContentTemplate(
            template_id="social_post",
            name="Social Media Teaching Post",
            content_type=ContentType.SOCIAL_MEDIA_POST,
            platforms=[Platform.INSTAGRAM_POST, Platform.LINKEDIN, Platform.FACEBOOK],
            structure={
                "hook": "Opening line that stops the scroll",
                "body": "Main teaching with 2-3 key points",
                "reflection": "Question for engagement",
                "call_to_action": "Next step or resource"
            },
            word_count_range=(150, 400),
            hashtag_count=10,
            requires_visuals=True,
            prompt_template="""
            Create an engaging social media post based on this Becoming One™ content:
            
            Source Content: {source_content}
            Platform: {platform}
            
            Structure:
            1. Hook: Start with something that makes people stop scrolling
            2. Main teaching: Break down the key insight into 2-3 digestible points
            3. Engagement question: Ask something that invites comments
            4. Call to action: Guide them to the next step
            
            Use line breaks for readability. Include relevant emojis sparingly.
            """
        )
        
        # Twitter thread template
        templates["twitter_thread"] = ContentTemplate(
            template_id="twitter_thread",
            name="Twitter Thread",
            content_type=ContentType.TWITTER_THREAD,
            platforms=[Platform.TWITTER],
            structure={
                "thread_hook": "Tweet 1: Hook that promises value",
                "main_points": "Tweets 2-8: Key insights, one per tweet",
                "conclusion": "Tweet 9: Summary and CTA"
            },
            word_count_range=(200, 600),
            hashtag_count=3,
            prompt_template="""
            Create a Twitter thread (8-10 tweets) based on this Becoming One™ teaching:
            
            Source Content: {source_content}
            
            Format each tweet as:
            Tweet 1: Hook that promises specific value
            Tweet 2-8: One key insight per tweet (max 280 characters each)
            Final Tweet: Summary + call to action
            
            Make each tweet valuable on its own while building a cohesive narrative.
            Use numbers, bullet points, and line breaks for clarity.
            """
        )
        
        # Email newsletter template
        templates["newsletter"] = ContentTemplate(
            template_id="newsletter",
            name="Email Newsletter Section",
            content_type=ContentType.EMAIL_NEWSLETTER,
            platforms=[Platform.EMAIL],
            structure={
                "subject_line": "Compelling subject line",
                "opening": "Personal greeting and context",
                "main_content": "Teaching content with stories",
                "practical_tip": "Actionable advice",
                "closing": "Personal sign-off and next step"
            },
            word_count_range=(300, 800),
            prompt_template="""
            Create an email newsletter section based on this Becoming One™ content:
            
            Source Content: {source_content}
            
            Write in Johan/Marianne's personal voice as if writing to a friend.
            Include:
            1. Subject line options (3 variations)
            2. Personal opening that connects to the teaching
            3. Main content with a story or example
            4. One practical tip they can try today
            5. Warm closing with next step
            
            Tone: Conversational, supportive, non-pushy
            """
        )
        
        # Quote graphic template
        templates["quote_graphic"] = ContentTemplate(
            template_id="quote_graphic",
            name="Quote Graphic",
            content_type=ContentType.QUOTE_GRAPHIC,
            platforms=[Platform.INSTAGRAM_POST, Platform.FACEBOOK, Platform.LINKEDIN],
            structure={
                "main_quote": "Powerful, quotable statement",
                "attribution": "- Johan or Marianne",
                "context": "Brief context if needed"
            },
            word_count_range=(10, 50),
            hashtag_count=8,
            requires_visuals=True,
            prompt_template="""
            Extract powerful, quotable statements from this Becoming One™ content:
            
            Source Content: {source_content}
            
            Create 3-5 quote options that:
            1. Stand alone without context
            2. Are under 50 words
            3. Capture the essence of the teaching
            4. Are memorable and shareable
            5. Sound authentic to Johan/Marianne
            
            Format as: "Quote text" - Johan/Marianne
            """
        )
        
        return templates
    
    async def generate_content_batch(
        self,
        theme: str,
        content_types: List[ContentType],
        quantity: int = 5
    ) -> List[GeneratedContent]:
        """Generate a batch of content around a specific theme"""
        
        # 1. Find relevant source content
        source_chunks = await self.knowledge_system.query_knowledge_base(
            query=theme,
            top_k=10
        )
        
        if not source_chunks:
            raise ValueError(f"No source content found for theme: {theme}")
        
        # 2. Generate content for each type
        generated_content = []
        
        for content_type in content_types:
            template = self.templates.get(content_type.value)
            if not template:
                continue
            
            # Generate multiple variations
            for i in range(quantity):
                try:
                    # Select source chunk(s)
                    chunk_index = i % len(source_chunks)
                    source_chunk = source_chunks[chunk_index]
                    
                    # Generate content for each platform
                    for platform in template.platforms:
                        content = await self._generate_single_content(
                            template=template,
                            platform=platform,
                            source_chunk=source_chunk,
                            theme=theme
                        )
                        generated_content.append(content)
                        
                except Exception as e:
                    print(f"❌ Error generating {content_type.value}: {e}")
        
        return generated_content
    
    async def _generate_single_content(
        self,
        template: ContentTemplate,
        platform: Platform,
        source_chunk: Dict[str, Any],
        theme: str
    ) -> GeneratedContent:
        """Generate a single piece of content"""
        
        # Prepare prompt
        prompt = template.prompt_template.format(
            source_content=source_chunk["content"],
            concepts=source_chunk.get("metadata", {}).get("concepts", []),
            platform=platform.value,
            theme=theme
        )
        
        # Add platform-specific instructions
        platform_instructions = self._get_platform_instructions(platform)
        full_prompt = f"{prompt}\n\nPlatform-specific notes:\n{platform_instructions}"
        
        # Generate content
        response = await self.openai_client.chat.completions.create(
            model="gpt-4-turbo-preview",
            messages=[
                {"role": "system", "content": self._get_system_prompt(template.content_type)},
                {"role": "user", "content": full_prompt}
            ],
            temperature=0.7,
            max_tokens=1000
        )
        
        # Parse response
        content_text = response.choices[0].message.content
        
        # Extract components
        components = self._parse_content_response(content_text, template)
        
        # Generate hashtags
        hashtags = await self._generate_hashtags(
            content_text,
            platform,
            template.hashtag_count
        )
        
        # Create content object
        content = GeneratedContent(
            content_id=str(uuid.uuid4()),
            content_type=template.content_type,
            platform=platform,
            title=components.get("title", f"{theme} - {platform.value}"),
            content_body=components.get("body", content_text),
            hook=components.get("hook"),
            call_to_action=components.get("call_to_action"),
            hashtags=hashtags,
            visual_suggestions=components.get("visual_suggestions", []),
            source_segments=[source_chunk.get("parent_id", "")],
            engagement_score=self._predict_engagement_score(content_text, platform),
            metadata={
                "theme": theme,
                "source_score": source_chunk.get("score", 0.0),
                "template_used": template.template_id,
                "generated_at": datetime.now().isoformat()
            }
        )
        
        return content
    
    def _get_system_prompt(self, content_type: ContentType) -> str:
        """Get system prompt for content type"""
        base_prompt = """
        You are a content creator specializing in the Becoming One™ methodology.
        Create authentic, engaging content that reflects Johan and Marianne's voice and teachings.
        
        Key principles:
        - Focus on feeling-states, not external objects
        - Treat obstacles as portals to growth
        - Use anti-bypass approach (no spiritual bypassing)
        - Be practical and actionable
        - Maintain warmth and authenticity
        """
        
        type_specific = {
            ContentType.SHORT_FORM_VIDEO: "Create video scripts that are visually engaging and work well with quick cuts and text overlays.",
            ContentType.SOCIAL_MEDIA_POST: "Write posts that encourage meaningful engagement and reflection.",
            ContentType.TWITTER_THREAD: "Each tweet should provide value while building toward a cohesive message.",
            ContentType.EMAIL_NEWSLETTER: "Write in a personal, conversational tone as if writing to a close friend.",
            ContentType.QUOTE_GRAPHIC: "Extract the most powerful, memorable statements that capture the essence of the teaching."
        }
        
        return f"{base_prompt}\n\n{type_specific.get(content_type, '')}"
    
    def _get_platform_instructions(self, platform: Platform) -> str:
        """Get platform-specific instructions"""
        instructions = {
            Platform.TIKTOK: "Keep it energetic, use trending sounds concepts, include visual hooks every 3-5 seconds",
            Platform.YOUTUBE_SHORTS: "Focus on educational value, use clear text overlays, include subscribe reminder",
            Platform.INSTAGRAM_REELS: "Make it aesthetically pleasing, use relevant audio, optimize for discovery",
            Platform.INSTAGRAM_POST: "Use line breaks for readability, include story elements, encourage saves",
            Platform.TWITTER: "Keep tweets under 280 characters, use threads for longer content, encourage retweets",
            Platform.LINKEDIN: "Professional tone, focus on business/career applications, encourage thoughtful discussion",
            Platform.EMAIL: "Personal and conversational, include clear next steps, avoid being salesy"
        }
        
        return instructions.get(platform, "Follow general best practices for the platform")
    
    def _parse_content_response(self, content_text: str, template: ContentTemplate) -> Dict[str, Any]:
        """Parse AI response into components"""
        components = {}
        
        # Try to extract structured components
        lines = content_text.split('\n')
        current_section = "body"
        current_content = []
        
        for line in lines:
            line = line.strip()
            if not line:
                continue
            
            # Check for section headers
            if any(keyword in line.lower() for keyword in ["hook:", "title:", "subject:", "cta:", "call to action:"]):
                if current_content:
                    components[current_section] = '\n'.join(current_content)
                
                if "hook" in line.lower():
                    current_section = "hook"
                elif "title" in line.lower() or "subject" in line.lower():
                    current_section = "title"
                elif "cta" in line.lower() or "call to action" in line.lower():
                    current_section = "call_to_action"
                
                # Extract content after colon
                if ":" in line:
                    content_after_colon = line.split(":", 1)[1].strip()
                    if content_after_colon:
                        current_content = [content_after_colon]
                    else:
                        current_content = []
                else:
                    current_content = []
            else:
                current_content.append(line)
        
        # Add final section
        if current_content:
            components[current_section] = '\n'.join(current_content)
        
        # If no structure found, use entire text as body
        if not components:
            components["body"] = content_text
        
        return components
    
    async def _generate_hashtags(self, content: str, platform: Platform, count: int) -> List[str]:
        """Generate relevant hashtags"""
        
        prompt = f"""
        Generate {count} relevant hashtags for this content on {platform.value}:
        
        Content: "{content[:200]}..."
        
        Include:
        - Becoming One™ related hashtags
        - General personal development hashtags
        - Platform-specific trending hashtags
        - Niche spiritual growth hashtags
        
        Return only the hashtags, one per line, with # symbol.
        """
        
        try:
            response = await self.openai_client.chat.completions.create(
                model="gpt-4-turbo-preview",
                messages=[
                    {"role": "system", "content": "You are an expert at social media hashtag research and optimization."},
                    {"role": "user", "content": prompt}
                ],
                temperature=0.5,
                max_tokens=200
            )
            
            hashtag_text = response.choices[0].message.content
            hashtags = [line.strip() for line in hashtag_text.split('\n') if line.strip().startswith('#')]
            
            return hashtags[:count]
            
        except Exception as e:
            # Fallback hashtags
            return [
                "#BecomingOne",
                "#PersonalDevelopment",
                "#Transformation",
                "#Mindfulness",
                "#Growth"
            ][:count]
    
    def _predict_engagement_score(self, content: str, platform: Platform) -> float:
        """Predict engagement score based on content characteristics"""
        score = 0.5  # Base score
        
        # Length optimization
        word_count = len(content.split())
        if platform in [Platform.TWITTER, Platform.TIKTOK]:
            # Shorter is better
            if word_count < 50:
                score += 0.2
        elif platform in [Platform.LINKEDIN, Platform.EMAIL]:
            # Medium length is better
            if 100 <= word_count <= 300:
                score += 0.2
        
        # Engagement signals
        if "?" in content:  # Questions increase engagement
            score += 0.1
        if any(word in content.lower() for word in ["you", "your", "yourself"]):  # Personal pronouns
            score += 0.1
        if any(word in content.lower() for word in ["imagine", "what if", "picture this"]):  # Imagination triggers
            score += 0.1
        
        # Becoming One™ specific signals
        if any(concept in content.lower() for concept in ["feeling-state", "anchor", "manifestation", "turn 180"]):
            score += 0.1
        
        return min(score, 1.0)


class ContentCalendarManager:
    """Manages content calendar and scheduling"""
    
    def __init__(self):
        self.generation_engine = ContentGenerationEngine()
    
    async def create_weekly_calendar(
        self,
        themes: List[str],
        start_date: datetime,
        content_mix: Dict[ContentType, int]  # e.g., {SHORT_FORM_VIDEO: 3, SOCIAL_POST: 5}
    ) -> List[ContentCalendar]:
        """Create a week's worth of content"""
        
        calendar_entries = []
        current_date = start_date
        
        for theme in themes:
            # Generate content for this theme
            content_types = list(content_mix.keys())
            generated_content = await self.generation_engine.generate_content_batch(
                theme=theme,
                content_types=content_types,
                quantity=max(content_mix.values())
            )
            
            # Schedule content throughout the week
            for content in generated_content:
                calendar_entry = ContentCalendar(
                    calendar_id=str(uuid.uuid4()),
                    scheduled_date=current_date,
                    content=content,
                    status="draft"
                )
                
                calendar_entries.append(calendar_entry)
                
                # Move to next posting slot
                current_date += timedelta(hours=8)  # Space content throughout days
                if current_date.date() > (start_date + timedelta(days=7)).date():
                    current_date = start_date + timedelta(days=1)
        
        return calendar_entries
    
    def export_calendar_to_csv(self, calendar_entries: List[ContentCalendar], filename: str):
        """Export calendar to CSV for review"""
        import csv
        
        with open(filename, 'w', newline='', encoding='utf-8') as csvfile:
            fieldnames = [
                'Date', 'Time', 'Platform', 'Content Type', 'Title', 
                'Content Preview', 'Hashtags', 'Status', 'Engagement Score'
            ]
            writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
            
            writer.writeheader()
            for entry in calendar_entries:
                writer.writerow({
                    'Date': entry.scheduled_date.strftime('%Y-%m-%d'),
                    'Time': entry.scheduled_date.strftime('%H:%M'),
                    'Platform': entry.content.platform.value,
                    'Content Type': entry.content.content_type.value,
                    'Title': entry.content.title,
                    'Content Preview': entry.content.content_body[:100] + "...",
                    'Hashtags': ' '.join(entry.content.hashtags),
                    'Status': entry.status,
                    'Engagement Score': f"{entry.content.engagement_score:.2f}"
                })
        
        print(f"📅 Calendar exported to: {filename}")


# Usage example
async def example_content_generation():
    """Example of how to use the content generation system"""
    
    engine = ContentGenerationEngine()
    calendar_manager = ContentCalendarManager()
    
    # Generate content around specific themes
    themes = ["emotional anchors", "manifestation", "procrastination as portal"]
    
    content_mix = {
        ContentType.SHORT_FORM_VIDEO: 2,
        ContentType.SOCIAL_MEDIA_POST: 3,
        ContentType.TWITTER_THREAD: 1,
        ContentType.QUOTE_GRAPHIC: 2
    }
    
    # Create weekly calendar
    start_date = datetime.now().replace(hour=9, minute=0, second=0, microsecond=0)
    calendar = await calendar_manager.create_weekly_calendar(
        themes=themes,
        start_date=start_date,
        content_mix=content_mix
    )
    
    # Export for review
    calendar_manager.export_calendar_to_csv(
        calendar, 
        f"content_calendar_{start_date.strftime('%Y%m%d')}.csv"
    )
    
    print(f"📅 Generated {len(calendar)} pieces of content for the week")
    
    # Show sample content
    for entry in calendar[:3]:
        print(f"\n📱 {entry.content.platform.value.upper()} - {entry.content.content_type.value}")
        print(f"🗓️ Scheduled: {entry.scheduled_date.strftime('%Y-%m-%d %H:%M')}")
        print(f"📝 Title: {entry.content.title}")
        print(f"💬 Preview: {entry.content.content_body[:150]}...")
        print(f"🏷️ Hashtags: {' '.join(entry.content.hashtags[:3])}")
        print(f"📊 Engagement Score: {entry.content.engagement_score:.2f}")


if __name__ == "__main__":
    asyncio.run(example_content_generation())
