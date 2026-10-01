from pathlib import Path

import folium
import numpy as np
import pandas as pd
import plotly.express as px
import streamlit as st
from branca.colormap import LinearColormap
from streamlit_folium import st_folium

st.set_page_config(
    page_title="WebGIS LST TP.HCM",
    page_icon="🌡️",
    layout="wide",
    initial_sidebar_state="expanded",
)

st.markdown(
    """
    <style>
    .stApp { background: #080d18; color: #eef5ff; }
    [data-testid="stSidebar"] { background: #0d1424; border-right: 1px solid #263b58; }
    [data-testid="stMetric"] { background: #111d30; border: 1px solid #263b58; padding: 14px; border-radius: 10px; }
    [data-testid="stMetricValue"] { color: #42d6ff; }
    .subtitle { color: #91a7c2; margin-top: -12px; }
    .source-box { background: #14263b; border-left: 4px solid #20c9d9; padding: 12px 16px; border-radius: 6px; }
    </style>
    """,
    unsafe_allow_html=True,
)

DATA_PATH = Path(__file__).parent / "data" / "lst_samples.csv"
AREAS = [
    "Toàn thành phố", "TP. Thủ Đức", "Quận 1", "Quận 4", "Quận 7",
    "Quận 10", "Quận 12", "Bình Thạnh", "Gò Vấp", "Tân Bình",
    "Bình Tân", "Củ Chi", "Cần Giờ",
]
CENTERS = {
    "TP. Thủ Đức": (10.803, 106.755), "Quận 1": (10.776, 106.700),
    "Quận 4": (10.758, 106.704), "Quận 7": (10.735, 106.722),
    "Quận 10": (10.773, 106.667), "Quận 12": (10.863, 106.650),
    "Bình Thạnh": (10.810, 106.709), "Gò Vấp": (10.838, 106.665),
    "Tân Bình": (10.801, 106.652), "Bình Tân": (10.763, 106.604),
    "Củ Chi": (11.006, 106.513), "Cần Giờ": (10.411, 106.954),
}
OUTLINE = [
    [10.95, 106.42], [11.08, 106.58], [10.98, 106.83], [10.79, 107.02],
    [10.52, 107.08], [10.32, 106.91], [10.38, 106.72], [10.53, 106.61],
    [10.60, 106.46], [10.76, 106.39],
]


@st.cache_data
def make_sample_data(month: int, year: int, area: str) -> pd.DataFrame:
    """Create stable demo observations for the selected month and year."""
    rng = np.random.default_rng(year * 100 + month)
    records = []
    for lat in np.linspace(10.42, 11.02, 30):
        for lon in np.linspace(106.48, 106.98, 34):
            urban_heat = 3.8 * np.exp(-(((lat - 10.78) / 0.18) ** 2 + ((lon - 106.68) / 0.16) ** 2))
            coastal_cooling = 2.8 * np.exp(-(((lat - 10.48) / 0.11) ** 2 + ((lon - 106.92) / 0.14) ** 2))
            seasonal = 1.3 * np.sin((month - 2) / 12 * 2 * np.pi)
            value = 29 + urban_heat - coastal_cooling + seasonal + rng.normal(0, 0.45)
            records.append({"lat": lat, "lon": lon, "lst_c": round(float(value), 2)})

    frame = pd.DataFrame(records)
    if area != "Toàn thành phố" and area in CENTERS:
        center_lat, center_lon = CENTERS[area]
        distance = ((frame.lat - center_lat) / 0.075) ** 2 + ((frame.lon - center_lon) / 0.09) ** 2
        selected = frame[distance <= 1]
        if len(selected) >= 5:
            return selected.reset_index(drop=True)
    return frame


