import pandas as pd
import geopandas as gpd
import matplotlib.pyplot as plt
import os

# ── PATHS ──────────────────────────────────────────────
data_folder = r"C:\Users\salvi\Documents\Western-Ghats-Fire-Risk\data"
output_folder = r"C:\Users\salvi\Documents\Western-Ghats-Fire-Risk\outputs"

# ── LOAD FIRE DATA ─────────────────────────────────────
print("Loading fire data...")
df_2022 = pd.read_csv(os.path.join(data_folder, "modis_2022_all_countries", "modis", "2022", "modis_2022_India.csv"))
df_2023 = pd.read_csv(os.path.join(data_folder, "modis_2023_all_countries", "modis", "2023", "modis_2023_India.csv"))
df_2024 = pd.read_csv(os.path.join(data_folder, "modis_2024_all_countries", "modis", "2024", "modis_2024_India.csv"))

# ── COMBINE ALL YEARS ──────────────────────────────────
df_all = pd.concat([df_2022, df_2023, df_2024])
print(f"Total fire records: {len(df_all)}")

# ── FILTER HIGH CONFIDENCE ONLY ────────────────────────
df_high = df_all[df_all["confidence"] >= 80]
print(f"High confidence fires: {len(df_high)}")

# ── CONVERT TO GEODATAFRAME ────────────────────────────
gdf = gpd.GeoDataFrame(
    df_high,
    geometry=gpd.points_from_xy(df_high.longitude, df_high.latitude),
    crs="EPSG:4326"
)

# ── LOAD WESTERN GHATS BOUNDARY ────────────────────────
wg = gpd.read_file(os.path.join(data_folder, "western_ghats_states.shp"))

# ── CLIP TO WESTERN GHATS ──────────────────────────────
fires_wg = gpd.clip(gdf, wg)
print(f"Fires in Western Ghats: {len(fires_wg)}")

# ── FIRE COUNTS BY YEAR ────────────────────────────────
fires_wg["year"] = pd.to_datetime(fires_wg["acq_date"]).dt.year
print("\n── Fire counts by year ──")
print(fires_wg.groupby("year").size())

# ── SAVE OUTPUT ────────────────────────────────────────
output_path = os.path.join(output_folder, "fires_western_ghats_clean.shp")
fires_wg.to_file(output_path, mode='w')
print(f"\nSaved to: {output_path}")
print("Done!")

# ── FIRE COUNT BY MONTH ────────────────────────────────
fires_wg["month"] = pd.to_datetime(fires_wg["acq_date"]).dt.month
monthly = fires_wg.groupby(["year", "month"]).size().reset_index(name="count")

# ── PLOT ───────────────────────────────────────────────
fig, ax = plt.subplots(figsize=(12, 5))

for year in [2022, 2023, 2024]:
    data = monthly[monthly["year"] == year]
    ax.plot(data["month"], data["count"], marker="o", label=str(year))

ax.set_title("Monthly Fire Activity in Western Ghats (2022-2024)", fontsize=14)
ax.set_xlabel("Month")
ax.set_ylabel("Number of Fires")
ax.set_xticks(range(1, 13))
ax.set_xticklabels(["Jan","Feb","Mar","Apr","May","Jun",
                     "Jul","Aug","Sep","Oct","Nov","Dec"])
ax.legend()
ax.grid(True, alpha=0.3)

plt.tight_layout()
plt.savefig(os.path.join(output_folder, "fire_monthly_trend.png"), dpi=150)
print("Chart saved!")

# ── FIRE COUNT BY STATE ────────────────────────────────
fires_wg["year"] = pd.to_datetime(fires_wg["acq_date"]).dt.year

# Spatial join to get state names
fires_with_state = gpd.sjoin(fires_wg, wg[["NAME_1", "geometry"]], how="left", predicate="within")

# Count by state
state_counts = fires_with_state.groupby("NAME_1").size().sort_values(ascending=False).reset_index(name="count")

# Plot
fig, ax = plt.subplots(figsize=(10, 5))
ax.bar(state_counts["NAME_1"], state_counts["count"], color=["#d73027","#f46d43","#fdae61","#fee08b","#d9ef8b","#91cf60"])
ax.set_title("Total Fire Incidents by State — Western Ghats (2022–2024)", fontsize=13)
ax.set_xlabel("State")
ax.set_ylabel("Number of Fires")
ax.grid(axis="y", alpha=0.3)

plt.tight_layout()
plt.savefig(os.path.join(output_folder, "fire_by_state.png"), dpi=150)
print("State chart saved!")

# ── HEATMAP TABLE: STATE vs MONTH ─────────────────────
import seaborn as sns

fires_with_state["month"] = pd.to_datetime(fires_with_state["acq_date"]).dt.month

pivot = fires_with_state.groupby(["NAME_1", "month"]).size().unstack(fill_value=0)
pivot.columns = ["Jan","Feb","Mar","Apr","May","Jun","Jul","Aug","Sep","Oct","Nov","Dec"]

fig, ax = plt.subplots(figsize=(14, 6))
sns.heatmap(pivot, annot=True, fmt="d", cmap="YlOrRd", ax=ax, linewidths=0.5)
ax.set_title("Fire Incidents by State and Month — Western Ghats (2022–2024)", fontsize=13)
ax.set_xlabel("Month")
ax.set_ylabel("State")

plt.tight_layout()
plt.savefig(os.path.join(output_folder, "fire_state_month_heatmap.png"), dpi=150)
print("Heatmap table saved!")
