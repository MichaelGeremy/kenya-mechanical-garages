# 🇰🇪 Kenya Mechanical Garages & Car Brand Intelligence Explorer

An interactive geospatial application, automotive market intelligence engine, and decision guide for car buyers in Kenya.

Built with **Streamlit**, **Folium**, **OpenStreetMap (Overpass API)**, and **Plotly**.

---

## 🌟 What's Inside

### 1. 📖 The Kenyan Car Buyer's Data Story
- **Market Tiers Breakdown:**
  - **Tier 1 (The Ubiquitous):** Toyota, Isuzu, Suzuki — parts in every duka, same-day repairs across all 47 counties.
  - **Tier 2 (Modern Contenders):** Mazda, Nissan, Subaru, Honda, Mitsubishi — high-tech driving dynamics, specific maintenance rules (CVT fluid, boxer cooling, SkyActiv batteries).
  - **Tier 3 (European Prestige):** Mercedes-Benz, BMW, Volkswagen/Audi, Land Rover/Range Rover — supreme comfort, specialized Nairobi corridors, higher maintenance budgets.
- **The Garage Matrix (Quadrant Chart):** Plots **Spare Parts Availability (0–100)** vs **Mechanic Familiarity (0–100)** with bubble sizes indicating relative maintenance cost multipliers.
- **Kirinyaga Road Price Basket:** Direct price comparison across brands for everyday wear-and-tear items (Oil/Air filters, Front Brake Pads, Shock Absorbers, Side Mirror assemblies, Spark Plugs, Bumpers) in Kenyan Shillings (KES).
- **Brand Dossiers & Mechanic Field Reports:** In-depth verdict, recommended engine codes, common failure points, and street theft vulnerability warnings.

### 2. 🎯 New Car Finder Matchmaker (Buyer Quiz)
- Interactive quiz tailored to the Kenyan driving context:
  1. Primary Driving Zone (Nairobi Urban vs Frequent Upcountry vs Rough/Safari)
  2. Monthly Maintenance Comfort (Frugal, Moderate, Flexible, High-End)
  3. #1 Vehicle Priority (Resale, Fuel Economy, Highway Stability, Executive Luxury)
  4. Sourcing Downtime Tolerance (Zero same-day vs 1–3 days vs import order)
- Generates a **tailored compatibility match score (%)** with the top 3 recommended brands and actionable buyer advice.

### 3. 🗺️ Interactive Garages & Spares Map
- Clustered Folium map with color-coded markers for:
  - 🚗 Auto Repair Workshops
  - 🏍️ Motorcycle / Boda Boda Mechanics
  - 🛞 Tyre Centers
  - 🔧 Auto Spares / Parts Stores
  - 🔨 Jua Kali Artisans & Welders
- Clickable popups with phone numbers, full address, brand specialization, and direct Google Maps navigation links.

### 4. 🌐 Real-Time In-App Data Harvester
- Pull live, up-to-date garage and auto spares data directly from OpenStreetMap without needing Google API keys or credit cards.

### 5. 📥 Data Export
- Download filtered datasets as Microsoft Excel-ready CSV (`.csv`) or GIS-ready GeoJSON (`.geojson`).

---

## 🚀 Quickstart

### 1. Clone & Install
```bash
git clone https://github.com/MichaelGeremy/kenya-mechanical-garages.git
cd kenya-mechanical-garages
pip install -r requirements.txt
```

### 2. Launch the Streamlit App
```bash
streamlit run app.py
```
Open `http://localhost:8501` in your browser.

---

## 📁 Repository Structure

```text
├── app.py                      # Main Streamlit web application & dashboard
├── brand_data.py               # Kenyan automotive market intelligence & parts matrix
├── kenyagaragemapper_osm.py    # Free OSM Overpass harvester CLI
├── kenyagaragemapper.py        # Official Google Places API (New) harvester CLI
├── requirements.txt            # Python dependencies
├── .gitignore                  # Git ignore rules
├── data/
│   ├── kenya_garages.csv       # Preloaded dataset with brand specializations
│   └── kenya_garages.geojson   # GeoJSON spatial feature collection
└── README.md                   # Full documentation & guide
```

---

## 📄 License
MIT License. Data derived from OpenStreetMap contributors under the Open Database License (ODbL).
