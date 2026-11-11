# Print Learn — Home Assistant Add-on Repository

Kho add-on chứa **Print Learn Server**: server SQLite nhỏ (cổng 8765) làm kho mã
lỗi tự học cho Zalo Print Bot trên Home Assistant.

## Cài đặt

1. Home Assistant → Settings → Add-ons → Add-on Store → menu ⋮ → **Repositories**.
2. Dán URL của repo này → **Add** → đóng hộp thoại.
3. Tìm **Print Learn Server** trong cửa hàng → Install → Start.
4. Kiểm tra Log có dòng `print-learn-server listening on :8765` và mở
   `http://<IP-may-HA>:8765/health` thấy `{"ok": true}`.

Automation Print Bot gọi server này qua `rest_command` — xem tài liệu kèm theo
trong thư mục `print_learn/DOCS.md`.
