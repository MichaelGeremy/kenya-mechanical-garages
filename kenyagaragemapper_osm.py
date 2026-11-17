#!/usr/bin/env python3
"""
kenyagaragemapper_osm.py
Collect mechanical garages, auto repair workshops, tyre centers, and Jua Kali mechanics
in Kenya using OpenStreetMap (OSM) via the Overpass API — 100% FREE, NO API KEY REQUIRED.

Features:
- Zero cost, no credit card, no Google Cloud account needed.
- No third-party pip dependencies required (runs on standard Python library).
- Uses OpenStreetMap Overpass spatial queries with automatic server failover.
- Queries either all of Kenya or specific counties / towns.
- Exports to both Excel-friendly CSV (.csv) and GIS-ready GeoJSON (.geojson).

Usage Examples:
    # 1. Map all mechanical garages and repair shops across all of Kenya:
    python kenyagaragemapper_osm.py --all-kenya --out kenya_garages_all

    # 2. Map garages in specific counties / towns:
    python kenyagaragemapper_osm.py --areas "Nairobi" "Kiambu" --out nairobi_kiambu

    # 3. Include Jua Kali metal / welding / chassis artisans:
    python kenyagaragemapper_osm.py --areas "Nakuru" --include-juakali --out nakuru_garages
"""

import argparse
import csv
import json
import os
import sys
import time
import urllib.parse
import urllib.request
import urllib.error

# Bounding box for Kenya (south, west, north, east)
KENYA_BOUNDS = (-4.9, 33.9, 5.1, 41.95)

# Built-in rough bounding boxes for major Kenyan counties (south, west, north, east)
# This allows instant zero-call execution without needing external geocoding!
KENYA_COUNTY_BBOXES = {
    "nairobi": (-1.444, 36.662, -1.160, 37.104),
    "mombasa": (-4.120, 39.550, -3.900, 39.770),
    "kiambu": (-1.290, 36.480, -0.750, 37.280),
    "machakos": (-1.750, 36.950, -0.850, 37.900),
    "nakuru": (-0.950, 35.450, 0.250, 36.500),
    "kisumu": (-0.450, 34.450, 0.050, 35.150),
    "uasin gishu": (0.150, 34.850, 0.950, 35.600),
    "kajiado": (-3.150, 36.050, -1.300, 37.950),
    "meru": (-0.350, 37.150, 0.700, 38.300),
    "kilifi": (-4.000, 39.050, -2.300, 40.200),
    "eldoret": (0.450, 35.200, 0.580, 35.350),
    "thika": (-1.080, 37.030, -0.990, 37.150),
}

OVERPASS_MIRRORS = [
    "https://overpass-api.de/api/interpreter",
    "https://overpass.openstreetmap.fr/api/interpreter",
    "https://lz4.overpass-api.de/api/interpreter",
    "https://overpass.kumi.systems/api/interpreter",
]

USER_AGENT = "KenyaGarageMapper/1.0 (OpenStreetMap Garage Extractor)"


def geocode_nominatim(area_name):
    """Free geocoder via OpenStreetMap Nominatim with Kenya restriction."""
    params = urllib.parse.urlencode({
        "q": area_name,
        "countrycodes": "ke",
        "format": "json",
        "limit": 1,
    })
    url = f"https://nominatim.openstreetmap.org/search?{params}"
    req = urllib.request.Request(url, headers={"User-Agent": USER_AGENT})
    try:
        time.sleep(1.0)  # Respect Nominatim 1 req/sec policy
        with urllib.request.urlopen(req, timeout=15) as resp:
            data = json.loads(resp.read().decode("utf-8"))
            if data:
                # boundingbox format in Nominatim: [south, north, west, east]
                bbox = [float(x) for x in data[0]["boundingbox"]]
                # convert to (south, west, north, east)
                return (bbox[0], bbox[2], bbox[1], bbox[3])
    except Exception as e:
        print(f"  Warning: Nominatim lookup for '{area_name}' failed: {e}")
    return None


