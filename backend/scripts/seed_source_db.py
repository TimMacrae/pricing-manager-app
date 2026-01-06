import os
import random
from datetime import date, timedelta
import pandas as pd
from sqlalchemy import create_engine, text

random.seed(42)

MYSQL_USER = os.getenv("MYSQL_USER")
MYSQL_PASSWORD = os.getenv("MYSQL_PASSWORD")
MYSQL_SOURCE_HOST = os.getenv("MYSQL_SOURCE_HOST", "mysql_source")
MYSQL_SOURCE_DB = os.getenv("MYSQL_SOURCE_DB", "source_db")

ENGINE = create_engine(
    f"mysql+pymysql://{MYSQL_USER}:{MYSQL_PASSWORD}@{MYSQL_SOURCE_HOST}:3306/{MYSQL_SOURCE_DB}"
)


def main():
    with ENGINE.begin() as conn:
        # Master data
        conn.execute(text(
            "INSERT IGNORE INTO sales_orgs(code,name) VALUES ('DE01','Germany Sales'),('AT01','Austria Sales')"))
        conn.execute(text(
            "INSERT IGNORE INTO plants(code,name) VALUES ('DEW1','Warehouse DE'),('ATW1','Warehouse AT')"))

        conn.execute(text("""
            INSERT IGNORE INTO vendors(vendor_name,country) VALUES
            ('Vendor A','DE'),('Vendor B','NL'),('Vendor C','CN'),('Vendor D','US')
        """))

        conn.execute(text("""
            INSERT IGNORE INTO customers(customer_no,name,customer_group,country) VALUES
            ('C1000','Retailer One','RETAIL','DE'),
            ('C2000','Reseller Two','RESELLER','DE'),
            ('C3000','Key Account','KEY','AT')
        """))

        conn.execute(text("""
            INSERT IGNORE INTO competitors(name,country) VALUES
            ('CompOne','DE'),('CompTwo','DE'),('CompThree','AT')
        """))

    # Pull IDs
    with ENGINE.connect() as conn:
        vendors = pd.read_sql("SELECT vendor_id FROM vendors", conn)[
            "vendor_id"].tolist()
        sales_orgs = pd.read_sql("SELECT sales_org_id FROM sales_orgs", conn)[
            "sales_org_id"].tolist()
        plants = pd.read_sql("SELECT plant_id FROM plants", conn)[
            "plant_id"].tolist()
        customers = pd.read_sql("SELECT customer_id FROM customers", conn)[
            "customer_id"].tolist()
        competitors = pd.read_sql("SELECT competitor_id FROM competitors", conn)[
            "competitor_id"].tolist()

    # Create 60 products (>=50)
    n_products = 60
    groups = ["NOTEBOOK", "MONITOR", "MOUSE", "KEYBOARD", "STORAGE", "NETWORK"]
    brands = ["BrandX", "BrandY", "BrandZ", "Lenovoish", "HPish", "Dellish"]

    materials = []
    for i in range(1, n_products + 1):
        sku = f"SKU{i:04d}"
        materials.append({
            "sku": sku,
            "description": f"Product {i}",
            "material_group": random.choice(groups),
            "brand": random.choice(brands),
            "vendor_id": random.choice(vendors),
            "base_uom": "EA",
        })
    df_mat = pd.DataFrame(materials)

    with ENGINE.begin() as conn:
        df_mat.to_sql("materials", conn, if_exists="append", index=False)

    # Reload materials with IDs
    with ENGINE.connect() as conn:
        mats = pd.read_sql(
            "SELECT material_id, sku, material_group FROM materials", conn)

    # Cost history (simple: one cost range per plant)
    today = date.today()
    valid_from = today - timedelta(days=120)
    valid_to = today + timedelta(days=365)

    cost_rows = []
    for _, row in mats.iterrows():
        base_cost = random.uniform(8, 900)
        for plant_id in plants:
            # slight plant variance
            cost_rows.append({
                "material_id": int(row["material_id"]),
                "plant_id": int(plant_id),
                "cost": round(base_cost * random.uniform(0.98, 1.03), 4),
                "cost_currency": "EUR",
                "valid_from": valid_from,
                "valid_to": valid_to
            })
    df_cost = pd.DataFrame(cost_rows)
    with ENGINE.begin() as conn:
        df_cost.to_sql("material_costs", conn, if_exists="append", index=False)

    # Daily prices (last 45 days)
    start = today - timedelta(days=45)
    days = 45

    price_rows = []
    # 8 skus with deliberate weirdness
    anomaly_skus = set(random.sample(mats["sku"].tolist(), 8))

    # create a "baseline" price per material then add noise per customer/day
    baseline = {}
    for _, m in mats.iterrows():
        # baseline markup over cost roughly
        base = random.uniform(15, 1200)
        baseline[m["sku"]] = base

    for d in range(days):
        dt = start + timedelta(days=d)
        for _, m in mats.iterrows():
            sku = m["sku"]
            for so in sales_orgs:
                for cust in customers:
                    p = baseline[sku] * random.uniform(0.97, 1.03)

                    # Inject anomalies:
                    if sku in anomaly_skus:
                        # 1) price spike on a random day
                        if d in (10, 20):
                            p *= random.uniform(1.25, 1.60)
                        # 2) occasional too-low price (potential negative margin)
                        if d in (15, 30):
                            p *= random.uniform(0.45, 0.70)

                    price_rows.append({
                        "dt": dt,
                        "sales_org_id": int(so),
                        "customer_id": int(cust),
                        "material_id": int(m["material_id"]),
                        "net_price": round(p, 4),
                        "currency": "EUR",
                        "source": "SAP"
                    })

    df_prices = pd.DataFrame(price_rows)
    with ENGINE.begin() as conn:
        # replace for repeatable learning runs
        conn.execute(text("DELETE FROM daily_prices"))
        df_prices.to_sql("daily_prices", conn, if_exists="append",
                         index=False, method="multi", chunksize=5000)

    # Competitor prices (match some SKUs, add divergence anomalies)
    comp_rows = []
    comp_anomaly_skus = set(random.sample(mats["sku"].tolist(), 10))

    for d in range(days):
        dt = start + timedelta(days=d)
        for comp in competitors:
            for sku, base in baseline.items():
                # competitor price baseline near ours
                cp = base * random.uniform(0.92, 1.08)

                # Inject competitor divergence anomalies
                if sku in comp_anomaly_skus and d in (12, 28, 40):
                    # competitor suddenly way cheaper or more expensive
                    cp *= random.choice([0.65, 0.75, 1.30, 1.45])

                comp_rows.append({
                    "dt": dt,
                    "competitor_id": int(comp),
                    "sku": sku,
                    "comp_price": round(cp, 4),
                    "currency": "EUR",
                    "availability": random.choice(["IN_STOCK", "IN_STOCK", "IN_STOCK", "OOS"]),
                })

    df_comp = pd.DataFrame(comp_rows)
    with ENGINE.begin() as conn:
        conn.execute(text("DELETE FROM competitor_prices"))
        df_comp.to_sql("competitor_prices", conn, if_exists="append",
                       index=False, method="multi", chunksize=5000)

    print("Seed complete.")
    print(f"Products: {len(mats)}")
    print(f"Daily prices rows: {len(df_prices)}")
    print(f"Competitor prices rows: {len(df_comp)}")
    print(
        f"Anomaly SKUs (pricing spikes/too low): {sorted(list(anomaly_skus))[:5]} ...")
    print(
        f"Competitor divergence SKUs: {sorted(list(comp_anomaly_skus))[:5]} ...")


if __name__ == "__main__":
    main()
