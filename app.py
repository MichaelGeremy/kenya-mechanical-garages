"""
app.py
Kenya Mechanical Garages, Auto Workshops & Car Brand Intelligence Explorer
A comprehensive, top-tier automotive intelligence platform for Kenyan car buyers,
fleet managers, and mechanics.
"""

import json
import os
import urllib.parse
import urllib.request
import urllib.error

import folium
from folium.plugins import MarkerCluster
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
import streamlit as st
from streamlit_folium import st_folium

from brand_data import BRANDS_DATA
from car_models_data import CAR_MODELS, match_exact_car_models
from tco_calculator import calculate_tco, EPRA_PRICES
from inspection_data import INSPECTION_SECTIONS, score_inspection
from spares_locator import PARTS_CATALOG, CORRIDORS_GUIDE
from duty_calculator import check_8_year_rule, calculate_kra_import_duty

# Page setup
st.set_page_config(
    page_title="Kenya Garages & Auto Intelligence Platform",
    page_icon="🚗",
    layout="wide",
    initial_sidebar_state="expanded",
)

DATA_PATH = os.path.join("data", "kenya_garages.csv")

CATEGORY_CONFIG = {
    "auto_repair": {"label": "Auto Repair / Garage", "color": "red", "icon": "wrench", "badge": "🚗 Auto Repair"},
    "motorcycle_repair": {"label": "Motorcycle / Boda Boda", "color": "green", "icon": "motorcycle", "badge": "🏍️ Motorcycle Repair"},
    "tyres": {"label": "Tyre Center", "color": "orange", "icon": "circle", "badge": "🛞 Tyres"},
    "auto_spares": {"label": "Auto Spares / Parts", "color": "purple", "icon": "cog", "badge": "🔧 Spares & Parts"},
    "jua_kali_craft": {"label": "Jua Kali Welder / Artisan", "color": "darkblue", "icon": "fire", "badge": "🔨 Jua Kali / Metal"},
}

DEFAULT_COUNTY_BBOXES = {
    "Nairobi": (-1.444, 36.662, -1.160, 37.104),
    "Mombasa": (-4.120, 39.550, -3.900, 39.770),
    "Kiambu": (-1.290, 36.480, -0.750, 37.280),
    "Nakuru": (-0.950, 35.450, 0.250, 36.500),
    "Machakos": (-1.750, 36.950, -0.850, 37.900),
    "Kisumu": (-0.450, 34.450, 0.050, 35.150),
    "Uasin Gishu (Eldoret)": (0.150, 34.850, 0.950, 35.600),
    "Kajiado": (-3.150, 36.050, -1.300, 37.950),
    "Meru": (-0.350, 37.150, 0.700, 38.300),
    "Kilifi": (-4.000, 39.050, -2.300, 40.200),
}

OVERPASS_MIRRORS = [
    "https://overpass.openstreetmap.fr/api/interpreter",
    "https://overpass-api.de/api/interpreter",
    "https://lz4.overpass-api.de/api/interpreter",
]


@st.cache_data(ttl=300)
def load_data(file_path):
    if not os.path.exists(file_path):
        return pd.DataFrame()
    df = pd.read_csv(file_path, encoding="utf-8-sig")
    df["lat"] = pd.to_numeric(df["lat"], errors="coerce")
    df["lng"] = pd.to_numeric(df["lng"], errors="coerce")
    df = df.dropna(subset=["lat", "lng"])
    for col in ["name", "category", "search_area", "phone", "address", "city", "brand", "brand_specialization"]:
        if col in df.columns:
            df[col] = df[col].fillna("").astype(str)
        else:
            df[col] = ""
    return df


def fetch_from_osm(bbox, search_area, include_juakali=True, include_spares=True):
    s, w, n, e = bbox
    box_str = f"({s:.4f},{w:.4f},{n:.4f},{e:.4f})"
    tags = ['["shop"="car_repair"]', '["amenity"="motorcycle_repair"]', '["shop"="tyres"]']
    if include_spares:
        tags.extend(['["shop"="car_parts"]', '["shop"="auto_parts"]'])
    if include_juakali:
        tags.extend(['["craft"="blacksmith"]', '["craft"="welder"]', '["craft"="metal_construction"]'])

    statements = []
    for t in tags:
        statements.append(f"  node{t}{box_str};")
        statements.append(f"  way{t}{box_str};")

    query = f"[out:json][timeout:60];(\n" + "\n".join(statements) + f"\n);\nout center tags;\n"
    data = urllib.parse.urlencode({"data": query}).encode("utf-8")

    elements = []
    for mirror in OVERPASS_MIRRORS:
        try:
            req = urllib.request.Request(mirror, data=data, headers={"User-Agent": "KenyaGaragesExplorer/2.0"})
            with urllib.request.urlopen(req, timeout=45) as resp:
                res = json.loads(resp.read().decode("utf-8"))
                elements = res.get("elements", [])
                if elements:
                    break
        except Exception:
            continue

    new_rows = []
    for elem in elements:
        tags_dict = elem.get("tags", {})
        elem_type = elem.get("type", "node")
        elem_id = elem.get("id", "")
        lat = elem.get("lat") or elem.get("center", {}).get("lat")
        lon = elem.get("lon") or elem.get("center", {}).get("lon")
        if lat is None or lon is None:
            continue

        name = tags_dict.get("name") or tags_dict.get("operator") or tags_dict.get("brand") or "(Unnamed Garage/Workshop)"
        cat = "auto_repair"
        if tags_dict.get("amenity") == "motorcycle_repair":
            cat = "motorcycle_repair"
        elif tags_dict.get("shop") == "tyres":
            cat = "tyres"
        elif tags_dict.get("shop") in ("car_parts", "auto_parts"):
            cat = "auto_spares"
        elif tags_dict.get("craft") in ("blacksmith", "welder", "metal_construction"):
            cat = "jua_kali_craft"

        phone = tags_dict.get("phone") or tags_dict.get("contact:phone") or tags_dict.get("contact:mobile") or ""
        website = tags_dict.get("website") or tags_dict.get("contact:website") or ""
        street = tags_dict.get("addr:street") or ""
        city = tags_dict.get("addr:city") or tags_dict.get("addr:town") or ""
        county = tags_dict.get("addr:county") or ""
        addr = ", ".join([p for p in (street, city, county) if p])

        new_rows.append({
            "osm_id": f"{elem_type}/{elem_id}",
            "name": name,
            "category": cat,
            "brand_specialization": "Multi-Brand / General",
            "search_area": search_area,
            "lat": lat,
            "lng": lon,
            "phone": phone,
            "website": website,
            "opening_hours": tags_dict.get("opening_hours", ""),
            "brand": tags_dict.get("brand", ""),
            "address": addr,
            "city": city,
            "county": county,
            "osm_url": f"https://www.openstreetmap.org/{elem_type}/{elem_id}",
        })
    return new_rows


