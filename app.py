"""
app.py
Kenya Mechanical Garages & Auto Workshops Explorer
An interactive Streamlit dashboard for exploring, mapping, and harvesting
auto repair businesses, mechanics, tyre centers, and Jua Kali artisans across Kenya.
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
import streamlit as st
from streamlit_folium import st_folium

# Page configuration
st.set_page_config(
    page_title="Kenya Garages Explorer",
    page_icon="🔧",
    layout="wide",
    initial_sidebar_state="expanded",
)

DATA_PATH = os.path.join("data", "kenya_garages.csv")

# Category color and icon mappings for Folium markers
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
    "https://overpass-api.de/api/interpreter",
    "https://overpass.openstreetmap.fr/api/interpreter",
    "https://lz4.overpass-api.de/api/interpreter",
]


@st.cache_data(ttl=300)
def load_data(file_path):
    """Load and sanitize garage dataset."""
    if not os.path.exists(file_path):
        return pd.DataFrame()
    df = pd.read_csv(file_path, encoding="utf-8-sig")
    # Ensure numeric coordinates
    df["lat"] = pd.to_numeric(df["lat"], errors="coerce")
    df["lng"] = pd.to_numeric(df["lng"], errors="coerce")
    df = df.dropna(subset=["lat", "lng"])
    # Clean string columns
    for col in ["name", "category", "search_area", "phone", "address", "city", "brand"]:
        if col in df.columns:
            df[col] = df[col].fillna("").astype(str)
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
                headers={"User-Agent": "KenyaGaragesExplorer/1.0"}
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


# -------------------------------------------------------------
# APPLICATION HEADER
# -------------------------------------------------------------
st.title("🇰🇪 Kenya Mechanical Garages & Auto Workshops")
st.markdown(
    "Explore, filter, and discover motor vehicle garages, mechanics, tyre centers, "
    "and Jua Kali auto workshops across Kenya."
)

# Load existing dataset
df = load_data(DATA_PATH)

# -------------------------------------------------------------
# SIDEBAR FILTERS & ACTIONS
# -------------------------------------------------------------
with st.sidebar:
    st.header("🔍 Filters & Search")

    # Search by text
    search_query = st.text_input("Search (Name, Street, Brand)", placeholder="e.g. Toyota, AutoXpress, Ngong...")

    # Filter by County / Search Area
    all_areas = sorted(list(df["search_area"].unique())) if not df.empty and "search_area" in df.columns else []
    selected_areas = st.multiselect(
        "County / Search Area",
        options=all_areas,
        default=all_areas,
        help="Filter places by county or region"
    )

    # Filter by Category
    all_categories = list(CATEGORY_CONFIG.keys())
    selected_categories = st.multiselect(
        "Service Category",
        options=all_categories,
        default=all_categories,
        format_func=lambda x: CATEGORY_CONFIG.get(x, {}).get("badge", x),
    )

    # Phone number presence toggle
    only_with_phone = st.checkbox("📞 Only show places with phone number", value=False)

    st.markdown("---")

    # LIVE OVERPASS SCRAPER INTEGRATION
    st.subheader("🌐 Live Data Ingestion")
    st.caption("Pull new live garage data from OpenStreetMap without API keys.")

    fetch_area = st.selectbox(
        "Select County to Harvest",
        options=list(DEFAULT_COUNTY_BBOXES.keys()),
    )
    harvest_juakali = st.checkbox("Include Jua Kali artisans", value=True)
    harvest_spares = st.checkbox("Include Auto Spares shops", value=True)

    if st.button("🚀 Fetch Live from OSM", use_container_width=True):
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
# DATA FILTERING LOGIC
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
        )
        filtered_df = filtered_df[mask]


# -------------------------------------------------------------
# DASHBOARD TABS
# -------------------------------------------------------------
tab_map, tab_analytics, tab_table = st.tabs(["🗺️ Interactive Map", "📊 Analytics & Insights", "📋 Directory & Export"])

# =============================================================
# TAB 1: INTERACTIVE MAP
# =============================================================
with tab_map:
    # Summary chips
    col1, col2, col3, col4 = st.columns(4)
    with col1:
        st.metric("Total Garages Showing", len(filtered_df))
    with col2:
        with_phone_cnt = len(filtered_df[filtered_df["phone"].str.len() > 2]) if not filtered_df.empty else 0
        st.metric("With Phone Number", f"{with_phone_cnt} ({int(with_phone_cnt / max(len(filtered_df), 1) * 100)}%)")
    with col3:
        unique_counties = filtered_df["search_area"].nunique() if not filtered_df.empty else 0
        st.metric("Counties / Areas", unique_counties)
    with col4:
        top_cat = filtered_df["category"].mode()[0] if not filtered_df.empty else "N/A"
        st.metric("Dominant Type", CATEGORY_CONFIG.get(top_cat, {}).get("label", top_cat))

    if filtered_df.empty:
        st.info("No garages match the selected filters. Try broadening your criteria.")
    else:
        # Calculate center point
        center_lat = filtered_df["lat"].mean()
        center_lng = filtered_df["lng"].mean()

        # Build Folium Map
        m = folium.Map(
            location=[center_lat, center_lng],
            zoom_start=11,
            tiles="OpenStreetMap",
            control_scale=True,
        )

        cluster = MarkerCluster(name="Garages Cluster").add_to(m)

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
            if row.get("brand"):
                brand_html = f"<p style='margin:4px 0;'>🏷️ <b>Brand/Speciality:</b> {row['brand']}</p>"

            gmaps_url = f"https://www.google.com/maps/search/?api=1&query={row['lat']},{row['lng']}"

            popup_content = f"""
            <div style="font-family: Arial, sans-serif; font-size: 13px; line-height: 1.4; min-width: 200px;">
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
                popup=folium.Popup(popup_content, max_width=300),
                tooltip=f"{row['name']} ({cfg['label']})",
                icon=folium.Icon(color=cfg["color"], icon=cfg["icon"], prefix="fa"),
            ).add_to(cluster)

        st_folium(m, width="100%", height=550, returned_objects=[])


