import os
import json
import urllib.request
import urllib.parse
import urllib.error
import base64
from typing import Dict, Any, List, Optional

import recommender

# Verified Retailer Search Link Builders
def get_retailer_search_url(platform: str, title: str) -> str:
    query = urllib.parse.quote_plus(title)
    platform_lower = (platform or "").lower()
    
    if "amazon" in platform_lower:
        return f"https://www.amazon.in/s?k={query}"
    elif "flipkart" in platform_lower:
        return f"https://www.flipkart.com/search?q={query}"
    elif "ikea" in platform_lower:
        return f"https://www.ikea.com/in/en/search/?q={query}"
    elif "pepperfry" in platform_lower:
        return f"https://www.pepperfry.com/site_product/search?q={query}"
    elif "urban ladder" in platform_lower:
        return f"https://www.urbanladder.com/products/search?q={query}"
    elif "swiggy" in platform_lower:
        return f"https://www.swiggy.com/search?query={query}"
    elif "zomato" in platform_lower:
        return f"https://www.zomato.com/search?q={query}"
    elif "oyo" in platform_lower:
        return f"https://www.oyorooms.com/"
    elif "tanishq" in platform_lower:
        return f"https://www.tanishq.co.in/shop/{query}"
    elif "caratlane" in platform_lower:
        return f"https://www.caratlane.com/search/{query}.html"
    elif "giva" in platform_lower:
        return f"https://www.giva.co/search?q={query}"
    elif "kalyan" in platform_lower:
        return f"https://www.kalyanjewellers.net/search.php?q={query}"
    elif "malabar" in platform_lower:
        return f"https://www.malabargoldanddiamonds.com/catalogsearch/result/?q={query}"
    elif "ferns" in platform_lower or "fnp" in platform_lower:
        return f"https://www.fnp.com/search?q={query}"
    elif "bakingo" in platform_lower:
        return f"https://www.bakingo.com/search?q={query}"
    else:
        return f"https://www.google.com/search?q={urllib.parse.quote_plus(f'{platform} {title}')}"

