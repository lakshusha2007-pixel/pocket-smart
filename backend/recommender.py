import os
import json
import random
from typing import Dict, Any, List

# Product Catalogs with realistic products, platforms, and prices
CATALOG_HOME = [
    # Furniture
    {"title": "Nordic 3-Seater Fabric Sofa", "category": "Furniture", "room": ["Living Room"], "price": 24999, "platform": "Pepperfry", "image": "https://images.unsplash.com/photo-1555041469-a586c61ea9bc?w=600&auto=format&fit=crop&q=80", "reason": "Durable solid-wood frame with high-density comfort foam and stain-resistant fabric."},
    {"title": "Compact 2-Seater Loveseat Sofa", "category": "Furniture", "room": ["Living Room", "Home Office"], "price": 14999, "platform": "Urban Ladder", "image": "https://images.unsplash.com/photo-1493663284031-b7e3aefcae8e?w=600&auto=format&fit=crop&q=80", "reason": "Space-saving modern sofa ideal for compact living rooms or reading lounges."},
    {"title": "Sheesham Solid Wood 4-Seater Dining Table Set", "category": "Furniture", "room": ["Dining Room", "Living Room"], "price": 18499, "platform": "Pepperfry", "image": "https://images.unsplash.com/photo-1617806118233-18e1de247200?w=600&auto=format&fit=crop&q=80", "reason": "Premium honey finish solid Sheesham dining set with four ergonomic cushioned chairs."},
    {"title": "Queen Size Upholstered Platform Bed with Storage", "category": "Furniture", "room": ["Bedroom"], "price": 21999, "platform": "IKEA", "image": "https://images.unsplash.com/photo-1505693416388-ac5ce068fe85?w=600&auto=format&fit=crop&q=80", "reason": "Sturdy engineered wood bed frame with hydraulic storage lift and padded headrest."},
    {"title": "Ergonomic High-Back Executive Office Chair", "category": "Furniture", "room": ["Home Office", "Bedroom"], "price": 8999, "platform": "Amazon", "image": "https://images.unsplash.com/photo-1580481077195-c22ae2499b9a?w=600&auto=format&fit=crop&q=80", "reason": "Breathable mesh back with adjustable lumbar support, 3D armrests, and synchro-tilt."},
    {"title": "Minimalist Solid Oak Study & Work Desk", "category": "Furniture", "room": ["Home Office", "Bedroom"], "price": 7499, "platform": "IKEA", "image": "https://images.unsplash.com/photo-1518455027359-f3f8164ba6bd?w=600&auto=format&fit=crop&q=80", "reason": "Cable management groove and dual drawers for neat workspace organization."},

    # Lighting
    {"title": "Modern Matte Black Pendant Light (Pack of 2)", "category": "Lighting", "room": ["Living Room", "Dining Room", "Kitchen"], "price": 2499, "platform": "IKEA", "image": "https://images.unsplash.com/photo-1513506003901-1e6a229e2d15?w=600&auto=format&fit=crop&q=80", "reason": "Sleek industrial aluminum drop lights delivering warm ambient living room illumination."},
    {"title": "AeroPlus 1200mm Silent BLDC Ceiling Fan", "category": "Lighting", "room": ["Living Room", "Bedroom", "Dining Room"], "price": 3299, "platform": "Amazon", "image": "https://images.unsplash.com/photo-1585338107529-13afc5f02586?w=600&auto=format&fit=crop&q=80", "reason": "5-star energy saving BLDC copper motor with RF remote control and timer function."},
    {"title": "Nordic Standing Floor Lamp with Linen Shade", "category": "Lighting", "room": ["Living Room", "Bedroom", "Home Office"], "price": 3199, "platform": "Urban Ladder", "image": "https://images.unsplash.com/photo-1507473885765-e6ed057f782c?w=600&auto=format&fit=crop&q=80", "reason": "Natural tripod wooden lamp that creates a cozy corner mood with soft diffused glow."},
    {"title": "Dimmable Smart LED Ceiling Downlight (Pack of 4)", "category": "Lighting", "room": ["Living Room", "Bedroom", "Kitchen"], "price": 2899, "platform": "Amazon", "image": "https://images.unsplash.com/photo-1524484485831-a92ffc0de03f?w=600&auto=format&fit=crop&q=80", "reason": "Tunable white and 16 million colors with smartphone and voice control compatibility."},

    # Storage
    {"title": "Modular 3-Door Engineered Wood Wardrobe", "category": "Storage", "room": ["Bedroom"], "price": 16499, "platform": "Pepperfry", "image": "https://images.unsplash.com/photo-1558997519-83ea9252def8?w=600&auto=format&fit=crop&q=80", "reason": "Spacious interior with full-length hanging rod, 5 shelves, and integrated dressing mirror."},
    {"title": "5-Tier Open Display Bookshelf & Organizer", "category": "Storage", "room": ["Living Room", "Home Office"], "price": 4999, "platform": "IKEA", "image": "https://images.unsplash.com/photo-1594980596870-8aa52a78d8cd?w=600&auto=format&fit=crop&q=80", "reason": "Geometric tiered display for books, indoor plants, and collectibles with anti-tip anchor."},
    {"title": "Engineered Wood Floating TV Entertainment Unit", "category": "Storage", "room": ["Living Room"], "price": 6299, "platform": "Urban Ladder", "image": "https://images.unsplash.com/photo-1600585154340-be6161a56a0c?w=600&auto=format&fit=crop&q=80", "reason": "Wall-mounted console accommodating up to 55-inch TVs with hidden wire routing."},

    # Decor & Accents
    {"title": "Bohemian Hand-Woven Floor Rug (5x7 Ft)", "category": "Decor", "room": ["Living Room", "Bedroom"], "price": 4499, "platform": "Urban Ladder", "image": "https://images.unsplash.com/photo-1600121848594-d8644e57abab?w=600&auto=format&fit=crop&q=80", "reason": "Plush low-pile textured rug that ties furniture together and softens room acoustics."},
    {"title": "Textured Blackout Eyelet Curtains (Set of 2)", "category": "Decor", "room": ["Living Room", "Bedroom"], "price": 1899, "platform": "Amazon", "image": "https://images.unsplash.com/photo-1513694203232-719a280e022f?w=600&auto=format&fit=crop&q=80", "reason": "Thermal insulated 90% blackout curtains with heavy linen drape and silver eyelets."},
    {"title": "Abstract Geometric Canvas Wall Art (Set of 3)", "category": "Decor", "room": ["Living Room", "Dining Room", "Home Office"], "price": 2499, "platform": "Pepperfry", "image": "https://images.unsplash.com/photo-1579783900882-c0d3dad7b119?w=600&auto=format&fit=crop&q=80", "reason": "Framed gallery wall art on museum-grade canvas for instant visual depth."}
]

