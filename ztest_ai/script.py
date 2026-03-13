import json
import os
from datetime import datetime
import google.generativeai as genai
 


GEMINI_API_KEY = ""

import json
import os
from datetime import datetime
from google import genai
from google.genai import types

# Configuration
MODEL_NAME = 'gemini-3-flash-preview' 

def read_trip_data(filename='test.json'):
    """Read trip information from JSON file"""
    try:
        with open(filename, 'r', encoding='utf-8') as f:
            return json.load(f)
    except FileNotFoundError:
        print(f"Error: {filename} not found")
        return None
    except json.JSONDecodeError as e:
        print(f"Error parsing JSON: {e}")
        return None

def create_prompt(trip_data):
    """Create a detailed prompt for Gemini to recommend places"""
    
    # Calculate trip duration
    from datetime import datetime
    start = datetime.strptime(trip_data['start_date'], '%Y-%m-%d')
    end = datetime.strptime(trip_data['end_date'], '%Y-%m-%d')
    duration = (end - start).days + 1
    
    prompt = f"""
You are an expert travel advisor. Recommend specific places, attractions, restaurants, and activities for travelers based on the following information.

TRIP DETAILS:
- Destination: {trip_data['destination_city']}, {trip_data['destination_country']}
- Dates: {trip_data['start_date']} to {trip_data['end_date']} ({duration} days)
- Budget: ${trip_data['min_budget']:,.0f} - ${trip_data['max_budget']:,.0f}
- Trip Description: {trip_data['description']}
- Planned Activities: {trip_data['planned_activities']}
- Planned Destinations: {trip_data['planned_destinations']}

TRAVELERS:
"""
    
    for user in trip_data['users']:
        prompt += f"""
- {user['name']} ({user['age']} years old, {user['gender']})
  From: {user['from_city']}, {user['from_country']}
  Bio: {user['bio']}
  Languages: {', '.join(user['languages'])}
  Interests: {', '.join(user['interests'])}
  Travel Style: {', '.join(user['travel_styles'])}
"""
    
    # Extract key interests and requirements dynamically
    all_interests = []
    all_styles = []
    for user in trip_data['users']:
        all_interests.extend(user['interests'])
        all_styles.extend(user['travel_styles'])
    
    unique_interests = list(set(all_interests))
    unique_styles = list(set(all_styles))
    
    prompt += f"""

RECOMMENDATION REQUIREMENTS:
1. Recommend specific places in {trip_data['destination_city']}, {trip_data['destination_country']}
2. Focus on interests: {', '.join(unique_interests)}
3. Match the travel style: {', '.join(unique_styles)}
4. Consider the trip description: "{trip_data['description']}"
5. Include places for activities: {trip_data['planned_activities']}
6. Provide realistic costs that fit the budget: ${trip_data['min_budget']:,.0f} - ${trip_data['max_budget']:,.0f}
7. Give actual place names with exact addresses and coordinates
8. Consider seasonal factors for the travel dates ({trip_data['start_date']} to {trip_data['end_date']})

Generate a list of recommended places in the following JSON structure:

{{
  "destination_overview": {{
    "city": "City Name",
    "country": "Country Name",
    "best_time_to_visit": "information about the travel dates",
    "estimated_daily_budget": {{
      "min": <number>,
      "max": <number>,
      "currency": "USD"
    }}
  }},
  "recommended_places": [
    {{
      "id": <number>,
      "name": "Place Name",
        "image_url": "URL of a representative photo of the place (official website, Google Maps, Unsplash, or tourism site)",
      "category": "attraction/restaurant/activity/shopping/entertainment/nature/cultural/nightlife",
      "address": "Full street address",
      "coordinates": {{
        "latitude": <number>,
        "longitude": <number>
      }},
      "estimated_cost": {{
        "amount": <number>,
        "currency": "USD",
        "cost_type": "per_person/entrance_fee/average_meal/free/varies"
      }},
      "description": "Brief description of what makes this place special",
      "best_for": ["interest 1", "interest 2"],
      "opening_hours": "typical hours or 'varies' or '24/7'",
      "recommended_duration": "how long to spend here (e.g., '2-3 hours', '30 minutes', 'half day')",
      "why_recommended": "why this matches the travelers' interests and trip description",
      "tips": ["practical tip 1", "practical tip 2"],
      "best_time_to_visit": "time of day or season recommendation"
    }}
  ],
  "recommendations_by_category": {{
    "must_see_attractions": [
      {{
        "name": "Place name",
        "estimated_cost": <number>,
        "priority": "high/medium/low"
      }}
    ],
    "restaurants": [
      {{
        "name": "Restaurant name",
        "cuisine_type": "cuisine",
        "price_range": "budget/moderate/expensive/luxury",
        "estimated_cost": <number>,
        "specialty_dish": "famous dish"
      }}
    ],
    "activities": [
      {{
        "name": "Activity name",
        "activity_type": "type",
        "estimated_cost": <number>,
        "booking_required": true/false
      }}
    ],
    "hidden_gems": [
      {{
        "name": "Place name",
        "why_special": "what makes it unique",
        "estimated_cost": <number>
      }}
    ]
  }},
  "practical_information": {{
    "getting_around": "transportation tips",
    "local_currency": "currency info",
    "language_tips": ["useful phrase 1", "useful phrase 2"],
    "cultural_notes": ["cultural tip 1", "cultural tip 2"]
  }}
}}

IMPORTANT:
- Include 20-30 specific places with exact names and addresses
- All costs must be realistic for {trip_data['destination_city']}
- Use actual coordinates (latitude/longitude)
- Match recommendations to the travelers' interests: {', '.join(unique_interests)}
- Consider the budget range: ${trip_data['min_budget']:,.0f} - ${trip_data['max_budget']:,.0f}
- Prioritize places mentioned in the trip description: "{trip_data['description']}"
- Include a good mix of categories (attractions, restaurants, activities, etc.)

Make recommendations SPECIFIC to {trip_data['destination_city']}, {trip_data['destination_country']} with real place names and addresses.
"""
    
    return prompt