df = load_data(DATA_PATH)

# Header
st.title("🇰🇪 Kenya Mechanical Garages & Auto Intelligence Platform")
st.markdown(
    "**The Definitive Vehicle Buying & Maintenance Platform for Kenya:** Match exact car models, "
    "compare rivals head-to-head, calculate 3-year TCO & fuel economics, detect auction lemons, "
    "locate Kirinyaga Road spares, and explore 300+ verified garages nationwide."
)

# Sidebar
with st.sidebar:
    st.image(
        "https://images.unsplash.com/photo-1486006920555-c77dce18193b?auto=format&fit=crop&w=400&q=80",
        caption="Kenya Auto Market & Garage Intelligence",
    )
    st.header("🔍 Global Garage Filter")
    search_query = st.text_input("Search Garage, Street, or Brand", placeholder="e.g. Toyota, Kirinyaga, Ngong...")

    all_areas = sorted([a for a in df["search_area"].unique() if a]) if not df.empty else []
    selected_areas = st.multiselect("County / Search Area", options=all_areas, default=all_areas)

    all_categories = list(CATEGORY_CONFIG.keys())
    selected_categories = st.multiselect(
        "Service Category",
        options=all_categories,
        default=all_categories,
        format_func=lambda x: CATEGORY_CONFIG.get(x, {}).get("badge", x),
    )

    only_with_phone = st.checkbox("📞 Only places with phone numbers", value=False)
    st.markdown("---")

    st.subheader("🌐 In-App Data Harvester")
    st.caption("Harvest live garages and spares stores from OpenStreetMap without API keys.")
    fetch_area = st.selectbox("Select County to Harvest", options=list(DEFAULT_COUNTY_BBOXES.keys()))
    harvest_juakali = st.checkbox("Include Jua Kali artisans", value=True)
    harvest_spares = st.checkbox("Include Auto Spares stores", value=True)

    if st.button("🚀 Harvest Live from OSM", width="stretch"):
        with st.spinner(f"Harvesting live data for {fetch_area}..."):
            bbox = DEFAULT_COUNTY_BBOXES[fetch_area]
            clean_name = fetch_area.split(" ")[0]
            new_places = fetch_from_osm(bbox, search_area=clean_name, include_juakali=harvest_juakali, include_spares=harvest_spares)
            if new_places:
                new_df = pd.DataFrame(new_places)
                combined_df = pd.concat([df, new_df], ignore_index=True)
                combined_df = combined_df.drop_duplicates(subset=["osm_id"], keep="first")
                os.makedirs("data", exist_ok=True)
                combined_df.to_csv(DATA_PATH, index=False, encoding="utf-8-sig")
                st.cache_data.clear()
                st.success(f"Added {len(new_places)} places in {clean_name}!")
                st.rerun()
            else:
                st.warning(f"No additional places returned from OSM for {clean_name}.")


# Filtering pipeline for garages
filtered_df = df.copy()
if not filtered_df.empty:
    if selected_areas:
        filtered_df = filtered_df[filtered_df["search_area"].isin(selected_areas)]
    if selected_categories:
        filtered_df = filtered_df[filtered_df["category"].isin(selected_categories)]
    if only_with_phone:
        filtered_df = filtered_df[filtered_df["phone"].str.len() > 2]
    if search_query:
        q = search_query.lower()
        mask = (
            filtered_df["name"].str.lower().str.contains(q)
            | filtered_df["address"].str.lower().str.contains(q)
            | filtered_df["brand"].str.lower().str.contains(q)
            | filtered_df["brand_specialization"].str.lower().str.contains(q)
        )
        filtered_df = filtered_df[mask]


# TABS SETUP
tabs = st.tabs([
    "🎯 Car Model Matchmaker",
    "⚔️ Head-to-Head Rival Comparison",
    "💰 3-Year TCO & Fuel Economics",
    "🔍 Pre-Purchase Inspection (Lemon Detector)",
    "🔩 Kirinyaga Road Spares Locator",
    "🚢 KRA 8-Year Rule & Import Duty",
    "🚘 50+ Car Models Catalog",
    "📖 The Car Buyer's Data Story",
    "🗺️ Interactive Garages & Spares Map",
    "📊 Market & County Analytics",
    "📋 Directory & Data Export",
])

