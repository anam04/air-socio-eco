# =========================
# 1. Install dependencies
# =========================
!pip -q install folium branca scipy plotly

# =========================
# 2. Imports
# =========================
import io
import warnings
import numpy as np
import pandas as pd
import folium
from scipy.spatial import cKDTree
from plotly.subplots import make_subplots
import plotly.graph_objects as go
from IPython.display import display

warnings.filterwarnings("ignore")
np.random.seed(42)

print("✓ Libraries loaded")


# =========================
# 3. SET YOUR CSV PATHS HERE
# =========================
WUSTL_CSV_PATH   = "/content/WUSTL_Delhi_2017_monthly.csv"
WRFCHEM_CSV_PATH = "/content/WRF_CHEM_2017.csv"


# =========================
# 4. Delhi crop bounding box
# =========================
# Approximate Delhi bounding box.
# You can refine this later using an official Delhi shapefile.

DELHI_LAT_MIN = 28.40
DELHI_LAT_MAX = 28.90
DELHI_LON_MIN = 76.80
DELHI_LON_MAX = 77.35


# =========================
# 5. Region labels
# =========================
REGIONS = {
    "North India":   (28.0, 37.0, 68.0, 80.0),
    "South India":   (8.0,  18.0, 74.0, 82.0),
    "East India":    (20.0, 27.0, 83.0, 97.0),
    "West India":    (20.0, 28.0, 68.0, 76.0),
    "Central India": (18.0, 26.0, 76.0, 83.0),
    "Northeast":     (22.0, 29.0, 88.0, 97.0),
}

def assign_region(lat, lon):
    for region, (lat_min, lat_max, lon_min, lon_max) in REGIONS.items():
        if lat_min <= lat <= lat_max and lon_min <= lon <= lon_max:
            return region
    return "Other"


# =========================
# 6. Flexible CSV reader
# =========================
def _read_csv_flexible(source):
    if isinstance(source, str):
        stripped = source.strip()
        if "\n" in stripped and "," in stripped[:200]:
            return pd.read_csv(io.StringIO(source))
        return pd.read_csv(source)
    raise ValueError("Input must be a CSV string or filepath.")


# =========================
# 7. Load WUSTL
# =========================
def load_wustl(source):
    """
    Reads WUSTL Delhi monthly PM2.5 file.

    Expected columns from your file:
      lat, lon, pm25_wustl, date, location_name

    Returns:
      date, month, lat, lon, pm25_wustl, location_name, region
    """

    df = _read_csv_flexible(source)
    df.columns = df.columns.str.strip().str.lower()

    rename_map = {}

    if "latitude" in df.columns and "lat" not in df.columns:
        rename_map["latitude"] = "lat"

    if "longitude" in df.columns and "lon" not in df.columns:
        rename_map["longitude"] = "lon"

    if "pm25" in df.columns and "pm25_wustl" not in df.columns:
        rename_map["pm25"] = "pm25_wustl"

    if "pm2.5" in df.columns and "pm25_wustl" not in df.columns:
        rename_map["pm2.5"] = "pm25_wustl"

    if rename_map:
        df = df.rename(columns=rename_map)

    required = {"lat", "lon", "pm25_wustl", "date"}
    missing = required - set(df.columns)

    if missing:
        raise ValueError(f"WUSTL CSV missing columns: {missing}")

    df["lat"] = pd.to_numeric(df["lat"], errors="coerce")
    df["lon"] = pd.to_numeric(df["lon"], errors="coerce")
    df["pm25_wustl"] = pd.to_numeric(df["pm25_wustl"], errors="coerce")

    df["date"] = pd.to_datetime(
        df["date"],
        errors="coerce",
        dayfirst=True
    )

    df = df.dropna(subset=["lat", "lon", "pm25_wustl", "date"]).copy()

    df["month"] = df["date"].dt.to_period("M").astype(str)
    df["date"] = df["date"].dt.strftime("%Y-%m-%d")

    if "location_name" not in df.columns:
        df["location_name"] = "Delhi_WUSTL_grid"

    df["region"] = df.apply(lambda r: assign_region(r["lat"], r["lon"]), axis=1)

    print(f"✓ WUSTL loaded — {len(df):,} rows across {df['month'].nunique()} months")
    print("\nWUSTL month counts:")
    print(df["month"].value_counts().sort_index())

    return df.reset_index(drop=True)