def resolve_bounds(area_name):
    """Resolve an area name to (south, west, north, east)."""
    key = area_name.strip().lower().replace(" county", "").replace(" town", "")
    if key in KENYA_COUNTY_BBOXES:
        return KENYA_COUNTY_BBOXES[key]
    
    print(f"Resolving '{area_name}' via free Nominatim...")
    bbox = geocode_nominatim(area_name)
    if bbox:
        return bbox
    
    print(f"Could not find specific bounds for '{area_name}', defaulting to Kenya national bounds.")
    return KENYA_BOUNDS


def build_overpass_query(bbox, include_juakali=False, include_spares=True):
    """Build Overpass QL query string for given bounding box."""
    s, w, n, e = bbox
    box_str = f"({s:.4f},{w:.4f},{n:.4f},{e:.4f})"

    # Primary automotive repair tags
    tags = [
        '["shop"="car_repair"]',
        '["amenity"="motorcycle_repair"]',
        '["shop"="tyres"]',
    ]

    if include_spares:
        tags.extend([
            '["shop"="car_parts"]',
            '["shop"="auto_parts"]',
        ])

    if include_juakali:
        tags.extend([
            '["craft"="blacksmith"]',
            '["craft"="welder"]',
            '["craft"="metal_construction"]',
        ])

    statements = []
    for tag in tags:
        statements.append(f"  node{tag}{box_str};")
        statements.append(f"  way{tag}{box_str};")

    query = (
        "[out:json][timeout:60];\n"
        "(\n" +
        "\n".join(statements) +
        "\n);\n"
        "out center tags;\n"
    )
    return query


def query_overpass(query):
    """Execute Overpass query with automatic mirror rotation and retries."""
    data = urllib.parse.urlencode({"data": query}).encode("utf-8")
    last_err = None

    for mirror in OVERPASS_MIRRORS:
        try:
            print(f"Connecting to Overpass server ({mirror.split('/')[2]})...")
            req = urllib.request.Request(
                mirror,
                data=data,
                headers={"User-Agent": USER_AGENT}
            )
            with urllib.request.urlopen(req, timeout=50) as resp:
                body = resp.read().decode("utf-8")
                res = json.loads(body)
                return res.get("elements", [])
        except urllib.error.HTTPError as he:
            last_err = f"HTTP {he.code}: {he.reason}"
            print(f"  Server busy or returned {last_err}, trying next mirror...")
            time.sleep(1)
        except Exception as e:
            last_err = str(e)
            print(f"  Connection error: {e}, trying next mirror...")
            time.sleep(1)

    raise RuntimeError(f"All Overpass mirrors failed. Last error: {last_err}")


def extract_location(elem):
    """Extract lat/lon from OSM node or way (center)."""
    if elem.get("type") == "node":
        return elem.get("lat"), elem.get("lon")
    center = elem.get("center", {})
    return center.get("lat"), center.get("lon")


def parse_element(elem, search_area="Kenya"):
    """Format an OSM element into a standardized record."""
    tags = elem.get("tags", {})
    lat, lon = extract_location(elem)
    osm_type = elem.get("type", "node")
    osm_id = elem.get("id", "")

    # Business name: fallback to operator or description if unnamed
    name = tags.get("name") or tags.get("operator") or tags.get("brand") or "(Unnamed Garage/Workshop)"

    # Category determination
    category = "auto_repair"
    if tags.get("amenity") == "motorcycle_repair":
        category = "motorcycle_repair"
    elif tags.get("shop") == "tyres":
        category = "tyres"
    elif tags.get("shop") in ("car_parts", "auto_parts"):
        category = "auto_spares"
    elif tags.get("craft") in ("blacksmith", "welder", "metal_construction"):
        category = "jua_kali_craft"

    # Contact information
    phone = (
        tags.get("phone")
        or tags.get("contact:phone")
        or tags.get("contact:mobile")
        or tags.get("mobile")
        or ""
    )
    website = (
        tags.get("website")
        or tags.get("contact:website")
        or ""
    )

    # Address composition
    street = tags.get("addr:street") or ""
    suburb = tags.get("addr:suburb") or tags.get("addr:neighbourhood") or ""
    city = tags.get("addr:city") or tags.get("addr:town") or ""
    county = tags.get("addr:county") or ""
    address_parts = [p for p in (street, suburb, city, county) if p]
    full_address = ", ".join(address_parts)

    return {
        "osm_id": f"{osm_type}/{osm_id}",
        "name": name,
        "category": category,
        "search_area": search_area,
        "lat": lat if lat is not None else "",
        "lng": lon if lon is not None else "",
        "phone": phone,
        "website": website,
        "opening_hours": tags.get("opening_hours", ""),
        "brand": tags.get("brand", ""),
        "address": full_address,
        "city": city,
        "county": county,
        "osm_url": f"https://www.openstreetmap.org/{osm_type}/{osm_id}",
    }


