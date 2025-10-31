# --- Quản Lý Đơn Hàng ---
elif page == "Quản Lý Đơn Hàng":
    st.header("🚚 Quản Lý Đơn Hàng")

    # --- Hiển thị danh sách đơn hàng ---
    st.subheader("📋 Danh Sách Đơn Hàng")
    st.dataframe(orders_data)

    # --- Cập nhật trạng thái ---
    st.subheader("🔄 Cập Nhật Trạng Thái Đơn Hàng")
    if len(orders_data) > 0:
        selected_update = st.selectbox("Chọn Mã Đơn để Cập Nhật", orders_data["Mã Đơn"])
        current_status = orders_data.loc[orders_data["Mã Đơn"] == selected_update, "Trạng Thái"].values[0]
        st.write(f"🟢 Trạng thái hiện tại: **{current_status}**")

        new_status = st.selectbox(
            "Chọn trạng thái mới",
            ["Pending", "In Transit", "Delivered"],
            index=["Pending", "In Transit", "Delivered"].index(current_status)
        )

        if st.button("Cập Nhật Trạng Thái"):
            st.session_state["orders"].loc[
                st.session_state["orders"]["Mã Đơn"] == selected_update, "Trạng Thái"
            ] = new_status
            st.success(f"✅ Đã cập nhật trạng thái đơn hàng {selected_update} thành '{new_status}'")
    else:
        st.info("Không có đơn hàng nào để cập nhật.")

    st.markdown("---")

    # --- Xóa Đơn Hàng ---
    st.subheader("🗑️ Xóa Đơn Hàng")
    if len(orders_data) > 0:
        selected_delete = st.selectbox("Chọn Mã Đơn để Xóa", orders_data["Mã Đơn"], key="delete_order")
        if st.button("Xóa Đơn Hàng"):
            st.session_state["orders"] = orders_data[orders_data["Mã Đơn"] != selected_delete].reset_index(drop=True)
            st.success(f"✅ Đã xóa đơn hàng {selected_delete} thành công!")
    else:
        st.info("Không có đơn hàng nào để xóa.")

    st.markdown("---")

    # --- Tạo Đơn Hàng Mới ---
    st.subheader("➕ Tạo Đơn Hàng Mới")
    with st.form(key="order_form"):
        ma_don = st.text_input("Mã Đơn")
        diem_lay = st.text_input("Điểm Lấy Hàng")
        diem_giao = st.text_input("Điểm Giao Hàng")
        pickup_lat = st.text_input("Pickup_Lat (Vĩ độ)")
        pickup_lon = st.text_input("Pickup_Lon (Kinh độ)")
        drop_lat = st.text_input("Dropoff_Lat (Vĩ độ)")
        drop_lon = st.text_input("Dropoff_Lon (Kinh độ)")
        thoi_gian = st.date_input("Thời Gian Dự Kiến")

        submit = st.form_submit_button("Tạo Đơn Hàng Mới")

        if submit:
            try:
                distance_km, cost = tinh_khoang_cach_chi_phi(pickup_lat, pickup_lon, drop_lat, drop_lon)
                if distance_km is None:
                    st.error("❌ Tọa độ không hợp lệ.")
                else:
                    new_order = pd.DataFrame([{
                        "Mã Đơn": ma_don,
                        "Điểm Lấy": diem_lay,
                        "Điểm Giao": diem_giao,
                        "Pickup_Lat": float(pickup_lat),
                        "Pickup_Lon": float(pickup_lon),
                        "Dropoff_Lat": float(drop_lat),
                        "Dropoff_Lon": float(drop_lon),
                        "Khoảng Cách (km)": distance_km,
                        "Chi Phí (VND)": cost,
                        "Trạng Thái": "Pending",
                        "Thời Gian Dự Kiến": thoi_gian.strftime("%Y-%m-%d")
                    }])
                    st.session_state["orders"] = pd.concat(
                        [st.session_state["orders"], new_order], ignore_index=True
                    )
                    st.success(f"✅ Đã tạo đơn hàng mới thành công ({distance_km} km – {cost:,.0f} VND)")
            except ValueError:
                st.error("❌ Vui lòng nhập đúng định dạng tọa độ (số thập phân).")