# =========================
# 8. Load REAL WRF-Chem CSV and crop to Delhi
# =========================
def load_wrfchem(source):
    """
    Reads the real WRF-Chem output CSV, crops it to Delhi,
    and returns a tidy dataframe.

    Expected WRF-Chem columns from your file:
      XTIME, bnds, lev, y, x, XTIME_bnds, PM2_5_DRY, XLONG, XLAT

    Important:
      Use XTIME for date parsing, not XTIME_bnds.
      XTIME_bnds caused incomplete month extraction earlier.

    Returns:
      date, month, lat, lon, pm25_wrfchem, grid_id,
      resolution_km, grid_center_lat, grid_center_lon, region
    """

    df = _read_csv_flexible(source)
    df.columns = df.columns.str.strip()

    print("\nWRF-Chem raw shape:", df.shape)
    print("WRF-Chem columns:", df.columns.tolist())

    # ── Identify PM2.5 column ────────────────────────────────────────────────
    pm25_col = None

    for candidate in [
        "PM2_5_DRY",
        "PM2_5_DI",
        "PM2_5",
        "PM25",
        "pm2_5_dry",
        "pm2_5_di",
        "pm25"
    ]:
        if candidate in df.columns:
            pm25_col = candidate
            break

    if pm25_col is None:
        raise ValueError(
            "Cannot find PM2.5 column in WRF-Chem CSV. "
            "Columns found: " + str(list(df.columns))
        )

    # ── Required coordinate and time columns ─────────────────────────────────
    required = {"XTIME", "XLAT", "XLONG", pm25_col}
    missing = required - set(df.columns)

    if missing:
        raise ValueError(f"WRF-Chem CSV missing columns: {missing}")

    # ── Numeric coercion before crop ─────────────────────────────────────────
    df["XLAT"] = pd.to_numeric(df["XLAT"], errors="coerce")
    df["XLONG"] = pd.to_numeric(df["XLONG"], errors="coerce")
    df[pm25_col] = pd.to_numeric(df[pm25_col], errors="coerce")

    df = df.dropna(subset=["XLAT", "XLONG", pm25_col]).copy()

    print("\nWRF-Chem latitude range before crop:")
    print(df["XLAT"].min(), df["XLAT"].max())

    print("\nWRF-Chem longitude range before crop:")
    print(df["XLONG"].min(), df["XLONG"].max())

    # ── Parse date using XTIME ───────────────────────────────────────────────
    df["date_dt"] = pd.to_datetime(
        df["XTIME"],
        format="%Y-%m-%d %H:%M:%S",
        errors="coerce"
    )

    failed_dates = df["date_dt"].isna().sum()
    print("\nRows with failed WRF-Chem XTIME parsing:", failed_dates)

    if failed_dates > 0:
        print("\nExamples of failed XTIME values:")
        print(df.loc[df["date_dt"].isna(), "XTIME"].dropna().unique()[:20])

    df = df.dropna(subset=["date_dt"]).copy()

    df["month"] = df["date_dt"].dt.to_period("M").astype(str)
    df["date"] = df["date_dt"].dt.strftime("%Y-%m-%d")

    print("\nWRF-Chem month counts BEFORE Delhi crop:")
    print(df["month"].value_counts().sort_index())

    # =========================
    # WRF-Chem Delhi crop block
    # =========================
    wrf_delhi = df[
        (df["XLAT"] >= DELHI_LAT_MIN) &
        (df["XLAT"] <= DELHI_LAT_MAX) &
        (df["XLONG"] >= DELHI_LON_MIN) &
        (df["XLONG"] <= DELHI_LON_MAX)
    ].copy()

    print("\nOriginal WRF-Chem rows after cleaning:", len(df))
    print("WRF-Chem rows after Delhi crop:", len(wrf_delhi))

    if wrf_delhi.empty:
        raise ValueError(
            "Delhi crop returned 0 rows. "
            "Check the Delhi bounding box or WRF-Chem coordinate columns."
        )

    print("\nWRF-Chem month counts AFTER Delhi crop:")
    print(wrf_delhi["month"].value_counts().sort_index())

    # ── Rename to clean internal names ───────────────────────────────────────
    wrf_delhi = wrf_delhi.rename(columns={
        "XLAT": "lat",
        "XLONG": "lon",
        pm25_col: "pm25_wrfchem"
    })

    # ── Aggregate duplicate month-lat-lon cells ──────────────────────────────
    # Since this is monthly comparison, aggregate by month and WRF grid location.
    wrf_delhi = (
        wrf_delhi
        .groupby(["month", "lat", "lon"], as_index=False)
        .agg(
            pm25_wrfchem=("pm25_wrfchem", "mean"),
            date=("date", "first")
        )
    )

    wrf_delhi["pm25_wrfchem"] = wrf_delhi["pm25_wrfchem"].round(2)

    # ── Add helper columns expected downstream ───────────────────────────────
    wrf_delhi["grid_id"] = [
        f"WRF_{row.month}_{i+1:05d}"
        for i, row in enumerate(wrf_delhi.itertuples(index=False))
    ]

    wrf_delhi["resolution_km"] = 25
    wrf_delhi["grid_center_lat"] = wrf_delhi["lat"]
    wrf_delhi["grid_center_lon"] = wrf_delhi["lon"]
    wrf_delhi["region"] = wrf_delhi.apply(
        lambda r: assign_region(r["lat"], r["lon"]),
        axis=1
    )

    print(
        f"\n✓ WRF-Chem Delhi crop loaded — {len(wrf_delhi):,} grid-month cells "
        f"across {wrf_delhi['month'].nunique()} months"
    )

    return wrf_delhi[[
        "date",
        "month",
        "lat",
        "lon",
        "pm25_wrfchem",
        "grid_id",
        "resolution_km",
        "grid_center_lat",
        "grid_center_lon",
        "region"
    ]].reset_index(drop=True)