def load_user_csv(month: int, year: int, area: str):
    """Load user CSV and optionally filter by month, year and area columns."""
    if not DATA_PATH.exists():
        return None, None
    try:
        frame = pd.read_csv(DATA_PATH)
    except (OSError, ValueError, pd.errors.ParserError):
        return None, None

    required = {"lat", "lon", "lst_c"}
    if not required.issubset(frame.columns):
        return None, "CSV phải có các cột lat, lon, lst_c"

    frame = frame.copy()
    for column in ["lat", "lon", "lst_c"]:
        frame[column] = pd.to_numeric(frame[column], errors="coerce")
    frame = frame.dropna(subset=["lat", "lon", "lst_c"])

    if "month" in frame.columns:
        frame = frame[pd.to_numeric(frame["month"], errors="coerce") == month]
    if "year" in frame.columns:
        frame = frame[pd.to_numeric(frame["year"], errors="coerce") == year]
    if "area" in frame.columns and area != "Toàn thành phố":
        frame = frame[frame["area"].astype(str).eq(area)]

    return (frame if not frame.empty else None), None


def load_data(month: int, year: int, area: str):
    user_frame, warning = load_user_csv(month, year, area)
    if user_frame is not None:
        return user_frame.reset_index(drop=True), "CSV LST do người dùng cung cấp", warning
    return make_sample_data(month, year, area), "Dữ liệu mẫu mô phỏng deterministic", warning


def make_map(frame: pd.DataFrame):
    fmap = folium.Map(
        location=[10.78, 106.70],
        zoom_start=10,
        tiles=None,
        control_scale=True,
    )
    folium.TileLayer("CartoDB dark_matter", name="Bản đồ tối", control=True).add_to(fmap)
    folium.TileLayer(
        tiles="https://server.arcgisonline.com/ArcGIS/rest/services/World_Imagery/MapServer/tile/{z}/{y}/{x}",
        attr="Esri World Imagery",
        name="Ảnh vệ tinh",
        overlay=False,
        control=True,
    ).add_to(fmap)

    folium.GeoJson(
        {
            "type": "Feature",
            "properties": {"name": "TP. Hồ Chí Minh"},
            "geometry": {
                "type": "Polygon",
                "coordinates": [[[lon, lat] for lat, lon in OUTLINE]],
            },
        },
        name="Ranh giới TP.HCM (minh họa)",
        style_function=lambda _: {
            "color": "#31c8ff", "weight": 2, "fillColor": "#1677a8", "fillOpacity": 0.08,
        },
        tooltip="TP. Hồ Chí Minh",
    ).add_to(fmap)

    cmap = LinearColormap(
        ["#1646b5", "#18b9c8", "#57c95a", "#ffd447", "#ff7b32", "#e63946"],
        vmin=18,
        vmax=40,
    )
    cmap.caption = "Nhiệt độ bề mặt đất (°C)"
    cmap.add_to(fmap)

    for row in frame.itertuples(index=False):
        color = cmap(float(row.lst_c))
        folium.CircleMarker(
            location=[row.lat, row.lon],
            radius=5,
            color=color,
            fill=True,
            fill_color=color,
            fill_opacity=0.8,
            weight=0.5,
            tooltip=f"LST: {row.lst_c:.1f} °C",
        ).add_to(fmap)

    folium.LayerControl(collapsed=False).add_to(fmap)
    return fmap


with st.sidebar:
    st.markdown("## 🌡️ LST Intelligence")
    st.caption("WebGIS nhiệt độ bề mặt đất")
    st.divider()
    st.markdown("### 🔍 BỘ LỌC DỮ LIỆU")
    st.selectbox("Tỉnh / thành phố", ["TP. Hồ Chí Minh"], disabled=True)
    area = st.selectbox("Quận / huyện / khu vực", AREAS)
    month = st.selectbox("Tháng", range(1, 13), index=8, format_func=lambda value: f"Tháng {value}")
    year = st.selectbox("Năm", range(2020, 2027), index=6)
    analyze = st.button("🌡️ PHÂN TÍCH LST", type="primary", use_container_width=True)
    if st.button("↺ ĐẶT LẠI", use_container_width=True):
        st.rerun()
    st.divider()
    st.markdown("### 🗺️ HƯỚNG DẪN")
    st.caption("Rê chuột lên điểm màu để xem nhiệt độ. Dùng nút lớp bản đồ ở góc phải để đổi nền.")
    st.caption("Ngưỡng điểm nóng: LST ≥ 35°C.")

