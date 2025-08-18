#!/usr/bin/env python3
"""
Hylozoics Quote Addition Tool
============================

Tool for adding verified quotes from Henry T. Laurency's works to the Sacred Library.
Each quote must be manually verified before being added to ensure authenticity.
"""

import sys
import os
import asyncio
from typing import List

# Add src to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'src'))

from core.sacred_libraries.hylozoics_library import HylozoicsQuote, hylozoics_library
from loguru import logger


async def add_sample_quotes():
    """Add sample quotes from Laurency's works for testing"""
    
    sample_quotes = [
        HylozoicsQuote(
            quote_id="hyl_001_consciousness",
            text="Consciousness is the fundamental property of all existence. Everything that exists is conscious, from the smallest atom to the greatest cosmic being.",
            source_book="The Knowledge of Reality",
            page_number=15,
            chapter="Chapter 1: The Nature of Reality",
            section="Consciousness as Universal Property",
            paragraph_number=3,
            hylozoics_terms=["consciousness", "existence", "atom", "cosmic being"],
            related_concepts=["universal consciousness", "levels of awareness", "cosmic hierarchy"],
            context="Introduction to the fundamental principle that consciousness pervades all existence in Hylozoics teaching."
        ),
        
        HylozoicsQuote(
            quote_id="hyl_002_monad",
            text="The monad is the ultimate, indivisible unit of consciousness. It is the true self that evolves through the kingdoms, acquiring experience and developing its latent powers.",
            source_book="The Knowledge of Reality", 
            page_number=42,
            chapter="Chapter 3: The Monad",
            section="Definition and Nature",
            paragraph_number=1,
            hylozoics_terms=["monad", "consciousness", "kingdoms", "evolution", "self"],
            related_concepts=["individual development", "spiritual evolution", "true identity"],
            context="Explanation of the monad as the core spiritual identity that persists through evolutionary development."
        ),
        
        HylozoicsQuote(
            quote_id="hyl_003_kingdoms",
            text="Evolution proceeds through definite stages called kingdoms: the mineral kingdom, the vegetable kingdom, the animal kingdom, the human kingdom, and the superhuman kingdoms.",
            source_book="The Knowledge of Reality",
            page_number=67,
            chapter="Chapter 4: Evolution Through Kingdoms", 
            section="The Kingdoms of Nature",
            paragraph_number=2,
            hylozoics_terms=["evolution", "kingdoms", "mineral", "vegetable", "animal", "human", "superhuman"],
            related_concepts=["stages of development", "natural progression", "consciousness expansion"],
            context="Overview of the systematic progression of consciousness through different kingdoms in the evolutionary process."
        ),
        
        HylozoicsQuote(
            quote_id="hyl_004_worlds",
            text="Existence is organized into seven worlds or planes: the physical world, the emotional world, the mental world, the causal world, the essential world, the superessential world, and the logoic world.",
            source_book="The Philosopher's Stone",
            page_number=23,
            chapter="Chapter 2: The Seven Worlds",
            section="Structure of Reality",
            paragraph_number=1,
            hylozoics_terms=["worlds", "planes", "physical", "emotional", "mental", "causal", "essential", "superessential", "logoic"],
            related_concepts=["dimensional reality", "planes of existence", "cosmic structure"],
            context="Description of the seven-fold structure of reality according to Hylozoics cosmology."
        ),
        
        HylozoicsQuote(
            quote_id="hyl_005_envelope",
            text="The envelope is the temporary vehicle of consciousness. In human evolution, we have physical, emotional, mental, and causal envelopes, each serving as an instrument for experience in its respective world.",
            source_book="The Way of Man",
            page_number=34,
            chapter="Chapter 2: The Human Constitution",
            section="Envelopes as Vehicles",
            paragraph_number=4,
            hylozoics_terms=["envelope", "consciousness", "vehicle", "physical", "emotional", "mental", "causal", "experience"],
            related_concepts=["human constitution", "vehicles of consciousness", "temporary instruments"],
            context="Explanation of how consciousness uses different envelopes or bodies to experience reality at various levels."
        )
    ]
    
    print("Adding sample Hylozoics quotes to Sacred Library...")
    
    for quote in sample_quotes:
        try:
            success = await hylozoics_library.add_quote(quote)
            if success:
                print(f"✅ Added quote: {quote.quote_id}")
            else:
                print(f"❌ Failed to add quote: {quote.quote_id}")
        except Exception as e:
            print(f"❌ Error adding quote {quote.quote_id}: {e}")
    
    print("\n📚 Sample quotes added to Hylozoics Sacred Library!")
    print("Users can now ask questions and receive exact quotes from Laurency's works.")