CATALOG_PARTY = [
    # Catering
    {"title": "Gourmet Live Multi-Cuisine Buffet (Per Head)", "category": "Catering", "price_per_guest": 380, "platform": "Swiggy Catering", "image": "https://images.unsplash.com/photo-1555244162-803834f70033?w=600&auto=format&fit=crop&q=80", "reason": "Comprehensive menu: 3 starters, 4 mains, assorted breads, rice, and hot gulab jamun."},
    {"title": "Finger Food & Cocktail Canapés Platter Service", "category": "Catering", "price_per_guest": 250, "platform": "Zomato Events", "image": "https://images.unsplash.com/photo-1541544741938-0af808871cc0?w=600&auto=format&fit=crop&q=80", "reason": "Bite-sized sliders, skewers, spring rolls, and dip platters perfect for casual mingling."},
    {"title": "Traditional Royal Thali / Banana Leaf Feast", "category": "Catering", "price_per_guest": 320, "platform": "Local Caterers", "image": "https://images.unsplash.com/photo-1610057099443-fde8c4d50f91?w=600&auto=format&fit=crop&q=80", "reason": "Authentic regional preparations served with live service staff and clean disposable cutlery."},

    # Cake & Bakery
    {"title": "Artisan Layered Truffle Celebration Cake (2 Kg)", "category": "Cake & Desserts", "fixed_price": 2499, "platform": "Ferns N Petals", "image": "https://images.unsplash.com/photo-1578985545062-69928b1d9587?w=600&auto=format&fit=crop&q=80", "reason": "Rich Belgian dark chocolate ganache cake with custom name piping and fresh berries."},
    {"title": "Theme Designer Fondant Specialty Cake (3 Kg)", "category": "Cake & Desserts", "fixed_price": 4200, "platform": "Bakingo", "image": "https://images.unsplash.com/photo-1535141192574-5d4897c13136?w=600&auto=format&fit=crop&q=80", "reason": "Customized character/anniversary tiered centerpiece cake tailored to event palette."},

    # Decor
    {"title": "Organic Pastel Balloon Archway & Welcome Board", "category": "Decorations", "fixed_price": 4500, "platform": "PartyMania", "image": "https://images.unsplash.com/photo-1530103862676-de8c9debad1d?w=600&auto=format&fit=crop&q=80", "reason": "120-balloon organic double-stuffed arch with personalized acrylic welcome easel."},
    {"title": "Exotic Fresh Floral Backdrop & Stage Styling", "category": "Decorations", "fixed_price": 8500, "platform": "Ferns N Petals", "image": "https://images.unsplash.com/photo-1519225424987-a2f02672bf65?w=600&auto=format&fit=crop&q=80", "reason": "Fresh orchids, baby's breath, and marigold draping with warm spotlight stage highlights."},
    {"title": "Warm Fairy Light Canopy & Paper Lantern Cluster", "category": "Decorations", "fixed_price": 2800, "platform": "Amazon Events", "image": "https://images.unsplash.com/photo-1514525253161-7a46d19cd819?w=600&auto=format&fit=crop&q=80", "reason": "100-meter weatherproof fairy lights with paper lantern globes for ambient backyard evenings."},

    # Audio & Entertainment
    {"title": "JBL PartyBox High-Power Bluetooth PA Speaker", "category": "Audio & Lights", "fixed_price": 2800, "platform": "Amazon", "image": "https://images.unsplash.com/photo-1545454675-3531b543be5d?w=600&auto=format&fit=crop&q=80", "reason": "Crisp acoustic output with dual wireless mic receiver for speeches and dance music."},
    {"title": "Compact DJ Sound & Dancefloor Strobe Setup", "category": "Audio & Lights", "fixed_price": 6000, "platform": "Local AV Hire", "image": "https://images.unsplash.com/photo-1470225620780-dba8ba36b745?w=600&auto=format&fit=crop&q=80", "reason": "Professional audio technician setup with 2 top speakers, sub, and sync party lights."}
]