tab_matchmaker = tabs[0]
tab_h2h = tabs[1]
tab_tco = tabs[2]
tab_ppi = tabs[3]
tab_spares = tabs[4]
tab_duty = tabs[5]
tab_models_catalog = tabs[6]
tab_story = tabs[7]
tab_map = tabs[8]
tab_analytics = tabs[9]
tab_directory = tabs[10]


# =============================================================
# TAB 1: EXACT CAR MODEL MATCHMAKER
# =============================================================
with tab_matchmaker:
    st.subheader("🎯 Discover the Exact Car Model You Need in Kenya")
    st.markdown(
        "Match your exact vehicle from our database of **54 top models (2015 – 2026)** "
        "based on **ground clearance**, **fuel economy**, **spare parts ease**, and **purchase budget (KES)**."
    )

    col_q1, col_q2, col_q3 = st.columns(3)
    with col_q1:
        user_budget_kes = st.slider(
            "1. Maximum Purchase Budget (KES):",
            min_value=800000,
            max_value=12000000,
            value=2500000,
            step=100000,
            format="KES %d",
        )
        user_usage = st.selectbox(
            "2. Primary Driving Purpose:",
            options=[
                "Daily Nairobi City Commute",
                "Family Upcountry & Weekend Trips",
                "Rough Rural Roads, Farm & Offroad",
                "Executive Business & Highway Status",
                "Business Logistics / Heavy Load Carry",
            ],
            index=1,
        )

    with col_q2:
        user_clearance = st.selectbox(
            "3. Ground Clearance Requirement:",
            options=[
                "Standard (150 - 185 mm is fine for city & highway)",
                "Must be High (190 mm+ for bumps & rough roads)",
            ],
            index=1,
        )
        user_body = st.selectbox(
            "4. Preferred Body Style:",
            options=["Any Body Style", "Crossover / SUV", "Sedan", "Hatchback", "Station Wagon", "Pickup", "Van / MPV", "Full-size 4x4"],
            index=1,
        )

    with col_q3:
        user_fuel = st.selectbox("5. Preferred Fuel Type:", options=["Any Fuel Type", "Petrol", "Diesel", "Hybrid"], index=0)
        user_spares = st.selectbox(
            "6. Spare Parts Availability Priority:",
            options=["Balanced (Nairobi/Mombasa stock is fine, 1-2 days wait ok)", "Maximum (Must find parts in every Kenyan town same day)"],
            index=0,
        )

    st.markdown("---")

    matched_results = match_exact_car_models(
        budget_kes=user_budget_kes,
        primary_usage=user_usage,
        ground_clearance_pref=user_clearance,
        body_style_pref=user_body,
        fuel_pref=user_fuel,
        spares_priority=user_spares,
    )

    st.subheader(f"🏆 Top Recommended Car Models for Your Profile (Budget: KES {user_budget_kes:,.0f})")

    top_3_cars = matched_results[:3]
    top_c1, top_c2, top_c3 = st.columns(3)
    medals = ["🥇 1st Choice", "🥈 2nd Choice", "🥉 3rd Choice"]

    for i, (car, score) in enumerate(top_3_cars):
        col_target = [top_c1, top_c2, top_c3][i]
        with col_target:
            st.success(f"### {medals[i]}: {car['model']}")
            st.metric("Compatibility Match", f"{score}%")
            st.caption(f"**Generation:** {car['generation']}")
            st.markdown(f"💰 **Estimated Price:** KES {car['price_min_kes']/1e6:.1f}M – {car['price_max_kes']/1e6:.1f}M")
            st.markdown(f"⛽ **Fuel Economy:** ~{car['fuel_economy_kml']} km/L ({car['fuel_type']})")
            st.markdown(f"📏 **Ground Clearance:** {car['ground_clearance_mm']} mm")
            st.markdown(f"🔩 **Parts Availability:** {car['parts_score']} / 100")
            st.markdown(f"👨‍🔧 **Mechanic Score:** {car['mechanic_score']} / 100")
            st.markdown(f"⚙️ **Best Engine:** `{car['best_engine']}`")

            with st.expander("🔍 Pros & Watch-outs"):
                st.write(f"**Pros in Kenya:** {car['pros']}")
                st.warning(f"**Mechanic Watch-out:** {car['cons_and_watchouts']}")
                st.info(f"**Target Persona:** {car['ideal_persona']}")

    st.markdown("---")
    st.subheader("🥈 Honorable Mentions / Alternative Contenders")
    runner_ups = matched_results[3:7]
    r_cols = st.columns(len(runner_ups))
    for j, (r_car, r_score) in enumerate(runner_ups):
        with r_cols[j]:
            st.info(f"**{r_car['model']}** ({r_score}%)")
            st.caption(f"{r_car['generation']} | {r_car['body_type']}")
            st.write(f"KES {r_car['price_min_kes']/1e6:.1f}M – {r_car['price_max_kes']/1e6:.1f}M")
            st.write(f"Ground: {r_car['ground_clearance_mm']} mm | {r_car['fuel_economy_kml']} km/L")


