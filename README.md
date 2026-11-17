# 🇰🇪 Kenya Mechanical Garages & Car Brand Intelligence Explorer

An interactive geospatial application, automotive market intelligence engine, and decision guide for car buyers in Kenya.

Built with **Streamlit**, **Folium**, **OpenStreetMap (Overpass API)**, and **Plotly**.

---

## 🌟 What's Inside

### 1. 🎯 Exact Car Model Matchmaker (Client Car Finder)
- Match the exact car model out of **50+ mainstream vehicles (2015 – 2026)** sold and driven in Kenya.
- Tailored match criteria:
  - **Purchase Budget (KES):** Sliders from KES 800,000 to KES 12,000,000+.
  - **Primary Purpose:** Daily Nairobi City Commute, Family Upcountry & Weekend Trips, Rough Rural Roads/Farm/Offroad, Executive Status, Business Logistics.
  - **Ground Clearance Requirement:** High (190 mm+ for speed humps & ruts) vs Standard.
  - **Body Style:** Crossover/SUV, Sedan, Hatchback, Station Wagon, Pickup, MPV, Full-size 4x4.
  - **Fuel Preference:** Petrol, Diesel, Hybrid, Any.
  - **Spare Parts Priority:** Maximum same-day nationwide vs Balanced stock.
- Generates **Top 3 Recommended Models** with:
  - Estimated price range in KES.
  - Fuel economy (km/L) & exact ground clearance (mm).
  - Parts availability & mechanic familiarity scores (0–100).
  - Best specific engine codes to buy (e.g. `1NZ-FE`, `SkyActiv-G 2.0L`, `FB20 NA`, `4JJ1-TC`).
  - Known mechanic watch-outs and common failure points.

### 2. 🚘 50+ Top Car Models in Kenya Catalog (2015 – 2026)
- Comprehensive database of **54 car models** across 12 brands:
  - **Toyota:** Fielder, Axio, Premio, Vitz, Probox/Succeed, RAV4, Harrier, Prado, Hilux, Rush, Noah/Voxy, Land Cruiser 200/300.
  - **Mazda:** CX-5, Demio, Axela, Atenza, CX-3, CX-8.
  - **Nissan:** X-Trail, Note, Serena, Wingroad, Navara, Patrol.
  - **Subaru:** Forester, Outback, XV, Impreza, Legacy.
  - **Honda:** Fit, Vezel, CR-V, Civic, Stepwgn.
  - **Isuzu:** D-Max, mu-X, N-Series commercial.
  - **Suzuki:** Alto, Swift, Jimny, Vitara.
  - **Mitsubishi:** Pajero, Outlander, RVR.
  - **Volkswagen / Audi:** Golf, Tiguan, Audi Q5.
  - **Mercedes-Benz:** C-Class, E-Class, GLE.
  - **BMW:** 3 Series, X3.
  - **Land Rover / Range Rover:** Discovery, Range Rover Sport.
- Interactive multi-parameter scatter plot comparing **Ground Clearance vs. Fuel Economy vs. Price**.

### 3. 📖 The Kenyan Car Buyer's Data Story
- **Market Tiers Breakdown:**
  - **Tier 1 (The Ubiquitous):** Toyota, Isuzu, Suzuki.
  - **Tier 2 (Modern Contenders):** Mazda, Nissan, Subaru, Honda, Mitsubishi.
  - **Tier 3 (European Prestige):** Mercedes-Benz, BMW, VW/Audi, Land Rover.
- **The Garage Matrix (Quadrant Chart):** Plots **Spare Parts Availability (0–100)** vs **Mechanic Familiarity (0–100)** with bubble sizes indicating relative maintenance cost multipliers.
- **Kirinyaga Road Price Basket:** Direct price comparison across brands for wear-and-tear items (Filters, Front Brake Pads, Shock Absorbers, Side Mirror assemblies, Spark Plugs, Bumpers) in Kenyan Shillings (KES).
- **Brand Dossiers & Mechanic Field Reports:** In-depth verdict, recommended engine codes, common failure points, and street theft vulnerability warnings.

### 4. 🗺️ Interactive Garages & Spares Map
- Clustered Folium map with color-coded markers for:
  - 🚗 Auto Repair Workshops
  - 🏍️ Motorcycle / Boda Boda Mechanics
  - 🛞 Tyre Centers
  - 🔧 Auto Spares / Parts Stores
  - 🔨 Jua Kali Artisans & Welders
- Clickable popups with phone numbers, full address, brand specialization, and direct Google Maps navigation links.

### 5. 🌐 Real-Time In-App Data Harvester
- Pull live, up-to-date garage and auto spares data directly from OpenStreetMap without needing Google API keys or credit cards.

### 6. 📥 Data Export
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
├── car_models_data.py          # Database of 50+ Kenyan car models (2015-2026) & matchmaker
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