CATALOG_JEWELRY = [
    # Necklaces
    {"title": "22K Yellow Gold Heritage Temple Choker", "category": "Necklace", "style": "Temple", "occasion": ["Wedding", "Festival"], "price": 48500, "platform": "Tanishq", "image": "https://images.unsplash.com/photo-1599643478518-a784e5dc4c8f?w=600&auto=format&fit=crop&q=80", "reason": "Intricate Lakshmi and peacock motif handcrafted in hallmark 22K gold with antique polish."},
    {"title": "Kundan Polki Choker with Emerald Droplets", "category": "Necklace", "style": "Kundan", "occasion": ["Wedding", "Reception", "Party"], "price": 28999, "platform": "Kalyan Jewellers", "image": "https://images.unsplash.com/photo-1535632066927-ab7c9ab60908?w=600&auto=format&fit=crop&q=80", "reason": "Hand-set uncut polki stones layered with natural green jade beads and adjustable thread."},
    {"title": "18K Rose Gold Minimalist Diamond Pendant", "category": "Necklace", "style": "Minimalist", "occasion": ["Daily Wear", "Party", "Reception"], "price": 14500, "platform": "CaratLane", "image": "https://images.unsplash.com/photo-1515562141207-7a88fb7ce338?w=600&auto=format&fit=crop&q=80", "reason": "Delicate geometric rose gold halo setting holding a conflict-free certified solitaire diamond."},
    {"title": "Oxidized 925 Sterling Silver Statement Collar", "category": "Necklace", "style": "Modern", "occasion": ["Daily Wear", "Party", "Festival"], "price": 4899, "platform": "GIVA", "image": "https://images.unsplash.com/photo-1611591475819-79b8b730ab8c?w=600&auto=format&fit=crop&q=80", "reason": "Authentic hallmarked 925 silver with tribal etching; versatile with western and ethnic attire."},

    # Earrings
    {"title": "22K Gold Antique Floral Jhumkas with Pearls", "category": "Earrings", "style": "Traditional", "occasion": ["Wedding", "Festival", "Reception"], "price": 22400, "platform": "Malabar Gold", "image": "https://images.unsplash.com/photo-1630019852942-f89202989a59?w=600&auto=format&fit=crop&q=80", "reason": "Classic bell jhumka with delicate seed pearl tassels and comfortable screw-back clasp."},
    {"title": "Swarovski Crystal Pavé Drop Earrings", "category": "Earrings", "style": "Modern", "occasion": ["Party", "Reception"], "price": 6499, "platform": "CaratLane", "image": "https://images.unsplash.com/photo-1535632787350-4e68ef0ac584?w=600&auto=format&fit=crop&q=80", "reason": "Radiant teardrop crystals reflecting prism highlights, lightweight for all-evening comfort."},
    {"title": "Solitaire Moissanite Studs in 14K White Gold", "category": "Earrings", "style": "Minimalist", "occasion": ["Daily Wear", "Party"], "price": 8999, "platform": "GIVA", "image": "https://images.unsplash.com/photo-1620656798579-1984d9e87dfa?w=600&auto=format&fit=crop&q=80", "reason": "Timeless 1-carat brilliant cut four-prong studs offering maximum sparkle with everyday durability."},

    # Bangles & Bracelets
    {"title": "Pair of Meenakari Filigree Gold Bangles", "category": "Bangles", "style": "Traditional", "occasion": ["Wedding", "Festival"], "price": 34500, "platform": "Tanishq", "image": "https://images.unsplash.com/photo-1601121141461-9d6647bca1ed?w=600&auto=format&fit=crop&q=80", "reason": "Exquisite hand-enameled red and green floral meenakari detailing over solid 22K gold."},
    {"title": "Rose Gold Adjustable Charm Tennis Bracelet", "category": "Bangles", "style": "Modern", "occasion": ["Party", "Daily Wear", "Reception"], "price": 9200, "platform": "CaratLane", "image": "https://images.unsplash.com/photo-1598560917505-59a3ad559071?w=600&auto=format&fit=crop&q=80", "reason": "Dainty rose gold bezel line bracelet with lobster clasp and extended sizing chain."},

    # Rings
    {"title": "Classic Princess Cut Solitaire Ring", "category": "Ring", "style": "Modern", "occasion": ["Wedding", "Reception", "Party"], "price": 18200, "platform": "CaratLane", "image": "https://images.unsplash.com/photo-1605100804763-247f67b3557e?w=600&auto=format&fit=crop&q=80", "reason": "Clean contemporary knife-edge band accentuating an eye-clean certified diamond."},
    {"title": "Vintage Royal Kundan Cocktail Statement Ring", "category": "Ring", "style": "Kundan", "occasion": ["Wedding", "Reception", "Festival"], "price": 7999, "platform": "Kalyan Jewellers", "image": "https://images.unsplash.com/photo-1573408301185-9146fe634ad0?w=600&auto=format&fit=crop&q=80", "reason": "Oversized flower motif set with uncut stones and adjustable shank for universal fit."}
]


