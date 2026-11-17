"""
inspection_data.py
Pre-Purchase Inspection (PPI) "Lemon Detector" Checklist for Kenyan Car Yards.
Designed for buyers inspecting cars on Kiambu Rd, Ngong Rd, Mombasa Rd, and Mombasa Port.
"""

INSPECTION_SECTIONS = [
    {
        "category": "1. Odometer & Document Verification",
        "weight": 20,
        "items": [
            {
                "id": "jevic_cert",
                "label": "JEVIC / QISJ Mileage Certificate Verification",
                "guide": "Cross-check the chassis number on the JEVIC/QISJ verification portal. If the yard says the certificate is 'lost', assume mileage was rolled back.",
                "red_flag": "Mileage Certificate missing or numbers don't match dashboard.",
            },
            {
                "id": "pedal_wear",
                "label": "Pedal Rubbers & Steering Wheel Texture vs Odometer",
                "guide": "A car showing 45,000 km should have textured steering leather and sharp rubber pedal ribs. If pedals are worn smooth to the metal, car has done 150,000+ km.",
                "red_flag": "Heavily worn pedals on a 'low mileage' vehicle.",
            },
            {
                "id": "logbook_status",
                "label": "NTSA TIMS / eCitizen Logbook & Caveat Check",
                "guide": "Verify on NTSA TIMS portal that there are no bank caveats, joint financial encumbrances, or court injunctions.",
                "red_flag": "Undisclosed bank loan or third-party logbook caveat.",
            },
        ],
    },
    {
        "category": "2. Structural Integrity & Accident Salvage Detection",
        "weight": 25,
        "items": [
            {
                "id": "spot_welds",
                "label": "A/B/C Pillar Factory Spot Welds & Door Rubber Seal",
                "guide": "Pull back the rubber door weatherstrips on all 4 doors. Factory spot welds must be round, sharp, and indented. If ground flat, covered in bondo, or wrinkled, car was in a rollover or severe t-bone collision.",
                "red_flag": "Smoothed over welds, mismatched paint, or visible putty.",
            },
            {
                "id": "radiator_support",
                "label": "Front Radiator Core Support & Fender Bolts",
                "guide": "Examine the 10mm bolts holding the front fenders and radiator support. Factory bolts have undisturbed factory paint. If bolt corners are stripped or show wrench marks, the front was dismantled after an accident.",
                "red_flag": "Chipped paint on fender bolts and mismatched headlights.",
            },
            {
                "id": "boot_floor",
                "label": "Spare Wheel Well & Rear Apron Inspection",
                "guide": "Lift the carpet in the boot and remove the spare tyre. The spare tyre well must have clean factory robotic sealant beads. If wavy, hammered straight, or rusted, car suffered rear-end shunting.",
                "red_flag": "Hammer marks, crumpled sheet metal, or wet standing water in spare well.",
            },
        ],
    },
    {
        "category": "3. Engine Health & Mechanical Secrets",
        "weight": 25,
        "items": [
            {
                "id": "cold_start",
                "label": "Cold Engine Startup Test (Demand 1st Start of Day)",
                "guide": "Insist the engine is cold to the touch before starting. Listen for metallic timing chain clatter or valve tap for the first 5 seconds. Smoke out the exhaust: Blue = burning oil (piston rings/valve stems); White sweet smell = blown head gasket; Black = rich fuel injectors.",
                "red_flag": "Puff of blue smoke or loud chain rattle on cold start.",
            },
            {
                "id": "oil_cap_milky",
                "label": "Oil Filler Cap & Dipstick Inspection",
                "guide": "Unscrew the engine oil filler cap. Look beneath the cap. Golden or black oil is normal. Creamy, milky mayonnaise-like residue indicates coolant mixing with oil (cracked cylinder head or blown gasket).",
                "red_flag": "Milky emulsified residue under oil cap.",
            },
            {
                "id": "blowby_test",
                "label": "Dipstick Blow-By & Compression Test",
                "guide": "With engine idling warm, pull the dipstick out and place a clean tissue or your palm over the hole. If it blows strong exhaust gas and oil mist, the engine has severe cylinder blow-by and needs an overhaul soon.",
                "red_flag": "Strong puffing smoke and oil spitting from dipstick tube.",
            },
        ],
    },
    {
        "category": "4. Transmission & Drivetrain Health",
        "weight": 20,
        "items": [
            {
                "id": "gear_engagement",
                "label": "Stationary Gear Engagement Jerk Test (P -> R -> D)",
                "guide": "Hold the brake firmly. Shift from Park to Reverse, wait 2 seconds, then shift to Neutral and Drive. The engagement should be immediate and smooth. A violent thud, jerk, or 3-second delay means worn clutch packs, valve body failure, or degraded CVT fluid.",
                "red_flag": "Hard violent thump or prolonged hesitation into gear.",
            },
            {
                "id": "cvt_slip",
                "label": "Low-Speed Incline Acceleration & Shudder Test",
                "guide": "Drive the car onto a slight incline at 20-40 km/h. Accelerate moderately. Watch the tachometer. If engine RPM revs up without road speed increasing, or if the car shudders and vibrates like driving over rumble strips, the CVT steel belt is slipping.",
                "red_flag": "Surging RPMs, juddering vibration, or whining gearbox noise.",
            },
            {
                "id": "full_lock_cv",
                "label": "Full Steering Lock Figure-8 CV Joint Test",
                "guide": "Find an open parking space. Turn the steering wheel to full left lock and drive slowly in a tight circle, then repeat with full right lock. Any repetitive 'click-click-click-clack' noise indicates torn CV joint boots and failing constant-velocity axles.",
                "red_flag": "Loud rhythmic clicking from front wheels on full lock.",
            },
        ],
    },
    {
        "category": "5. Suspension, Rust & Undercarriage",
        "weight": 10,
        "items": [
            {
                "id": "coastal_rust",
                "label": "Japanese Snow/Salt & Coastal Rust Inspection",
                "guide": "Look underneath the sills, exhaust, brake calipers, and subframe. Surface brown rust is common from northern Japanese winter road salt (Hokkaido), but flaking structural rust on suspension arms will fail Kenyan NTSA inspection.",
                "red_flag": "Heavy flaking structural rust on subframe mounting points.",
            },
            {
                "id": "shock_leak",
                "label": "Shock Absorbers & Bushing Tear Test",
                "guide": "Inspect all 4 shock absorbers behind the wheels. They should be dry and dusty. If shiny, wet, and coated with oily grime, the shock seals have blown. Push down hard on each car corner: it should rebound once and settle, not bounce 3 times.",
                "red_flag": "Wet oil running down shock absorber body.",
            },
        ],
    },
]