def enrich_items_with_links(items: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
    enriched = []
    for it in items:
        item_copy = dict(it)
        if "url" not in item_copy or not item_copy["url"]:
            item_copy["url"] = get_retailer_search_url(item_copy.get("platform", "Amazon"), item_copy.get("title", ""))
        enriched.append(item_copy)
    return enriched

def get_gemini_api_key() -> Optional[str]:
    return os.environ.get("GEMINI_API_KEY", "").strip() or None

def call_gemini_rest(prompt: str, image_bytes: bytes = None, mime_type: str = "image/jpeg") -> Optional[str]:
    api_key = get_gemini_api_key()
    if not api_key:
        return None

    # Model: Gemini 1.5 Flash
    url = f"https://generativelanguage.googleapis.com/v1beta/models/gemini-1.5-flash:generateContent?key={api_key}"
    
    parts: List[Dict[str, Any]] = [{"text": prompt}]
    if image_bytes:
        b64_data = base64.b64encode(image_bytes).decode('utf-8')
        parts.append({
            "inlineData": {
                "mimeType": mime_type,
                "data": b64_data
            }
        })

    payload = {
        "contents": [{"parts": parts}],
        "generationConfig": {
            "temperature": 0.3,
            "responseMimeType": "application/json"
        }
    }

    try:
        req = urllib.request.Request(
            url,
            data=json.dumps(payload).encode('utf-8'),
            headers={"Content-Type": "application/json"},
            method="POST"
        )
        with urllib.request.urlopen(req, timeout=12) as response:
            res_data = json.loads(response.read().decode('utf-8'))
            candidates = res_data.get("candidates", [])
            if candidates:
                content = candidates[0].get("content", {})
                parts = content.get("parts", [])
                if parts and "text" in parts[0]:
                    return parts[0]["text"]
    except Exception as e:
        # Fallback to local catalog
        print(f"[Gemini API Notice] Falling back to catalog engine: {e}")
        return None

    return None

# ==================== VALIDATE GEMINI CONNECTION ====================

def validate_gemini_connection(api_key: Optional[str] = None) -> Dict[str, Any]:
    key = api_key or get_gemini_api_key()
    if not key:
        return {
            "configured": False,
            "connected": False,
            "model": "gemini-1.5-flash",
            "message": "GEMINI_API_KEY is not set in environment. Running with local smart catalog fallback."
        }

    try:
        url = f"https://generativelanguage.googleapis.com/v1beta/models/gemini-1.5-flash:generateContent?key={key}"
        test_payload = {
            "contents": [{"parts": [{"text": "Respond with JSON: {\"status\": \"ok\", \"model\": \"gemini-1.5-flash\"}"}]}],
            "generationConfig": {"temperature": 0.1, "responseMimeType": "application/json"}
        }
        req = urllib.request.Request(
            url,
            data=json.dumps(test_payload).encode('utf-8'),
            headers={"Content-Type": "application/json"},
            method="POST"
        )
        with urllib.request.urlopen(req, timeout=8) as response:
            res_data = json.loads(response.read().decode('utf-8'))
            return {
                "configured": True,
                "connected": True,
                "model": "gemini-1.5-flash",
                "message": "Gemini 1.5 Flash Pro is successfully connected and responding."
            }
    except Exception as e:
        return {
            "configured": True,
            "connected": False,
            "model": "gemini-1.5-flash",
            "message": f"Connection check failed: {str(e)}. Operating in fallback mode."
        }

# ==================== HOME INTERIOR RECOMMENDATIONS ====================

def generate_home_recommendations(data: Dict[str, Any]) -> Dict[str, Any]:
    budget = float(data.get("budget", 50000))
    room_type = data.get("room_type", "Living Room")
    items_req = data.get("items", {})

    prompt = f"""
    You are PocketSmart AI Home Interior Planner.
    User Budget: INR {budget}
    Room Type: {room_type}
    Requested item quantities: {json.dumps(items_req)}
    
    Recommend high quality, budget-conscious products sourced from popular retailers like IKEA, Amazon, Pepperfry, and Urban Ladder.
    Balance functionality, style, and price. Do NOT exceed the budget.
    
    Return STRICT JSON matching this schema:
    {{
      "budget": {budget},
      "estimated_total": <number>,
      "remaining": <number>,
      "status": "Within Budget" or "Exceeded Budget",
      "categories": [
        {{"name": "Furniture", "amount": <number>}},
        {{"name": "Lighting", "amount": <number>}},
        {{"name": "Storage", "amount": <number>}},
        {{"name": "Decor", "amount": <number>}}
      ],
      "items": [
        {{
          "title": "<Product Name>",
          "category": "Furniture|Lighting|Storage|Decor",
          "platform": "IKEA|Amazon|Pepperfry|Urban Ladder",
          "price": <number>,
          "image": "<valid unsplash image URL>",
          "status": "Within Budget",
          "reason": "<one sentence explanation why this item fits the space and budget>"
        }}
      ]
    }}
    """
    
    raw_response = call_gemini_rest(prompt)
    if raw_response:
        try:
            parsed = json.loads(raw_response)
            if "items" in parsed and len(parsed["items"]) > 0:
                parsed["items"] = enrich_items_with_links(parsed["items"])
                parsed["room_type"] = room_type
                return parsed
        except Exception:
            pass

    # Fallback to deterministic catalog engine
    result = recommender.generate_home_recommendations(data)
    result["items"] = enrich_items_with_links(result["items"])
    return result

# ==================== PARTY BUDGET RECOMMENDATIONS ====================

def generate_party_recommendations(data: Dict[str, Any]) -> Dict[str, Any]:
    budget = float(data.get("budget", 30000))
    guest_count = int(data.get("guest_count", 40))
    event_type = data.get("event_type", "Birthday")
    venue = data.get("venue", "Home / Backyard")
    food_pref = data.get("food_pref", "Buffet Dinner")
    decor_pref = data.get("decor_pref", "Balloon Theme")

    prompt = f"""
    You are PocketSmart AI Party Budget Planner.
    User Budget: INR {budget}
    Guest Count: {guest_count}
    Event Type: {event_type}
    Venue: {venue}
    Food Preference: {food_pref}
    Decoration Preference: {decor_pref}
    
    Proportionally allocate budget across catering (Swiggy/Zomato/Local Caterers), custom cake (Ferns N Petals/Bakingo), decor (PartyMania/Amazon), and sound/entertainment.
    Ensure total stays within or close to INR {budget}.
    
    Return STRICT JSON matching this schema:
    {{
      "budget": {budget},
      "estimated_total": <number>,
      "remaining": <number>,
      "status": "Within Budget" or "Exceeded Budget",
      "categories": [
        {{"name": "Catering & Food", "amount": <number>}},
        {{"name": "Cake & Desserts", "amount": <number>}},
        {{"name": "Decorations", "amount": <number>}},
        {{"name": "Audio & Entertainment", "amount": <number>}}
      ],
      "items": [
        {{
          "title": "<Package or Item Title>",
          "category": "Catering & Food|Cake & Desserts|Decorations|Audio & Entertainment",
          "platform": "Swiggy Catering|Zomato Events|Ferns N Petals|Bakingo|Amazon|OYO",
          "price": <number>,
          "image": "<valid unsplash image URL>",
          "status": "Within Budget",
          "reason": "<reason tailored to event type, guest count, and venue>"
        }}
      ]
    }}
    """

    raw_response = call_gemini_rest(prompt)
    if raw_response:
        try:
            parsed = json.loads(raw_response)
            if "items" in parsed and len(parsed["items"]) > 0:
                parsed["items"] = enrich_items_with_links(parsed["items"])
                parsed["event_type"] = event_type
                parsed["guest_count"] = guest_count
                return parsed
        except Exception:
            pass

    # Fallback
    result = recommender.generate_party_recommendations(data)
    result["items"] = enrich_items_with_links(result["items"])
    return result

# ==================== JEWELRY RECOMMENDATIONS (MULTIMODAL) ====================

def generate_jewelry_recommendations(data: Dict[str, Any], outfit_image_bytes: bytes = None, mime_type: str = "image/jpeg") -> Dict[str, Any]:
    budget = float(data.get("budget", 25000))
    occasion = data.get("occasion", "Wedding")
    jewelry_type = data.get("jewelry_type", "All")
    preferred_style = data.get("preferred_style", "Traditional")
    color_pref = data.get("color_pref", "Gold")
    outfit_image_url = data.get("outfit_image", None)

    multimodal_note = "An outfit image is provided. Coordinate necklace, earrings, or bangles with its color palette and styling." if outfit_image_bytes else "No outfit image provided; match based on occasion and style preferences."

    prompt = f"""
    You are PocketSmart AI Jewelry Budget Planner.
    User Budget: INR {budget}
    Occasion: {occasion}
    Category Type: {jewelry_type}
    Preferred Style: {preferred_style}
    Color/Metal Preference: {color_pref}
    {multimodal_note}
    
    Recommend hallmarked, elegant jewelry options from verified brands like Tanishq, CaratLane, Kalyan Jewellers, Malabar Gold, GIVA, and Amazon.
    Ensure total stays within INR {budget}.
    
    Return STRICT JSON matching this schema:
    {{
      "budget": {budget},
      "estimated_total": <number>,
      "remaining": <number>,
      "status": "Within Budget" or "Exceeded Budget",
      "categories": [
        {{"name": "Necklace", "amount": <number>}},
        {{"name": "Earrings", "amount": <number>}},
        {{"name": "Bangles", "amount": <number>}},
        {{"name": "Ring", "amount": <number>}}
      ],
      "items": [
        {{
          "title": "<Jewelry piece title>",
          "category": "Necklace|Earrings|Bangles|Ring",
          "platform": "Tanishq|CaratLane|Kalyan Jewellers|Malabar Gold|GIVA|Amazon",
          "price": <number>,
          "image": "<valid unsplash jewelry URL>",
          "status": "Within Budget",
          "reason": "<reason matching occasion and outfit aesthetics>"
        }}
      ]
    }}
    """

    raw_response = call_gemini_rest(prompt, image_bytes=outfit_image_bytes, mime_type=mime_type)
    if raw_response:
        try:
            parsed = json.loads(raw_response)
            if "items" in parsed and len(parsed["items"]) > 0:
                parsed["items"] = enrich_items_with_links(parsed["items"])
                parsed["occasion"] = occasion
                parsed["preferred_style"] = preferred_style
                parsed["color_pref"] = color_pref
                parsed["outfit_image"] = outfit_image_url
                return parsed
        except Exception:
            pass

    # Fallback
    result = recommender.generate_jewelry_recommendations(data)
    result["items"] = enrich_items_with_links(result["items"])
    return result
