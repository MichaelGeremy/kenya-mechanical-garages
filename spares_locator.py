"""
spares_locator.py
Kirinyaga Road, Grogan & Industrial Area Auto Spares Locator.
Provides price tiers (OEM vs Quality Aftermarket vs Ex-Japan Used) and
specific sourcing hubs for high-demand spare parts in Kenya.
"""

PARTS_CATALOG = {
    "Side Mirror Assembly (Complete Electric Folding)": {
        "part_name": "Side Mirror Assembly (Complete Electric Folding)",
        "description": "Complete motorized side mirror with glass, motor, indicator LED, and cover. Top stolen item in Nairobi.",
        "category": "Body & Electrical",
        "theft_factor": "Extremely High (Fielder, Demio, Axio, Vitz)",
        "prices": {
            "Toyota (Fielder/Axio/Premio)": {"OEM_New": 16000, "Aftermarket": 8500, "ExJapan_Used": 5500},
            "Mazda (Demio/CX-5)": {"OEM_New": 22000, "Aftermarket": 11000, "ExJapan_Used": 7500},
            "Nissan (X-Trail/Note)": {"OEM_New": 18000, "Aftermarket": 9500, "ExJapan_Used": 6500},
            "Subaru (Forester/Outback)": {"OEM_New": 25000, "Aftermarket": 13000, "ExJapan_Used": 9000},
            "Honda (Fit/Vezel/CR-V)": {"OEM_New": 24000, "Aftermarket": 12000, "ExJapan_Used": 8500},
            "German (Mercedes/BMW/VW)": {"OEM_New": 55000, "Aftermarket": 28000, "ExJapan_Used": 18000},
        },
        "recommended_hubs": [
            "Kirinyaga Road (Central Nairobi) - 200+ dedicated mirror & lighting shops",
            "Grogan (Upper Kirinyaga Rd) - Ex-Japan used & scrap body panels",
            "Gikomba Auto Spares - High availability of imported used assemblies",
        ],
        "pro_tip": "Always rivet the base and chemically etch your registration number onto the glass immediately after purchase to deter street thieves.",
    },
    "Front Shock Absorber (Pair)": {
        "part_name": "Front Shock Absorber (Pair)",
        "description": "Front suspension hydraulic/gas strut shock absorbers to soak up Kenyan potholes.",
        "category": "Suspension & Steering",
        "theft_factor": "Low",
        "prices": {
            "Toyota (Fielder/Axio/Premio)": {"OEM_New": 26000, "Aftermarket": 14000, "ExJapan_Used": 9000},
            "Mazda (Demio/CX-5)": {"OEM_New": 32000, "Aftermarket": 18000, "ExJapan_Used": 12000},
            "Nissan (X-Trail/Note)": {"OEM_New": 28000, "Aftermarket": 16000, "ExJapan_Used": 10500},
            "Subaru (Forester/Outback)": {"OEM_New": 38000, "Aftermarket": 22000, "ExJapan_Used": 14000},
            "Honda (Fit/Vezel/CR-V)": {"OEM_New": 34000, "Aftermarket": 20000, "ExJapan_Used": 13000},
            "German (Mercedes/BMW/VW)": {"OEM_New": 75000, "Aftermarket": 42000, "ExJapan_Used": 24000},
        },
        "recommended_hubs": [
            "Kirinyaga Road - Authorized KYB / Tokico Japanese suspension distributors",
            "Baricho Road (Industrial Area) - AutoXpress and specialist suspension centers",
            "Dar es Salaam Road - German and European suspension specialists",
        ],
        "pro_tip": "Never buy used shocks for heavy upcountry use. Invest in Japanese KYB (Excel-G) or Tokico aftermarket — they last 60,000+ km on Kenyan roads.",
    },
    "Brake Pads Set (Front Ceramic / Semi-Metallic)": {
        "part_name": "Brake Pads Set (Front Ceramic / Semi-Metallic)",
        "description": "Essential high-friction stopping pads for front ventilated brake discs.",
        "category": "Braking System",
        "theft_factor": "None",
        "prices": {
            "Toyota (Fielder/Axio/Premio)": {"OEM_New": 7500, "Aftermarket": 3500, "ExJapan_Used": 1500},
            "Mazda (Demio/CX-5)": {"OEM_New": 9000, "Aftermarket": 4500, "ExJapan_Used": 2000},
            "Nissan (X-Trail/Note)": {"OEM_New": 8000, "Aftermarket": 4000, "ExJapan_Used": 1800},
            "Subaru (Forester/Outback)": {"OEM_New": 11000, "Aftermarket": 5500, "ExJapan_Used": 2500},
            "Honda (Fit/Vezel/CR-V)": {"OEM_New": 9500, "Aftermarket": 4800, "ExJapan_Used": 2200},
            "German (Mercedes/BMW/VW)": {"OEM_New": 18000, "Aftermarket": 8500, "ExJapan_Used": 3500},
        },
        "recommended_hubs": [
            "Kirinyaga Road - Akebono, MK Kashiyama & Ferodo distributors",
            "Grogon - Quick on-the-spot disc skim & pad replacement",
            "Mombasa Road - Commercial brake lining specialists",
        ],
        "pro_tip": "Insist on Japanese 'Akebono' or 'MK Kashiyama' ceramic pads to prevent black dust on your alloy wheels and rotor squealing.",
    },
    "CVT Transmission Fluid & Filter Kit": {
        "part_name": "CVT Transmission Fluid & Filter Kit",
        "description": "Specialized synthetic transmission fluid + pan gasket + fine mesh oil filter.",
        "category": "Powertrain & Drivetrain",
        "theft_factor": "None",
        "prices": {
            "Toyota (Fielder/Axio/Premio)": {"OEM_New": 9500, "Aftermarket": 6500, "ExJapan_Used": 0},
            "Mazda (Demio/CX-5)": {"OEM_New": 12000, "Aftermarket": 8500, "ExJapan_Used": 0},
            "Nissan (X-Trail/Note)": {"OEM_New": 11500, "Aftermarket": 7800, "ExJapan_Used": 0},
            "Subaru (Forester/Outback)": {"OEM_New": 14000, "Aftermarket": 9500, "ExJapan_Used": 0},
            "Honda (Fit/Vezel/CR-V)": {"OEM_New": 11000, "Aftermarket": 8000, "ExJapan_Used": 0},
            "German (Mercedes/BMW/VW)": {"OEM_New": 24000, "Aftermarket": 15000, "ExJapan_Used": 0},
        },
        "recommended_hubs": [
            "Baricho Road - Professional fluid flushing workshops with diagnostic scanners",
            "Kirinyaga Road - Genuine Japanese tin can fluids (Toyota FE/TC, Nissan NS-3, Subaru Lineartronic)",
        ],
        "pro_tip": "Strictly buy 4-litre sealed metal Japanese cans. Never buy transmission fluid decanted from 200L drums, and never use generic red ATF.",
    },
    "Lower Control Arm & Ball Joint Assembly": {
        "part_name": "Lower Control Arm & Ball Joint Assembly",
        "description": "Crucial suspension wishbone maintaining wheel alignment and absorbing curb strikes.",
        "category": "Suspension & Steering",
        "theft_factor": "None",
        "prices": {
            "Toyota (Fielder/Axio/Premio)": {"OEM_New": 18000, "Aftermarket": 8000, "ExJapan_Used": 4500},
            "Mazda (Demio/CX-5)": {"OEM_New": 24000, "Aftermarket": 11000, "ExJapan_Used": 6500},
            "Nissan (X-Trail/Note)": {"OEM_New": 20000, "Aftermarket": 9500, "ExJapan_Used": 5500},
            "Subaru (Forester/Outback)": {"OEM_New": 26000, "Aftermarket": 12500, "ExJapan_Used": 7500},
            "Honda (Fit/Vezel/CR-V)": {"OEM_New": 22000, "Aftermarket": 10500, "ExJapan_Used": 6000},
            "German (Mercedes/BMW/VW)": {"OEM_New": 48000, "Aftermarket": 22000, "ExJapan_Used": 12000},
        },
        "recommended_hubs": [
            "Kirinyaga Road - 555 (Three Five Japan) licensed retailers",
            "Industrial Area (Dar es Salaam Rd) - Heavy duty polyurethane bush pressing",
        ],
        "pro_tip": "Look for the embossed '555 Made in Japan' stamp on aftermarket ball joints to avoid cheap Chinese counterfeits that snap on speed bumps.",
    },
    "LED Headlight Assembly (Complete)": {
        "part_name": "LED Headlight Assembly (Complete)",
        "description": "High-intensity discharge / LED headlamp with daytime running light (DRL) strip.",
        "category": "Lighting & Electrical",
        "theft_factor": "High (Prado, Harrier, CX-5, Note)",
        "prices": {
            "Toyota (Fielder/Axio/Premio)": {"OEM_New": 42000, "Aftermarket": 18000, "ExJapan_Used": 12000},
            "Mazda (Demio/CX-5)": {"OEM_New": 55000, "Aftermarket": 24000, "ExJapan_Used": 16000},
            "Nissan (X-Trail/Note)": {"OEM_New": 38000, "Aftermarket": 19000, "ExJapan_Used": 13000},
            "Subaru (Forester/Outback)": {"OEM_New": 62000, "Aftermarket": 28000, "ExJapan_Used": 19000},
            "Honda (Fit/Vezel/CR-V)": {"OEM_New": 48000, "Aftermarket": 22000, "ExJapan_Used": 15000},
            "German (Mercedes/BMW/VW)": {"OEM_New": 120000, "Aftermarket": 58000, "ExJapan_Used": 38000},
        },
        "recommended_hubs": [
            "Kirinyaga Road (Central) - Major importer stockists for Koito, Stanley & Depo lighting",
            "Grogan - High stock of tested Ex-Japan front clips and headlights",
        ],
        "pro_tip": "Ex-Japan units are left-hand beam compliant. Ensure the seller aligns the beam pattern during installation so you don't blind oncoming traffic on the highway.",
    },
}