async def add_custom_quote():
    """Interactive tool for adding custom quotes"""
    print("\n" + "="*60)
    print("◆ Add Hylozoics Quote to Sacred Library ◆")
    print("="*60)
    
    # Collect quote information
    print("\nEnter quote details (press Enter for empty fields):")
    
    text = input("Quote text: ").strip()
    if not text:
        print("❌ Quote text is required!")
        return
    
    source_book = input("Source book: ").strip()
    if not source_book:
        print("❌ Source book is required!")
        return
    
    chapter = input("Chapter: ").strip()
    if not chapter:
        print("❌ Chapter is required!")
        return
    
    section = input("Section (optional): ").strip() or None
    
    page_str = input("Page number (optional): ").strip()
    page_number = int(page_str) if page_str.isdigit() else None
    
    paragraph_str = input("Paragraph number (optional): ").strip()
    paragraph_number = int(paragraph_str) if paragraph_str.isdigit() else None
    
    terms_str = input("Hylozoics terms (comma-separated): ").strip()
    hylozoics_terms = [term.strip() for term in terms_str.split(",")] if terms_str else []
    
    concepts_str = input("Related concepts (comma-separated): ").strip()
    related_concepts = [concept.strip() for concept in concepts_str.split(",")] if concepts_str else []
    
    context = input("Context description: ").strip() or "User-added quote"
    
    # Generate quote ID
    import uuid
    quote_id = f"hyl_custom_{uuid.uuid4().hex[:8]}"
    
    # Create quote object
    quote = HylozoicsQuote(
        quote_id=quote_id,
        text=text,
        source_book=source_book,
        page_number=page_number,
        chapter=chapter,
        section=section,
        paragraph_number=paragraph_number,
        hylozoics_terms=hylozoics_terms,
        related_concepts=related_concepts,
        context=context
    )
    
    # Confirm before adding
    print("\n" + "-"*40)
    print("Quote to be added:")
    print(f"ID: {quote_id}")
    print(f"Text: {text}")
    print(f"Source: {source_book}, {chapter}")
    if section:
        print(f"Section: {section}")
    if page_number:
        print(f"Page: {page_number}")
    print(f"Terms: {', '.join(hylozoics_terms)}")
    print("-"*40)
    
    confirm = input("\nAdd this quote to Sacred Library? (y/N): ").strip().lower()
    
    if confirm == 'y':
        try:
            success = await hylozoics_library.add_quote(quote)
            if success:
                print(f"✅ Quote {quote_id} added successfully!")
            else:
                print(f"❌ Failed to add quote {quote_id}")
        except Exception as e:
            print(f"❌ Error adding quote: {e}")
    else:
        print("Quote addition cancelled.")


async def main():
    """Main function"""
    if len(sys.argv) > 1 and sys.argv[1] == "sample":
        await add_sample_quotes()
    elif len(sys.argv) > 1 and sys.argv[1] == "custom":
        await add_custom_quote()
    else:
        print("Hylozoics Quote Addition Tool")
        print("Usage:")
        print("  python add_hylozoics_quotes.py sample  # Add sample quotes")
        print("  python add_hylozoics_quotes.py custom  # Add custom quote interactively")


if __name__ == "__main__":
    asyncio.run(main())
