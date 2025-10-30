import streamlit as st
import pandas as pd
import numpy as np
from geopy.distance import great_circle
import folium
from streamlit_folium import st_folium
import time

st.set_page_config(page_title="TMS Demo App", layout="wide")

# --- Mock dữ liệu nhà vận tải ---
CARRIERS = [
    {"id": 1, "name": "Carrier A", "cost_per_km": 0.8, "speed_kmph": 50, "reliability": 0.95},
    {"id": 2, "name": "Carrier B", "cost_per_km": 0.6, "speed_kmph": 40, "reliability": 0.90},
]

# --- Hàm tính khoảng cách và ETA ---
def calculate_distance(origin, dest):
    return great_circle(origin, dest).km

def calculate_options(distance_km):
    results = []
    for c in CARRIERS:
        cost = c["cost_per_km"] * distance_km
        time_h = distance_km / c["speed_kmph"]
        score = (0.6 * cost / distance_km) + (0.3 * time_h) + (0.1 * (1 - c["reliability"]))
        results.append({
            "Carrier": c["name"],
            "Cost ($)": round(cost, 2),
            "ETA (h)": round(time_h, 1),
            "Reliability": c["reliability"],
            "Score": round(score, 3)
        })
    return pd.DataFrame(results).sort_values(by="Score")

# --- Hàm hiển thị bản đồ ---
def show_route(origin, dest):
    m = folium.Map(location=origin, zoom_start=5)
    folium.Marker(origin, tooltip="Origin", icon=folium.Icon(color="green")).add_to(m)
    folium.Marker(dest, tooltip="Destination", icon=folium.Icon(color="red")).add_to(m)
    folium.PolyLine([origin, dest], color="blue", weight=3).add_to(m)
    st_folium(m, width=700, height=400)

# --- Ứng dụng Streamlit ---
st.title("🚚 Transportation Management System (TMS) — Student Demo")
st.write("Ứng dụng mô phỏng việc lập kế hoạch vận tải và tối ưu lựa chọn nhà vận chuyển.")

tab1, tab2, tab3 = st.tabs(["1️⃣ Nhập đơn hàng", "2️⃣ Lập kế hoạch vận tải", "3️⃣ Giả lập theo dõi"])

with tab1:
    st.subheader("📦 Tạo đơn hàng mới")

    col1, col2 = st.columns(2)
    with col1:
        origin_lat = st.number_input("Vĩ độ điểm đi", value=10.762622, format="%.6f")
        origin_lng = st.number_input("Kinh độ điểm đi", value=106.660172, format="%.6f")
    with col2:
        dest_lat = st.number_input("Vĩ độ điểm đến", value=21.027764, format="%.6f")
        dest_lng = st.number_input("Kinh độ điểm đến", value=105.834160, format="%.6f")

    weight = st.number_input("Trọng lượng hàng (kg)", value=200)
    priority = st.selectbox("Mức ưu tiên giao hàng", ["Bình thường", "Nhanh"])

    if st.button("Tính khoảng cách và xem bản đồ"):
        origin = (origin_lat, origin_lng)
        dest = (dest_lat, dest_lng)
        distance_km = calculate_distance(origin, dest)
        st.success(f"Khoảng cách: **{distance_km:.2f} km**")
        show_route(origin, dest)
        st.session_state["order"] = {
            "origin": origin,
            "dest": dest,
            "distance": distance_km,
            "weight": weight,
            "priority": priority
        }

with tab2:
    st.subheader("📊 So sánh nhà vận tải")

    if "order" not in st.session_state:
        st.warning("Hãy tạo đơn hàng trước ở tab 1.")
    else:
        order = st.session_state["order"]
        df = calculate_options(order["distance"])
        st.dataframe(df, use_container_width=True)
        best = df.iloc[0]
        st.success(f"✅ Đề xuất chọn: **{best['Carrier']}** (Chi phí: ${best['Cost ($)']}, ETA: {best['ETA (h)']}h)")
        st.session_state["plan"] = best

with tab3:
    st.subheader("🚛 Giả lập theo dõi vận chuyển")

    if "plan" not in st.session_state:
        st.warning("Hãy lập kế hoạch ở tab 2 trước.")
    else:
        order = st.session_state["order"]
        plan = st.session_state["plan"]
        st.write(f"**Nhà vận tải:** {plan['Carrier']} — **Khoảng cách:** {order['distance']:.1f} km")
        st.write(f"**Thời gian dự kiến:** {plan['ETA (h)']} giờ — **Chi phí:** ${plan['Cost ($)']}")
        progress_bar = st.progress(0)
        status = st.empty()

        steps = 10
        for i in range(steps + 1):
            progress_bar.progress(i / steps)
            status.text(f"Đang vận chuyển... {i*10}% hoàn thành")
            time.sleep(0.3)

        st.success("🎉 Hàng đã được giao thành công!")
        st.balloons()
