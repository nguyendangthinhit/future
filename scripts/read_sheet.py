"""
Đọc dữ liệu từ Google Sheet công khai (public) — KHÔNG cần credentials.

Cách hoạt động: Google Sheets cho phép export bất kỳ sheet công khai nào ra CSV
qua endpoint export?format=csv. Script tải CSV đó (kèm cache-buster để luôn lấy
bản mới nhất) rồi in ra dạng bảng.

Chạy:  python scripts/read_sheet.py
"""

import csv
import io
import sys
import time
import urllib.request

# Ép stdout sang UTF-8 để in được tiếng Việt trên Windows console
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding="utf-8")

# ID của Google Sheet (lấy từ URL: .../spreadsheets/d/<ID>/edit)
SHEET_ID = "1Gtb4iKtGZqupxGSLdXbSC9M2GSMqj67v9AMd2Byk2wM"

# gid của tab muốn đọc (lấy từ URL khi bấm vào tab: .../edit#gid=<số>).
# Tab đầu tiên luôn là gid=0.
SHEET_GID = "0"


def build_csv_url(sheet_id: str, gid: str) -> str:
    # Dùng endpoint export thay vì gviz: trả dữ liệu mới hơn, ít bị cache.
    # Thêm cache-buster (cb=timestamp) để Google không trả bản cache cũ.
    cb = int(time.time())
    return (
        f"https://docs.google.com/spreadsheets/d/{sheet_id}"
        f"/export?format=csv&gid={gid}&cb={cb}"
    )


def fetch_rows(url: str) -> list[list[str]]:
    # no-cache header: ép lấy bản mới nhất, tránh đọc nhầm dữ liệu cũ
    req = urllib.request.Request(
        url, headers={"Cache-Control": "no-cache", "Pragma": "no-cache"}
    )
    with urllib.request.urlopen(req, timeout=30) as resp:
        raw = resp.read().decode("utf-8", errors="replace")
    return list(csv.reader(io.StringIO(raw)))


def print_table(rows: list[list[str]]) -> None:
    if not rows:
        print("(Sheet rỗng — không có dữ liệu)")
        return

    header, *data = rows
    # Cột header rỗng -> đặt tên tạm "(cột N)" cho dễ nhìn
    header = [h.strip() if h.strip() else f"(cột {i+1})"
              for i, h in enumerate(header)]
    ncols = len(header)

    # Tính độ rộng mỗi cột để canh lề đẹp
    widths = [len(str(h)) for h in header]
    for row in data:
        for i in range(ncols):
            cell = row[i] if i < len(row) else ""
            widths[i] = max(widths[i], len(str(cell)))

    def fmt(row: list[str]) -> str:
        cells = []
        for i in range(ncols):
            cell = str(row[i]) if i < len(row) else ""
            cells.append(cell.ljust(widths[i]))
        return " | ".join(cells)

    sep = "-+-".join("-" * w for w in widths)
    print(fmt(header))
    print(sep)
    for row in data:
        print(fmt(row))


def main() -> int:
    url = build_csv_url(SHEET_ID, SHEET_GID)
    print(f"Đang kết nối tới Google Sheet...\nURL: {url}\n")

    try:
        rows = fetch_rows(url)
    except Exception as e:
        print(f"LỖI khi tải sheet: {e}")
        print("Kiểm tra: sheet đã để 'Anyone with the link' chưa? Mạng có chặn không?")
        return 1

    n_data = max(0, len(rows) - 1)
    print(f"Kết nối THÀNH CÔNG. Đọc được {len(rows)} dòng "
          f"(1 dòng header + {n_data} dòng dữ liệu).\n")
    print_table(rows)

    if n_data == 0:
        print("\n>> Sheet hiện CHƯA có dòng dữ liệu nào (chỉ có header).")
        print(">> Hãy nhập vài dòng vào sheet rồi chạy lại script để thấy data.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
