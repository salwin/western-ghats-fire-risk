import geopandas as gpd
from sqlalchemy import create_engine
import os

# ── DATABASE CONNECTION ────────────────────────────────
engine = create_engine("postgresql://postgres:YOUR_PASSWORD@localhost:5432/fire_risk_wg")

# ── LOAD FIRE DATA ─────────────────────────────────────
output_folder = r"C:\Users\salvi\Documents\Western-Ghats-Fire-Risk\outputs"
fires = gpd.read_file(os.path.join(output_folder, "fires_western_ghats_clean.shp"))

# ── UPLOAD TO POSTGIS ──────────────────────────────────
print("Uploading fire data to PostGIS...")
fires.to_postgis("fire_incidents", engine, if_exists="replace", index=False)
print(f"Uploaded {len(fires)} fire records to database!")