# =========================
# 9. Spatial join
# =========================
def spatial_join(wustl_df, wrf_df, max_dist=0.3):
    """
    Spatially matches each WUSTL point to the nearest WRF-Chem grid cell
    within the same month.

    max_dist is in degrees, not km.
    0.3 degrees is roughly around 30 km, depending on latitude.
    """

    merged_parts = []

    common_months = sorted(set(wustl_df["month"]).intersection(set(wrf_df["month"])))

    if not common_months:
        raise ValueError("No overlapping months between WUSTL and WRF-Chem data.")

    print(f"\n✓ {len(common_months)} overlapping months found for spatial join:")
    print(common_months)

    for month_value in common_months:
        w_sub = wustl_df[wustl_df["month"] == month_value].copy()
        r_sub = wrf_df[wrf_df["month"] == month_value].copy()

        if w_sub.empty or r_sub.empty:
            continue

        tree = cKDTree(r_sub[["lat", "lon"]].values)
        distances, indices = tree.query(w_sub[["lat", "lon"]].values, k=1)

        temp = w_sub.copy()
        temp["wrf_idx_local"] = indices
        temp["match_dist"] = distances

        temp = temp[temp["match_dist"] <= max_dist].copy()

        if temp.empty:
            print(f"Warning: No matches found for {month_value} within max_dist={max_dist}")
            continue

        matched_wrf = r_sub.iloc[temp["wrf_idx_local"].values].reset_index(drop=True)
        temp = temp.reset_index(drop=True)

        temp["pm25_wrfchem"] = matched_wrf["pm25_wrfchem"].values
        temp["wrf_grid_id"] = matched_wrf["grid_id"].values
        temp["wrf_lat"] = matched_wrf["lat"].values
        temp["wrf_lon"] = matched_wrf["lon"].values
        temp["wrf_date"] = matched_wrf["date"].values

        temp["delta"] = (temp["pm25_wustl"] - temp["pm25_wrfchem"]).round(2)
        temp["abs_delta"] = temp["delta"].abs()

        temp["pct_diff"] = (
            (temp["delta"] / temp["pm25_wrfchem"].replace(0, np.nan)) * 100
        ).round(1)

        merged_parts.append(temp)

    if not merged_parts:
        return pd.DataFrame()

    merged = pd.concat(merged_parts, ignore_index=True)

    print(f"\n✓ Spatial join complete — {len(merged):,} matched WUSTL points")

    return merged


