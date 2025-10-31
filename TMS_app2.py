import streamlit as st
import pandas as pd
import numpy as np
from math import radians, cos, sin, asin, sqrt
from datetime import date

st.set_page_config(page_title="Hệ Thống Quản Lý Vận Tải (TMS) Đơn Giản", layout="wide")

# -------------------------
# Helper: hàm tính khoảng cách (Haversine)
# -------------------------
def haversine(lat1, lon1, lat2, lon2):
    # tất cả bằng độ
    try:
        lat1, lon1, lat2, lon2 = map(float, (lat1, lon1, lat2, lon2))
    except Exception:
        return None
    # bán kính trái đất (km)
    R = 6371.0
    dlat = radians(lat2 - lat1)
    dlon = radians(lon2 - lon1)
    a = sin(dlat/2)**2 + cos(radians(lat1)) * cos(radians(lat2)) * sin(dlon/2)**2
    c = 2 * asin(sqrt(a))
    return R * c

# -------------------------
# Khởi tạo dữ liệu mặc định (chỉ chạy lần đầu)
# -------------------------
default_orders = pd.DataFrame({
    "Mã Đơn": ["DH001", "DH002", "DH003"],
    "Điểm Lấy": ["Hà Nội", "TP.HCM", "Đà Nẵng"],
    "Điểm Giao": ["TP.HCM", "Hà Nội", "Nha Trang"],
    "Trạng Thái": ["Pending", "In Transit", "Delivered"],
    "Thời Gian Dự Kiến": ["2025-11-01", "2025-11-02", "2025-11-03"],
    "Chi Phí": [500000, 700000, 400000],
    # Thêm cột toạ độ mặc định (None nếu chưa có)
    "Pickup_Lat": [21.02, 10.77, 16.07],
    "Pickup_Lon": [105.84, 106.70, 108.22],
    "Dropoff_Lat": [10.77, 21.02, 12.25],
    "Dropoff_Lon": [106.70, 105.84, 109.19],
})

# session_state: orders lưu DataFrame để mọi trang dùng chung
if 'orders' not in st.session_state:
    st.session_state['orders'] = default_orders.copy()

# session_state: KPIs (cho phép chỉnh)
if 'kpis' not in st.session_state:
    st.session_state['kpis'] = {
        "so_don_hom_nay": 25,
        "ty_le_dung_han": 95.0,   # %
        "chi_phi_trung_binh": 500000,  # VND
        "phuong_tien_san_sang": 10
    }

# -------------------------
# Layout / Menu
# -------------------------
st.title("Hệ Thống Quản Lý Vận Tải (TMS) Đơn Giản")

st.sidebar.title("Menu")
page = st.sidebar.radio("Chọn trang", ["Dashboard", "Quản Lý Đơn Hàng", "Lập Kế Hoạch Tuyến Đường", "Theo Dõi Hàng Hóa", "Báo Cáo"])

orders_df = st.session_state['orders']  # pd.DataFrame