def score_inspection(checked_pass_ids, checked_fail_ids):
    """
    Score the inspection and provide a verdict:
    - Low Risk Clean Buy (85 - 100)
    - Moderate Risk / Negotiate Hard (65 - 84)
    - High Risk / Walk Away Danger (< 65 or critical safety fails)
    """
    total_items = sum(len(sec["items"]) for sec in INSPECTION_SECTIONS)
    fails_count = len(checked_fail_ids)
    passes_count = len(checked_pass_ids)

    # Critical dealbreaker IDs
    dealbreakers = ["spot_welds", "oil_cap_milky", "blowby_test", "cvt_slip", "jevic_cert"]
    critical_fails = [f_id for f_id in checked_fail_ids if f_id in dealbreakers]

    # Percentage score
    score_pct = int(max(0, 100 - (fails_count * 8)))

    if critical_fails or score_pct < 65:
        verdict = "🚨 HIGH RISK / WALK AWAY"
        verdict_color = "red"
        advice = (
            f"This vehicle triggered {len(critical_fails)} critical dealbreaker fails: {', '.join(critical_fails)}. "
            "You are at high risk of buying an accident-rebuilt salvage car or an engine needing an immediate KES 150k+ overhaul. Walk away!"
        )
    elif score_pct < 85:
        verdict = "⚠️ MODERATE RISK / NEGOTIATE HARD"
        verdict_color = "orange"
        advice = (
            f"The car has {fails_count} mechanical or wear defects. It is likely salvageable, but you should deduct "
            f"at least KES {fails_count * 30000:,.0f} from the asking price to cover immediate garage repairs."
        )
    else:
        verdict = "✅ LOW RISK / CLEAN UNIT"
        verdict_color = "green"
        advice = "The vehicle passed all primary structural, engine, and transmission tests. Proceed to NTSA logbook transfer and buy with confidence!"

    return {
        "score_pct": score_pct,
        "verdict": verdict,
        "verdict_color": verdict_color,
        "advice": advice,
        "passes_count": passes_count,
        "fails_count": fails_count,
        "critical_fails": critical_fails,
    }