# =============================================================
# TAB 2: ANALYTICS & INSIGHTS
# =============================================================
with tab_analytics:
    st.subheader("Automotive Service Distribution in Kenya")

    if filtered_df.empty:
        st.info("No data available to display charts.")
    else:
        col_c1, col_c2 = st.columns(2)

        with col_c1:
            # Breakdown by Category
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
                title="Garages by Category",
                color_discrete_sequence=px.colors.qualitative.Safe,
            )
            fig_donut.update_traces(textposition="inside", textinfo="percent+label")
            st.plotly_chart(fig_donut, use_container_width=True)

        with col_c2:
            # Breakdown by County / Search Area
            area_counts = filtered_df["search_area"].value_counts().reset_index()
            area_counts.columns = ["Area", "Count"]

            fig_bar = px.bar(
                area_counts,
                x="Count",
                y="Area",
                orientation="h",
                title="Garages by County / Search Area",
                color="Count",
                color_continuous_scale="Blues",
            )
            fig_bar.update_layout(yaxis=dict(autorange="reversed"))
            st.plotly_chart(fig_bar, use_container_width=True)

        # Phone availability distribution
        st.subheader("Contactability Rate")
        phone_available = (filtered_df["phone"].str.len() > 2).value_counts().reset_index()
        phone_available.columns = ["Has Phone", "Count"]
        phone_available["Status"] = phone_available["Has Phone"].map({True: "Phone Listed", False: "No Phone Listed"})

        fig_phone = px.bar(
            phone_available,
            x="Status",
            y="Count",
            color="Status",
            color_discrete_map={"Phone Listed": "#10b981", "No Phone Listed": "#f87171"},
            title="Business Contactability (Listed Phone)",
        )
        st.plotly_chart(fig_phone, use_container_width=True)


# =============================================================
# TAB 3: DIRECTORY & EXPORT
# =============================================================
with tab_table:
    st.subheader("Browse Garage Directory")

    display_cols = ["name", "category", "search_area", "phone", "address", "brand", "lat", "lng", "osm_url"]
    valid_cols = [c for c in display_cols if c in filtered_df.columns]

    st.dataframe(
        filtered_df[valid_cols],
        use_container_width=True,
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
            use_container_width=True,
        )

    with dcol2:
        # Convert to GeoJSON
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
            use_container_width=True,
        )
