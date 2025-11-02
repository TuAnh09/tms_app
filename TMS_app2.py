import streamlit as st
import pandas as pd
import numpy as np
import folium
from streamlit_folium import st_folium
import streamlit.components.v1 as components

st.set_page_config(page_title="TMS Demo App", layout="wide")

# --- Khởi tạo dữ liệu nếu chưa có ---
if "orders" not in st.session_state:
    st.session_state["orders"] = pd.DataFrame({
        "Mã Đơn": ["DH001", "DH002", "DH003"],
        "Điểm Lấy": ["Hà Nội", "TP.HCM", "Đà Nẵng"],
        "Điểm Giao": ["TP.HCM", "Hà Nội", "Nha Trang"],
        "Pickup_Lat": [21.0285, 10.7769, 16.0471],
        "Pickup_Lon": [105.8542, 106.7009, 108.2068],
        "Dropoff_Lat": [10.7769, 21.0285, 12.2388],
        "Dropoff_Lon": [106.7009, 105.8542, 109.1967],
        "Trạng Thái": ["Pending", "In Transit", "Delivered"],
        "Thời Gian Dự Kiến": ["2025-11-01", "2025-11-02", "2025-11-03"],
        "Chi Phí": [500000, 700000, 400000]
    })

orders_data = st.session_state["orders"]

# --- Sidebar ---
st.sidebar.title("Menu")
page = st.sidebar.radio("Chọn trang", ["Dashboard", "Quản Lý Đơn Hàng", "Lập Kế Hoạch Tuyến Đường", "Theo Dõi Hàng Hóa", "Báo Cáo"])

# --- Dashboard ---
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

# --- Quản Lý Đơn Hàng ---
elif page == "Quản Lý Đơn Hàng":
    st.header("Quản Lý Đơn Hàng")

    st.subheader("Danh Sách Đơn Hàng")
    st.dataframe(orders_data)

    st.subheader("Tạo Đơn Hàng Mới")
    with st.form(key="order_form"):
        ma_don = st.text_input("Mã Đơn")
        diem_lay = st.text_input("Điểm Lấy Hàng")
        diem_giao = st.text_input("Điểm Giao Hàng")
        pickup_lat = st.text_input("Pickup_Lat (Vĩ độ)")
        pickup_lon = st.text_input("Pickup_Lon (Kinh độ)")
        drop_lat = st.text_input("Dropoff_Lat (Vĩ độ)")
        drop_lon = st.text_input("Dropoff_Lon (Kinh độ)")
        loai_hang = st.selectbox("Loại Hàng Hóa", ["Thường", "Dễ Vỡ", "Nguy Hiểm"])
        thoi_gian = st.date_input("Thời Gian Dự Kiến")
        chi_phi = st.number_input("Chi Phí (VND)", value=0)
        submit = st.form_submit_button("Tạo Đơn")

        if submit:
            try:
                new_order = pd.DataFrame([{
                    "Mã Đơn": ma_don,
                    "Điểm Lấy": diem_lay,
                    "Điểm Giao": diem_giao,
                    "Pickup_Lat": float(pickup_lat),
                    "Pickup_Lon": float(pickup_lon),
                    "Dropoff_Lat": float(drop_lat),
                    "Dropoff_Lon": float(drop_lon),
                    "Trạng Thái": "Pending",
                    "Thời Gian Dự Kiến": thoi_gian.strftime("%Y-%m-%d"),
                    "Chi Phí": chi_phi
                }])
                st.session_state["orders"] = pd.concat([orders_data, new_order], ignore_index=True)
                st.success("✅ Đơn hàng đã được tạo thành công!")
            except ValueError:
                st.error("❌ Vui lòng nhập đúng định dạng số cho tọa độ (Lat, Lon)!")

