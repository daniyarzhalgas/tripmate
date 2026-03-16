"""
Script to populate database with sample data for users, profiles, vacancies, and offers.

Usage:
    python populate_sample_data.py

Note: Run this after running database migrations (alembic upgrade head)
      and after running populate_db.py for languages/interests/travel_styles
"""

import asyncio
from datetime import date, datetime

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.database import AsyncSessionLocal
from app.models.user import User
from app.models.profile import Profile
from app.models.trip_vacancy import TripVacancy
from app.models.offer import Offer


# -------------------------------------------------------------------
# Helpers
# -------------------------------------------------------------------

def hash_password(plain: str) -> str:
    """Hash a plaintext password. Replace with your actual hashing util."""
    from app.core.security import get_password_hash  # adjust import as needed
    return get_password_hash(plain)


async def get_or_skip(session: AsyncSession, model, filters) -> bool:
    """Return True if any rows matching filters already exist."""
    result = await session.execute(select(model).filter_by(**filters))
    return result.scalars().first() is not None


# -------------------------------------------------------------------
# Users
# -------------------------------------------------------------------

async def populate_users(session: AsyncSession) -> list[User]:
    users_data = [
        {
            "email": "atapkell@gmail.com",
            "password": hash_password("testtest"),
            "role": "user",
            "is_verified": True,
            "is_active": True,
        },
        {
            "email": "test@gmail.com",
            "password": hash_password("testtest"),
            "role": "user",
            "is_verified": True,
            "is_active": True,
        },
    ]

    users: list[User] = []
    created = 0

    for data in users_data:
        if await get_or_skip(session, User, {"email": data["email"]}):
            print(f"  User {data['email']} already exists. Skipping...")
            result = await session.execute(select(User).filter_by(email=data["email"]))
            users.append(result.scalars().first())
            continue

        user = User(**data)
        session.add(user)
        await session.flush()   # get user.id before commit
        users.append(user)
        created += 1

    await session.commit()
    if created:
        print(f"✓ Added {created} users")
    return users


# -------------------------------------------------------------------
# Profiles
# -------------------------------------------------------------------

async def populate_profiles(session: AsyncSession, users: list[User]) -> None:
    profiles_data = [
        {
            "user_id": users[0].id,
            "first_name": "Beibarys",
            "last_name": "Atapkel",
            "date_of_birth": date(2004, 11, 22),
            "gender": "Male",
            "country": "Kazakhstan",
            "city": "Atyrau",
            "nationality": "Kazakhstani",
            "phone": "+77011234567",
            "instagram_handle": "beibarys.travels",
            "telegram_handle": "@beibarys_j",
            "bio": "I am student of SWE, I love building software products, I passionaite about startups",
            "profile_photo": None,
        },
        {
            "user_id": users[1].id,
            "first_name": "Bob",
            "last_name": "Smith",
            "date_of_birth": date(2005, 6, 19),
            "gender": "Female",
            "country": "Kazakhstan",
            "city": "Atyrau",
            "nationality": "Kazakhstani",
            "phone": "+77029876543",
            "instagram_handle": "bobexplores",
            "telegram_handle": "@bob_smith",
            "bio": "I am teacher of English, I love traveling and exploring new cultures. Always up for an adventure!",
            "profile_photo": None,
        },
    ]

    created = 0
    for data in profiles_data:
        if await get_or_skip(session, Profile, {"user_id": data["user_id"]}):
            print(f"  Profile for user_id={data['user_id']} already exists. Skipping...")
            continue

        profile = Profile(**data)
        session.add(profile)
        created += 1

    await session.commit()
    if created:
        print(f"✓ Added {created} profiles")


# -------------------------------------------------------------------
# Trip Vacancy
# -------------------------------------------------------------------

async def populate_vacancy(session: AsyncSession, requester: User) -> TripVacancy:
    existing = await get_or_skip(
        session, TripVacancy,
        {"requester_id": requester.id, "destination_city": "Barcelona"}
    )
    if existing:
        print("  TripVacancy already exists. Skipping...")
        result = await session.execute(
            select(TripVacancy).filter_by(requester_id=requester.id, destination_city="Barcelona")
        )
        return result.scalars().first()

    vacancy = TripVacancy(
        requester_id=requester.id,
        destination_city="Barcelona",
        destination_country="Spain",
        start_date=date(2025, 7, 10),
        end_date=date(2025, 7, 20),
        min_budget=800,
        max_budget=1500,
        people_needed=3,
        people_joined=0,
        description="Looking for travel buddies for a 10-day Barcelona trip! "
                    "Planning to explore art, food, and beaches.",
        planned_activities="Sagrada Familia, Park Güell, beach days, tapas tours",
        planned_destinations="Barcelona Old Town, Barceloneta Beach, Gothic Quarter",
        transportation_preference="Any",
        accommodation_preference="Any",
        min_age=22,
        max_age=35,
        gender_preference="Any",
        status="open",
    )
    session.add(vacancy)
    await session.flush()
    await session.commit()
    print("✓ Added 1 trip vacancy")
    return vacancy


# -------------------------------------------------------------------
# Offer
# -------------------------------------------------------------------

# async def populate_offer(
#     session: AsyncSession,
#     vacancy: TripVacancy,
#     offerer: User,
# ) -> None:
#     existing = await get_or_skip(
#         session, Offer,
#         {"trip_vacancy_id": vacancy.id, "offerer_id": offerer.id}
#     )
#     if existing:
#         print("  Offer already exists. Skipping...")
#         return

#     offer = Offer(
#         trip_vacancy_id=vacancy.id,
#         offerer_id=offerer.id,
#         message="Hey! I'd love to join your Barcelona trip. "
#                 "I've been there before and know some hidden gems. "
#                 "My budget fits perfectly in your range.",
#         proposed_budget=1200,
#         status="pending",
#     )
#     session.add(offer)
#     await session.commit()
#     print("✓ Added 1 offer")


# -------------------------------------------------------------------
# Main
# -------------------------------------------------------------------

async def main():
    print("Populating database with sample data...")
    print("-" * 50)

    async with AsyncSessionLocal() as session:
        users = await populate_users(session)
        await populate_profiles(session, users)

        # Alice (users[0]) posts the vacancy, Bob (users[1]) sends the offer
        vacancy = await populate_vacancy(session, requester=users[0])
        # await populate_offer(session, vacancy=vacancy, offerer=users[1])

    print("-" * 50)
    print("✓ Sample data population complete!")


if __name__ == "__main__":
    asyncio.run(main())