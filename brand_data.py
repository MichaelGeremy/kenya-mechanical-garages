"""
brand_data.py
Kenyan Automotive Market Intelligence & Brand Spare Parts Matrix.
Provides domain metrics, parts availability indices, maintenance cost tiers,
mechanic familiarity scores, and spare parts pricing baskets for Kenya.
"""

BRANDS_DATA = {
    "Toyota": {
        "brand": "Toyota",
        "tagline": "The Default Kenyan Currency on Wheels",
        "origin": "Japan",
        "market_share_est": "48%",
        "parts_availability_index": 99,
        "mechanic_familiarity": 98,
        "upcountry_reliability": 99,
        "cost_tier": "$ (Budget)",
        "cost_multiplier": 1.0,
        "theft_risk": "High",
        "theft_risk_note": "Side mirrors, headlights, catalytic converters are top street targets in Nairobi.",
        "kirinyaga_rd_support": "Every shop stocks Toyota parts (OEM & 555/Taiwan aftermarket).",
        "recommended_verdict": "A+ (Safest Buy for First-Time Owners)",
        "popular_models": ["Premio", "Fielder", "Axio", "Vitz", "Probox", "Prado TX", "Hilux", "Land Cruiser"],
        "recommended_engines": "1NZ-FE (1.5L), 2ZR-FAE (1.8L), 2TR-FE (2.7L), 1GD/2GD (Diesel)",
        "mechanic_secrets": "You can break down anywhere from Lodwar to Voi and find both a mechanic and parts within 2 hours. High initial purchase price ('Toyota tax') is offset by instant resale value.",
        "basket_prices_kes": {
            "Oil & Air Filter Set": 2500,
            "Front Brake Pads": 3500,
            "Front Shock Absorber": 7500,
            "Side Mirror Assembly": 6000,
            "Iridium Plugs (Set of 4)": 4800,
            "Front Bumper Cover": 9000,
        },
    },
    "Mazda": {
        "brand": "Mazda",
        "tagline": "The Modern Kenyan Favorite: Style & SkyActiv Dynamics",
        "origin": "Japan",
        "market_share_est": "14%",
        "parts_availability_index": 82,
        "mechanic_familiarity": 78,
        "upcountry_reliability": 74,
        "cost_tier": "$$ (Moderate)",
        "cost_multiplier": 1.25,
        "theft_risk": "High (Demio)",
        "theft_risk_note": "Demio side mirrors, wiper arms, and badges frequently targeted.",
        "kirinyaga_rd_support": "Excellent on Kirinyaga Rd & Grogan; rapidly expanding upcountry.",
        "recommended_verdict": "A- (Superb Modern Daily Driver)",
        "popular_models": ["CX-5 (KE/KF)", "Demio (DJ/DE)", "Axela", "Atenza"],
        "recommended_engines": "SkyActiv-G 2.0L / 2.5L Petrol (Bulletproof)",
        "mechanic_secrets": "Stick to petrol SkyActiv-G models. Avoid the 2.2L SkyActiv-D clean diesel unless you have a dedicated DPF specialist mechanic. Requires specialized Q-85 / T-110 EFB battery for i-stop system.",
        "basket_prices_kes": {
            "Oil & Air Filter Set": 3500,
            "Front Brake Pads": 4500,
            "Front Shock Absorber": 9500,
            "Side Mirror Assembly": 7500,
            "Iridium Plugs (Set of 4)": 6500,
            "Front Bumper Cover": 12000,
        },
    },
    "Nissan": {
        "brand": "Nissan",
        "tagline": "Spacious & High-Tech at an Accessible Price",
        "origin": "Japan",
        "market_share_est": "12%",
        "parts_availability_index": 86,
        "mechanic_familiarity": 82,
        "upcountry_reliability": 80,
        "cost_tier": "$$ (Moderate)",
        "cost_multiplier": 1.15,
        "theft_risk": "Moderate",
        "theft_risk_note": "Normal risk. Wingroad and Note mirrors occasionally taken.",
        "kirinyaga_rd_support": "Very broad support across Nairobi, Mombasa, Nakuru, and Kisumu.",
        "recommended_verdict": "B+ (High Value Per Shilling, Mind the Gearbox)",
        "popular_models": ["X-Trail (T31/T32)", "Note (E12)", "Serena", "Wingroad", "Tiida", "Patrol"],
        "recommended_engines": "HR12DE (Note), MR20DE (X-Trail), TB48 (Patrol)",
        "mechanic_secrets": "The single biggest failure point is CVT gearbox fluid contamination. Never let a mechanic use generic ATF; strictly demand genuine Nissan NS-2 or NS-3 fluid every 40,000 km.",
        "basket_prices_kes": {
            "Oil & Air Filter Set": 2800,
            "Front Brake Pads": 4000,
            "Front Shock Absorber": 8500,
            "Side Mirror Assembly": 6500,
            "Iridium Plugs (Set of 4)": 5200,
            "Front Bumper Cover": 10500,
        },
    },
    "Subaru": {
        "brand": "Subaru",
        "tagline": "The Highway King: Boxer Balance & Symmetrical AWD",
        "origin": "Japan",
        "market_share_est": "9%",
        "parts_availability_index": 79,
        "mechanic_familiarity": 76,
        "upcountry_reliability": 71,
        "cost_tier": "$$$ (Moderate-High)",
        "cost_multiplier": 1.4,
        "theft_risk": "Moderate",
        "theft_risk_note": "Forester / Outback fog lights and badges occasionally targeted.",
        "kirinyaga_rd_support": "High concentration in Baricho Rd, Kirinyaga Rd, and Industrial Area.",
        "recommended_verdict": "B+ (Unbeatable Highway Traction & Safety)",
        "popular_models": ["Forester (SH/SJ/SK)", "Outback (BR/BS)", "Impreza", "Legacy"],
        "recommended_engines": "FB20 / FB25 Naturally Aspirated, EJ20 (Turbo)",
        "mechanic_secrets": "Boxer engines sit low and horizontally. Always verify genuine full-synthetic oil (0W-20 or 5W-30) and monitor coolant levels diligently. Never use a roadside mechanic who lacks boxer experience.",
        "basket_prices_kes": {
            "Oil & Air Filter Set": 4200,
            "Front Brake Pads": 5500,
            "Front Shock Absorber": 11500,
            "Side Mirror Assembly": 9000,
            "Iridium Plugs (Set of 4)": 7200,
            "Front Bumper Cover": 14000,
        },
    },
    "Honda": {
        "brand": "Honda",
        "tagline": "Bulletproof Japanese Engineering with Selective Parts Sourcing",
        "origin": "Japan",
        "market_share_est": "6%",
        "parts_availability_index": 73,
        "mechanic_familiarity": 71,
        "upcountry_reliability": 66,
        "cost_tier": "$$ (Moderate)",
        "cost_multiplier": 1.3,
        "theft_risk": "Low",
        "theft_risk_note": "Infrequently targeted by street thieves compared to Toyota/Mazda.",
        "kirinyaga_rd_support": "Dedicated specialist merchants on Kirinyaga Rd and Mombasa Rd.",
        "recommended_verdict": "B+ (Ultra-Reliable, Spares Require Advance Planning)",
        "popular_models": ["Fit (GE6/GK3)", "Vezel / HR-V", "CR-V", "Civic"],
        "recommended_engines": "L13A / L15A (Fit), K24A (CR-V)",
        "mechanic_secrets": "Hondas rarely break down. However, when parts are needed (especially suspension links, engine mounts, and Vezel dual-clutch transmission actuators), you may wait 1-2 days outside Nairobi.",
        "basket_prices_kes": {
            "Oil & Air Filter Set": 3200,
            "Front Brake Pads": 4800,
            "Front Shock Absorber": 10500,
            "Side Mirror Assembly": 8000,
            "Iridium Plugs (Set of 4)": 6000,
            "Front Bumper Cover": 13000,
        },
    },
    "Isuzu": {
        "brand": "Isuzu",
        "tagline": "The Heavy-Duty Workhorse Assembled in Nairobi",
        "origin": "Japan / Kenya Assembly",
        "market_share_est": "5%",
        "parts_availability_index": 97,
        "mechanic_familiarity": 96,
        "upcountry_reliability": 98,
        "cost_tier": "$$ (Durable Value)",
        "cost_multiplier": 1.1,
        "theft_risk": "Moderate",
        "theft_risk_note": "D-Max tailgates and side mirrors targeted in commercial hubs.",
        "kirinyaga_rd_support": "Nationwide parts supply in all 47 counties through Isuzu East Africa.",
        "recommended_verdict": "A+ (Undisputed King for Pickups & Commercial Duty)",
        "popular_models": ["D-Max", "NPR", "FRR", "FTR"],
        "recommended_engines": "4JJ1-TC (3.0L Turbo Diesel), 4JK1 (2.5L)",
        "mechanic_secrets": "Assembled locally in Industrial Area Nairobi. Unmatched parts availability across all rural counties. Suspension and chassis built specifically for rough Kenyan terrain.",
        "basket_prices_kes": {
            "Oil & Air Filter Set": 3800,
            "Front Brake Pads": 5000,
            "Front Shock Absorber": 9000,
            "Side Mirror Assembly": 7000,
            "Iridium Plugs (Set of 4)": 4000,
            "Front Bumper Cover": 12500,
        },
    },
    "Suzuki": {
        "brand": "Suzuki",
        "tagline": "The Fuel Sipper: King of Nairobi Urban Commutes",
        "origin": "Japan / India",
        "market_share_est": "4%",
        "parts_availability_index": 87,
        "mechanic_familiarity": 89,
        "upcountry_reliability": 84,
        "cost_tier": "$ (Cheapest)",
        "cost_multiplier": 0.85,
        "theft_risk": "Moderate",
        "theft_risk_note": "Alto hubcaps and side mirrors common street targets.",
        "kirinyaga_rd_support": "Massive stock due to huge Uber/Bolt ride-hailing fleet.",
        "recommended_verdict": "A (Maximum Fuel Economy & Dirt-Cheap Maintenance)",
        "popular_models": ["Alto", "Swift", "Every", "Jimny", "Grand Vitara"],
        "recommended_engines": "K10B (1.0L), K12M (1.2L)",
        "mechanic_secrets": "Every corner garage in Nairobi knows how to repair an Alto or Swift. Extremely cheap suspension and service parts, though cabin insulation is modest.",
        "basket_prices_kes": {
            "Oil & Air Filter Set": 1900,
            "Front Brake Pads": 2600,
            "Front Shock Absorber": 5800,
            "Side Mirror Assembly": 4500,
            "Iridium Plugs (Set of 4)": 3800,
            "Front Bumper Cover": 7500,
        },
    },
    "Mitsubishi": {
        "brand": "Mitsubishi",
        "tagline": "Tough 4x4 Heritage and Rugged Logistics",
        "origin": "Japan",
        "market_share_est": "4%",
        "parts_availability_index": 81,
        "mechanic_familiarity": 79,
        "upcountry_reliability": 77,
        "cost_tier": "$$ (Moderate)",
        "cost_multiplier": 1.2,
        "theft_risk": "Low",
        "theft_risk_note": "Minimal street theft interest.",
        "kirinyaga_rd_support": "Widely available on Kirinyaga Rd and commercial corridors.",
        "recommended_verdict": "B (Rugged & Reliable, Inspect Outlander CVT)",
        "popular_models": ["Pajero (V98)", "Outlander", "RVR", "Canter"],
        "recommended_engines": "4M41 (3.2 Di-D), 4B12 (2.4 MIVEC)",
        "mechanic_secrets": "Pajero is an overland champion with parts in most county capitals. For Outlander petrol models, treat the CVT transmission with the same care as Nissan.",
        "basket_prices_kes": {
            "Oil & Air Filter Set": 3400,
            "Front Brake Pads": 4500,
            "Front Shock Absorber": 9500,
            "Side Mirror Assembly": 7000,
            "Iridium Plugs (Set of 4)": 5800,
            "Front Bumper Cover": 11500,
        },
    },
    "Volkswagen / Audi": {
        "brand": "Volkswagen / Audi",
        "tagline": "German Road Manners at Attainable Price Points",
        "origin": "Germany",
        "market_share_est": "3%",
        "parts_availability_index": 67,
        "mechanic_familiarity": 60,
        "upcountry_reliability": 52,
        "cost_tier": "$$$ (Moderate-High)",
        "cost_multiplier": 1.6,
        "theft_risk": "Low",
        "theft_risk_note": "Low theft rate.",
        "kirinyaga_rd_support": "Specialist European dealers only (Dar es Salaam Rd, Kirinyaga Rd).",
        "recommended_verdict": "B- (Engaging Drive, Requires Specialized Diagnostic Care)",
        "popular_models": ["Golf (Mk6/Mk7)", "Tiguan", "Passat", "Audi A4", "Audi Q5"],
        "recommended_engines": "1.4 TSI, 2.0 TSI (EA888 Gen 3)",
        "mechanic_secrets": "The Golf TSI handles brilliantly. But avoid roadside mechanics: DSG dual-clutch transmission mechatronics, water pump housings, and ignition coils require proper VCDS software diagnostics.",
        "basket_prices_kes": {
            "Oil & Air Filter Set": 4500,
            "Front Brake Pads": 6500,
            "Front Shock Absorber": 14000,
            "Side Mirror Assembly": 11000,
            "Iridium Plugs (Set of 4)": 8000,
            "Front Bumper Cover": 18000,
        },
    },
    "Mercedes-Benz": {
        "brand": "Mercedes-Benz",
        "tagline": "The Executive Standard of Prestige and Comfort",
        "origin": "Germany",
        "market_share_est": "2.5%",
        "parts_availability_index": 63,
        "mechanic_familiarity": 55,
        "upcountry_reliability": 46,
        "cost_tier": "$$$$ (High)",
        "cost_multiplier": 2.1,
        "theft_risk": "Low (Emblems Only)",
        "theft_risk_note": "Bonnet stars and wheel caps are street targets.",
        "kirinyaga_rd_support": "Found mainly through specialized European importers and CFAO/DT Dobie.",
        "recommended_verdict": "B- (Commanding Ride, Demands Healthy Maintenance Budget)",
        "popular_models": ["C-Class (W204/W205)", "E-Class (W212/W213)", "GLE", "S-Class"],
        "recommended_engines": "M274 (2.0L Turbo), OM651 (Diesel)",
        "mechanic_secrets": "Ride quality on smooth highways is second to none. However, rough Kenyan potholes punish airmatic suspensions and plastic cooling connectors. You must have a trusted European indie mechanic in Nairobi.",
        "basket_prices_kes": {
            "Oil & Air Filter Set": 6500,
            "Front Brake Pads": 9000,
            "Front Shock Absorber": 22000,
            "Side Mirror Assembly": 18000,
            "Iridium Plugs (Set of 4)": 10500,
            "Front Bumper Cover": 28000,
        },
    },
    "BMW": {
        "brand": "BMW",
        "tagline": "Pure Driving Dynamics with Strict Preventative Discipline",
        "origin": "Germany",
        "market_share_est": "2%",
        "parts_availability_index": 59,
        "mechanic_familiarity": 52,
        "upcountry_reliability": 42,
        "cost_tier": "$$$$ (High)",
        "cost_multiplier": 2.2,
        "theft_risk": "Low",
        "theft_risk_note": "Wheel center caps occasionally taken.",
        "kirinyaga_rd_support": "Specialist European dealers only in Nairobi and Mombasa.",
        "recommended_verdict": "C+ (Thrilling for Car Enthusiasts, Not for Frugal Beginners)",
        "popular_models": ["3 Series (E90/F30)", "5 Series (F10/G30)", "X3", "X5"],
        "recommended_engines": "N20 / B48 (2.0L Turbo), B58 (3.0L Inline 6)",
        "mechanic_secrets": "Driving dynamics and engine note are intoxicating. But cooling system plastic fittings, valve cover gaskets, and sensor warnings require rigorous preventative servicing. Do not take upcountry on bad terrain.",
        "basket_prices_kes": {
            "Oil & Air Filter Set": 6800,
            "Front Brake Pads": 9500,
            "Front Shock Absorber": 24000,
            "Side Mirror Assembly": 19000,
            "Iridium Plugs (Set of 4)": 11000,
            "Front Bumper Cover": 30000,
        },
    },
    "Land Rover / Range Rover": {
        "brand": "Land Rover / Range Rover",
        "tagline": "Aristocratic Presence with Maximum Maintenance Overhead",
        "origin": "United Kingdom",
        "market_share_est": "1.5%",
        "parts_availability_index": 62,
        "mechanic_familiarity": 50,
        "upcountry_reliability": 48,
        "cost_tier": "$$$$$ (Highest)",
        "cost_multiplier": 2.8,
        "theft_risk": "Low",
        "theft_risk_note": "Low street theft.",
        "kirinyaga_rd_support": "Specialist Land Rover garages (Range Rover Centre, CMC, Roverland).",
        "recommended_verdict": "C (Regal Status, Only for Buyers with Deep Maintenance Reserves)",
        "popular_models": ["Range Rover Sport", "Range Rover Vogue", "Discovery 4", "Defender"],
        "recommended_engines": "3.0L Supercharged Petrol, 3.0 TDV6 (Watch bearings)",
        "mechanic_secrets": "Nothing matches its road presence. But air suspension compressors, coolant crossover pipes, and electronic gremlins will strand you if neglected. Expect annual maintenance budgets above KES 250,000.",
        "basket_prices_kes": {
            "Oil & Air Filter Set": 8500,
            "Front Brake Pads": 14000,
            "Front Shock Absorber": 38000,
            "Side Mirror Assembly": 28000,
            "Iridium Plugs (Set of 4)": 14000,
            "Front Bumper Cover": 45000,
        },
    },
}