# =============================================================
# TAB 2: HEAD-TO-HEAD RIVAL COMPARISON
# =============================================================
with tab_h2h:
    st.subheader("⚔️ Head-to-Head Rival Comparison Engine")
    st.markdown(
        "Compare any 2 or 3 rival car models side-by-side to settle the classic Kenyan debates "
        "*(e.g. Mazda CX-5 vs Toyota RAV4 vs Subaru Forester)*."
    )

    model_names = [c["model"] for c in CAR_MODELS]
    h_col1, h_col2, h_col3 = st.columns(3)
    with h_col1:
        sel_car_1 = st.selectbox("Select Contender #1:", options=model_names, index=12)  # CX-5
    with h_col2:
        sel_car_2 = st.selectbox("Select Contender #2:", options=model_names, index=5)   # RAV4
    with h_col3:
        sel_car_3 = st.selectbox("Select Contender #3 (Optional):", options=["None"] + model_names, index=25)  # Forester

    car1_obj = next(c for c in CAR_MODELS if c["model"] == sel_car_1)
    car2_obj = next(c for c in CAR_MODELS if c["model"] == sel_car_2)
    car3_obj = next(c for c in CAR_MODELS if c["model"] == sel_car_3) if sel_car_3 != "None" else None

    # Side-by-side spec comparison table
    compare_cars = [car1_obj, car2_obj]
    if car3_obj:
        compare_cars.append(car3_obj)

    spec_rows = [
        ("Brand & Model", [c["model"] for c in compare_cars]),
        ("Generation", [c["generation"] for c in compare_cars]),
        ("Price Range (KES)", [f"KES {c['price_min_kes']/1e6:.1f}M - {c['price_max_kes']/1e6:.1f}M" for c in compare_cars]),
        ("Ground Clearance (mm)", [f"{c['ground_clearance_mm']} mm" for c in compare_cars]),
        ("Fuel Economy (km/L)", [f"{c['fuel_economy_kml']} km/L" for c in compare_cars]),
        ("Fuel Type", [c["fuel_type"] for c in compare_cars]),
        ("Engine Capacity", [f"{c['engine_cc']} cc" for c in compare_cars]),
        ("Transmission", [c["transmission"] for c in compare_cars]),
        ("Drivetrain", [c["drivetrain"] for c in compare_cars]),
        ("Parts Availability Score", [f"{c['parts_score']} / 100" for c in compare_cars]),
        ("Mechanic Familiarity", [f"{c['mechanic_score']} / 100" for c in compare_cars]),
        ("Maintenance Cost Tier", [c["maintenance_tier"] for c in compare_cars]),
        ("Recommended Engine", [c["best_engine"] for c in compare_cars]),
        ("Key Strength in Kenya", [c["pros"] for c in compare_cars]),
        ("Mechanic Watch-out", [c["cons_and_watchouts"] for c in compare_cars]),
    ]

    comp_df = pd.DataFrame({row[0]: row[1] for row in spec_rows}).T
    comp_df.columns = [c["model"] for c in compare_cars]
    st.table(comp_df)

    # RADAR CHART
    st.markdown("#### Multi-Dimensional Radar Comparison")
    radar_categories = ["Ground Clearance", "Fuel Economy", "Parts Availability", "Mechanic Familiarity", "Price Affordability"]

    fig_radar = go.Figure()

    for c in compare_cars:
        # Normalize scores to 0-100 for clean radar visualization
        clearance_norm = min(100, (c["ground_clearance_mm"] / 230) * 100)
        fuel_norm = min(100, (c["fuel_economy_kml"] / 24) * 100)
        price_afford_norm = max(20, 100 - (c["price_min_kes"] / 7000000 * 80))
        r_values = [clearance_norm, fuel_norm, c["parts_score"], c["mechanic_score"], price_afford_norm]
        r_values.append(r_values[0])  # Close loop

        fig_radar.add_trace(go.Scatterpolar(
            r=r_values,
            theta=radar_categories + [radar_categories[0]],
            fill="toself",
            name=c["model"],
        ))

    fig_radar.update_layout(
        polar=dict(radialaxis=dict(visible=True, range=[0, 100])),
        showlegend=True,
        height=480,
    )
    st.plotly_chart(fig_radar, width="stretch")


