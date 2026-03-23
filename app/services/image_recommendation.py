import asyncio
import logging
from typing import Optional

import httpx
from sqlalchemy import update
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.config import config
from app.models.recommended_place import RecommendedPlace
from app.schemas.recommendation import RecommendedPlaceSchema

logger = logging.getLogger(__name__)

UNSPLASH_API_BASE = "https://api.unsplash.com"


async def _fetch_unsplash_photo(
    client: httpx.AsyncClient,
    query: str,
) -> Optional[str]:
    """Search Unsplash and return the image URL, or None on failure."""
    logger.info("[Unsplash] Fetching photo for query: %r", query)
    try:
        response = await client.get(
            f"{UNSPLASH_API_BASE}/search/photos",
            params={
                "query": query,
                "per_page": 1,
            },
            headers={"Authorization": f"Client-ID {config.UNSPLASH_ACCESS_KEY}"},
            timeout=10.0,
        )
        logger.debug("[Unsplash] Status %s for query: %r", response.status_code, query)
        response.raise_for_status()

        results = response.json().get("results", [])
        if not results:
            logger.warning("[Unsplash] No results for query: %r", query)
            return None

        image_url = results[0]["urls"]["regular"]
        logger.info("[Unsplash] Found image for %r: %s", query, image_url)
        return image_url

    except httpx.HTTPStatusError as exc:
        logger.error("[Unsplash] HTTP %s for query %r: %s", exc.response.status_code, query, exc.response.text)
    except httpx.RequestError as exc:
        logger.error("[Unsplash] Request error for query %r: %s", query, exc)
    except (KeyError, IndexError) as exc:
        logger.error("[Unsplash] Unexpected response shape for query %r: %s", query, exc)

    return None


async def enrich_with_unsplash_images(places: list[RecommendedPlaceSchema]) -> None:
    """Mutates each schema object's image_url in-place. All requests run concurrently."""
    logger.info("[Unsplash] Enriching %d place(s)...", len(places))
    async with httpx.AsyncClient() as client:
        async def _enrich_one(place: RecommendedPlaceSchema) -> None:
            query = place.query_to_search or place.name
            url = await _fetch_unsplash_photo(client, query)
            if url:
                place.image_url = url
                logger.info("[Unsplash] Set image for %r", place.name)
            else:
                logger.warning("[Unsplash] No image for %r, keeping original", place.name)

        await asyncio.gather(*[_enrich_one(p) for p in places])
    logger.info("[Unsplash] Done.")


async def enrich_db_places_with_unsplash(db: AsyncSession, db_places: list[RecommendedPlace]) -> None:
    """Updates image_url in-memory + DB. Commit is left to the caller."""
    logger.info("[Unsplash] Enriching %d DB place(s)...", len(db_places))
    async with httpx.AsyncClient() as client:
        async def _enrich_one(place: RecommendedPlace) -> None:
            query = place.query_to_search or place.name
            url = await _fetch_unsplash_photo(client, query)
            if url:
                place.image_url = url
                await db.execute(
                    update(RecommendedPlace)
                    .where(RecommendedPlace.id == place.id)
                    .values(image_url=url)
                )
                logger.info("[Unsplash] Updated DB image for id=%s %r", place.id, place.name)
            else:
                logger.warning("[Unsplash] No image for id=%s %r, skipping", place.id, place.name)

        await asyncio.gather(*[_enrich_one(p) for p in db_places])
    logger.info("[Unsplash] Done.")