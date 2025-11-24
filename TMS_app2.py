# app.py
import streamlit as st
import pandas as pd
import numpy as np
from math import radians, sin, cos, sqrt, atan2
import folium
from streamlit_folium import st_folium
import io

st.set_page_config(page_title="TMS Demo - Route Optimization", layout="wide")

# ---------------------------
# Utilities
# ---------------------------
def haversine(lat1, lon1, lat2, lon2):
    R = 6371.0
    dlat = radians(lat2 - lat1)
    dlon = radians(lon2 - lon1)
    a = sin(dlat/2)**2 + cos(radians(lat1)) * cos(radians(lat2)) * sin(dlon/2)**2
    c = 2 * atan2(sqrt(a), sqrt(1 - a))
    return R * c

def pairwise_distance_matrix(points):
    n = len(points)
    mat = [[0.0]*n for _ in range(n)]
    for i in range(n):
        for j in range(n):
            if i != j:
                mat[i][j] = haversine(points[i][0], points[i][1], points[j][0], points[j][1])
    return mat

def route_distance(route, distmat):
    total = 0.0
    for i in range(len(route)-1):
        total += distmat[route[i]][route[i+1]]
    return total

def nearest_neighbor(distmat, start=0):
    n = len(distmat)
    unvisited = set(range(n))
    route = [start]
    unvisited.remove(start)
    current = start
    while unvisited:
        next_node = min(unvisited, key=lambda x: distmat[current][x])
        route.append(next_node)
        unvisited.remove(next_node)
        current = next_node
    route.append(start)
    return route

def two_opt(route, distmat, improvement_threshold=0.01):
    best = route
    improved = True
    best_distance = route_distance(best, distmat)
    while improved:
        improved = False
        for i in range(1, len(best) - 2):
            for j in range(i+1, len(best) - 1):
                if j - i == 1:
                    continue
                new_route = best[:]
                new_route[i:j+1] = reversed(best[i:j+1])
                new_distance = route_distance(new_route, distmat)
                if new_distance + 1e-6 < best_distance:
                    best = new_route
                    best_distance = new_distance
                    improved = True
    return best

# ---------------------------
# Initial demo data
# ---------------------------
if "orders" not in st.session_state:
    st.session_state["orders"] = pd.DataFrame([
        {"Mã Đơn": "DH001", "Điểm Lấy": "Kho Hà Nội", "Điểm Giao": "Ba Đình", "Lat": 21.0366, "Lon": 105.8342, "Khối Lượng": 1.2, "Trạng Thái":"Pending", "Thời Gian":"2025-11-01"},
        {"Mã Đơn": "DH002", "Điểm Lấy": "Kho Hà Nội", "Điểm Giao": "Long Biên", "Lat": 21.0500, "Lon": 105.8900, "Khối Lượng": 0.8, "Trạng Thái":"Pending", "Thời Gian":"2025-11-01"},
        {"Mã Đơn": "DH003", "Điểm Lấy": "Kho Hà Nội", "Điểm Giao": "Hà Đông", "Lat": 20.9910, "Lon": 105.7940, "Khối Lượng": 1.5, "Trạng Thái":"Pending", "Thời Gian":"2025-11-01"},
        {"Mã Đơn": "DH004", "Điểm Lấy": "Kho Hà Nội", "Điểm Giao": "Thanh Trì", "Lat": 20.9891, "Lon": 105.8689, "Khối Lượng": 2.0, "Trạng Thái":"Pending", "Thời Gian":"2025-11-01"},
        {"Mã Đơn": "DH005", "Điểm Lấy": "Kho Hà Nội", "Điểm Giao": "Sóc Sơn", "Lat": 21.2150, "Lon": 105.7809, "Khối Lượng": 0.5, "Trạng Thái":"Pending", "Thời Gian":"2025-11-01"},
    ])

# ---------------------------
# Sidebar
# ---------------------------
st.sidebar.title("TMS Demo - Menu")
page = st.sidebar.radio("Chọn trang", ["Dashboard", "Quản Lý Đơn Hàng", "Lập Kế Hoạch Tuyến Đường", "Báo Cáo / Xuất"])

# ---------------------------
# Dashboard
# ---------------------------
if page == "Dashboard":
    st.header("Tổng Quan TMS - Demo")
    df = st.session_state["orders"]
    col1, col2, col3 = st.columns(3)
    with col1:
        st.metric("Số đơn hiện có", len(df))
    with col2:
        ontime = int((df["Trạng Thái"] == "Delivered").sum())
        st.metric("Số đơn đã giao", ontime)
    with col3:
        st.metric("Tổng khối lượng (tấn)", f"{df['Khối Lượng'].sum():.2f}")
    st.subheader("Danh sách đơn hàng")
    df_display = df.drop(columns=[], errors="ignore")  # Chi phí đã bị loại bỏ
    st.dataframe(df_display.reset_index(drop=True))