# =============================================================
# TAB 3: 3-YEAR TCO & FUEL ECONOMICS
# =============================================================
with tab_tco:
    st.subheader("💰 Kenyan 3-Year Total Cost of Ownership (TCO) & Fuel Calculator")
    st.markdown(
        "Buying the car is only 50% of the cost. Calculate the **real monthly running cost** in Kenya "
        "including EPRA fuel pricing, comprehensive insurance, servicing, tyres, and depreciation."
    )

    tco_c1, tco_c2, tco_c3 = st.columns(3)
    with tco_c1:
        tco_selected_car_name = st.selectbox("Select Car Model for TCO Analysis:", options=model_names, index=12)
        tco_car = next(c for c in CAR_MODELS if c["model"] == tco_selected_car_name)
    with tco_c2:
        commute_daily_km = st.slider("Daily Commute Roundtrip (km):", min_value=5, max_value=150, value=45, step=5,
                                     help="e.g. Rongai to Upper Hill = 45 km, Thika to Westlands = 90 km.")
    with tco_c3:
        weekend_monthly_km = st.slider("Monthly Weekend / Upcountry Trips (km):", min_value=50, max_value=2000, value=300, step=50,
                                       help="e.g. Monthly trip to Naivasha/Machakos/Nakuru.")

    tco_data = calculate_tco(tco_car, commute_daily_km, weekend_monthly_km, years=3)

    # Metric Cards
    m1, m2, m3, m4 = st.columns(4)
    with m1:
        st.metric("Total Monthly Running Cost", f"KES {tco_data['monthly_running_cost_kes']:,}")
    with m2:
        st.metric("Monthly Fuel Bill", f"KES {tco_data['monthly_fuel_kes']:,}")
    with m3:
        st.metric("Monthly Insurance", f"KES {tco_data['monthly_insurance_kes']:,}")
    with m4:
        st.metric("Cost per Kilometer", f"KES {tco_data['cost_per_km_kes']} / km")

    # 3-Year Cost Breakdown Pie/Bar
    col_t1, col_t2 = st.columns(2)
    with col_t1:
        tco_breakdown_df = pd.DataFrame({
            "Cost Category": ["Fuel (3 Years)", "Comprehensive Insurance (3 Years)", "Routine Servicing & Tyres (3 Years)", "Depreciation Loss (3 Years)"],
            "Amount (KES)": [tco_data["total_fuel_3yr"], tco_data["total_insurance_3yr"], tco_data["total_maintenance_3yr"], tco_data["total_depreciation_3yr"]],
        })
        fig_tco_donut = px.pie(
            tco_breakdown_df,
            names="Cost Category",
            values="Amount (KES)",
            hole=0.45,
            title=f"3-Year Ownership Cost Breakdown: {tco_car['model']}",
            color_discrete_sequence=px.colors.qualitative.Bold,
        )
        fig_tco_donut.update_traces(textinfo="percent+label")
        st.plotly_chart(fig_tco_donut, width="stretch")

    with col_t2:
        st.markdown(f"#### 📊 3-Year Financial Summary for {tco_car['model']}")
        st.write(f"- **Estimated Car Purchase Price:** KES {tco_data['car_price_avg']:,.0f}")
        st.write(f"- **Total Mileage Driven over 3 Years:** {tco_data['annual_total_km'] * 3:,.0f} km")
        st.write(f"- **Total Fuel Spend (3 Years):** KES {tco_data['total_fuel_3yr']:,}")
        st.write(f"- **Total Insurance Spend (3 Years):** KES {tco_data['total_insurance_3yr']:,}")
        st.write(f"- **Total Servicing & Tyres (3 Years):** KES {tco_data['total_maintenance_3yr']:,}")
        st.write(f"- **Expected Residual Resale Value after 3 Years:** KES {tco_data['residual_value_3yr']:,}")
        st.success(f"**Total 3-Year Cost of Ownership:** KES {tco_data['total_ownership_3yr']:,}")


# =============================================================
# TAB 4: PRE-PURCHASE INSPECTION (LEMON DETECTOR)
# =============================================================
with tab_ppi:
    st.subheader("🔍 Pre-Purchase Inspection (PPI) 'Lemon Detector' Checklist")
    st.markdown(
        "Take this interactive digital checklist with you to car yards on Kiambu Rd, Ngong Rd, or Mombasa Rd. "
        "Identify rolled-back odometers, accident salvage cover-ups, and blown transmissions before parting with your money."
    )

    passes = []
    fails = []

    for section in INSPECTION_SECTIONS:
        st.markdown(f"### {section['category']}")
        for item in section["items"]:
            ic1, ic2 = st.columns([3, 1])
            with ic1:
                st.write(f"**{item['label']}**")
                st.caption(f"ℹ️ {item['guide']}")
                st.markdown(f"🚨 *Red Flag: {item['red_flag']}*")
            with ic2:
                status = st.radio(
                    f"Result ({item['id']}):",
                    options=["Pass ✅", "Fail ❌", "Not Tested"],
                    key=f"ppi_{item['id']}",
                    horizontal=True,
                )
                if status == "Pass ✅":
                    passes.append(item["id"])
                elif status == "Fail ❌":
                    fails.append(item["id"])
        st.markdown("---")

    report = score_inspection(passes, fails)

    st.subheader("📋 Inspection Scorecard & Risk Verdict")
    sc1, sc2, sc3 = st.columns(3)
    with sc1:
        st.metric("Vehicle Health Score", f"{report['score_pct']}%")
    with sc2:
        st.metric("Tests Passed", f"{report['passes_count']}")
    with sc3:
        st.metric("Critical Fails", f"{len(report['critical_fails'])}")

    if report["verdict_color"] == "red":
        st.error(f"### {report['verdict']}\n{report['advice']}")
    elif report["verdict_color"] == "orange":
        st.warning(f"### {report['verdict']}\n{report['advice']}")
    else:
        st.success(f"### {report['verdict']}\n{report['advice']}")


# =============================================================
# TAB 5: KIRINYAGA ROAD SPARES LOCATOR
# =============================================================
with tab_spares:
    st.subheader("🔩 Kirinyaga Road, Grogan & Industrial Area Spares Locator")
    st.markdown(
        "Search high-demand spare parts in Kenya, compare price tiers (**Genuine OEM** vs **Quality Japanese Aftermarket** vs **Ex-Japan Used**), "
        "and find the exact Nairobi streets and corridors where parts are stocked."
    )

    sp_col1, sp_col2 = st.columns([2, 1])
    with sp_col1:
        sel_part_name = st.selectbox("Select Spare Part to Source:", options=list(PARTS_CATALOG.keys()))
        part_info = PARTS_CATALOG[sel_part_name]
    with sp_col2:
        st.caption("Category: " + part_info["category"])
        st.warning("Theft Factor: " + part_info["theft_factor"])

    st.info(f"💡 **Mechanic Pro Tip:** {part_info['pro_tip']}")

    # Price Table by Brand
    st.markdown("#### Estimated Retail Price Tiers in Nairobi (KES):")
    price_table_rows = []
    for brand_key, prices in part_info["prices"].items():
        price_table_rows.append({
            "Brand Group": brand_key,
            "Brand New OEM (KES)": f"KES {prices['OEM_New']:,}",
            "Quality Aftermarket (555/KYB)": f"KES {prices['Aftermarket']:,}",
            "Ex-Japan Tested Used (KES)": f"KES {prices['ExJapan_Used']:,}" if prices["ExJapan_Used"] > 0 else "N/A (Buy New)",
        })
    st.table(pd.DataFrame(price_table_rows))

    st.markdown("#### Recommended Nairobi Sourcing Hubs:")
    for hub in part_info["recommended_hubs"]:
        st.write(f"- 📍 {hub}")

    st.markdown("---")
    st.subheader("🗺️ Guide to Kenya's Automotive Spares Corridors")
    for corridor in CORRIDORS_GUIDE:
        with st.expander(f"📍 {corridor['name']}"):
            st.write(f"**Speciality:** {corridor['speciality']}")
            st.write(f"**Best for:** {corridor['best_for']}")
            st.info(f"**Bargaining & Quality Tip:** {corridor['bargaining_tip']}")