frame, source, warning = load_data(month, year, area)
mean_lst = float(frame.lst_c.mean())
max_lst = float(frame.lst_c.max())
min_lst = float(frame.lst_c.min())
hot_ratio = float((frame.lst_c >= 35).mean() * 100)

st.title("🌡️ Không gian Trực quan hóa & Phân tích Nhiệt độ Bề mặt đất")
st.markdown(
    '<div class="subtitle">WebGIS LST cho Thành phố Hồ Chí Minh — theo dõi điểm nóng đô thị và biến động nhiệt bề mặt</div>',
    unsafe_allow_html=True,
)
st.markdown(
    f'<div class="source-box">📡 <b>Nguồn dữ liệu:</b> {source} &nbsp;|&nbsp; '
    f'<b>Khu vực:</b> TP. Hồ Chí Minh — {area} &nbsp;|&nbsp; <b>Thời gian:</b> {month:02d}/{year}</div>',
    unsafe_allow_html=True,
)
if warning:
    st.warning(warning + ". Ứng dụng đang dùng dữ liệu mẫu.")
if analyze:
    st.success("Đã cập nhật phân tích theo bộ lọc hiện tại.")

map_col, stat_col = st.columns([3, 1])
with map_col:
    st.subheader("🗺️ Bản đồ LST theo không gian")
    st_folium(make_map(frame), height=570, width=None, key="lst_map")
with stat_col:
    st.subheader("📊 CHỈ SỐ VÙNG")
    st.metric("LST TRUNG BÌNH", f"{mean_lst:.1f} °C")
    st.metric("LST CAO NHẤT", f"{max_lst:.1f} °C")
    st.metric("LST THẤP NHẤT", f"{min_lst:.1f} °C")
    st.metric("KHU VỰC ≥ 35°C", f"{hot_ratio:.1f}%")
    st.metric("SỐ ĐIỂM DỮ LIỆU", f"{len(frame):,}")

chart_col, trend_col = st.columns(2)
with chart_col:
    st.subheader("🌈 Phân bố nhiệt độ")
    bins = [-np.inf, 20, 25, 30, 35, np.inf]
    labels = ["<20°C", "20–25°C", "25–30°C", "30–35°C", "≥35°C"]
    distribution = pd.cut(frame.lst_c, bins=bins, labels=labels).value_counts().reindex(labels, fill_value=0).reset_index()
    distribution.columns = ["Khoảng nhiệt độ", "Số điểm"]
    fig = px.bar(
        distribution,
        x="Khoảng nhiệt độ",
        y="Số điểm",
        color="Khoảng nhiệt độ",
        color_discrete_sequence=["#2463d4", "#17b6c8", "#54c85b", "#ffbd32", "#e94b43"],
    )
    fig.update_layout(template="plotly_dark", height=330, showlegend=False, margin=dict(l=10, r=10, t=10, b=10))
    st.plotly_chart(fig, use_container_width=True)

with trend_col:
    st.subheader("📈 Xu hướng LST theo tháng")
    trend = pd.DataFrame(
        [
            {"Tháng": f"T{i}", "LST trung bình (°C)": round(float(make_sample_data(i, year, area).lst_c.mean()), 2)}
            for i in range(1, 13)
        ]
    )
    fig = px.line(trend, x="Tháng", y="LST trung bình (°C)", markers=True)
    fig.update_traces(line_color="#20c9d9", marker_color="#ffb52e")
    fig.update_layout(template="plotly_dark", height=330, margin=dict(l=10, r=10, t=10, b=10))
    st.plotly_chart(fig, use_container_width=True)

with st.expander("ℹ️ Cách thay dữ liệu mẫu bằng dữ liệu LST thật"):
    st.markdown(
        """
        CSV tối thiểu cần có `lat`, `lon`, `lst_c`. Có thể thêm `month`, `year`, `area` để bộ lọc hoạt động theo thời gian/khu vực.

        Dữ liệu demo và đường bao TP.HCM hiện chỉ phục vụ minh họa giao diện. Khi làm báo cáo chính thức, nên thay bằng GeoTIFF LST đã xử lý và GeoJSON hành chính chính thức.
        """
    )
