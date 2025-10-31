import streamlit as st
import pandas as pd
import numpy as np

# Tiêu đề ứng dụng
st.title("Hệ Thống Quản Lý Vận Tải (TMS) Đơn Giản")

# Sidebar cho menu điều hướng
st.sidebar.title("Menu")
page = st.sidebar.radio("Chọn trang", ["Dashboard", "Quản Lý Đơn Hàng", "Lập Kế Hoạch Tuyến Đường", "Theo Dõi Hàng Hóa", "Báo Cáo"])

# Dữ liệu giả để demo (bạn có thể thay bằng database thực)
orders_data = pd.DataFrame({
    "Mã Đơn": ["DH001", "DH002", "DH003"],
    "Điểm Lấy": ["Hà Nội", "TP.HCM", "Đà Nẵng"],
    "Điểm Giao": ["TP.HCM", "Hà Nội", "Nha Trang"],
    "Trạng Thái": ["Pending", "In Transit", "Delivered"],
    "Thời Gian Dự Kiến": ["2025-11-01", "2025-11-02", "2025-11-03"],
    "Chi Phí": [500000, 700000, 400000]
})

# Trang Dashboard
if page == "Dashboard":
    st.header("Tổng Quan")
    
    # Cards KPI
    col1, col2, col3, col4 = st.columns(4)
    with col1:
        st.metric("Số Đơn Hàng Hôm Nay", "25", "5%")
    with col2:
        st.metric("Tỷ Lệ Đúng Hạn", "95%", "2%")
    with col3:
        st.metric("Chi Phí Trung Bình", "500k VND", "-10%")
    with col4:
        st.metric("Phương Tiện Sẵn Sàng", "10", "2")
    
    # Bản đồ đơn giản (sử dụng dữ liệu giả)
    st.subheader("Bản Đồ Tuyến Đường")
    map_data = pd.DataFrame(
        np.random.randn(3, 2) / [50, 50] + [21.02, 105.84],  # Vị trí Hà Nội làm ví dụ
        columns=['lat', 'lon'])
    st.map(map_data)
    
    # Danh sách đơn hàng gần nhất
    st.subheader("Đơn Hàng Gần Nhất")
    st.dataframe(orders_data)

# Trang Quản Lý Đơn Hàng
elif page == "Quản Lý Đơn Hàng":
    st.header("Quản Lý Đơn Hàng")
    
    # Danh sách đơn hàng
    st.subheader("Danh Sách Đơn Hàng")
    st.dataframe(orders_data)
    
    # Form tạo đơn hàng mới
    st.subheader("Tạo Đơn Hàng Mới")
    with st.form(key="order_form"):
        ma_don = st.text_input("Mã Đơn")
        diem_lay = st.text_input("Điểm Lấy Hàng")
        diem_giao = st.text_input("Điểm Giao Hàng")
        loai_hang = st.selectbox("Loại Hàng Hóa", ["Thường", "Dễ Vỡ", "Nguy Hiểm"])
        thoi_gian = st.date_input("Thời Gian Dự Kiến")
        submit = st.form_submit_button("Tạo Đơn")
        if submit:
            st.success("Đơn hàng đã được tạo!")

# Trang Lập Kế Hoạch Tuyến Đường
elif page == "Lập Kế Hoạch Tuyến Đường":
    st.header("Lập Kế Hoạch Tuyến Đường")
    
    # Form nhập tuyến đường
    diem_lay = st.text_input("Điểm Lấy Hàng")
    diem_giao = st.text_input("Điểm Giao Hàng")
    if st.button("Tính Tuyến Đường"):
        st.info("Tuyến đường tối ưu: Khoảng cách 500km, Thời gian 8 giờ, Chi phí 1.000.000 VND")  # Giả lập
    
    # Bản đồ
    st.subheader("Bản Đồ")
    map_data = pd.DataFrame(
        np.random.randn(2, 2) / [50, 50] + [10.77, 106.70],  # Vị trí TP.HCM làm ví dụ
        columns=['lat', 'lon'])
    st.map(map_data)

# Trang Theo Dõi Hàng Hóa
elif page == "Theo Dõi Hàng Hóa":
    st.header("Theo Dõi Hàng Hóa")
    
    # Chọn đơn hàng để theo dõi
    selected_order = st.selectbox("Chọn Mã Đơn", orders_data["Mã Đơn"])
    st.subheader(f"Trạng Thái: {orders_data[orders_data['Mã Đơn'] == selected_order]['Trạng Thái'].values[0]}")
    
    # Timeline giả
    st.write("Timeline:")
    st.write("- Created: 2025-10-30")
    st.write("- Picked Up: 2025-10-31")
    st.write("- In Transit: Đang di chuyển")
    
    # Bản đồ theo dõi
    st.subheader("Vị Trí Hiện Tại")
    map_data = pd.DataFrame([[21.02, 105.84]], columns=['lat', 'lon'])
    st.map(map_data)

# Trang Báo Cáo
elif page == "Báo Cáo":
    st.header("Báo Cáo")
    
    # Filter
    date_range = st.date_input("Chọn Khoảng Thời Gian", [])
    
    # Biểu đồ đơn giản
    st.subheader("Biểu Đồ Chi Phí")
    chart_data = pd.DataFrame(
        np.random.randn(10, 1),
        columns=['Chi Phí'])
    st.line_chart(chart_data)
    
    # Export
    if st.button("Xuất Báo Cáo"):
        st.download_button("Tải PDF", data="Nội dung báo cáo giả", file_name="report.pdf")