def write_outputs(records, out_prefix):
    """Write collected records to CSV and GeoJSON."""
    if not records:
        print("No records to write.")
        return

    csv_path = f"{out_prefix}.csv"
    geojson_path = f"{out_prefix}.geojson"

    # 1. Export CSV (with UTF-8 BOM for Microsoft Excel)
    fieldnames = list(records[0].keys())
    with open(csv_path, "w", newline="", encoding="utf-8-sig") as f:
        writer = csv.DictWriter(f, fieldnames=fieldnames)
        writer.writeheader()
        writer.writerows(records)

    # 2. Export GeoJSON
    features = []
    for r in records:
        if r["lat"] == "" or r["lng"] == "":
            continue
        props = {k: v for k, v in r.items() if k not in ("lat", "lng")}
        features.append({
            "type": "Feature",
            "geometry": {
                "type": "Point",
                "coordinates": [float(r["lng"]), float(r["lat"])],
            },
            "properties": props,
        })

    with open(geojson_path, "w", encoding="utf-8") as f:
        json.dump({
            "type": "FeatureCollection",
            "features": features,
        }, f, indent=2)

    print(f"\n[DONE] Saved {len(records)} places:")
    print(f"  -> CSV:     {csv_path}")
    print(f"  -> GeoJSON: {geojson_path}")


def main():
    parser = argparse.ArgumentParser(
        description="Map mechanical garages & repair shops in Kenya via OpenStreetMap (100% Free, No API Key)."
    )
    group = parser.add_mutually_exclusive_group(required=True)
    group.add_argument(
        "--all-kenya", action="store_true",
        help="Search across all of Kenya"
    )
    group.add_argument(
        "--areas", nargs="+",
        help='Specific county or town names, e.g. "Nairobi" "Kiambu" "Mombasa"'
    )

    parser.add_argument(
        "--out", default="kenya_garages",
        help="Output file prefix (default: kenya_garages)"
    )
    parser.add_argument(
        "--include-juakali", action="store_true",
        help="Include Jua Kali welders, blacksmiths, and metal chassis artisans"
    )
    parser.add_argument(
        "--no-spares", action="store_true",
        help="Exclude auto parts and spare shops (focus only on repair/garages)"
    )

    args = parser.parse_args()

    all_records = {}

    print("==================================================")
    print(" Kenya Garage Mapper (OpenStreetMap / Free Route)")
    print(" No Google API Key or billing required.")
    print("==================================================")

    if args.all_kenya:
        print("\nQuerying all of Kenya...")
        query = build_overpass_query(
            KENYA_BOUNDS,
            include_juakali=args.include_juakali,
            include_spares=not args.no_spares
        )
        elements = query_overpass(query)
        print(f"Retrieved {len(elements)} raw OpenStreetMap features.")
        for elem in elements:
            rec = parse_element(elem, search_area="Kenya")
            all_records[rec["osm_id"]] = rec
    else:
        for area in args.areas:
            print(f"\nProcessing Area: '{area}'...")
            bbox = resolve_bounds(area)
            query = build_overpass_query(
                bbox,
                include_juakali=args.include_juakali,
                include_spares=not args.no_spares
            )
            elements = query_overpass(query)
            print(f"  Found {len(elements)} raw features in {area}.")
            for elem in elements:
                rec = parse_element(elem, search_area=area)
                all_records[rec["osm_id"]] = rec

    write_outputs(list(all_records.values()), args.out)


if __name__ == "__main__":
    main()
