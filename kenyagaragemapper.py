#!/usr/bin/env python3
"""
kenyagaragemapper.py
Collect mechanical garages / auto repair businesses in Kenyan counties or
sub-counties using the official Google Places API (New) Text Search.

Why the API and not HTML scraping: scraping the Google Maps website breaks
Google's terms and gets blocked. The Places API is the supported route.

How it works
1. Each area name is geocoded to a bounding box (Kenya only).
2. The box is tiled into coarse cells.
3. Every cell is searched with each query term. A single query returns at most
   60 results, so any cell that hits that cap is split into 4 and searched again
   (adaptive quadtree). Dense areas like Nairobi get fine cells, rural areas stay coarse.
4. Results are de-duplicated by place ID, optionally tagged with a sub-county
   using a boundary GeoJSON, and written to CSV and GeoJSON.

Setup
    pip install requests
    pip install shapely        # only needed for --boundary
    export GOOGLE_MAPS_API_KEY="your key"   (Places API (New) + Geocoding API enabled)

Examples
    python kenyagaragemapper.py --areas "Machakos County" --out machakos
    python kenyagaragemapper.py --areas "Nairobi County" "Kiambu County" --out central
    python kenyagaragemapper.py --areas "Mombasa County" --boundary subcounties.geojson \
        --boundary-name-field ADM2_EN --out mombasa
    python kenyagaragemapper.py --areas "Nakuru County" --dry-run
"""

import argparse
import csv
import json
import os
import sys
import time

import requests

SEARCH_URL = "https://places.googleapis.com/v1/places:searchText"
GEOCODE_URL = "https://maps.googleapis.com/maps/api/geocode/json"

# Keep the field mask lean: rating, phone and website fields bill at a higher
# SKU than basic fields. Remove them if you only need locations.
FIELD_MASK = ",".join([
    "nextPageToken",
    "places.id",
    "places.displayName",
    "places.formattedAddress",
    "places.location",
    "places.types",
    "places.primaryType",
    "places.businessStatus",
    "places.rating",
    "places.userRatingCount",
    "places.nationalPhoneNumber",
    "places.websiteUri",
    "places.googleMapsUri",
])

# Kenya-flavoured search terms. Add Swahili or local terms as you find them.
DEFAULT_QUERIES = [
    "car garage",
    "auto repair",
    "motor vehicle repair",
    "mechanic",
    "panel beating",
    "auto electrician",
    "vehicle service centre",
    "jua kali garage",
]

KENYA_BOUNDS = (-4.9, 33.9, 5.1, 41.95)  # south, west, north, east
MAX_PAGES = 3  # 3 x 20 = 60 results is the API ceiling per query


class Budget:
    def __init__(self, max_requests):
        self.max = max_requests
        self.used = 0

    def spend(self):
        if self.used >= self.max:
            raise RuntimeError(f"Request budget of {self.max} reached; stopping.")
        self.used += 1


def geocode(area, key):
    params = {"address": area, "components": "country:KE", "region": "ke", "key": key}
    r = requests.get(GEOCODE_URL, params=params, timeout=30)
    r.raise_for_status()
    data = r.json()
    if data.get("status") != "OK" or not data.get("results"):
        raise ValueError(f"Could not geocode '{area}': {data.get('status')}")
    geom = data["results"][0]["geometry"]
    box = geom.get("bounds") or geom["viewport"]
    return (
        box["southwest"]["lat"], box["southwest"]["lng"],
        box["northeast"]["lat"], box["northeast"]["lng"],
    )


def post_search(body, key, budget, pause):
    budget.spend()
    headers = {
        "Content-Type": "application/json",
        "X-Goog-Api-Key": key,
        "X-Goog-FieldMask": FIELD_MASK,
    }
    for attempt in range(5):
        r = requests.post(SEARCH_URL, headers=headers, json=body, timeout=30)
        if r.status_code == 200:
            time.sleep(pause)
            return r.json()
        if r.status_code in (429, 500, 502, 503, 504):
            time.sleep(2 ** attempt)
            continue
        raise RuntimeError(f"Places API error {r.status_code}: {r.text[:300]}")
    raise RuntimeError("Places API kept failing after retries.")


def fetch_all(query, rect, key, budget, pause):
    """Return (places, capped). capped=True means more results exist than the API will page through."""
    places, token = [], None
    for _ in range(MAX_PAGES):
        body = {
            "textQuery": query,
            "pageSize": 20,
            "regionCode": "KE",
            "languageCode": "en",
            "locationRestriction": {
                "rectangle": {
                    "low": {"latitude": rect[0], "longitude": rect[1]},
                    "high": {"latitude": rect[2], "longitude": rect[3]},
                }
            },
        }
        if token:
            body["pageToken"] = token
        data = post_search(body, key, budget, pause)
        places.extend(data.get("places", []))
        token = data.get("nextPageToken")
        if not token:
            return places, False
    return places, True


def crawl(query, rect, key, budget, pause, min_cell, store, depth=0):
    places, capped = fetch_all(query, rect, key, budget, pause)
    for p in places:
        store.setdefault(p["id"], p)
    height, width = rect[2] - rect[0], rect[3] - rect[1]
    if capped and max(height, width) > min_cell:
        mid_lat, mid_lng = (rect[0] + rect[2]) / 2, (rect[1] + rect[3]) / 2
        quads = [
            (rect[0], rect[1], mid_lat, mid_lng),
            (rect[0], mid_lng, mid_lat, rect[3]),
            (mid_lat, rect[1], rect[2], mid_lng),
            (mid_lat, mid_lng, rect[2], rect[3]),
        ]
        for q in quads:
            crawl(query, q, key, budget, pause, min_cell, store, depth + 1)