# =========================
# 10. Summaries
# =========================
def region_summary(merged):
    return (
        merged.groupby("region")["delta"]
        .agg(
            n="count",
            mean="mean",
            median="median",
            std="std",
            pct_wustl_higher=lambda x: round((x > 0).mean() * 100, 1),
        )
        .round(2)
        .reset_index()
    )


def north_india_verdict(merged):
    north = merged[merged["region"] == "North India"]

    if north.empty:
        return "No North India points in dataset."

    m = north["delta"].mean()
    s = north["delta"].std()
    pct = (north["delta"] > 0).mean() * 100

    if pd.isna(s):
        return (
            f"North India has too few points for spread estimation. "
            f"Mean delta = {m:+.1f} µg/m³."
        )

    if s < abs(m) * 0.5:
        return (
            f"SYSTEMATIC bias detected — WUSTL reads {m:+.1f} µg/m³ vs WRF-Chem "
            f"(std={s:.1f}, {pct:.0f}% of points WUSTL > WRF)."
        )

    return (
        f"SCATTERED deviation — mean delta={m:+.1f} µg/m³ but high spread "
        f"(std={s:.1f}). No strong regional bias."
    )


# =========================
# 11. Map
# =========================
def build_map(merged, wrf_df):
    def delta_color(delta):
        if delta < -30:
            return "#042C53"
        elif delta < -15:
            return "#185FA5"
        elif delta < 0:
            return "#85B7EB"
        elif delta < 15:
            return "#EF9F27"
        elif delta < 30:
            return "#D85A30"
        else:
            return "#A32D2D"

    if merged.empty:
        print("No merged points available for map.")
        return

    center_lat = merged["lat"].mean()
    center_lon = merged["lon"].mean()

    m = folium.Map(
        location=[center_lat, center_lon],
        zoom_start=9,
        tiles="CartoDB positron"
    )

    # WRF grid layer
    wrf_layer = folium.FeatureGroup(name="WRF-Chem Delhi crop grid", show=True)

    # Avoid drawing too many duplicate rectangles.
    wrf_unique = wrf_df.drop_duplicates(subset=["lat", "lon"])

    for _, row in wrf_unique.iterrows():
        half = 0.125

        folium.Rectangle(
            bounds=[
                [row.lat - half, row.lon - half],
                [row.lat + half, row.lon + half]
            ],
            color="#3B6D11",
            weight=1,
            fill=True,
            fill_color="#3B6D11",
            fill_opacity=0.08,
            tooltip=folium.Tooltip(
                f"<b>WRF-Chem grid</b><br>"
                f"Lat: {row.lat:.3f}<br>"
                f"Lon: {row.lon:.3f}<br>"
                f"Resolution: approx. 25km × 25km"
            ),
        ).add_to(wrf_layer)

    wrf_layer.add_to(m)

    # WUSTL point layer
    wustl_layer = folium.FeatureGroup(name="WUSTL points matched to WRF-Chem", show=True)

    for _, row in merged.iterrows():
        popup_html = f"""
        <div style='font-family:sans-serif;font-size:13px;min-width:260px'>
          <b style='font-size:14px'>{row.location_name}</b><br>
          <span style='color:#888;font-size:11px'>{row.region} · {row.month}</span>
          <hr style='margin:5px 0'>
          <table style='width:100%'>
            <tr>
              <td>WUSTL PM2.5</td>
              <td align='right'><b style='color:#185FA5'>{row.pm25_wustl:.1f} µg/m³</b></td>
            </tr>
            <tr>
              <td>WRF-Chem PM2.5</td>
              <td align='right'><b style='color:#3B6D11'>{row.pm25_wrfchem:.1f} µg/m³</b></td>
            </tr>
            <tr>
              <td><b>Delta Δ</b></td>
              <td align='right'><b style='color:{"#A32D2D" if row.delta > 0 else "#185FA5"}'>{row.delta:+.1f} µg/m³</b></td>
            </tr>
            <tr>
              <td>% difference</td>
              <td align='right'>{row.pct_diff:+.1f}%</td>
            </tr>
            <tr>
              <td>Nearest WRF distance</td>
              <td align='right'>{row.match_dist:.3f} degrees</td>
            </tr>
          </table>
        </div>
        """

        folium.CircleMarker(
            location=[row.lat, row.lon],
            radius=4,
            color="white",
            weight=0.8,
            fill=True,
            fill_color=delta_color(row.delta),
            fill_opacity=0.9,
            popup=folium.Popup(popup_html, max_width=280),
            tooltip=folium.Tooltip(
                f"{row.location_name} · {row.month} · Δ = {row.delta:+.1f} µg/m³"
            ),
        ).add_to(wustl_layer)

    wustl_layer.add_to(m)

    legend_html = """
    <div style='position:fixed;bottom:30px;left:30px;z-index:1000;background:white;
                padding:12px 16px;border-radius:8px;border:1px solid #ddd;
                font-family:sans-serif;font-size:12px;line-height:1.8'>
      <b>Δ WUSTL − WRF-Chem (µg/m³)</b><br>
      <span style='background:#A32D2D;padding:1px 8px;border-radius:3px;color:white'>■</span> &gt; +30<br>
      <span style='background:#D85A30;padding:1px 8px;border-radius:3px;color:white'>■</span> +15 to +30<br>
      <span style='background:#EF9F27;padding:1px 8px;border-radius:3px;color:white'>■</span> 0 to +15<br>
      <span style='background:#85B7EB;padding:1px 8px;border-radius:3px;color:white'>■</span> −15 to 0<br>
      <span style='background:#185FA5;padding:1px 8px;border-radius:3px;color:white'>■</span> −30 to −15<br>
      <span style='background:#042C53;padding:1px 8px;border-radius:3px;color:white'>■</span> &lt; −30
    </div>
    """

    m.get_root().html.add_child(folium.Element(legend_html))
    folium.LayerControl().add_to(m)

    m.save("pm25_delta_map.html")
    print("✓ Map saved → pm25_delta_map.html")

    display(m)