# ---------------------------
# Quản lý đơn hàng
# ---------------------------
elif page == "Quản Lý Đơn Hàng":
    st.header("Quản Lý Đơn Hàng")
    df = st.session_state["orders"]
    st.subheader("Danh sách hiện tại")
    st.dataframe(df)

    st.subheader("Tạo đơn hàng mới")
    with st.form("form_add"):
        code = st.text_input("Mã Đơn", value=f"DH{len(df)+1:03d}")
        pickup = st.text_input("Điểm Lấy (Ghi 'Kho Hà Nội' nếu là kho)", value="Kho Hà Nội")
        dropoff = st.text_input("Điểm Giao", value="")
        lat = st.text_input("Vĩ độ (lat)", value="")
        lon = st.text_input("Kinh độ (lon)", value="")
        khối_lượng = st.number_input("Khối lượng (tấn)", min_value=0.0, step=0.1, value=0.5)
        status = st.selectbox("Trạng Thái", ["Pending", "In Transit", "Delivered"])
        date = st.date_input("Ngày Dự Kiến")
        submit = st.form_submit_button("Thêm đơn")
        if submit:
            try:
                new = {
                    "Mã Đơn": code,
                    "Điểm Lấy": pickup,
                    "Điểm Giao": dropoff,
                    "Lat": float(lat),
                    "Lon": float(lon),
                    "Khối Lượng": float(khối_lượng),
                    "Trạng Thái": status,
                    "Thời Gian": date.strftime("%Y-%m-%d")
                }
                st.session_state["orders"] = pd.concat([df, pd.DataFrame([new])], ignore_index=True)
                st.success("Đã thêm đơn hàng.")
            except Exception as e:
                st.error("Lỗi khi thêm đơn. Kiểm tra tọa độ. " + str(e))