def generate_place_recommendations(trip_data):
    """Send data to Gemini and get place recommendations"""
    
    if not GEMINI_API_KEY:
        print("Error: GEMINI_API_KEY environment variable not set")
        print("Set it using: export GEMINI_API_KEY='your-api-key'")
        return None
    
    try:
        # Configure Gemini with new SDK
        client = genai.Client(api_key=GEMINI_API_KEY)
        
        # Create prompt
        prompt = create_prompt(trip_data)
        
        print("Sending request to Gemini API...")
        print(f"Destination: {trip_data['destination_city']}, {trip_data['destination_country']}")
        print(f"Dates: {trip_data['start_date']} to {trip_data['end_date']}")
        print(f"Travelers: {len(trip_data['users'])}")
        print("\nGenerating place recommendations... (this may take 30-60 seconds)\n")
        
        # Generate content using new SDK
        response = client.models.generate_content(
            model=MODEL_NAME,
            contents=prompt
        )
        
        # Extract text from response
        response_text = response.text
        
        # Try to extract JSON from markdown code blocks if present
        if '```json' in response_text:
            start = response_text.find('```json') + 7
            end = response_text.find('```', start)
            response_text = response_text[start:end].strip()
        elif '```' in response_text:
            start = response_text.find('```') + 3
            end = response_text.find('```', start)
            response_text = response_text[start:end].strip()
        
        # Parse JSON
        plan = json.loads(response_text)
        
        return plan
        
    except Exception as e:
        print(f"Error generating recommendations: {e}")
        return None

def save_recommendations(recommendations, output_filename=None):
    """Save the generated recommendations to a JSON file"""
    
    if recommendations is None:
        print("No recommendations to save")
        return False
    
    if output_filename is None:
        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
        output_filename = f'place_recommendations_{timestamp}.json'
    
    try:
        with open(output_filename, 'w', encoding='utf-8') as f:
            json.dump(recommendations, f, indent=2, ensure_ascii=False)
        
        print(f"✓ Recommendations saved successfully to: {output_filename}")
        
        # Print summary
        if 'destination_overview' in recommendations:
            overview = recommendations['destination_overview']
            print(f"\n📋 DESTINATION:")
            print(f"   {overview.get('city', 'N/A')}, {overview.get('country', 'N/A')}")
        
        if 'recommended_places' in recommendations:
            print(f"   Total Places Recommended: {len(recommendations['recommended_places'])}")
            
            # Count by category
            categories = {}
            for place in recommendations['recommended_places']:
                cat = place.get('category', 'other')
                categories[cat] = categories.get(cat, 0) + 1
            
            print(f"   Categories:")
            for cat, count in categories.items():
                print(f"      - {cat.title()}: {count}")
        
        return True
        
    except Exception as e:
        print(f"Error saving recommendations: {e}")
        return False

def main():
    """Main execution function"""
    
    print("=" * 60)
    print("📍 AI PLACE RECOMMENDER - DISCOVER YOUR DESTINATION")
    print("=" * 60)
    print()
    
    # Read trip data
    print("📖 Reading trip data from test.json...")
    trip_data = read_trip_data('test.json')
    
    if trip_data is None:
        return
    
    print("✓ Trip data loaded successfully\n")
    
    # Generate place recommendations
    recommendations = generate_place_recommendations(trip_data)
    
    if recommendations is None:
        return
    
    print("✓ Recommendations generated successfully\n")
    
    # Save recommendations
    save_recommendations(recommendations)
    
    print("\n" + "=" * 60)
    print("✨ Process completed!")
    print("=" * 60)

if __name__ == "__main__":
    main()