# 🇰🇪 Kenya Mechanical Garages & Auto Intelligence Platform

The definitive, enterprise-grade automotive intelligence platform for Kenyan car buyers, fleet operators, and mechanics.

Built with **Streamlit**, **Folium**, **OpenStreetMap (Overpass API)**, and **Plotly**.

---

## 🌟 Top-Tier Features

### 1. 🎯 Exact Car Model Matchmaker
- Recommends the exact specific vehicle from a database of **54 top car models (2015 – 2026)**.
- Tailored match criteria: Purchase Budget (KES), Primary Driving Purpose, Ground Clearance ($190\text{ mm}+$ for bumps vs Standard), Body Style, Fuel Type, and Spare Parts Sourcing Priority.
- Returns Top 3 vehicles with match percentage, target engine variant (e.g. `1NZ-FE`, `SkyActiv-G 2.0L`, `FB20 NA`), mechanic watch-outs, and pricing in KES.

### 2. ⚔️ Head-to-Head Rival Comparison Engine
- Compare any 2 or 3 rival models side-by-side *(e.g. Mazda CX-5 vs Toyota RAV4 vs Subaru Forester)*.
- **Interactive Radar Chart:** Compares Ground Clearance, Fuel Economy, Parts Availability, Mechanic Familiarity, and Price Affordability.
- Side-by-side spec comparison table with Kenyan market verdicts.

### 3. 💰 3-Year Total Cost of Ownership (TCO) & Fuel Economics
- Real-world Kenyan parameters: Live EPRA fuel prices (Super Petrol, Diesel, Hybrid), daily commute distance (km/day), and weekend travel.
- Monthly running costs in KES: Fuel bill + Comprehensive Insurance (4.2% rate) + Routine Servicing & Tyres (oil/filters every $6,000\text{ km}$).
- 3-Year cumulative financial breakdown with estimated residual resale value and cost per kilometer (KES/km).

### 4. 🔍 Pre-Purchase Inspection (PPI) "Lemon Detector" Checklist
- Take this interactive digital checklist to car yards on Kiambu Rd, Ngong Rd, or Mombasa Rd:
  - **Odometer & Document Verification:** JEVIC/QISJ certificate check and pedal wear vs reported km.
  - **Structural & Salvage Detection:** A/B/C pillar spot welds, fender/radiator support bolts, boot spare well sealant.
  - **Engine & Mechanical Secrets:** Cold start rattle, smoke color, oil cap mayonnaise residue, dipstick blow-by test.
  - **Transmission Tests:** Stationary gear engagement jerk test ($P \to R \to D$), low-speed incline CVT slip, figure-8 CV joint clicking.
  - **Underbody & Rust:** Japanese coastal/snow road salt rust vs subframe structural flaking.
- **Risk Assessment Verdict:** Automatic scorecard (Low Risk Clean Buy vs Moderate Risk vs Critical Dealbreaker Walk Away).

### 5. 🔩 Kirinyaga Road, Grogan & Industrial Area Spares Locator
- Search high-demand wear-and-tear and theft-vulnerable parts:
  - Complete Side Mirror Assemblies (theft factor alert)
  - Front Shock Absorber Pairs
  - Ceramic Brake Pad Sets
  - CVT Fluid & Transmission Filter Kits
  - Lower Control Arm & Ball Joint Assemblies
  - Complete LED Headlamp Assemblies
- **Price Tiers Comparison in KES:** Brand New Genuine OEM vs Quality Japanese/Taiwanese Aftermarket (555, KYB, Tokico) vs Ex-Japan Used/Scrap.
- **Sourcing Corridors Guide:** Kirinyaga Rd, Grogan, Baricho Rd, Dar es Salaam Rd, Gikomba, and Mombasa.

### 6. 🚢 KRA 8-Year Age Rule & Import Duty Calculator
- Validates vehicle age eligibility under Kenya's strict 8-year import rule.
- Calculates CRSP depreciation schedule (10% to 70%).
- Computes: Import Duty (35%), Excise Duty (20% – 35%), VAT (16%), IDF (2.5%), RDL (1.5%), Port/CFS clearing charges, and total estimated landed cost in KES.

### 7. 🚘 50+ Car Models Database (2015 – 2026)
- Comprehensive catalog of 54 mainstream vehicles across 12 brands (Toyota, Mazda, Nissan, Subaru, Honda, Isuzu, Suzuki, Mitsubishi, Volkswagen/Audi, Mercedes-Benz, BMW, Land Rover).
- Multi-parameter scatter plot: **Ground Clearance vs Fuel Economy vs Price**.

### 8. 📖 The Kenyan Car Buyer's Data Story
- The 3 Brand Tiers in Kenya (Tier 1: Ubiquitous, Tier 2: Modern Contenders, Tier 3: European Prestige).
- The Garage Matrix (Quadrant chart): Parts Availability vs Mechanic Familiarity.
- Kirinyaga Road Price Basket Bar Chart for routine service items.

### 9. 🗺️ Interactive Garages & Spares Map
- Clustered Folium map with 300+ verified facilities across Kenya with click-to-dial phone numbers and Google Maps navigation links.

### 10. 📊 Market & County Analytics
- Geospatial concentration and brand specialization distribution.

### 11. 📋 Directory & Data Export
- Filterable table with one-click CSV and GeoJSON downloads.

---

## 🚀 Quickstart

```bash
git clone https://github.com/MichaelGeremy/kenya-mechanical-garages.git
cd kenya-mechanical-garages
pip install -r requirements.txt
streamlit run app.py
```
Open `http://localhost:8501` in your browser.

---

## 📁 Repository Structure

```text
├── app.py                      # Master Streamlit web application (11 tabs)
├── tco_calculator.py           # 3-Year TCO & EPRA fuel economics calculator
├── inspection_data.py          # Pre-Purchase Inspection Lemon Detector checklist
├── spares_locator.py           # Kirinyaga Road & Industrial Area spares locator
├── duty_calculator.py          # KRA 8-year rule & import duty calculator
├── car_models_data.py          # 54 Kenyan car models (2015-2026) database & matchmaker
├── brand_data.py               # Kenyan automotive market intelligence & parts matrix
├── kenyagaragemapper_osm.py    # Free OSM Overpass harvester CLI
├── kenyagaragemapper.py        # Official Google Places API (New) harvester CLI
├── requirements.txt            # Python dependencies
├── .gitignore                  # Git ignore rules
├── data/
│   ├── kenya_garages.csv       # Preloaded dataset with brand specializations
│   └── kenya_garages.geojson   # GeoJSON spatial feature collection
└── README.md                   # Full documentation & platform guide
```

---

## 📄 License
MIT License. Data derived from OpenStreetMap contributors under the Open Database License (ODbL).