# =========================
# 12. Charts
# =========================
def build_charts(merged, summary):
    if merged.empty:
        print("No merged points available for charts.")
        return

    fig = make_subplots(
        rows=2,
        cols=2,
        subplot_titles=[
            "WUSTL vs WRF-Chem — scatter",
            "Delta by region",
            "Distribution of all deltas",
            "Mean delta per region",
        ],
    )

    fig.add_trace(
        go.Scatter(
            x=merged["pm25_wrfchem"],
            y=merged["pm25_wustl"],
            mode="markers",
            marker=dict(
                color=merged["delta"],
                colorscale="RdBu_r",
                size=7,
                showscale=True,
                colorbar=dict(title="Δ µg/m³", x=0.46),
            ),
            text=merged["location_name"],
            hovertemplate=(
                "<b>%{text}</b><br>"
                "WRF: %{x:.1f} µg/m³<br>"
                "WUSTL: %{y:.1f} µg/m³<br>"
                "<extra></extra>"
            ),
            name="Points",
        ),
        row=1,
        col=1,
    )

    min_val = min(merged["pm25_wrfchem"].min(), merged["pm25_wustl"].min())
    max_val = max(merged["pm25_wrfchem"].max(), merged["pm25_wustl"].max())

    fig.add_trace(
        go.Scatter(
            x=[min_val, max_val],
            y=[min_val, max_val],
            mode="lines",
            line=dict(dash="dash", color="gray", width=1),
            showlegend=False,
        ),
        row=1,
        col=1,
    )

    colors = ["#185FA5", "#3B6D11", "#D85A30", "#7F77DD", "#1D9E75", "#BA7517"]

    for i, region in enumerate(merged["region"].unique()):
        fig.add_trace(
            go.Box(
                y=merged[merged["region"] == region]["delta"],
                name=region,
                marker_color=colors[i % len(colors)],
                showlegend=False,
            ),
            row=1,
            col=2,
        )

    fig.add_hline(y=0, line_dash="dot", line_color="gray", row=1, col=2)

    fig.add_trace(
        go.Histogram(
            x=merged["delta"],
            nbinsx=30,
            marker_color="#378ADD",
            opacity=0.8,
            showlegend=False,
        ),
        row=2,
        col=1,
    )

    fig.add_vline(x=0, line_dash="dash", line_color="gray", row=2, col=1)

    fig.add_trace(
        go.Bar(
            x=summary["region"],
            y=summary["mean"],
            marker_color=[
                "#A32D2D" if v > 0 else "#185FA5"
                for v in summary["mean"]
            ],
            text=summary["mean"].apply(lambda x: f"{x:+.1f}"),
            textposition="outside",
            showlegend=False,
        ),
        row=2,
        col=2,
    )

    fig.add_hline(y=0, line_dash="dash", line_color="gray", row=2, col=2)

    fig.update_layout(
        height=720,
        title_text="PM2.5 Delta Analysis — WUSTL vs Delhi-Cropped WRF-Chem",
        title_font_size=15,
        paper_bgcolor="white",
        plot_bgcolor="white",
        font=dict(size=11),
    )

    fig.update_xaxes(showgrid=True, gridcolor="#eee")
    fig.update_yaxes(showgrid=True, gridcolor="#eee")

    fig.show()
    fig.write_html("pm25_delta_charts.html")

    print("✓ Charts saved → pm25_delta_charts.html")