def generate_home_recommendations(data: Dict[str, Any]) -> Dict[str, Any]:
    budget = float(data.get("budget", 50000))
    room_type = data.get("room_type", "Living Room")
    items_requested = data.get("items", {})

    # Categorize items into priorities
    # Allocate approximate budget proportions
    # Filter catalog items for this room type
    selected_items = []
    current_cost = 0

    # Ensure we include requested items
    for item_key, count in items_requested.items():
        if count <= 0:
            continue
        
        # Match with catalog
        cat_matches = [
            prod for prod in CATALOG_HOME 
            if room_type in prod["room"] and (
                (item_key in ["lights", "ceiling_fans"] and prod["category"] == "Lighting") or
                (item_key in ["sofa", "dining_table"] and prod["category"] == "Furniture") or
                (item_key in ["storage"] and prod["category"] == "Storage") or
                (item_key in ["decorations"] and prod["category"] == "Decor")
            )
        ]

        if not cat_matches:
            cat_matches = [prod for prod in CATALOG_HOME if prod["category"] == "Lighting" or prod["category"] == "Decor"]

        for _ in range(min(count, 3)): # cap to reasonable items
            available = [p for p in cat_matches if p not in selected_items]
            if not available:
                break
            
            # Pick product that fits remaining budget reasonably
            best_fit = available[0]
            for p in available:
                if current_cost + p["price"] <= budget:
                    best_fit = p
                    break
            
            # Clone and calculate status
            item_copy = dict(best_fit)
            is_within = (current_cost + item_copy["price"] <= budget * 1.05)
            item_copy["status"] = "Within Budget" if is_within else "Slightly Over Budget"
            selected_items.append(item_copy)
            current_cost += item_copy["price"]

    # If user selected nothing or selected items didn't fill budget enough, add default room essentials
    if len(selected_items) < 3:
        for p in CATALOG_HOME:
            if room_type in p["room"] and p not in selected_items:
                if current_cost + p["price"] <= budget:
                    item_copy = dict(p)
                    item_copy["status"] = "Within Budget"
                    selected_items.append(item_copy)
                    current_cost += p["price"]
                if len(selected_items) >= 4:
                    break

    # Calculate categories
    cat_summary = {}
    for item in selected_items:
        c = item["category"]
        cat_summary[c] = cat_summary.get(c, 0) + item["price"]

    categories = [{"name": k, "amount": v} for k, v in cat_summary.items()]
    remaining = max(0, budget - current_cost)

    return {
        "budget": budget,
        "estimated_total": current_cost,
        "remaining": remaining,
        "status": "Within Budget" if current_cost <= budget else "Exceeded Budget",
        "categories": categories,
        "items": selected_items,
        "room_type": room_type
    }


