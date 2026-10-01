# WebGIS LST TP. Hồ Chí Minh

Dashboard Streamlit phân tích nhiệt độ bề mặt đất (LST) cho Thành phố Hồ Chí Minh.

## Chạy ứng dụng

```bash
pip install -r requirements.txt
streamlit run app.py
```

## Dữ liệu CSV

Tạo file `data/lst_samples.csv` với các cột:

```csv
lat,lon,lst_c
10.776,106.700,31.4
10.810,106.709,34.2
10.735,106.722,36.1
```

Nếu file CSV chưa tồn tại, ứng dụng tự tạo dữ liệu mẫu deterministic để chạy thử. Dữ liệu mẫu không phải sản phẩm vệ tinh chính thức. Ranh giới TP.HCM trong bản demo là đường bao minh họa; khi nghiên cứu nên thay bằng GeoJSON hành chính chính thức.

## Deploy Streamlit Community Cloud

Chọn repository này, branch `main` và file `app.py`; hệ thống sẽ cài thư viện từ `requirements.txt`.

## Hướng phát triển

- Đọc GeoTIFF bằng `rasterio`.
- Thay đường bao minh họa bằng GeoJSON hành chính chính thức.
- Kết nối Landsat/MODIS hoặc Google Earth Engine.
- Bổ sung phân tích theo quận, mùa và thời gian.
