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

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.database import AsyncSessionLocal
from app.models.city import City
from app.models.country import Country
from app.models.interest import Interest
from app.models.language import Language
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
            {"name": "Turkish"},
            {"name": "Arabic"},
            {"name": "Chinese"},
            {"name": "French"},
            {"name": "German"},
            {"name": "Spanish"},
            {"name": "Japanese"},
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
            {"name": "Food & Dining"},
            {"name": "Adventure & Sports"},
            {"name": "Culture & History"},
            {"name": "Nature & Outdoors"},
            {"name": "Arts & Entertainment"},
            {"name": "Shopping"},
            {"name": "Wellness & Relaxation"},
            {"name": "Photography"},
            {"name": "Nightlife"},
            {"name": "Local Experiences"},
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
            {"name": "Luxury"},
            {"name": "Budget-Friendly"},
            {"name": "Adventure"},
            {"name": "Cultural Immersion"},
            {"name": "Relaxation"},
        ]

        for style_data in travel_styles:
            travel_style = TravelStyle(**style_data)
            session.add(travel_style)

        await session.commit()
        print(f"✓ Added {len(travel_styles)} travel styles")


async def populate_countries_and_cities():
    """Populate countries and cities tables with default data."""
    async with AsyncSessionLocal() as session:
        # Check if countries already exist
        result = await session.execute(select(Country))
        existing = result.scalars().all()

        if existing:
            print(
                f"Countries already populated ({len(existing)} countries found). Skipping..."
            )
            return

        countries_with_cities = {
            "Kazakhstan": ["Qulsary","Almaty", "Astana", "Shymkent", "Aktobe", "Karaganda", "Atyrau", "Mangystau"],
            "Turkey": ["Istanbul", "Ankara", "Antalya", "Izmir", "Bodrum", "Cappadocia", "Trabzon"],
            "United Arab Emirates": ["Dubai", "Abu Dhabi", "Sharjah", "Ajman"],
            "United States": ["New York", "Los Angeles", "San Francisco", "Miami", "Las Vegas", "Chicago", "Houston"],
            "United Kingdom": ["London", "Manchester", "Edinburgh", "Birmingham", "Liverpool"],
            "France": ["Paris", "Nice", "Lyon", "Marseille", "Bordeaux"],
            "Germany": ["Berlin", "Munich", "Frankfurt", "Hamburg", "Cologne"],
            "Italy": ["Rome", "Milan", "Venice", "Florence", "Naples"],
            "Spain": ["Madrid", "Barcelona", "Seville", "Valencia", "Malaga"],
            "Japan": ["Tokyo", "Osaka", "Kyoto", "Yokohama", "Sapporo"],
            "South Korea": ["Seoul", "Busan", "Jeju", "Incheon"],
            "China": ["Beijing", "Shanghai", "Guangzhou", "Shenzhen", "Chengdu"],
            "Thailand": ["Bangkok", "Phuket", "Chiang Mai", "Pattaya"],
            "Indonesia": ["Jakarta", "Bali", "Yogyakarta", "Surabaya"],
            "Malaysia": ["Kuala Lumpur", "Penang", "Langkawi", "Johor Bahru"],
            "Singapore": ["Singapore"],
            "Russia": ["Moscow", "Saint Petersburg", "Kazan", "Sochi", "Novosibirsk"],
            "Georgia": ["Tbilisi", "Batumi", "Kutaisi"],
            "Uzbekistan": ["Tashkent", "Samarkand", "Bukhara", "Khiva"],
            "Kyrgyzstan": ["Bishkek", "Osh", "Issyk-Kul"],
            "Egypt": ["Cairo", "Hurghada", "Sharm El Sheikh", "Luxor", "Alexandria"],
            "Mexico": ["Mexico City", "Cancun", "Playa del Carmen", "Guadalajara"],
            "Brazil": ["Rio de Janeiro", "Sao Paulo", "Salvador", "Brasilia"],
            "Australia": ["Sydney", "Melbourne", "Brisbane", "Perth"],
            "Canada": ["Toronto", "Vancouver", "Montreal", "Ottawa"],
            "India": ["Delhi", "Mumbai", "Goa", "Bangalore", "Jaipur"],
            "Greece": ["Athens", "Santorini", "Mykonos", "Thessaloniki", "Crete"],
            "Portugal": ["Lisbon", "Porto", "Faro", "Madeira"],
            "Netherlands": ["Amsterdam", "Rotterdam", "The Hague", "Utrecht"],
            "Czech Republic": ["Prague", "Brno", "Karlovy Vary"],
            "Austria": ["Vienna", "Salzburg", "Innsbruck"],
            "Switzerland": ["Zurich", "Geneva", "Bern", "Lucerne"],
            "Poland": ["Warsaw", "Krakow", "Gdansk", "Wroclaw"],
            "Hungary": ["Budapest", "Debrecen"],
            "Croatia": ["Zagreb", "Dubrovnik", "Split"],
            "Montenegro": ["Podgorica", "Budva", "Kotor"],
            "Maldives": ["Male"],
            "Sri Lanka": ["Colombo", "Kandy", "Galle"],
            "Vietnam": ["Hanoi", "Ho Chi Minh City", "Da Nang"],
            "Philippines": ["Manila", "Cebu", "Boracay", "Palawan"],
            "Morocco": ["Marrakech", "Casablanca", "Fes", "Tangier"],
            "South Africa": ["Cape Town", "Johannesburg", "Durban"],
            "Tanzania": ["Dar es Salaam", "Zanzibar", "Arusha"],
            "Kenya": ["Nairobi", "Mombasa"],
            "Argentina": ["Buenos Aires", "Mendoza", "Bariloche"],
            "Colombia": ["Bogota", "Medellin", "Cartagena"],
            "Peru": ["Lima", "Cusco", "Arequipa"],
            "Chile": ["Santiago", "Valparaiso"],
            "New Zealand": ["Auckland", "Wellington", "Queenstown"],
            "Norway": ["Oslo", "Bergen", "Tromso"],
            "Sweden": ["Stockholm", "Gothenburg", "Malmo"],
            "Finland": ["Helsinki", "Rovaniemi", "Turku"],
            "Denmark": ["Copenhagen", "Aarhus"],
            "Iceland": ["Reykjavik"],
            "Ireland": ["Dublin", "Cork", "Galway"],
            "Scotland": ["Edinburgh", "Glasgow"],
            "Saudi Arabia": ["Riyadh", "Jeddah", "Mecca", "Medina"],
            "Qatar": ["Doha"],
            "Oman": ["Muscat"],
            "Bahrain": ["Manama"],
            "Jordan": ["Amman", "Petra", "Aqaba"],
            "Israel": ["Tel Aviv", "Jerusalem", "Haifa"],
            "Azerbaijan": ["Baku"],
            "Armenia": ["Yerevan"],
        }

        total_cities = 0
        for country_name, city_names in countries_with_cities.items():
            country = Country(name=country_name)
            session.add(country)
            await session.flush()

            for city_name in city_names:
                city = City(name=city_name, country_id=country.id)
                session.add(city)
                total_cities += 1

        await session.commit()
        print(f"Added {len(countries_with_cities)} countries and {total_cities} cities")


async def main():
    """Main function to populate all default data."""
    print("Populating database with initial data...")
    print("-" * 50)

    await populate_countries_and_cities()
    await populate_languages()
    await populate_interests()
    await populate_travel_styles()

    print("-" * 50)
    print("Database population complete!")


if __name__ == "__main__":
    asyncio.run(main())