# =============================================================
# TAB 6: KRA 8-YEAR RULE & IMPORT DUTY
# =============================================================
with tab_duty:
    st.subheader("🚢 KRA 8-Year Age Rule & Import Duty Calculator")
    st.markdown(
        "Kenya strictly enforces an **8-year age limit** on imported vehicles. "
        "Calculate whether your target car is eligible for import and estimate KRA customs duties, port clearing, and landed costs in KES."
    )

    d_col1, d_col2, d_col3 = st.columns(3)
    with d_col1:
        imp_year = st.number_input("Year of Manufacture / First Registration:", min_value=2014, max_value=2026, value=2018)
    with d_col2:
        imp_crsp = st.number_input("KRA CRSP Value (Original Showroom Price in KES):", min_value=1000000, max_value=30000000, value=3500000, step=250000)
    with d_col3:
        imp_engine = st.number_input("Engine Capacity (cc):", min_value=600, max_value=6000, value=1998, step=100)

    duty_result = calculate_kra_import_duty(imp_crsp, int(imp_year), int(imp_engine))

    if not duty_result.get("is_allowed", False):
        st.error(duty_result["error"])
    else:
        st.success(f"✅ **ELIGIBLE FOR IMPORT:** Vehicle manufactured in {imp_year} meets Kenya's 8-year age requirement.")

        k1, k2, k3, k4 = st.columns(4)
        with k1:
            st.metric("Total Landed Cost in Kenya", f"KES {duty_result['total_landed_cost_kes']:,}")
        with k2:
            st.metric("Total KRA Taxes Payable", f"KES {duty_result['total_taxes_kes']:,}")
        with k3:
            st.metric("Depreciation Allowed", f"{duty_result['depreciation_pct']}%")
        with k4:
            st.metric("Customs Value", f"KES {duty_result['customs_value_kes']:,}")

        # Tax Breakdown Table
        tax_breakdown = [
            ("Import Duty (35%)", f"KES {duty_result['import_duty_kes']:,}"),
            ("Excise Duty", f"KES {duty_result['excise_duty_kes']:,}"),
            ("Value Added Tax (16% VAT)", f"KES {duty_result['vat_kes']:,}"),
            ("Import Declaration Fee (2.5% IDF)", f"KES {duty_result['idf_kes']:,}"),
            ("Railway Development Levy (1.5% RDL)", f"KES {duty_result['rdl_kes']:,}"),
            ("Port, CFS, Radiation & NTSA Registration", f"KES {duty_result['port_and_clearing_kes']:,}"),
            ("Estimated CIF Japan Purchase & Shipping", f"KES {duty_result['cif_japan_kes']:,}"),
            ("TOTAL ESTIMATED LANDED COST (KES)", f"KES {duty_result['total_landed_cost_kes']:,}"),
        ]
        st.table(pd.DataFrame(tax_breakdown, columns=["Cost Component", "Amount in KES"]))


# =============================================================
# TAB 7: 50+ CAR MODELS CATALOG
# =============================================================
with tab_models_catalog:
    st.subheader("🚘 Kenya's Top 50+ Car Models Database (2015 – 2026)")
    st.markdown("Explore and compare all 54 mainstream car models sold and driven across Kenya.")

    models_df = pd.DataFrame(CAR_MODELS)
    fcol1, fcol2, fcol3 = st.columns(3)
    with fcol1:
        cat_brands = sorted(list(models_df["brand"].unique()))
        sel_cat_brand = st.multiselect("Filter by Brand:", options=cat_brands, default=cat_brands)
    with fcol2:
        cat_body = sorted(list(models_df["body_type"].unique()))
        sel_cat_body = st.multiselect("Filter by Body Type:", options=cat_body, default=cat_body)
    with fcol3:
        max_catalog_budget = st.slider("Filter Price Ceiling (KES):", min_value=1000000, max_value=25000000, value=25000000, step=500000, format="KES %d")

    filtered_models = models_df[
        (models_df["brand"].isin(sel_cat_brand))
        & (models_df["body_type"].isin(sel_cat_body))
        & (models_df["price_min_kes"] <= max_catalog_budget)
    ]

    st.markdown("#### Market Positioning: Ground Clearance vs. Fuel Economy vs. Price")
    fig_models = px.scatter(
        filtered_models,
        x="ground_clearance_mm",
        y="fuel_economy_kml",
        size=[p / 1e5 for p in filtered_models["price_min_kes"]],
        color="brand",
        text="model",
        hover_data=["generation", "price_min_kes", "price_max_kes", "parts_score", "best_engine"],
        labels={"ground_clearance_mm": "Ground Clearance (mm)", "fuel_economy_kml": "Fuel Economy (km/L)"},
    )
    fig_models.update_traces(textposition="top center")
    fig_models.add_vline(x=190, line_dash="dash", line_color="orange", annotation_text="190mm SUV Threshold")
    fig_models.update_layout(height=520)
    st.plotly_chart(fig_models, width="stretch")

    catalog_display_cols = [
        "model", "brand", "generation", "body_type", "price_min_kes", "price_max_kes",
        "ground_clearance_mm", "fuel_economy_kml", "fuel_type", "engine_cc",
        "parts_score", "mechanic_score", "maintenance_tier", "best_engine",
    ]
    st.dataframe(
        filtered_models[catalog_display_cols],
        width="stretch",
        column_config={
            "price_min_kes": st.column_config.NumberColumn("Min Price (KES)", format="KES %d"),
            "price_max_kes": st.column_config.NumberColumn("Max Price (KES)", format="KES %d"),
            "ground_clearance_mm": st.column_config.NumberColumn("Clearance (mm)"),
            "fuel_economy_kml": st.column_config.NumberColumn("Fuel (km/L)"),
            "parts_score": st.column_config.ProgressColumn("Spares Ease", min_value=0, max_value=100),
            "mechanic_score": st.column_config.ProgressColumn("Mechanic Score", min_value=0, max_value=100),
        },
        height=450,
    )