def get_recommendation(driving_zone, budget_comfort, priority_goal, parts_tolerance):
    """
    Intelligent matchmaker algorithm for a New Car Finder in Kenya.
    Scores each brand from 0 to 100 based on buyer profile.
    """
    scores = {}
    
    for brand_name, info in BRANDS_DATA.items():
        score = 50.0  # Base
        
        # 1. Driving Zone Impact
        if driving_zone == "Nairobi / Mombasa Urban Only":
            if info["origin"] == "Germany" or info["origin"] == "United Kingdom":
                score += 15
            else:
                score += 10
        elif driving_zone == "Frequent Upcountry / Mixed County Roads":
            if info["upcountry_reliability"] >= 80:
                score += 25
            elif info["upcountry_reliability"] >= 70:
                score += 10
            else:
                score -= 30
        elif driving_zone == "Remote / Rough Terrain / Safari":
            if brand_name in ["Toyota", "Isuzu", "Mitsubishi"]:
                score += 35
            else:
                score -= 25

        # 2. Budget & Maintenance Willingness
        if budget_comfort == "Frugal (Under KES 10,000/month)":
            if info["cost_tier"].startswith("$ "):
                score += 30
            elif info["cost_tier"].startswith("$$ "):
                score += 10
            else:
                score -= 40
        elif budget_comfort == "Moderate (KES 10,000 - 25,000/month)":
            if info["cost_tier"].startswith("$$ ") or info["cost_tier"].startswith("$ "):
                score += 25
            elif info["cost_tier"].startswith("$$$ "):
                score += 5
            else:
                score -= 20
        elif budget_comfort == "Flexible (KES 25,000 - 50,000/month)":
            if info["cost_tier"].startswith("$$$ ") or info["cost_tier"].startswith("$$ "):
                score += 20
        elif budget_comfort == "High End (KES 50,000+/month)":
            if info["origin"] in ["Germany", "United Kingdom"]:
                score += 25

        # 3. Priority Goal
        if priority_goal == "Peace of Mind & Easy Resale":
            if brand_name in ["Toyota", "Isuzu"]:
                score += 35
            elif brand_name in ["Mazda", "Nissan"]:
                score += 15
        elif priority_goal == "Fuel Economy & Daily Commuting":
            if brand_name in ["Suzuki", "Toyota", "Mazda", "Honda", "Nissan"]:
                score += 25
        elif priority_goal == "Highway Stability, Driving Joy & Speed":
            if brand_name in ["Subaru", "BMW", "Volkswagen / Audi", "Mazda"]:
                score += 30
        elif priority_goal == "Executive Status & Luxury Presence":
            if brand_name in ["Mercedes-Benz", "Land Rover / Range Rover", "BMW", "Toyota"]:
                score += 35

        # 4. Spares Waiting Tolerance
        if parts_tolerance == "Zero (Must be fixed same day)":
            if info["parts_availability_index"] >= 90:
                score += 25
            elif info["parts_availability_index"] < 75:
                score -= 25
        elif parts_tolerance == "1-3 Days is fine":
            if info["parts_availability_index"] >= 75:
                score += 15

        # Clamp between 20 and 99
        final_score = int(max(20, min(99, score)))
        scores[brand_name] = final_score

    # Sort descending
    sorted_brands = sorted(scores.items(), key=lambda x: x[1], reverse=True)
    return sorted_brands
