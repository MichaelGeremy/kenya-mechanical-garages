"""
duty_calculator.py
Kenya Revenue Authority (KRA) 8-Year Age Rule & Import Duty Estimator.
Computes estimated taxes, port clearing, and landed costs for vehicle imports into Kenya.
"""

CURRENT_YEAR = 2024  # Base year for 8-year rule calculation


def check_8_year_rule(year_of_manufacture, current_year=CURRENT_YEAR):
    """
    Checks if a vehicle is legally eligible for import into Kenya under the 8-year rule.
    In Kenya, vehicles older than 8 years from year of first registration/manufacture cannot be imported.
    """
    earliest_allowed_year = current_year - 7  # E.g. in 2024, 2017 is allowed (2017 to 2024 = 8 calendar years)
    is_allowed = year_of_manufacture >= earliest_allowed_year
    return {
        "is_allowed": is_allowed,
        "earliest_year": earliest_allowed_year,
        "vehicle_year": year_of_manufacture,
        "age_years": current_year - year_of_manufacture + 1,
    }


def calculate_kra_import_duty(crsp_kes, year_of_manufacture, engine_cc, current_year=CURRENT_YEAR):
    """
    Calculate KRA import duty taxes based on Current Retail Selling Price (CRSP) schedule.
    """
    age_check = check_8_year_rule(year_of_manufacture, current_year)
    if not age_check["is_allowed"]:
        return {
            "error": f"BANNED FROM IMPORT: Vehicle manufactured in {year_of_manufacture} exceeds Kenya's strict 8-year limit (Earliest allowed: {age_check['earliest_year']}).",
            "is_allowed": False,
        }

    age = age_check["age_years"]

    # KRA Depreciation Schedule
    depreciation_table = {
        1: 0.10,
        2: 0.15,
        3: 0.20,
        4: 0.30,
        5: 0.40,
        6: 0.50,
        7: 0.60,
        8: 0.70,
    }
    dep_rate = depreciation_table.get(min(8, max(1, age)), 0.70)

    # 1. Customs Value (Depreciated CRSP)
    customs_value_kes = crsp_kes * (1 - dep_rate)

    # 2. Import Duty (35% under revised EAC CET)
    import_duty_kes = customs_value_kes * 0.35

    # 3. Excise Duty (20% for <=1500cc, 25% for 1501-2500cc, 35% for >2500cc)
    excise_base = customs_value_kes + import_duty_kes
    if engine_cc <= 1500:
        excise_rate = 0.20
    elif engine_cc <= 2500:
        excise_rate = 0.25
    else:
        excise_rate = 0.35
    excise_duty_kes = excise_base * excise_rate

    # 4. VAT (16%)
    vat_base = customs_value_kes + import_duty_kes + excise_duty_kes
    vat_kes = vat_base * 0.16

    # 5. IDF (2.5%) and RDL (1.5%)
    idf_kes = customs_value_kes * 0.025
    rdl_kes = customs_value_kes * 0.015

    total_taxes_kes = import_duty_kes + excise_duty_kes + vat_kes + idf_kes + rdl_kes

    # 6. Port, CFS, Shipping & Registration
    port_and_clearing_kes = 145000  # Port charges, CFS storage, radiation test, NTSA plates, clearing agent

    # 7. Estimated Purchase CIF in Japan (typically ~35-45% of total landed cost)
    cif_japan_kes = customs_value_kes * 0.85

    total_landed_cost_kes = cif_japan_kes + total_taxes_kes + port_and_clearing_kes

    return {
        "is_allowed": True,
        "vehicle_year": year_of_manufacture,
        "age_years": age,
        "crsp_kes": round(crsp_kes),
        "depreciation_pct": round(dep_rate * 100),
        "customs_value_kes": round(customs_value_kes),
        "import_duty_kes": round(import_duty_kes),
        "excise_duty_kes": round(excise_duty_kes),
        "vat_kes": round(vat_kes),
        "idf_kes": round(idf_kes),
        "rdl_kes": round(rdl_kes),
        "total_taxes_kes": round(total_taxes_kes),
        "port_and_clearing_kes": round(port_and_clearing_kes),
        "cif_japan_kes": round(cif_japan_kes),
        "total_landed_cost_kes": round(total_landed_cost_kes),
    }