# ---------------------------
# Lập kế hoạch tuyến đường (VRP demo)
# ---------------------------
elif page == "Lập Kế Hoạch Tuyến Đường":
    st.header("Lập Kế Hoạch Tuyến Đường - Module VRP (Demo)")

    df = st.session_state["orders"].reset_index(drop=True)

    st.subheader("Chọn Kho (depot)")
    depot_option = st.selectbox("Chọn Kho", options=["Kho Hà Nội (21.0278, 105.8342)", "Nhập tay"])
    if depot_option.startswith("Kho Hà Nội"):
        depot = ("Kho Hà Nội", 21.0278, 105.8342)
    else:
        depot_name = st.text_input("Tên Kho", value="Kho Tùy Chỉnh")
        dlat = st.number_input("Lat kho", value=21.0278)
        dlon = st.number_input("Lon kho", value=105.8342)
        depot = (depot_name, float(dlat), float(dlon))

    st.subheader("Danh sách đơn chọn để lập tuyến")
    selected = st.multiselect("Chọn mã đơn (tối đa 10 để demo tìm kiếm toàn cục)", df["Mã Đơn"].tolist(), default=df["Mã Đơn"].tolist()[:5])
    subset = df[df["Mã Đơn"].isin(selected)].reset_index(drop=True)

    st.write("Tham số xe & ràng buộc")
    col1, col2 = st.columns(2)
    with col1:
        vehicle_capacity = st.number_input("Tải trọng xe (tấn)", min_value=0.1, step=0.1, value=5.0)
    with col2:
        cost_per_km = st.number_input("Chi phí ước tính (VND/km)", min_value=0.0, step=1000.0, value=3000.0)

    points = [(depot[1], depot[2])]
    labels = [depot[0]]
    demands = [0.0]

    for _, row in subset.iterrows():
        points.append((row["Lat"], row["Lon"]))
        labels.append(f"{row['Mã Đơn']} - {row['Điểm Giao']}")
        demands.append(float(row["Khối Lượng"]))

    n = len(points)
    if n <= 1:
        st.warning("Vui lòng chọn ít nhất 1 đơn hàng để lập tuyến.")
    else:
        distmat = pairwise_distance_matrix(points)
        original_route = list(range(n)) + [0]
        original_distance = route_distance(original_route, distmat)
        nn_route = nearest_neighbor(distmat, start=0)
        nn_route = two_opt(nn_route, distmat)
        optimized_distance = route_distance(nn_route, distmat)

        # Check capacity
        capacity_ok = True
        cum_load = 0.0
        for idx in nn_route:
            cum_load += demands[idx]
            if cum_load > vehicle_capacity + 1e-9:
                capacity_ok = False
                break

        cost_original = original_distance * cost_per_km
        cost_optimized = optimized_distance * cost_per_km
        savings_km = original_distance - optimized_distance
        savings_pct = (savings_km / original_distance * 100) if original_distance > 0 else 0
        savings_vnd = cost_original - cost_optimized

        st.subheader("Kết quả tối ưu hóa (một xe demo)")
        col1, col2, col3 = st.columns(3)
        col1.metric("Quãng đường - Trước (km)", f"{original_distance:.2f}")
        col2.metric("Quãng đường - Sau (km)", f"{optimized_distance:.2f}", delta=f"{savings_km:.2f} km")
        col3.metric("Tỷ lệ tiết kiệm", f"{savings_pct:.2f} %", delta=f"{int(savings_vnd):,} VND")
        st.write("Feasibility kiểm tra tải trọng đơn giản:", "✅ OK" if capacity_ok else "❌ Vượt tải xe (cần phân chia nhiều xe)")

        # Map
        center_lat = np.mean([p[0] for p in points])
        center_lon = np.mean([p[1] for p in points])
        m = folium.Map(location=[center_lat, center_lon], zoom_start=11)
        folium.Marker([points[0][0], points[0][1]], popup=f"Depot: {labels[0]}", tooltip="Depot",
                      icon=folium.Icon(color="darkblue", icon="warehouse", prefix="fa")).add_to(m)
        for i in range(1, n):
            folium.Marker([points[i][0], points[i][1]], popup=f"{labels[i]} (demand: {demands[i]} t)",
                          tooltip=labels[i],
                          icon=folium.DivIcon(html=f"""<div style="font-size:12px;color:black;background:rgba(255,255,255,0.8);padding:2px;border-radius:3px;">{i}</div>""")
                          ).add_to(m)
        orig_coords = [[points[i][0], points[i][1]] for i in original_route]
        folium.PolyLine(orig_coords, color="gray", weight=3, opacity=0.6, tooltip="Tuyến gốc").add_to(m)
        opt_coords = [[points[i][0], points[i][1]] for i in nn_route]
        folium.PolyLine(opt_coords, color="blue", weight=4, opacity=0.8, tooltip="Tuyến tối ưu").add_to(m)
        for seq, idx in enumerate(nn_route):
            folium.map.Marker([points[idx][0], points[idx][1]],
                              icon=folium.DivIcon(html=f"""<div style="font-size:10px;color:white;background:green;padding:4px;border-radius:50%;">{seq}</div>""")
                              ).add_to(m)
        st_folium(m, width=900, height=600)

        # Xuất CSV
        csv_buf = io.StringIO()
        out_rows = []
        for seq, idx in enumerate(nn_route):
            out_rows.append({"order_index": idx, "label": labels[idx], "lat": points[idx][0], "lon": points[idx][1], "seq": seq})
        out_df = pd.DataFrame(out_rows)
        out_df.to_csv(csv_buf, index=False)
        st.download_button("📥 Tải tuyến tối ưu (CSV)", data=csv_buf.getvalue(), file_name="tuyen_toi_uu.csv", mime="text/csv")

        # Bảng chi tiết tuyến tối ưu
        st.subheader("Bảng chi tiết tuyến tối ưu (không hiển thị Chi Phí)")
        display_df = out_df.copy()
        display_df.loc[display_df["order_index"] == 0, "label"] = "Depot"
        display_df = display_df[["seq", "label", "lat", "lon"]].rename(columns={
            "seq": "Thứ tự",
            "label": "Điểm",
            "lat": "Vĩ độ",
            "lon": "Kinh độ"
        })
        st.dataframe(display_df)

# ---------------------------
# Báo cáo / Xuất
# ---------------------------
elif page == "Báo Cáo / Xuất":
    st.header("Báo Cáo & Xuất Dữ Liệu")
    df = st.session_state["orders"]
    st.subheader("Bảng hiện tại")
    st.dataframe(df)
    csv = df.to_csv(index=False).encode('utf-8')
    st.download_button("📥 Tải danh sách đơn (CSV)", data=csv, file_name="orders.csv", mime="text/csv")
    st.subheader("Thống kê nhanh")
    st.write(f"- Tổng số đơn: {len(df)}")
    st.write(f"- Tổng khối lượng (tấn): {df['Khối Lượng'].sum():.2f}")