# =============================================================
# TAB 8: THE DATA STORY
# =============================================================
with tab_story:
    st.subheader("Buying a Car in Kenya: The Reality of Garages and Spare Parts")
    col_s1, col_s2, col_s3 = st.columns(3)
    with col_s1:
        st.info("### 🥇 Tier 1: The Ubiquitous\n**Toyota, Isuzu, Suzuki**\n\n- **Parts:** In every duka.\n- **Mechanics:** 98% familiarity.\n- **Turnaround:** Same-day repairs.")
    with col_s2:
        st.success("### 🥈 Tier 2: The Modern Contenders\n**Mazda, Nissan, Subaru, Honda**\n\n- **Parts:** Abundant in Nairobi/Mombasa.\n- **Mechanics:** Requires knowledgeable indie shops.")
    with col_s3:
        st.warning("### 🥉 Tier 3: European Prestige\n**Mercedes, BMW, VW, Range Rover**\n\n- **Parts:** Specialized importers.\n- **Mechanics:** Dedicated European diagnostic shops.")

    st.markdown("---")
    st.subheader("1. The Kenyan Garage Matrix: Availability vs. Technician Familiarity")

    brand_rows = []
    for b_name, b_info in BRANDS_DATA.items():
        brand_rows.append({
            "Brand": b_name,
            "Parts Availability Index (0-100)": b_info["parts_availability_index"],
            "Mechanic Familiarity (0-100)": b_info["mechanic_familiarity"],
            "Upcountry Reliability": b_info["upcountry_reliability"],
            "Cost Multiplier": b_info["cost_multiplier"],
            "Cost Tier": b_info["cost_tier"],
            "Origin": b_info["origin"],
            "Verdict": b_info["recommended_verdict"],
        })
    brands_df = pd.DataFrame(brand_rows)

    fig_quad = px.scatter(
        brands_df,
        x="Parts Availability Index (0-100)",
        y="Mechanic Familiarity (0-100)",
        text="Brand",
        color="Origin",
        size=[b["Cost Multiplier"] * 15 for _, b in brands_df.iterrows()],
        hover_data=["Verdict", "Cost Tier", "Upcountry Reliability"],
    )
    fig_quad.update_traces(textposition="top center")
    fig_quad.add_hline(y=75, line_dash="dot", line_color="gray", annotation_text="High Familiarity")
    fig_quad.add_vline(x=75, line_dash="dot", line_color="gray", annotation_text="High Spares Availability")
    fig_quad.update_layout(height=500)
    st.plotly_chart(fig_quad, width="stretch")

    st.markdown("---")
    st.subheader("2. Kirinyaga Road Price Basket Comparison (KES)")
    basket_records = []
    for b_name, b_info in BRANDS_DATA.items():
        for item, price in b_info["basket_prices_kes"].items():
            basket_records.append({"Brand": b_name, "Spare Part": item, "Price (KES)": price, "Origin": b_info["origin"]})
    basket_df = pd.DataFrame(basket_records)

    selected_part = st.selectbox("Select Spare Part to Compare Across Brands:", options=sorted(list(basket_df["Spare Part"].unique())), index=0)
    part_slice = basket_df[basket_df["Spare Part"] == selected_part].sort_values("Price (KES)")
    fig_part = px.bar(part_slice, x="Brand", y="Price (KES)", color="Price (KES)", color_continuous_scale="Reds", text="Price (KES)")
    fig_part.update_traces(texttemplate="KES %{text:,.0f}", textposition="outside")
    fig_part.update_layout(height=420)
    st.plotly_chart(fig_part, width="stretch")