# -------------------------
# Dashboard
# -------------------------
if page == "Dashboard":
    st.header("Tổng Quan")
    # KPI columns with editable inputs
    col1, col2, col3, col4 = st.columns(4)
    with col1:
        st.subheader("Số Đơn Hôm Nay")
        so_don = st.number_input("Số Đơn Hôm Nay", min_value=0, value=int(st.session_state['kpis']['so_don_hom_nay']), key="kpi_so_don")
        st.session_state['kpis']['so_don_hom_nay'] = so_don
        st.metric("Số Đơn Hôm Nay", value=f"{so_don}", delta="+" + str(int(so_don*0.05)) if so_don else "0")
    with col2:
        st.subheader("Tỷ Lệ Đúng Hạn (%)")
        ty_le = st.number_input("Tỷ Lệ Đúng Hạn (%)", min_value=0.0, max_value=100.0, value=float(st.session_state['kpis']['ty_le_dung_han']), key="kpi_ty_le")
        st.session_state['kpis']['ty_le_dung_han'] = ty_le
        st.metric("Tỷ Lệ Đúng Hạn", value=f"{ty_le}%", delta="2%")
    with col3:
        st.subheader("Chi Phí Trung Bình (VND)")
        cp = st.number_input("Chi Phí Trung Bình (VND)", min_value=0, value=int(st.session_state['kpis']['chi_phi_trung_binh']), key="kpi_chiphi")
        st.session_state['kpis']['chi_phi_trung_binh'] = cp
        st.metric("Chi Phí Trung Bình", value=f"{cp:,} VND", delta="-10%")
    with col4:
        st.subheader("Phương Tiện Sẵn Sàng")
        pts = st.number_input("Phương Tiện Sẵn Sàng", min_value=0, value=int(st.session_state['kpis']['phuong_tien_san_sang']), key="kpi_pts")
        st.session_state['kpis']['phuong_tien_san_sang'] = pts
        st.metric("Phương Tiện Sẵn Sàng", value=f"{pts}", delta="2")

    # Không hiện bản đồ tuyến đường ở Dashboard theo yêu cầu
    st.info("Dashboard đã cập nhật: KPI có thể chỉnh. Bản đồ tuyến không hiển thị ở trang này.")

    st.subheader("Đơn Hàng Gần Nhất")
    st.dataframe(st.session_state['orders'].reset_index(drop=True))

# -------------------------
# Quản Lý Đơn Hàng
# -------------------------
elif page == "Quản Lý Đơn Hàng":
    st.header("Quản Lý Đơn Hàng")

    st.subheader("Danh Sách Đơn Hàng (từ session)")
    st.dataframe(st.session_state['orders'].reset_index(drop=True))

    st.subheader("Tạo Đơn Hàng Mới")
    with st.form(key="order_form"):
        ma_don = st.text_input("Mã Đơn (để trống sẽ auto tạo)", value="")
        diem_lay = st.text_input("Điểm Lấy Hàng", value="")
        diem_giao = st.text_input("Điểm Giao Hàng", value="")
        loai_hang = st.selectbox("Loại Hàng Hóa", ["Thường", "Dễ Vỡ", "Nguy Hiểm"])
        thoi_gian = st.date_input("Thời Gian Dự Kiến", value=date.today())
        chi_phi = st.number_input("Chi Phí (VND)", min_value=0, value=0)
        # Tùy chọn toạ độ (nếu có)
        st.markdown("**(Tùy chọn)** Nhập toạ độ để hiển thị trên bản đồ (độ thập phân). Nếu để trống sẽ giữ None.")
        pickup_lat = st.text_input("Pickup Lat (ví dụ 21.02)", value="")
        pickup_lon = st.text_input("Pickup Lon (ví dụ 105.84)", value="")
        drop_lat = st.text_input("Dropoff Lat", value="")
        drop_lon = st.text_input("Dropoff Lon", value="")
        submit = st.form_submit_button("Tạo Đơn")
        if submit:
            # tự tạo mã đơn nếu để trống
            if ma_don.strip() == "":
                # tìm mã tiếp theo theo số
                existing = st.session_state['orders']["Mã Đơn"].astype(str).tolist()
                idx = 1
                while True:
                    candidate = f"DH{idx:03d}"
                    if candidate not in existing:
                        ma_don = candidate
                        break
                    idx += 1
            # chuẩn hoá dữ liệu toạ độ
            def none_if_blank(x):
                return float(x) if x not in (None, "", " ") else None
            pl = none_if_blank(pickup_lat)
            pol = none_if_blank(pickup_lon)
            dl = none_if_blank(drop_lat)
            dol = none_if_blank(drop_lon)
            new_row = {
                "Mã Đơn": ma_don,
                "Điểm Lấy": diem_lay,
                "Điểm Giao": diem_giao,
                "Trạng Thái": "Pending",
                "Thời Gian Dự Kiến": thoi_gian.isoformat(),
                "Chi Phí": int(chi_phi),
                "Pickup_Lat": pl,
                "Pickup_Lon": pol,
                "Dropoff_Lat": dl,
                "Dropoff_Lon": dol
            }
            # thêm vào session_state
            st.session_state['orders'] = pd.concat([st.session_state['orders'], pd.DataFrame([new_row])], ignore_index=True)
            st.success(f"Đã tạo đơn {ma_don} và lưu vào hệ thống.")
            # cập nhật local var
            orders_df = st.session_state['orders']