def generate_party_recommendations(data: Dict[str, Any]) -> Dict[str, Any]:
    budget = float(data.get("budget", 30000))
    guest_count = int(data.get("guest_count", 40))
    event_type = data.get("event_type", "Birthday")
    venue = data.get("venue", "Home / Lawn")
    food_pref = data.get("food_pref", "Buffet")
    decor_pref = data.get("decor_pref", "Balloon & Pastel")

    selected_items = []
    current_cost = 0

    # 1. Food calculation
    food_choice = CATALOG_PARTY[0] # Default gourmet buffet
    if "Finger" in food_pref or "Cocktail" in food_pref:
        food_choice = CATALOG_PARTY[1]
    elif "Thali" in food_pref or "Traditional" in food_pref:
        food_choice = CATALOG_PARTY[2]

    catering_cost = food_choice["price_per_guest"] * guest_count
    selected_items.append({
        "title": f"{food_choice['title']} ({guest_count} Guests)",
        "category": "Catering & Food",
        "platform": food_choice["platform"],
        "price": catering_cost,
        "image": food_choice["image"],
        "status": "Within Budget" if catering_cost < budget * 0.7 else "Major Expense",
        "reason": f"Allocated for {guest_count} guests with live service setup according to '{food_pref}' selection."
    })
    current_cost += catering_cost

    # 2. Cake
    cake_choice = CATALOG_PARTY[3] if budget < 35000 else CATALOG_PARTY[4]
    selected_items.append({
        "title": cake_choice["title"],
        "category": "Cake & Desserts",
        "platform": cake_choice["platform"],
        "price": cake_choice["fixed_price"],
        "image": cake_choice["image"],
        "status": "Within Budget",
        "reason": f"Specialty confection crafted for {event_type} occasion."
    })
    current_cost += cake_choice["fixed_price"]

    # 3. Decor
    decor_choice = CATALOG_PARTY[5] # Balloon
    if "Floral" in decor_pref or budget > 40000:
        decor_choice = CATALOG_PARTY[6]
    elif "Fairy" in decor_pref or "Minimal" in decor_pref:
        decor_choice = CATALOG_PARTY[7]
        
    selected_items.append({
        "title": decor_choice["title"],
        "category": "Decorations",
        "platform": decor_choice["platform"],
        "price": decor_choice["fixed_price"],
        "image": decor_choice["image"],
        "status": "Within Budget",
        "reason": f"Custom backdrop and ambiance styled for {venue} setting."
    })
    current_cost += decor_choice["fixed_price"]

    # 4. Audio / Entertainment
    audio_choice = CATALOG_PARTY[8] if budget < 35000 else CATALOG_PARTY[9]
    selected_items.append({
        "title": audio_choice["title"],
        "category": "Audio & Entertainment",
        "platform": audio_choice["platform"],
        "price": audio_choice["fixed_price"],
        "image": audio_choice["image"],
        "status": "Within Budget",
        "reason": "Complete sound coverage for music, announcements, and party flow."
    })
    current_cost += audio_choice["fixed_price"]

    cat_summary = {}
    for item in selected_items:
        c = item["category"]
        cat_summary[c] = cat_summary.get(c, 0) + item["price"]

    categories = [{"name": k, "amount": v} for k, v in cat_summary.items()]
    remaining = max(0, budget - current_cost)

    return {
        "budget": budget,
        "estimated_total": current_cost,
        "remaining": remaining,
        "status": "Within Budget" if current_cost <= budget else "Exceeded Budget",
        "categories": categories,
        "items": selected_items,
        "event_type": event_type,
        "guest_count": guest_count
    }


