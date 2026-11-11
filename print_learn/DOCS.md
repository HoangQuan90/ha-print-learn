# Print Learn Server (HAOS add-on)

Kho mã lỗi tự học cho Zalo Print Bot. Dữ liệu SQLite nằm ở `/data/print_learn.db`
của add-on — bền qua restart, có mặt trong backup của add-on.

## API (cổng 8765)

- `POST /learn` — `{"code": "E999", "text": "...", "group_id": "..."}` thêm hoặc ghi đè 1 mã.
- `GET /lookup?code=E999` — tra 1 mã.
- `GET /list` — xem toàn bộ mã đã học (mở bằng trình duyệt).
- `DELETE /learn?code=E999` — xóa 1 mã đã học.
- `GET /health` — kiểm tra server sống.

## Tùy chọn

- `token` — để trống thì ai trong LAN cũng ghi được. Nếu đặt token, phải khai báo
  cùng token đó trong header `X-Token` của 3 lệnh `rest_command` bên Home Assistant.

## Cách Home Assistant gọi

Automation Print v3 gọi add-on này qua `rest_command` tới địa chỉ
`http://<IP-LAN-cua-may-HA>:8765` — add-on đã mở cổng 8765 ra máy chủ HAOS,
và Home Assistant Core trên HAOS chạy host network nên gọi địa chỉ này là tới nơi.