CORRIDORS_GUIDE = [
    {
        "name": "Kirinyaga Road & Grogan (Nairobi CBD)",
        "speciality": "The undisputed capital of automotive spares in East Africa. Every part imaginable for Japanese & German cars.",
        "best_for": "Body panels, mirrors, lights, 555 suspension parts, clutches, brake pads, electrical relays.",
        "bargaining_tip": "Always negotiate 20-30% below the first quote. Take your damaged sample part with you for physical comparison.",
    },
    {
        "name": "Baricho Road & Dar es Salaam Road (Industrial Area)",
        "speciality": "Formal importers, certified alignment centers, high-end lubricants, and German car specialists.",
        "best_for": "Engine overhauls, diagnostic scanners, genuine European parts (Bosch, Bilstein, Lemförder), tyre fitment.",
        "bargaining_tip": "Prices are often fixed with VAT receipts. Ideal for corporate receipts and warranty claims.",
    },
    {
        "name": "Gikomba Auto Spares Section",
        "speciality": "Huge open-air yard for freshly containers of Ex-Japan half-cuts, engines, gearboxes, and suspension arms.",
        "best_for": "Complete replacement engines (1NZ, FB20, SkyActiv), manual/auto gearboxes, steering racks.",
        "bargaining_tip": "Demand a 30-day testing warranty (stamped on receipt) when buying complete engines or gearboxes.",
    },
    {
        "name": "Mombasa (Jomo Kenyatta Ave & Mwangeka Rd)",
        "speciality": "Port city entry point for containerized spares. Often KES 1,000 - 3,000 cheaper than Nairobi due to zero freight markup.",
        "best_for": "Coastal imports, alloy rims, tyres, diesel injection pumps, marine & transport spares.",
        "bargaining_tip": "Buy directly from clearing agent importers along Jomo Kenyatta Avenue.",
    },
]
