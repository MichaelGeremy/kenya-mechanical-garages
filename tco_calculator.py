"""
tco_calculator.py
Kenya Total Cost of Ownership (TCO) & Fuel Economics Calculator.
Computes 3-year running costs including EPRA fuel pricing, comprehensive insurance,
routine servicing, tyres, Nairobi Expressway/tolls, and depreciation in Kenyan Shillings (KES).
"""

# Kenyan EPRA Benchmark Fuel Prices (KES per Litre) - Updated baseline
EPRA_PRICES = {
    "Super Petrol": 182.50,
    "Diesel": 171.00,
    "Hybrid (Petrol Equivalent)": 182.50,
}

INSURANCE_RATE_ANNUAL = 0.042  # 4.2% average comprehensive insurance rate in Kenya
ANNUAL_NTSA_INSPECTION_KES = 2500  # Commercial / Private inspection & road safety


def calculate_tco(car, daily_commute_km, weekend_trips_monthly_km, years=3):
    """
    Calculate comprehensive 3-year Total Cost of Ownership for a specific car model in Kenya.
    """
    car_price = (car["price_min_kes"] + car["price_max_kes"]) / 2
    fuel_type = car["fuel_type"]
    fuel_economy = max(5.0, car["fuel_economy_kml"])

    # Fuel price selection
    if "diesel" in fuel_type.lower():
        fuel_price_per_l = EPRA_PRICES["Diesel"]
    elif "hybrid" in fuel_type.lower():
        fuel_price_per_l = EPRA_PRICES["Hybrid (Petrol Equivalent)"]
    else:
        fuel_price_per_l = EPRA_PRICES["Super Petrol"]

    # Annual mileage in Kenya
    # 250 working days * commute + 12 months * weekend trips
    annual_commute_km = daily_commute_km * 250
    annual_weekend_km = weekend_trips_monthly_km * 12
    annual_total_km = annual_commute_km + annual_weekend_km

    # 1. Fuel Cost
    annual_litres = annual_total_km / fuel_economy
    annual_fuel_kes = annual_litres * fuel_price_per_l
    monthly_fuel_kes = annual_fuel_kes / 12

    # 2. Insurance Cost (Comprehensive in Kenya)
    annual_insurance_kes = car_price * INSURANCE_RATE_ANNUAL
    monthly_insurance_kes = annual_insurance_kes / 12

    # 3. Scheduled Servicing & Wear-and-Tear (Oil, filters, brakes every 6,000 km)
    services_per_year = max(1, round(annual_total_km / 6000))
    tier = car.get("maintenance_tier", "Moderate")
    service_cost_map = {
        "Very Low": 6500,
        "Low": 8500,
        "Low-Moderate": 11000,
        "Moderate": 14000,
        "Moderate-High": 22000,
        "High": 35000,
        "Very High": 55000,
    }
    cost_per_service = service_cost_map.get(tier, 14000)
    annual_service_kes = services_per_year * cost_per_service

    # Tyres (Set of 4 replaced every 45,000 km)
    tyre_cost_map = {
        "Very Low": 28000,
        "Low": 36000,
        "Low-Moderate": 44000,
        "Moderate": 55000,
        "Moderate-High": 85000,
        "High": 130000,
        "Very High": 180000,
    }
    tyre_set_cost = tyre_cost_map.get(tier, 55000)
    annual_tyre_kes = (annual_total_km / 45000) * tyre_set_cost

    annual_maintenance_kes = annual_service_kes + annual_tyre_kes
    monthly_maintenance_kes = annual_maintenance_kes / 12

    # 4. Depreciation in Kenya
    # Japanese cars in Kenya depreciate slower than global averages
    depreciation_rate_map = {
        "Toyota": 0.08,   # 8% annual
        "Isuzu": 0.08,
        "Suzuki": 0.09,
        "Mazda": 0.11,
        "Nissan": 0.12,
        "Subaru": 0.11,
        "Honda": 0.11,
        "Mitsubishi": 0.12,
        "Volkswagen / Audi": 0.15,
        "Mercedes-Benz": 0.16,
        "BMW": 0.17,
        "Land Rover / Range Rover": 0.20,
    }
    dep_rate = depreciation_rate_map.get(car["brand"], 0.12)
    # 3-year residual value
    residual_value = car_price * ((1 - dep_rate) ** years)
    total_depreciation_3yr = car_price - residual_value
    annual_depreciation = total_depreciation_3yr / years
    monthly_depreciation = annual_depreciation / 12

    # Cumulative calculations
    total_fuel_3yr = annual_fuel_kes * years
    total_insurance_3yr = annual_insurance_kes * years
    total_maintenance_3yr = annual_maintenance_kes * years
    total_ownership_3yr = total_fuel_3yr + total_insurance_3yr + total_maintenance_3yr + total_depreciation_3yr

    total_km_3yr = annual_total_km * years
    cost_per_km = total_ownership_3yr / max(1, total_km_3yr)
    running_cost_per_month = monthly_fuel_kes + monthly_insurance_kes + monthly_maintenance_kes

    return {
        "car_model": car["model"],
        "car_price_avg": car_price,
        "annual_total_km": annual_total_km,
        "monthly_fuel_kes": round(monthly_fuel_kes),
        "monthly_insurance_kes": round(monthly_insurance_kes),
        "monthly_maintenance_kes": round(monthly_maintenance_kes),
        "monthly_running_cost_kes": round(running_cost_per_month),
        "annual_fuel_kes": round(annual_fuel_kes),
        "annual_insurance_kes": round(annual_insurance_kes),
        "annual_maintenance_kes": round(annual_maintenance_kes),
        "total_fuel_3yr": round(total_fuel_3yr),
        "total_insurance_3yr": round(total_insurance_3yr),
        "total_maintenance_3yr": round(total_maintenance_3yr),
        "total_depreciation_3yr": round(total_depreciation_3yr),
        "residual_value_3yr": round(residual_value),
        "total_ownership_3yr": round(total_ownership_3yr),
        "cost_per_km_kes": round(cost_per_km, 1),
    }