# --- Lập Kế Hoạch Tuyến Đường ---
elif page == "Lập Kế Hoạch Tuyến Đường":
    st.header("Lập Kế Hoạch Tuyến Đường")

    selected_order = st.selectbox("Chọn Mã Đơn", orders_data["Mã Đơn"])
    order_info = orders_data[orders_data["Mã Đơn"] == selected_order].iloc[0]

    diem_lay = order_info["Điểm Lấy"]
    diem_giao = order_info["Điểm Giao"]

    # Ép kiểu float và kiểm tra NaN
    try:
        pickup_lat = float(order_info["Pickup_Lat"])
        pickup_lon = float(order_info["Pickup_Lon"])
        drop_lat = float(order_info["Dropoff_Lat"])
        drop_lon = float(order_info["Dropoff_Lon"])
    except Exception as e:
        st.error("Không thể đọc tọa độ từ dữ liệu đơn hàng. Vui lòng kiểm tra giá trị Pickup/Dropoff Lat/Lon.")
        st.stop()

    st.write(f"📦 **Điểm Lấy:** {diem_lay} ({pickup_lat}, {pickup_lon})")
    st.write(f"🚚 **Điểm Giao:** {diem_giao} ({drop_lat}, {drop_lon})")

    if st.button("Hiển Thị Tuyến Đường"):
        # Tọa độ trung tâm map (giữa 2 điểm)
        center_lat = (pickup_lat + drop_lat) / 2
        center_lon = (pickup_lon + drop_lon) / 2

        # Tạo map folium
        m = folium.Map(location=[center_lat, center_lon], zoom_start=6)

        # Marker cho hai điểm (chỉ hiển thị, không nối)
        folium.Marker(
            [pickup_lat, pickup_lon],
            tooltip=f"Điểm Lấy Hàng: {diem_lay}",
            popup=f"Tọa độ: ({pickup_lat}, {pickup_lon})",
            icon=folium.Icon(color="green")
        ).add_to(m)

        folium.Marker(
            [drop_lat, drop_lon],
            tooltip=f"Điểm Giao Hàng: {diem_giao}",
            popup=f"Tọa độ: ({drop_lat}, {drop_lon})",
            icon=folium.Icon(color="red")
        ).add_to(m)

        # --- Thử render bằng st_folium; nếu không hiện, fallback sang components.html ---
        rendered = None
        try:
            # Một số phiên bản st_folium yêu cầu args khác; nhưng thử call cơ bản trước
            rendered = st_folium(m, width=800, height=500)
        except Exception as e:
            st.warning("st_folium gặp lỗi khi render; thử fallback bằng components.html.")
            try:
                html = m.get_root().render()
                components.html(html, height=500, scrolling=True)
            except Exception as e2:
                st.error("Không thể render bản đồ bằng cả st_folium và components.html. Kiểm tra lại cài đặt thư viện (folium, streamlit_folium).")
                st.exception(e2)

# --- Theo Dõi Hàng Hóa ---
elif page == "Theo Dõi Hàng Hóa":
    st.header("Theo Dõi Hàng Hóa")

    selected_order = st.selectbox("Chọn Mã Đơn", orders_data["Mã Đơn"])
    status = orders_data[orders_data["Mã Đơn"] == selected_order]["Trạng Thái"].values[0]
    st.subheader(f"Trạng Thái: {status}")

    st.write("Timeline:")
    st.write("- Created: 2025-10-30")
    st.write("- Picked Up: 2025-10-31")
    st.write("- In Transit: Đang di chuyển")

    order_info = orders_data[orders_data["Mã Đơn"] == selected_order].iloc[0]
    map_data = pd.DataFrame([[order_info["Pickup_Lat"], order_info["Pickup_Lon"]]], columns=["lat", "lon"])
    st.map(map_data)

# --- Báo Cáo ---
elif page == "Báo Cáo":
    st.header("Báo Cáo")

    date_range = st.date_input("Chọn Khoảng Thời Gian", [])
    st.subheader("Biểu Đồ Chi Phí")
    chart_data = orders_data["Chi Phí"]
    st.line_chart(chart_data)

    st.download_button("Tải PDF", data="Nội dung báo cáo giả", file_name="report.pdf")