# =========================
# 13. Optional monthly summary
# =========================
def monthly_summary(merged):
    if merged.empty:
        return pd.DataFrame()

    return (
        merged
        .groupby("month")
        .agg(
            n=("delta", "count"),
            mean_wustl=("pm25_wustl", "mean"),
            mean_wrfchem=("pm25_wrfchem", "mean"),
            mean_delta=("delta", "mean"),
            median_delta=("delta", "median"),
            pct_wustl_higher=("delta", lambda x: round((x > 0).mean() * 100, 1))
        )
        .round(2)
        .reset_index()
    )


# =========================
# 14. Master run
# =========================
def run_pipeline(wustl_source, wrfchem_source):
    wustl_df = load_wustl(wustl_source)
    wrf_df = load_wrfchem(wrfchem_source)

    merged = spatial_join(
        wustl_df,
        wrf_df,
        max_dist=0.3
    )

    if merged.empty:
        raise ValueError(
            "Spatial join returned 0 rows. "
            "Try increasing max_dist or checking coordinate systems."
        )

    summary = region_summary(merged)
    month_summary = monthly_summary(merged)
    verdict = north_india_verdict(merged)

    return wustl_df, wrf_df, merged, summary, month_summary, verdict


# =========================
# 15. Run
# =========================
wustl_df, wrf_df, merged, summary, month_summary_df, verdict = run_pipeline(
    WUSTL_CSV_PATH,
    WRFCHEM_CSV_PATH
)

print(f"\n✓ Pipeline complete — {len(merged):,} matched points")

print(f"\n── North India verdict ──")
print(verdict)

print(f"\n── Region summary ──")
print(summary.to_string(index=False))

print(f"\n── Monthly summary ──")
print(month_summary_df.to_string(index=False))

build_map(merged, wrf_df)
build_charts(merged, summary)


# =========================
# 16. Save outputs
# =========================
merged.to_csv("processed_delta_data.csv", index=False)
wrf_df.to_csv("WRF_real_data_delhi_cropped.csv", index=False)
summary.to_csv("region_summary.csv", index=False)
month_summary_df.to_csv("monthly_summary.csv", index=False)

print("\n✓ Saved processed_delta_data.csv")
print("✓ Saved WRF_real_data_delhi_cropped.csv")
print("✓ Saved region_summary.csv")
print("✓ Saved monthly_summary.csv")