def generate_jewelry_recommendations(data: Dict[str, Any]) -> Dict[str, Any]:
    budget = float(data.get("budget", 25000))
    occasion = data.get("occasion", "Wedding")
    jewelry_type = data.get("jewelry_type", "All")
    preferred_style = data.get("preferred_style", "Traditional")
    color_pref = data.get("color_pref", "Gold")
    outfit_image = data.get("outfit_image", None)

    # Filter by budget, occasion, style
    selected_items = []
    current_cost = 0

    # Categorize pool
    pool = CATALOG_JEWELRY.copy()
    
    # Prioritize items matching style or occasion
    pool.sort(key=lambda x: (
        1 if x["style"] == preferred_style else 0,
        1 if occasion in x["occasion"] else 0,
        -abs(budget - x["price"])
    ), reverse=True)

    for item in pool:
        if jewelry_type != "All" and item["category"].lower() != jewelry_type.lower():
            continue
            
        if current_cost + item["price"] <= budget * 1.05 or len(selected_items) < 2:
            item_copy = dict(item)
            item_copy["status"] = "Within Budget" if item["price"] <= budget else "Premium Choice"
            if outfit_image:
                item_copy["reason"] += " Complements the tones detected in your uploaded outfit."
            selected_items.append(item_copy)
            current_cost += item["price"]
            
        if len(selected_items) >= 4:
            break

    # If user budget is larger and few items picked, add complimentary jewelry pieces
    if current_cost < budget * 0.7:
        for item in pool:
            if item not in selected_items and current_cost + item["price"] <= budget:
                item_copy = dict(item)
                item_copy["status"] = "Within Budget"
                selected_items.append(item_copy)
                current_cost += item["price"]
                if len(selected_items) >= 4:
                    break

    cat_summary = {}
    for item in selected_items:
        c = item["category"]
        cat_summary[c] = cat_summary.get(c, 0) + item["price"]

    categories = [{"name": k, "amount": v} for k, v in cat_summary.items()]
    remaining = max(0, budget - current_cost)

    return {
        "budget": budget,
        "estimated_total": current_cost,
        "remaining": remaining,
        "status": "Within Budget" if current_cost <= budget else "Exceeded Budget",
        "categories": categories,
        "items": selected_items,
        "occasion": occasion,
        "preferred_style": preferred_style,
        "color_pref": color_pref,
        "outfit_image": outfit_image
    }
