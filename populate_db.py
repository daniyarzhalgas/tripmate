"""
Script to populate database with initial data for languages, interests, and travel styles.

This script adds:
- Languages: Kazakh, English, Russian
- Interests: Adventure, Culture, Food & Dining, etc.
- Travel Styles: Budget, Luxury, Backpacker, etc.

Usage:
    python populate_db.py

Note: Run this after running database migrations (alembic upgrade head)
"""

import asyncio
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select

from app.core.database import AsyncSessionLocal
from app.models.language import Language
from app.models.interest import Interest
from app.models.travel_style import TravelStyle


async def populate_languages():
    """Populate languages table with default languages."""
    async with AsyncSessionLocal() as session:
        # Check if languages already exist
        result = await session.execute(select(Language))
        existing = result.scalars().all()

        if existing:
            print(
                f"Languages already populated ({len(existing)} languages found). Skipping..."
            )
            return

        languages = [
            {"name": "Kazakh"},
            {"name": "English"},
            {"name": "Russian"},
        ]

        for lang_data in languages:
            language = Language(**lang_data)
            session.add(language)

        await session.commit()
        print(f"✓ Added {len(languages)} languages")


async def populate_interests():
    """Populate interests table with default interests."""
    async with AsyncSessionLocal() as session:
        # Check if interests already exist
        result = await session.execute(select(Interest))
        existing = result.scalars().all()

        if existing:
            print(
                f"Interests already populated ({len(existing)} interests found). Skipping..."
            )
            return

        interests = [
            {"name": "Adventure"},
            {"name": "Culture"},
            {"name": "Food & Dining"},
            {"name": "Photography"},
            {"name": "Nature & Wildlife"},
            {"name": "History"},
            {"name": "Shopping"},
            {"name": "Nightlife"},
            {"name": "Sports & Fitness"},
            {"name": "Art & Museums"},
            {"name": "Beach & Relaxation"},
            {"name": "Music & Festivals"},
            {"name": "Hiking & Trekking"},
            {"name": "Water Sports"},
            {"name": "Camping"},
            {"name": "City Tours"},
            {"name": "Local Experiences"},
            {"name": "Wellness & Spa"},
        ]

        for interest_data in interests:
            interest = Interest(**interest_data)
            session.add(interest)

        await session.commit()
        print(f"✓ Added {len(interests)} interests")


async def populate_travel_styles():
    """Populate travel_styles table with default travel styles."""
    async with AsyncSessionLocal() as session:
        # Check if travel styles already exist
        result = await session.execute(select(TravelStyle))
        existing = result.scalars().all()

        if existing:
            print(
                f"Travel styles already populated ({len(existing)} travel styles found). Skipping..."
            )
            return

        travel_styles = [
            {"name": "Budget"},
            {"name": "Luxury"},
            {"name": "Backpacker"},
            {"name": "Adventure"},
            {"name": "Relaxation"},
            {"name": "Cultural"},
            {"name": "Business"},
            {"name": "Family-Friendly"},
            {"name": "Solo"},
            {"name": "Group"},
            {"name": "Eco-Tourism"},
            {"name": "Road Trip"},
        ]

        for style_data in travel_styles:
            travel_style = TravelStyle(**style_data)
            session.add(travel_style)

        await session.commit()
        print(f"✓ Added {len(travel_styles)} travel styles")


async def main():
    """Main function to populate all default data."""
    print("Populating database with initial data...")
    print("-" * 50)

    await populate_languages()
    await populate_interests()
    await populate_travel_styles()

    print("-" * 50)
    print("✓ Database population complete!")


if __name__ == "__main__":
    asyncio.run(main())
