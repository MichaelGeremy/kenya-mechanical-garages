# 🇰🇪 Kenya Mechanical Garages & Auto Workshops Explorer

An interactive geospatial dashboard and data collection engine for mapping mechanical garages, auto repair workshops, tyre service centers, and *Jua Kali* artisans across Kenyan counties.

Built with **Streamlit**, **Folium**, **OpenStreetMap (Overpass API)**, and **Plotly**.

---

## 🌟 Key Features

- **🗺️ Interactive Map with Clustered Markers**:
  - Color-coded pins for Auto Repair, Motorcycle/Boda Boda mechanics, Tyre Centers, Spares shops, and Jua Kali artisans.
  - Interactive popups displaying phone numbers (with direct `tel:` dialing links), physical street address, vehicle brand specialization, and one-click Google Maps navigation.
- **📊 Analytics & Service Distribution**:
  - Donut chart of service categories across Kenya.
  - County-by-county breakdown and ranking.
  - Phone contactability rate analysis.
- **🔍 Multi-Level Filtering & Live Search**:
  - Filter by County (Nairobi, Mombasa, Kiambu, Nakuru, Machakos, Kisumu, etc.).
  - Filter by Service Category.
  - Live text search across garage names, streets, and brands (e.g. *Toyota*, *AutoXpress*, *Ngong Road*).
  - Toggle to isolate only workshops with verified phone contacts.
- **🌐 Real-Time In-App Data Harvester**:
  - Pull live, up-to-date garage data directly from OpenStreetMap without needing Google API keys or credit cards.
- **📥 Dual Export**:
  - Download filtered datasets as Microsoft Excel-ready CSV (`.csv`) or GIS-ready GeoJSON (`.geojson`).

---

## 🚀 Quickstart

### 1. Clone the Repository
```bash
git clone https://github.com/YOUR_USERNAME/YOUR_REPOSITORY.git
cd "Mechanical Garages project"
```

### 2. Install Dependencies
```bash
pip install -r requirements.txt
```

### 3. Launch the Streamlit App
```bash
streamlit run app.py
```
The dashboard will open automatically in your browser at `http://localhost:8501`.

---

## 🛠️ CLI Data Harvester Scripts

The repository includes two harvesting scripts:

### A. Free Route (OpenStreetMap / Overpass - Recommended)
Requires **zero API keys** and zero cost:
```bash
# Harvest garages in specific counties
python kenyagaragemapper_osm.py --areas "Nairobi" "Kiambu" "Mombasa" --out data/kenya_garages

# Include informal Jua Kali mechanics and welders
python kenyagaragemapper_osm.py --areas "Nakuru" --include-juakali

# Harvest nationwide across all 47 Kenyan counties
python kenyagaragemapper_osm.py --all-kenya --out data/kenya_all
```

### B. Google Places API Route
If you have a Google Maps API Key enabled for Places API (New) & Geocoding:
```bash
export GOOGLE_MAPS_API_KEY="your_api_key_here"
python kenyagaragemapper.py --areas "Nairobi County" --out data/nairobi_google
```

---

## 📁 Project Structure

```text
├── app.py                      # Main Streamlit web application
├── kenyagaragemapper_osm.py    # Free OSM Overpass harvester CLI
├── kenyagaragemapper.py        # Google Places API harvester CLI
├── requirements.txt            # Python dependencies
├── .gitignore                  # Git ignore rules
├── data/
│   ├── kenya_garages.csv       # Preloaded baseline dataset
│   └── kenya_garages.geojson   # GeoJSON spatial feature collection
└── README.md                   # Documentation
```

---

## 🌐 Deploying to Streamlit Cloud

1. Push this repository to GitHub.
2. Sign in to [share.streamlit.io](https://share.streamlit.io/).
3. Click **"New app"**, select your repository, branch (`main`), and set the main file path to `app.py`.
4. Click **Deploy!** — your Kenya Garages Explorer will be live on the web for free.

---

## 📄 License
MIT License. Data derived from OpenStreetMap contributors under the Open Database License (ODbL).