# -------------------------
# Lập Kế Hoạch Tuyến Đường
# -------------------------
elif page == "Lập Kế Hoạch Tuyến Đường":
    st.header("Lập Kế Hoạch Tuyến Đường")

    orders_df = st.session_state['orders']
    if orders_df.empty:
        st.warning("Không có đơn hàng nào trong hệ thống.")
    else:
        # chọn mã đơn để lập kế hoạch
        selected_code = st.selectbox("Chọn Mã Đơn để lập kế hoạch", orders_df["Mã Đơn"].tolist())
        order_row = orders_df[orders_df["Mã Đơn"] == selected_code].iloc[0]

        st.write("**Thông tin đơn**")
        st.write(f"- Mã Đơn: {order_row['Mã Đơn']}")
        st.write(f"- Điểm Lấy: {order_row['Điểm Lấy']}")
        st.write(f"- Điểm Giao: {order_row['Điểm Giao']}")
        st.write(f"- Thời Gian Dự Kiến: {order_row['Thời Gian Dự Kiến']}")
        st.write(f"- Chi Phí: {order_row['Chi Phí']:,} VND")
        st.write(f"- Trạng Thái: {order_row['Trạng Thái']}")

        # Cho phép sửa toạ độ nhanh (nếu muốn) trước khi tính tuyến
        st.markdown("**Cập nhật / nhập toạ độ (nếu cần)**")
        colA, colB = st.columns(2)
        with colA:
            p_lat = st.text_input("Pickup Lat", value=str(order_row.get("Pickup_Lat", "") or ""))
            p_lon = st.text_input("Pickup Lon", value=str(order_row.get("Pickup_Lon", "") or ""))
        with colB:
            d_lat = st.text_input("Dropoff Lat", value=str(order_row.get("Dropoff_Lat", "") or ""))
            d_lon = st.text_input("Dropoff Lon", value=str(order_row.get("Dropoff_Lon", "") or ""))

        if st.button("Cập nhật toạ độ cho đơn"):
            # cập nhật vào session
            def to_none(x):
                return float(x) if x not in (None, "", " ") else None
            idx = st.session_state['orders'].index[st.session_state['orders']["Mã Đơn"] == selected_code][0]
            st.session_state['orders'].at[idx, "Pickup_Lat"] = to_none(p_lat)
            st.session_state['orders'].at[idx, "Pickup_Lon"] = to_none(p_lon)
            st.session_state['orders'].at[idx, "Dropoff_Lat"] = to_none(d_lat)
            st.session_state['orders'].at[idx, "Dropoff_Lon"] = to_none(d_lon)
            st.success("Đã cập nhật toạ độ vào đơn hàng.")

        # Khi tính tuyến:
        if st.button("Tính Tuyến Đường (Ước lượng)"):
            pl = order_row.get("Pickup_Lat")
            pol = order_row.get("Pickup_Lon")
            dl = order_row.get("Dropoff_Lat")
            dol = order_row.get("Dropoff_Lon")

            # nếu user vừa cập nhật và chưa reload order_row, lấy từ session
            updated = st.session_state['orders'][st.session_state['orders']["Mã Đơn"] == selected_code].iloc[0]
            pl = updated.get("Pickup_Lat")
            pol = updated.get("Pickup_Lon")
            dl = updated.get("Dropoff_Lat")
            dol = updated.get("Dropoff_Lon")

            if None in (pl, pol, dl, dol):
                st.warning("Thiếu toạ độ: vui lòng nhập đầy đủ Pickup_Lat, Pickup_Lon, Dropoff_Lat, Dropoff_Lon để vẽ bản đồ và tính khoảng cách.")
            else:
                distance_km = haversine(pl, pol, dl, dol)
                # ước lượng thời gian & chi phí giả
                eta_hours = max(1, round(distance_km / 60, 1))  # giả định tốc độ 60 km/h
                estimated_cost = int(distance_km * 2000)  # giả định 2.000 VND / km
                st.success(f"Tuyến đường: ~{distance_km:.1f} km — Thời gian ~{eta_hours} giờ — Chi phí ước tính {estimated_cost:,} VND")
                # Bản đồ: 2 điểm
                map_df = pd.DataFrame([[pl, pol], [dl, dol]], columns=['lat', 'lon'])
                st.subheader("Bản Đồ Tuyến Đường")
                st.map(map_df)

