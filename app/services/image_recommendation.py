import asyncio
from typing import Optional

import httpx
from sqlalchemy import update
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.config import config as settings
# from app.core import AppError
from app.models.recommended_place import RecommendedPlace


UNSPLASH_API_BASE = "https://api.unsplash.com"


async def _fetch_unsplash_photo(
    client: httpx.AsyncClient,
    query: str,
) -> Optional[str]:
    """
    Search Unsplash for a single landscape photo matching `query`.
    Returns the regular-size image URL, or None on any failure.
    """
    print(f"Fetching Unsplash image for query: '{query}'")
    try:
        response = await client.get(
            f"{UNSPLASH_API_BASE}/search/photos",
            params={
                "query": query,
                "per_page": 1,
                "orientation": "landscape",
            },
            headers={"Authorization": f"Client-ID {settings.UNPLASH_ACCESS_KEY}"},
            timeout=10.0,
        )
        response.raise_for_status()
        data = response.json()
        results = data.get("results", [])
        if results:
            print("Unsplash image found for query: '{query}'")
            return results[0]["urls"]["regular"]
    except httpx.HTTPStatusError as exc:
        # print(exc)
        print(f"Error fetching Unsplash image for query: '{query}'")
        pass
    except httpx.RequestError as exc:
        # print(exc)
        print(f"Request error fetching Unsplash image for query: '{query}'")
        pass
    return None


# ------------------------------------------------------------------ #
# 1. Schema-level enrichment (before DB insert)
#    Used in ai_service.py right after Gemini validation.
# ------------------------------------------------------------------ #

async def enrich_with_unsplash_images(
    places: list,  # list[RecommendedPlaceSchema]
) -> None:
    """
    Mutates each Pydantic schema object's `image_url` in-place.
    All HTTP requests run concurrently.
    Falls back to the AI-generated URL silently on failure.
    """
    print("Enriching places with Unsplash images...")
    async with httpx.AsyncClient() as client:

        async def _enrich_one(place) -> None:
            # query = f"{place.name} {place.city}"
            query = f"{place.name}"

            url = await _fetch_unsplash_photo(client, query)
            if url:
                place.image_url = url

        await asyncio.gather(*[_enrich_one(p) for p in places])


# ------------------------------------------------------------------ #
# 2. DB-level enrichment (after DB insert / for existing rows)
#    Used wherever you have ORM RecommendedPlace objects and a session.
# ------------------------------------------------------------------ #

async def enrich_db_places_with_unsplash(
    db: AsyncSession,
    db_places: list[RecommendedPlace],
) -> None:
    """
    Fetches Unsplash images for a list of ORM RecommendedPlace objects,
    updates `image_url` on the ORM object AND issues a DB UPDATE.
    Commit is intentionally left to the caller.

    Usage example:
        await enrich_db_places_with_unsplash(db, saved_places)
        await db.commit()
    """
    # if not getattr(settings, "UNSPLASH_ACCESS_KEY", None):
        # raise 

    async with httpx.AsyncClient() as client:

        async def _enrich_one(place: RecommendedPlace) -> None:
            # query = f"{place.name} {place.city}"
            query = f"{place.name}"
            url = await _fetch_unsplash_photo(client, query)
            if url:
                # Update the in-memory ORM object so callers see the change
                place.image_url = url
                # Persist directly — no need to reload the object
                await db.execute(
                    update(RecommendedPlace)
                    .where(RecommendedPlace.id == place.id)
                    .values(image_url=url)
                )

        await asyncio.gather(*[_enrich_one(p) for p in db_places])