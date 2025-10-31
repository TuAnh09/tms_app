import streamlit as st
import pandas as pd
import numpy as np
import pydeck as pdk

# Khởi tạo dữ liệu nếu chưa có
if "orders" not in st.session_state:
    st.session_state["orders"] = pd.DataFrame({
        "Mã Đơn": ["DH001", "DH002", "DH003"],
        "Điểm Lấy": ["Hà Nội", "TP.HCM", "Đà Nẵng"],
        "Điểm Giao": ["TP.HCM", "Hà Nội", "Nha Trang"],
        "Trạng Thái": ["Pending", "In Transit", "Delivered"],
        "Thời Gian Dự Kiến": ["2025-11-01", "2025-11-02", "2025-11-03"],
        "Chi Phí": [500000, 700000, 400000],
        "pickup_Lon": [105.84, 106.70, 108.22],
        "pickup_Lat": [21.02, 10.77, 16.07],
        "dropoff_Lon": [106.70, 105.84, 109.19],
        "dropoff_Lat": [10.77, 21.02, 12.25]
    })

orders_data = st.session_state["orders"]

# Sidebar
st.sidebar.title("Menu")
page = st.sidebar.radio("Chọn trang", ["Dashboard", "Quản Lý Đơn Hàng", "Lập Kế Hoạch Tuyến Đường", "Theo Dõi Hàng Hóa", "Báo Cáo"])

# Dashboard
if page == "Dashboard":
    st.header("Tổng Quan")

    col1, col2, col3, col4 = st.columns(4)
    with col1:
        don_hang = st.number_input("Số Đơn Hàng Hôm Nay", value=25)
    with col2:
        ty_le = st.slider("Tỷ Lệ Đúng Hạn (%)", 0, 100, value=95)
    with col3:
        chi_phi_tb = st.number_input("Chi Phí Trung Bình (VND)", value=500000)
    with col4:
        phuong_tien = st.number_input("Phương Tiện Sẵn Sàng", value=10)

    st.subheader("Đơn Hàng Gần Nhất")
    st.dataframe(orders_data)

# Quản Lý Đơn Hàng
elif page == "Quản Lý Đơn Hàng":
    st.header("Quản Lý Đơn Hàng")

    st.subheader("Danh Sách Đơn Hàng")
    st.dataframe(orders_data)

    st.subheader("Tạo Đơn Hàng Mới")
    with st.form(key="order_form"):
        ma_don = st.text_input("Mã Đơn")
        diem_lay = st.text_input("Điểm Lấy Hàng")
        diem_giao = st.text_input("Điểm Giao Hàng")
        loai_hang = st.selectbox("Loại Hàng Hóa", ["Thường", "Dễ Vỡ", "Nguy Hiểm"])
        thoi_gian = st.date_input("Thời Gian Dự Kiến")
        chi_phi = st.number_input("Chi Phí (VND)", value=0)
        pickup_Lon = st.number_input("Kinh độ Điểm Lấy", value=0.0)
        pickup_Lat = st.number_input("Vĩ độ Điểm Lấy", value=0.0)
        dropoff_Lon = st.number_input("Kinh độ Điểm Giao", value=0.0)
        dropoff_Lat = st.number_input("Vĩ độ Điểm Giao", value=0.0)
        trang_thai = st.selectbox("Trạng Thái", ["Pending", "In Transit", "Delivered"])
        submit = st.form_submit_button("Tạo Đơn")

        if submit:
            new_order = pd.DataFrame([{
                "Mã Đơn": ma_don,
                "Điểm Lấy": diem_lay,
                "Điểm Giao": diem_giao,
                "Trạng Thái": trang_thai,
                "Thời Gian Dự Kiến": thoi_gian.strftime("%Y-%m-%d"),
                "Chi Phí": chi_phi,
                "pickup_Lon": pickup_Lon,
                "pickup_Lat": pickup_Lat,
                "dropoff_Lon": dropoff_Lon,
                "dropoff_Lat": dropoff_Lat
            }])
            st.session_state["orders"] = pd.concat([orders_data, new_order], ignore_index=True)
            st.success("Đơn hàng đã được tạo!")

# Lập Kế Hoạch Tuyến Đường
elif page == "Lập Kế Hoạch Tuyến Đường":
    st.header("Lập Kế Hoạch Tuyến Đường")

    selected_order = st.selectbox("Chọn Mã Đơn", orders_data["Mã Đơn"])
    order_info = orders_data[orders_data["Mã Đơn"] == selected_order].iloc[0]

    diem_lay = order_info["Điểm Lấy"]
    diem_giao = order_info["Điểm Giao"]
    pickup_lat = order_info["pickup_Lat"]
    pickup_lon = order_info["pickup_Lon"]
    dropoff_lat = order_info["dropoff_Lat"]
    dropoff_lon = order_info["dropoff_Lon"]

    st.write(f"Điểm Lấy: {diem_lay} ({pickup_lat}, {pickup_lon})")
    st.write(f"Điểm Giao: {diem_giao} ({dropoff_lat}, {dropoff_lon})")

    if st.button("Tính Tuyến Đường"):
        st.info(f"Tuyến đường từ {diem_lay} đến {diem_giao}: Khoảng cách 500km, Thời gian 8 giờ, Chi phí 1.000.000 VND")

    st.subheader("Bản Đồ Tuyến Đường")
    route_data = pd.DataFrame([
        {"lat": pickup_lat, "lon": pickup_lon},
        {"lat": dropoff_lat, "lon": dropoff_lon}
    ])

    st.pydeck_chart(pdk.Deck(
        initial_view_state=pdk.ViewState(
            latitude=(pickup_lat + dropoff_lat) / 2,
            longitude=(pickup_lon + dropoff_lon) / 2,
            zoom=5,
            pitch=0,
        ),
        layers=[
            pdk.Layer(
                "ScatterplotLayer",
                data=route_data,
                get_position='[lon, lat]',
                get_color='[200, 30, 0, 160]',
                get_radius=50000,
            ),
            pdk.Layer(
                "LineLayer",
                data=route_data,
                get_source_position='[lon, lat]',
                get_target_position='[lon, lat]',
                get_color='[0, 0, 255]',
                auto_highlight=True,
                width_scale=2,
                width_min_pixels=2,
            )
        ]
    ))

# Theo Dõi Hàng Hóa
elif page == "Theo Dõi Hàng Hóa":
    st.header("Theo Dõi Hàng Hóa")

    selected_order = st.selectbox("Chọn Mã Đơn", orders_data["Mã Đơn"])
    status = orders_data[orders_data["Mã Đơn"] == selected_order]["Trạng Thái"].values[0]
    st.subheader(f"Trạng Thái: {status}")

    st.write("Timeline:")
    st.write("- Created: 2025-10-30")
    st.write("- Picked Up: 2025-10-31")
    st.write("- In Transit: Đang di chuyển")

    st.subheader("Vị Trí Hiện Tại")
    current_location = orders_data[orders_data["Mã Đơn"] == selected_order][["pickup_Lat", "pickup_Lon"]]
    st.map(current_location.rename(columns={"pickup_Lat": "lat", "pickup_Lon": "lon"}))

# Báo Cáo
elif page == "Báo Cáo":
    st.header("Báo Cáo")

    date_range = st.date_input("Chọn Khoảng Thời Gian", [])
    st.subheader("Biểu Đồ Chi Phí")
    chart_data = orders_data["Chi Phí"]
    st.line_chart(chart_data)

    if st.button("Xuất Báo Cáo"):
        st.download_button("Tải PDF", data="Nội dung báo cáo giả", file_name="report.pdf")