def tile(bounds, step):
    s, w, n, e = bounds
    lat = s
    while lat < n:
        lng = w
        while lng < e:
            yield (lat, lng, min(lat + step, n), min(lng + step, e))
            lng += step
        lat += step


def load_boundaries(path, name_field):
    try:
        from shapely.geometry import shape
    except ImportError:
        sys.exit("--boundary needs shapely: pip install shapely")
    with open(path, encoding="utf-8") as f:
        gj = json.load(f)
    feats = []
    for ft in gj["features"]:
        props = ft.get("properties", {})
        name = props.get(name_field)
        if name is None:
            sys.exit(f"Field '{name_field}' not found. Available: {list(props)}")
        feats.append((str(name), shape(ft["geometry"])))
    return feats


def assign_area(lat, lng, feats):
    from shapely.geometry import Point
    pt = Point(lng, lat)
    for name, geom in feats:
        if geom.contains(pt):
            return name
    return ""


def flatten(p, area_label, admin_area):
    loc = p.get("location", {})
    return {
        "place_id": p["id"],
        "name": p.get("displayName", {}).get("text", ""),
        "search_area": area_label,
        "admin_area": admin_area,
        "address": p.get("formattedAddress", ""),
        "lat": loc.get("latitude", ""),
        "lng": loc.get("longitude", ""),
        "primary_type": p.get("primaryType", ""),
        "types": "|".join(p.get("types", [])),
        "is_car_repair": "car_repair" in p.get("types", []),
        "business_status": p.get("businessStatus", ""),
        "rating": p.get("rating", ""),
        "rating_count": p.get("userRatingCount", ""),
        "phone": p.get("nationalPhoneNumber", ""),
        "website": p.get("websiteUri", ""),
        "maps_url": p.get("googleMapsUri", ""),
    }


def write_outputs(rows, out):
    if not rows:
        print("No results to write.")
        return
    with open(f"{out}.csv", "w", newline="", encoding="utf-8-sig") as f:
        w = csv.DictWriter(f, fieldnames=list(rows[0].keys()))
        w.writeheader()
        w.writerows(rows)
    features = []
    for r in rows:
        if r["lat"] == "" or r["lng"] == "":
            continue
        props = {k: v for k, v in r.items() if k not in ("lat", "lng")}
        features.append({
            "type": "Feature",
            "geometry": {"type": "Point", "coordinates": [r["lng"], r["lat"]]},
            "properties": props,
        })
    with open(f"{out}.geojson", "w", encoding="utf-8") as f:
        json.dump({"type": "FeatureCollection", "features": features}, f)
    print(f"Wrote {len(rows)} places to {out}.csv and {out}.geojson")


def main():
    ap = argparse.ArgumentParser(description="Map garages in Kenya via Google Places API (New).")
    ap.add_argument("--areas", nargs="+", required=True,
                    help='Area names, e.g. "Machakos County" "Westlands, Nairobi"')
    ap.add_argument("--queries", nargs="+", default=DEFAULT_QUERIES, help="Search terms")
    ap.add_argument("--out", default="kenyagarages", help="Output file prefix")
    ap.add_argument("--start-cell", type=float, default=0.1,
                    help="Initial cell size in degrees (0.1 is about 11 km)")
    ap.add_argument("--min-cell", type=float, default=0.004,
                    help="Smallest cell size in degrees before splitting stops (0.004 is about 450 m)")
    ap.add_argument("--max-requests", type=int, default=2000,
                    help="Hard cap on API requests, to control cost")
    ap.add_argument("--pause", type=float, default=0.1, help="Seconds between requests")
    ap.add_argument("--boundary", help="GeoJSON of Kenyan counties or sub-counties (polygons)")
    ap.add_argument("--boundary-name-field", default="ADM2_EN",
                    help="Property holding the area name in the boundary file")
    ap.add_argument("--keep-outside", action="store_true",
                    help="With --boundary, keep places that fall outside every polygon")
    ap.add_argument("--dry-run", action="store_true",
                    help="Geocode and count starting cells only; no searches")
    args = ap.parse_args()

    key = os.environ.get("GOOGLE_MAPS_API_KEY")
    if not key:
        sys.exit("Set GOOGLE_MAPS_API_KEY first.")

    feats = load_boundaries(args.boundary, args.boundary_name_field) if args.boundary else None
    budget = Budget(args.max_requests)
    all_rows = {}

    try:
        for area in args.areas:
            bounds = geocode(area, key)
            cells = list(tile(bounds, args.start_cell))
            print(f"{area}: bbox {tuple(round(b, 4) for b in bounds)}, "
                  f"{len(cells)} starting cells x {len(args.queries)} queries "
                  f"= at least {len(cells) * len(args.queries)} requests")
            if args.dry_run:
                continue
            store = {}
            for i, cell in enumerate(cells, 1):
                for q in args.queries:
                    crawl(q, cell, key, budget, args.pause, args.min_cell, store)
                print(f"  cell {i}/{len(cells)} done, {len(store)} unique places, "
                      f"{budget.used} requests used")
            for pid, p in store.items():
                loc = p.get("location", {})
                admin = ""
                if feats and loc:
                    admin = assign_area(loc["latitude"], loc["longitude"], feats)
                    if not admin and not args.keep_outside:
                        continue
                all_rows.setdefault(pid, flatten(p, area, admin))
    except (RuntimeError, KeyboardInterrupt) as e:
        print(f"\nStopped early: {e}. Saving what was collected.")
    finally:
        if not args.dry_run:
            write_outputs(list(all_rows.values()), args.out)
            print(f"Requests used: {budget.used}")


if __name__ == "__main__":
    main()
