import json

from fastapi import HTTPException, status
from google.generativeai import GenerativeModel, configure
from google.generativeai.types import GenerationConfig
from pydantic import ValidationError as PydanticValidationError

from app.core.config import config
from app.schemas.recommendation import (GenerateRecommendationsRequest,
                                        PlaceRecommendationsSchema)


def create_prompt(trip_data: GenerateRecommendationsRequest) -> str:
    duration = (trip_data.end_date - trip_data.start_date).days + 1

    users = "\n".join(
        (
            f"- {user.name} ({user.age}, {user.gender}) from {user.from_city}, {user.from_country}\n"
            f"  Bio: {user.bio}\n"
            f"  Languages: {', '.join(user.languages)}\n"
            f"  Interests: {', '.join(user.interests)}\n"
            f"  Travel Style: {', '.join(user.travel_styles)}"
        )
        for user in trip_data.users
    )

    interests = sorted(
        {interest for user in trip_data.users for interest in user.interests}
    )
    styles = sorted({style for user in trip_data.users for style in user.travel_styles})

    return f"""
You are an expert travel recommendation AI.
Recommend 20-30 real places in {trip_data.destination_city}, {trip_data.destination_country}.

Trip: {trip_data.start_date} to {trip_data.end_date} ({duration} days)
Budget: ${trip_data.min_budget:,.0f} - ${trip_data.max_budget:,.0f}
Description: {trip_data.description}
Planned Activities: {trip_data.planned_activities}
Planned Destinations: {trip_data.planned_destinations}
Transportation Preference: {trip_data.transportation_preference}
Accommodation Preference: {trip_data.accommodation_preference}

Travelers:
{users}

Rules:
1. Match interests: {', '.join(interests)}
2. Match travel style: {', '.join(styles)}
3. Use real places with accurate coordinates and full addresses.
4. image_url must be a direct Google Maps / Google Place photo URL.
5. If no valid Google Maps photo exists, skip that place.
6. For every place include opening_hours (monday-sunday, notes optional).
7. For every place include contact_information (phone, website, email; null allowed if unavailable).
8. For every place include age_range with min_age and max_age.
9. For every place include audience using only: kids, teens, adults, seniors, family, couples, friends, solo_travelers.
10. Return JSON only.
11. Query to search place from unsplash this is image API, I must search it with very clear word, also if youdon't have idea give query to search similar place.
""".strip()


def _strip_json_fences(text: str) -> str:
    if text.startswith("```"):
        lines = text.splitlines()
        if lines and lines[0].startswith("```"):
            lines = lines[1:]
        if lines and lines[-1].strip() == "```":
            lines = lines[:-1]
        return "\n".join(lines).strip()
    return text


def _validate_recommendations(raw_text: str) -> PlaceRecommendationsSchema:
    cleaned_text = _strip_json_fences(raw_text)

    try:
        parsed_payload = json.loads(cleaned_text)
    except json.JSONDecodeError as exc:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Gemini did not return valid JSON",
        ) from exc

    try:
        return PlaceRecommendationsSchema.model_validate(parsed_payload)
    except PydanticValidationError as exc:
        # logger.warning("Gemini response failed schema validation", errors=exc.errors())
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Gemini response does not match the expected schema",
        ) from exc


async def generate_recommendations(
    trip_data: GenerateRecommendationsRequest,
) -> PlaceRecommendationsSchema:
    if not config.GEMINI_API_KEY:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="GEMINI_API_KEY is not configured",
        )

    configure(api_key=config.GEMINI_API_KEY)
    model = GenerativeModel(
        model_name=config.GEMINI_MODEL,
        generation_config=GenerationConfig(
            response_mime_type="application/json",
            response_schema=PlaceRecommendationsSchema,
        ),
    )
    print("We configured Gemini model with name:", config.GEMINI_MODEL)

    prompt = create_prompt(trip_data)

    try:
        print("We sending request to Gemini with prompt:")
        response = await model.generate_content_async(
            prompt,
            request_options={"timeout": config.GEMINI_TIMEOUT_SECONDS},
        )
    except Exception as e:
        print("Error while calling Gemini API:", str(e))
        raise HTTPException(
            status_code=status.HTTP_502_BAD_GATEWAY,
            detail="Error while calling Gemini API",
        )
    if not response.candidates:
        print("Gemini returned no candidates")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Gemini returned no candidates",
        )

    raw_text = response.text.strip()
    if not raw_text:
        print("Gemini returned an empty response")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Gemini returned an empty response",
        )

    result = _validate_recommendations(raw_text)

    return result
