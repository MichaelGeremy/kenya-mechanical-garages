"""
app.py
Kenya Mechanical Garages, Auto Workshops & Car Brand Intelligence Explorer
A data-driven interactive application to map garages, evaluate car brand performance,
and guide new car buyers on spare parts availability across Kenya.
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

from brand_data import BRANDS_DATA, get_recommendation

# Page setup
st.set_page_config(
    page_title="Kenya Garages & Car Brand Explorer",
    page_icon="🚗",
    layout="wide",
    initial_sidebar_state="expanded",
)

DATA_PATH = os.path.join("data", "kenya_garages.csv")

CATEGORY_CONFIG = {
    "auto_repair": {
        "label": "Auto Repair / Garage",
        "color": "red",
        "icon": "wrench",
        "badge": "🚗 Auto Repair",
    },
    "motorcycle_repair": {
        "label": "Motorcycle / Boda Boda",
        "color": "green",
        "icon": "motorcycle",
        "badge": "🏍️ Motorcycle Repair",
    },
    "tyres": {
        "label": "Tyre Center",
        "color": "orange",
        "icon": "circle",
        "badge": "🛞 Tyres",
    },
    "auto_spares": {
        "label": "Auto Spares / Parts",
        "color": "purple",
        "icon": "cog",
        "badge": "🔧 Spares & Parts",
    },
    "jua_kali_craft": {
        "label": "Jua Kali Welder / Artisan",
        "color": "darkblue",
        "icon": "fire",
        "badge": "🔨 Jua Kali / Metal",
    },
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
    """Load and sanitize garage dataset."""
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
    """Fetch live points from OpenStreetMap via Overpass API."""
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
            req = urllib.request.Request(
                mirror,
                data=data,
                headers={"User-Agent": "KenyaGaragesExplorer/2.0"}
            )
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
        if elem_type == "node":
            lat, lon = elem.get("lat"), elem.get("lon")
        else:
            center = elem.get("center", {})
            lat, lon = center.get("lat"), center.get("lon")

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


# Load existing dataset
df = load_data(DATA_PATH)

# -------------------------------------------------------------
# APPLICATION HEADER
# -------------------------------------------------------------
st.title("🇰🇪 Kenya Mechanical Garages & Car Brand Intelligence")
st.markdown(
    "**The Ultimate Guide for Kenya Car Buyers:** Discover how car brands perform in Kenyan garages, "
    "benchmark spare parts availability, avoid costly maintenance traps, and explore real repair facilities nationwide."
)

# -------------------------------------------------------------
# SIDEBAR FILTERS & CONTROLS
# -------------------------------------------------------------
with st.sidebar:
    st.image(
        "https://images.unsplash.com/photo-1486006920555-c77dce18193b?auto=format&fit=crop&w=400&q=80",
        caption="Kenya Auto Market & Garage Intelligence",
    )
    st.header("🔍 Global Search & Filters")

    search_query = st.text_input("Search Garage, Street, or Brand", placeholder="e.g. Toyota, Kirinyaga, Ngong...")

    # Filter by County / Search Area
    all_areas = sorted([a for a in df["search_area"].unique() if a]) if not df.empty else []
    selected_areas = st.multiselect(
        "County / Search Area",
        options=all_areas,
        default=all_areas,
        help="Filter places by county or region"
    )

    # Filter by Service Category
    all_categories = list(CATEGORY_CONFIG.keys())
    selected_categories = st.multiselect(
        "Service Category",
        options=all_categories,
        default=all_categories,
        format_func=lambda x: CATEGORY_CONFIG.get(x, {}).get("badge", x),
    )

    only_with_phone = st.checkbox("📞 Only places with phone numbers", value=False)

    st.markdown("---")

    # LIVE OVERPASS HARVESTER
    st.subheader("🌐 In-App Data Harvester")
    st.caption("Pull live garage and spares locations from OpenStreetMap without API keys.")

    fetch_area = st.selectbox("Select County to Harvest", options=list(DEFAULT_COUNTY_BBOXES.keys()))
    harvest_juakali = st.checkbox("Include Jua Kali artisans", value=True)
    harvest_spares = st.checkbox("Include Auto Spares stores", value=True)

    if st.button("🚀 Harvest Live from OSM", width="stretch"):
        with st.spinner(f"Harvesting live data for {fetch_area}..."):
            bbox = DEFAULT_COUNTY_BBOXES[fetch_area]
            clean_name = fetch_area.split(" ")[0]
            new_places = fetch_from_osm(
                bbox,
                search_area=clean_name,
                include_juakali=harvest_juakali,
                include_spares=harvest_spares,
            )
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


# -------------------------------------------------------------
# FILTERING PIPELINE
# -------------------------------------------------------------
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


# -------------------------------------------------------------
# MAIN APPLICATION TABS
# -------------------------------------------------------------
tab_story, tab_matchmaker, tab_map, tab_analytics, tab_directory = st.tabs([
    "📖 The Kenyan Car Buyer's Data Story",
    "🎯 New Car Finder Matchmaker",
    "🗺️ Interactive Garages & Spares Map",
    "📊 Market & County Analytics",
    "📋 Directory & Data Export",
])

# =============================================================
# TAB 1: THE DATA STORY
# =============================================================
with tab_story:
    st.subheader("Buying a Car in Kenya: The Reality of Garages and Spare Parts")
    st.markdown("""
    > *"In Kenya, you don't just buy a car because of its brochure; you buy the car that can survive Kenyan roads and be fixed by your local mechanic without stranding you for weeks."*
    """)

    # Story chapter 1
    col_s1, col_s2, col_s3 = st.columns(3)
    with col_s1:
        st.info("### 🥇 Tier 1: The Ubiquitous\n**Toyota, Isuzu, Suzuki**\n\n- **Parts:** In every duka from Mombasa to Lodwar.\n- **Mechanics:** 98% familiarity.\n- **Turnaround:** Same-day repairs.\n- **Downside:** High purchase premium & street theft.")
    with col_s2:
        st.success("### 🥈 Tier 2: The Modern Contenders\n**Mazda, Nissan, Subaru, Honda**\n\n- **Parts:** Abundant in Nairobi/Mombasa, moderate upcountry.\n- **Mechanics:** Requires knowledgeable indie shops.\n- **Turnaround:** 1-2 days for niche parts.\n- **Downside:** Sensitive gearboxes/cooling.")
    with col_s3:
        st.warning("### 🥉 Tier 3: European Prestige\n**Mercedes, BMW, VW, Range Rover**\n\n- **Parts:** Specialized Nairobi importers.\n- **Mechanics:** Dedicated European diagnostic shops.\n- **Turnaround:** Often 3-7 days for sensors/bags.\n- **Downside:** Heavy maintenance bills.")

    st.markdown("---")

    # QUADRANT CHART: Parts Availability vs Mechanic Familiarity
    st.subheader("1. The Kenyan Garage Matrix: Availability vs. Technician Familiarity")
    st.caption("How easily can you find spare parts vs. finding a mechanic who knows the engine without guessing?")

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
        title="Kenyan Market Positioning (Bubble size = Relative Maintenance Cost)",
    )
    fig_quad.update_traces(textposition="top center", marker=dict(line=dict(width=1, color="DarkSlateGrey")))
    # Add quadrant reference lines
    fig_quad.add_hline(y=75, line_dash="dot", line_color="gray", annotation_text="High Familiarity Threshold")
    fig_quad.add_vline(x=75, line_dash="dot", line_color="gray", annotation_text="High Spares Availability Threshold")
    fig_quad.update_layout(height=520)
    st.plotly_chart(fig_quad, width="stretch")

    st.markdown("---")

    # BASKET OF SPARE PARTS COMPARISON
    st.subheader("2. Kirinyaga Road Price Basket Comparison (KES)")
    st.caption(
        "Estimated average retail prices in Nairobi auto spares corridors (Kirinyaga Rd, Grogan, Baricho Rd) "
        "for routine service and wear-and-tear items."
    )

    basket_records = []
    for b_name, b_info in BRANDS_DATA.items():
        for item, price in b_info["basket_prices_kes"].items():
            basket_records.append({
                "Brand": b_name,
                "Spare Part": item,
                "Price (KES)": price,
                "Origin": b_info["origin"],
            })
    basket_df = pd.DataFrame(basket_records)

    selected_part = st.selectbox(
        "Select Spare Part to Compare Across Brands:",
        options=sorted(list(basket_df["Spare Part"].unique())),
        index=0,
    )

    part_slice = basket_df[basket_df["Spare Part"] == selected_part].sort_values("Price (KES)")

    fig_part = px.bar(
        part_slice,
        x="Brand",
        y="Price (KES)",
        color="Price (KES)",
        color_continuous_scale="Reds",
        text="Price (KES)",
        title=f"Comparative Price: {selected_part} Across Brands in Kenya",
    )
    fig_part.update_traces(texttemplate="KES %{text:,.0f}", textposition="outside")
    fig_part.update_layout(uniformtext_minsize=8, uniformtext_mode="hide", height=430)
    st.plotly_chart(fig_part, width="stretch")

    st.markdown("---")

    # BRAND DEEP-DIVE DOSSIERS
    st.subheader("3. Comprehensive Brand Dossiers & Mechanic Field Reports")
    selected_brand_dossier = st.selectbox(
        "Explore Detailed Brand Intelligence:",
        options=list(BRANDS_DATA.keys()),
        index=0,
    )
    b_data = BRANDS_DATA[selected_brand_dossier]

    c_d1, c_d2 = st.columns([2, 3])
    with c_d1:
        st.markdown(f"### {b_data['brand']}")
        st.caption(f"*{b_data['tagline']}*")
        st.metric("Buyer Verdict", b_data["recommended_verdict"])
        st.metric("Parts Availability Index", f"{b_data['parts_availability_index']} / 100")
        st.metric("Mechanic Familiarity", f"{b_data['mechanic_familiarity']} / 100")
        st.metric("Maintenance Cost Tier", b_data["cost_tier"])
        st.metric("Upcountry Reliability", f"{b_data['upcountry_reliability']} / 100")

    with c_d2:
        st.markdown("#### 🛠️ What Kenyan Mechanics Say:")
        st.info(b_data["mechanic_secrets"])

        st.markdown("#### 🚨 Street Theft Vulnerability in Kenya:")
        st.warning(f"**Level:** {b_data['theft_risk']} — {b_data['theft_risk_note']}")

        st.markdown("#### 🏢 Kirinyaga Road & Grogan Spares Support:")
        st.write(b_data["kirinyaga_rd_support"])

        st.markdown("#### 🚗 Top Popular Models & Recommended Engines:")
        st.write(f"**Models:** {', '.join(b_data['popular_models'])}")
        st.write(f"**Recommended Engines / Codes:** `{b_data['recommended_engines']}`")


# =============================================================
# TAB 2: NEW CAR FINDER MATCHMAKER
# =============================================================
with tab_matchmaker:
    st.subheader("🎯 The New Car Finder Matchmaker")
    st.markdown(
        "Answer 4 simple lifestyle questions to discover which car brand best matches "
        "your driving zone, maintenance budget, and spare parts availability in Kenya."
    )

    col_q1, col_q2 = st.columns(2)
    with col_q1:
        q_zone = st.selectbox(
            "1. Where will you primarily drive and live?",
            options=[
                "Nairobi / Mombasa Urban Only",
                "Frequent Upcountry / Mixed County Roads",
                "Remote / Rough Terrain / Safari",
            ],
            help="Determines upcountry parts availability and suspension durability."
        )

        q_budget = st.selectbox(
            "2. What is your monthly maintenance budget comfort?",
            options=[
                "Frugal (Under KES 10,000/month)",
                "Moderate (KES 10,000 - 25,000/month)",
                "Flexible (KES 25,000 - 50,000/month)",
                "High End (KES 50,000+/month)",
            ],
            help="Routine maintenance, oil, wear-and-tear reserve."
        )

    with col_q2:
        q_priority = st.selectbox(
            "3. What is your #1 priority for this vehicle?",
            options=[
                "Peace of Mind & Easy Resale",
                "Fuel Economy & Daily Commuting",
                "Highway Stability, Driving Joy & Speed",
                "Executive Status & Luxury Presence",
            ],
            help="What matters most to you on a day-to-day basis?"
        )

        q_tolerance = st.selectbox(
            "4. What is your tolerance if a rare spare part needs sourcing?",
            options=[
                "Zero (Must be fixed same day)",
                "1-3 Days is fine",
                "Don't mind waiting 1-2 weeks for order",
            ],
            help="How critical is vehicle downtime for your daily livelihood?"
        )

    st.markdown("---")

    recommendations = get_recommendation(q_zone, q_budget, q_priority, q_tolerance)

    st.subheader("🏆 Your Tailored Brand Compatibility Ranking")

    top_3 = recommendations[:3]
    top_cols = st.columns(3)

    medals = ["🥇 1st Choice", "🥈 2nd Choice", "🥉 3rd Choice"]
    for i, (brand_key, score) in enumerate(top_3):
        with top_cols[i]:
            b_info = BRANDS_DATA[brand_key]
            st.success(f"### {medals[i]}: {brand_key}")
            st.metric("Compatibility Match", f"{score}%")
            st.caption(f"*{b_info['tagline']}*")
            st.markdown(f"**Spares Index:** {b_info['parts_availability_index']}/100")
            st.markdown(f"**Cost Tier:** {b_info['cost_tier']}")
            st.markdown(f"**Verdict:** {b_info['recommended_verdict']}")
            st.markdown(f"**Top Engine:** `{b_info['recommended_engines']}`")

    # Detailed summary advice
    best_brand = top_3[0][0]
    best_info = BRANDS_DATA[best_brand]

    st.markdown("### 💡 Expert Advice for Your Profile:")
    st.info(
        f"Based on your driving zone in **{q_zone}** and your priority of **{q_priority}**, "
        f"**{best_brand}** offers the ideal sweet spot. {best_info['mechanic_secrets']} "
        f"Be mindful of street theft: *{best_info['theft_risk_note']}*"
    )


# =============================================================
# TAB 3: INTERACTIVE MAP
# =============================================================
with tab_map:
    # Summary chips
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

        m = folium.Map(
            location=[center_lat, center_lng],
            zoom_start=10,
            tiles="OpenStreetMap",
            control_scale=True,
        )

        cluster = MarkerCluster(name="Garages & Spares Cluster").add_to(m)

        for _, row in filtered_df.iterrows():
            cat = row.get("category", "auto_repair")
            cfg = CATEGORY_CONFIG.get(cat, CATEGORY_CONFIG["auto_repair"])

            phone_html = ""
            if row.get("phone"):
                phone_html = f"<p style='margin:4px 0;'>📞 <b>Phone:</b> <a href='tel:{row['phone']}'>{row['phone']}</a></p>"

            address_html = ""
            if row.get("address"):
                address_html = f"<p style='margin:4px 0;'>📍 <b>Address:</b> {row['address']}</p>"

            brand_html = ""
            if row.get("brand_specialization"):
                brand_html = f"<p style='margin:4px 0;'>🏷️ <b>Brand Focus:</b> {row['brand_specialization']}</p>"

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
# TAB 4: MARKET & COUNTY ANALYTICS
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
            cat_counts["Category Label"] = cat_counts["Category"].map(
                lambda c: CATEGORY_CONFIG.get(c, {}).get("badge", c)
            )

            fig_donut = px.pie(
                cat_counts,
                names="Category Label",
                values="Count",
                hole=0.45,
                title="Service Type Breakdown",
                color_discrete_sequence=px.colors.qualitative.Safe,
            )
            fig_donut.update_traces(textposition="inside", textinfo="percent+label")
            st.plotly_chart(fig_donut, width="stretch")

        with col_c2:
            area_counts = filtered_df["search_area"].value_counts().reset_index()
            area_counts.columns = ["Area", "Count"]

            fig_bar = px.bar(
                area_counts,
                x="Count",
                y="Area",
                orientation="h",
                title="Garages & Spares by County / Region",
                color="Count",
                color_continuous_scale="Blues",
            )
            fig_bar.update_layout(yaxis=dict(autorange="reversed"))
            st.plotly_chart(fig_bar, width="stretch")

        # Brand specializations mapped
        st.subheader("Brand Specialization Mentions in Kenyan Garages")
        brand_spec_counts = filtered_df["brand_specialization"].value_counts().reset_index()
        brand_spec_counts.columns = ["Specialization", "Count"]

        fig_spec = px.bar(
            brand_spec_counts.head(10),
            x="Specialization",
            y="Count",
            color="Count",
            color_continuous_scale="Teal",
            title="Top Detected Brand Specializations in Repair Facilities",
        )
        st.plotly_chart(fig_spec, width="stretch")


# =============================================================
# TAB 5: DIRECTORY & EXPORT
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
    st.subheader("📥 Export Filtered Data")
    dcol1, dcol2 = st.columns(2)

    with dcol1:
        csv_data = filtered_df.to_csv(index=False, encoding="utf-8-sig")
        st.download_button(
            label="💾 Download Filtered CSV (Excel compatible)",
            data=csv_data,
            file_name="kenya_garages_filtered.csv",
            mime="text/csv",
            width="stretch",
        )

    with dcol2:
        geojson_features = []
        for _, r in filtered_df.iterrows():
            geojson_features.append({
                "type": "Feature",
                "geometry": {
                    "type": "Point",
                    "coordinates": [float(r["lng"]), float(r["lat"])],
                },
                "properties": {k: v for k, v in r.items() if k not in ("lat", "lng")},
            })
        geojson_str = json.dumps({"type": "FeatureCollection", "features": geojson_features}, indent=2)

        st.download_button(
            label="🌐 Download Filtered GeoJSON (GIS / Mapbox)",
            data=geojson_str,
            file_name="kenya_garages_filtered.geojson",
            mime="application/geo+json",
            width="stretch",
        )
