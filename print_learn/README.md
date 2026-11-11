# Print Learn Server

Kho mã lỗi tự học cho Zalo Print Bot.

- SQLite tại `/data/print_learn.db` của add-on, API cổng **8765**:
  `POST /learn`, `GET /lookup?code=`, `GET /list`, `DELETE /learn?code=`, `GET /health`.
- Mã học mới được bot tra **trước** kho 194 mã gốc trong automation.
- Đặt `token` trong Configuration của add-on để khóa ghi (để trống = ai trong LAN cũng ghi được).
