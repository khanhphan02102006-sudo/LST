# WebGIS LST TP. Hồ Chí Minh

Dashboard Streamlit phân tích nhiệt độ bề mặt đất (LST) cho Thành phố Hồ Chí Minh.

## Tính năng

- Bản đồ WebGIS nền tối và lớp ảnh vệ tinh Esri không cần token.
- Lớp điểm màu LST, tooltip, chú giải nhiệt độ và điều khiển layer.
- Bộ lọc khu vực, tháng và năm.
- Chỉ số LST trung bình, cao nhất, thấp nhất, tỷ lệ điểm nóng >=35°C và số điểm dữ liệu.
- Biểu đồ phân bố nhiệt độ và xu hướng LST theo tháng.
- Có thể thay dữ liệu demo bằng CSV LST của người dùng.

## Chạy ứng dụng

```bash
python -m venv .venv
# Windows
.venv\\Scripts\\activate
# macOS/Linux
source .venv/bin/activate

pip install -r requirements.txt
streamlit run app.py
```

## Định dạng dữ liệu CSV

Tạo file `data/lst_samples.csv` với tối thiểu các cột:

```csv
lat,lon,lst_c
10.776,106.700,31.4
10.810,106.709,34.2
10.735,106.722,36.1
```

Có thể thêm các cột để bộ lọc hoạt động theo thời gian và khu vực:

```csv
lat,lon,lst_c,month,year,area
10.776,106.700,31.4,9,2026,Quận 1
10.810,106.709,34.2,9,2026,Bình Thạnh
```

Nếu CSV chưa tồn tại hoặc không hợp lệ, ứng dụng tự tạo dữ liệu mẫu deterministic. Dữ liệu mẫu không phải sản phẩm vệ tinh chính thức.

## Lấy dữ liệu LST thật

Có thể dùng Google Earth Engine để xuất LST từ Landsat hoặc MODIS, sau đó chuyển thành CSV/GeoTIFF. Quy trình tối thiểu:

1. Chọn khu vực TP.HCM.
2. Chọn bộ dữ liệu Landsat 8/9 hoặc MODIS.
3. Lọc theo tháng/năm và loại mây.
4. Tính LST theo công thức của bộ dữ liệu hoặc dùng sản phẩm LST đã có.
5. Xuất bảng điểm gồm `lat`, `lon`, `lst_c` và đặt vào `data/lst_samples.csv`.

Không nên dùng dữ liệu demo để kết luận nhiệt độ thực tế hoặc làm số liệu chính thức.

## Deploy Streamlit Community Cloud

Chọn repository `khanhphan02102006-sudo/LST`, branch `main`, file chính `app.py`. Hệ thống sẽ cài các thư viện trong `requirements.txt`.

## Hướng phát triển

- Đọc trực tiếp GeoTIFF bằng `rasterio`.
- Thay đường bao minh họa bằng GeoJSON hành chính chính thức.
- Tích hợp Google Earth Engine để tự động cập nhật ảnh vệ tinh.
- Bổ sung phân tích theo quận, mùa, đảo nhiệt đô thị và chuỗi thời gian.