# -------------------------
# Theo Dõi Hàng Hóa
# -------------------------
elif page == "Theo Dõi Hàng Hóa":
    st.header("Theo Dõi Hàng Hóa")

    if st.session_state['orders'].empty:
        st.warning("Không có đơn hàng để theo dõi.")
    else:
        selected_order = st.selectbox("Chọn Mã Đơn", st.session_state['orders']["Mã Đơn"].tolist())
        row = st.session_state['orders'][st.session_state['orders']["Mã Đơn"] == selected_order].iloc[0]
        st.subheader(f"Trạng Thái: {row['Trạng Thái']}")
        st.write("**Chi tiết đơn**")
        st.write(f"- Điểm Lấy: {row['Điểm Lấy']}")
        st.write(f"- Điểm Giao: {row['Điểm Giao']}")
        st.write(f"- Thời Gian Dự Kiến: {row['Thời Gian Dự Kiến']}")
        st.write(f"- Chi Phí: {row['Chi Phí']:,} VND")

        st.write("Timeline (ví dụ):")
        # Tạo timeline động dựa trên trạng thái
        if row['Trạng Thái'] == "Pending":
            st.write("- Created: " + str(row['Thời Gian Dự Kiến']))
        elif row['Trạng Thái'] == "In Transit":
            st.write("- Created: " + str(row['Thời Gian Dự Kiến']))
            st.write("- Picked Up: Đã lấy hàng")
            st.write("- In Transit: Đang di chuyển")
        else:
            st.write("- Created: " + str(row['Thời Gian Dự Kiến']))
            st.write("- Delivered: Đã giao")

        # Bản đồ vị trí hiện tại: nếu có toạ độ dropoff/pickup, hiển thị điểm dropoff
        map_points = []
        if pd.notna(row.get("Pickup_Lat")) and pd.notna(row.get("Pickup_Lon")):
            map_points.append([row["Pickup_Lat"], row["Pickup_Lon"]])
        if pd.notna(row.get("Dropoff_Lat")) and pd.notna(row.get("Dropoff_Lon")):
            map_points.append([row["Dropoff_Lat"], row["Dropoff_Lon"]])
        if map_points:
            st.subheader("Vị Trí (theo toạ độ nếu có)")
            map_df = pd.DataFrame(map_points, columns=['lat', 'lon'])
            st.map(map_df)
        else:
            st.info("Chưa có toạ độ để hiển thị trên bản đồ. Bạn có thể thêm toạ độ trong trang 'Lập Kế Hoạch Tuyến Đường'.")

# -------------------------
# Báo Cáo
# -------------------------
elif page == "Báo Cáo":
    st.header("Báo Cáo")

    orders_df = st.session_state['orders'].copy()
    st.subheader("Danh sách đơn (báo cáo nhanh)")
    st.dataframe(orders_df.reset_index(drop=True))

    st.subheader("Biểu đồ Chi Phí (mẫu)")
    if not orders_df.empty:
        chart_data = pd.DataFrame({
            "Chi Phí": orders_df["Chi Phí"].fillna(0).astype(float)
        })
        st.line_chart(chart_data)
    else:
        st.info("Không có dữ liệu biểu đồ.")

    # Xuất báo cáo CSV
    csv = orders_df.to_csv(index=False).encode('utf-8')
    st.download_button("Tải báo cáo (CSV)", data=csv, file_name="orders_report.csv", mime="text/csv")