# =============================================================
# TAB 9: INTERACTIVE MAP
# =============================================================
with tab_map:
    col1, col2, col3, col4 = st.columns(4)
    with col1:
        st.metric("Total Garages & Spares", len(filtered_df))
    with col2:
        with_phone_cnt = len(filtered_df[filtered_df["phone"].str.len() > 2]) if not filtered_df.empty else 0
        st.metric("Contactable (With Phone)", f"{with_phone_cnt} ({int(with_phone_cnt / max(len(filtered_df), 1) * 100)}%)")
    with col3:
        unique_counties = filtered_df["search_area"].nunique() if not filtered_df.empty else 0
        st.metric("Counties Mapped", unique_counties)
    with col4:
        top_cat = filtered_df["category"].mode()[0] if not filtered_df.empty else "N/A"
        st.metric("Dominant Facility", CATEGORY_CONFIG.get(top_cat, {}).get("label", top_cat))

    if filtered_df.empty:
        st.info("No places match your selected filters.")
    else:
        center_lat = filtered_df["lat"].mean()
        center_lng = filtered_df["lng"].mean()
        m = folium.Map(location=[center_lat, center_lng], zoom_start=10, tiles="OpenStreetMap", control_scale=True)
        cluster = MarkerCluster(name="Garages & Spares Cluster").add_to(m)

        for _, row in filtered_df.iterrows():
            cat = row.get("category", "auto_repair")
            cfg = CATEGORY_CONFIG.get(cat, CATEGORY_CONFIG["auto_repair"])
            phone_html = f"<p style='margin:4px 0;'>📞 <b>Phone:</b> <a href='tel:{row['phone']}'>{row['phone']}</a></p>" if row.get("phone") else ""
            address_html = f"<p style='margin:4px 0;'>📍 <b>Address:</b> {row['address']}</p>" if row.get("address") else ""
            brand_html = f"<p style='margin:4px 0;'>🏷️ <b>Brand Focus:</b> {row['brand_specialization']}</p>" if row.get("brand_specialization") else ""
            gmaps_url = f"https://www.google.com/maps/search/?api=1&query={row['lat']},{row['lng']}"

            popup_content = f"""
            <div style="font-family: Arial, sans-serif; font-size: 13px; line-height: 1.4; min-width: 220px;">
                <h4 style="margin: 0 0 6px 0; color: #1f2937;">{row['name']}</h4>
                <span style="display:inline-block; padding: 2px 8px; border-radius: 4px; background:#f3f4f6; color:#374151; font-weight:bold; font-size:11px; margin-bottom:6px;">
                    {cfg['badge']}
                </span>
                {phone_html}
                {address_html}
                {brand_html}
                <hr style="margin: 8px 0; border: none; border-top: 1px solid #e5e7eb;">
                <div style="display:flex; justify-content: space-between;">
                    <a href="{gmaps_url}" target="_blank" style="color: #2563eb; text-decoration: none; font-weight: bold;">Google Maps ↗</a>
                    <a href="{row.get('osm_url', '#')}" target="_blank" style="color: #4b5563; text-decoration: none;">OSM Profile ↗</a>
                </div>
            </div>
            """
            folium.Marker(
                location=[row["lat"], row["lng"]],
                popup=folium.Popup(popup_content, max_width=320),
                tooltip=f"{row['name']} ({cfg['label']})",
                icon=folium.Icon(color=cfg["color"], icon=cfg["icon"], prefix="fa"),
            ).add_to(cluster)

        st_folium(m, width="100%", height=560, returned_objects=[])


# =============================================================
# TAB 10: MARKET & COUNTY ANALYTICS
# =============================================================
with tab_analytics:
    st.subheader("Geographical Distribution & Automotive Infrastructure")
    if filtered_df.empty:
        st.info("No data available.")
    else:
        col_c1, col_c2 = st.columns(2)
        with col_c1:
            cat_counts = filtered_df["category"].value_counts().reset_index()
            cat_counts.columns = ["Category", "Count"]
            cat_counts["Category Label"] = cat_counts["Category"].map(lambda c: CATEGORY_CONFIG.get(c, {}).get("badge", c))
            fig_donut = px.pie(cat_counts, names="Category Label", values="Count", hole=0.45, title="Service Type Breakdown")
            st.plotly_chart(fig_donut, width="stretch")
        with col_c2:
            area_counts = filtered_df["search_area"].value_counts().reset_index()
            area_counts.columns = ["Area", "Count"]
            fig_bar = px.bar(area_counts, x="Count", y="Area", orientation="h", title="Garages & Spares by County / Region", color="Count", color_continuous_scale="Blues")
            fig_bar.update_layout(yaxis=dict(autorange="reversed"))
            st.plotly_chart(fig_bar, width="stretch")


# =============================================================
# TAB 11: DIRECTORY & EXPORT
# =============================================================
with tab_directory:
    st.subheader("Browse Garage Directory")
    display_cols = ["name", "category", "brand_specialization", "search_area", "phone", "address", "lat", "lng", "osm_url"]
    valid_cols = [c for c in display_cols if c in filtered_df.columns]
    st.dataframe(
        filtered_df[valid_cols],
        width="stretch",
        column_config={
            "osm_url": st.column_config.LinkColumn("OSM Link", display_text="View on OSM"),
            "lat": st.column_config.NumberColumn(format="%.5f"),
            "lng": st.column_config.NumberColumn(format="%.5f"),
        },
        height=450,
    )
    st.markdown("---")
    dcol1, dcol2 = st.columns(2)
    with dcol1:
        st.download_button(
            label="💾 Download Filtered CSV (Excel compatible)",
            data=filtered_df.to_csv(index=False, encoding="utf-8-sig"),
            file_name="kenya_garages_filtered.csv",
            mime="text/csv",
            width="stretch",
        )
    with dcol2:
        geojson_features = []
        for _, r in filtered_df.iterrows():
            geojson_features.append({
                "type": "Feature",
                "geometry": {"type": "Point", "coordinates": [float(r["lng"]), float(r["lat"])]},
                "properties": {k: v for k, v in r.items() if k not in ("lat", "lng")},
            })
        st.download_button(
            label="🌐 Download Filtered GeoJSON (GIS / Mapbox)",
            data=json.dumps({"type": "FeatureCollection", "features": geojson_features}, indent=2),
            file_name="kenya_garages_filtered.geojson",
            mime="application/geo+json",
            width="stretch",
        )
