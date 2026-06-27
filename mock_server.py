import csv
import os
import json
from http.server import HTTPServer, BaseHTTPRequestHandler
from urllib.parse import parse_qs

PORT = 5000
CSV_FILE = "mock_leads.csv"

# Google Sheet Headers
HEADERS = [
    "접수일시", "이름", "연락처", "개발자정보", "문의유형", "관심평형",
    "방문희망일시", "개인정보동의", "유입페이지", "사용자기기", "비고",
    "요청ID", "유입소스"
]

def init_csv():
    if not os.path.exists(CSV_FILE):
        with open(CSV_FILE, "w", newline="", encoding="utf-8-sig") as f:
            writer = csv.writer(f)
            writer.writerow(HEADERS)

class MockAppsScriptHandler(BaseHTTPRequestHandler):
    def log_message(self, format, *args):
        # Suppress default server logs for cleaner console output
        pass

    def do_OPTIONS(self):
        self.send_response(200)
        self.send_cors_headers()
        self.end_headers()

    def do_POST(self):
        if self.path.startswith("/macros/s/mock/exec"):
            content_length = int(self.headers.get('Content-Length', 0))
            body = self.rfile.read(content_length).decode('utf-8')
            params = parse_qs(body)
            
            # Extract parameters (matching google_apps_script.gs parameter extraction)
            name = params.get('name', [''])[0].strip()
            phone = params.get('phone', [''])[0].replace('-', '').strip()
            developer = params.get('developer', ['이신우'])[0].strip()
            inquiry_type = params.get('inquiryType', [''])[0].strip()
            unit_type = params.get('unitType', [''])[0].strip()
            visit_date_time = params.get('visitDateTime', [''])[0].strip()
            consent = params.get('consent', [''])[0].strip()
            page_url = params.get('pageUrl', [''])[0].strip()
            device = params.get('device', [''])[0].strip()
            created_at = params.get('createdAt', [''])[0].strip()
            request_id = params.get('requestId', [''])[0].strip()
            lead_source = params.get('leadSource', [''])[0].strip()
            note = params.get('note', [''])[0].strip()
            
            if not name or not phone:
                self.send_response(400)
                self.send_cors_headers()
                self.send_header('Content-Type', 'application/json; charset=utf-8')
                self.end_headers()
                self.wfile.write(json.dumps({"ok": False, "message": "Missing required fields"}).encode('utf-8'))
                print("[-] Error: Missing required name or phone field.")
                return

            # Append to local CSV file
            row = [
                created_at, name, phone, developer, inquiry_type, unit_type,
                visit_date_time, consent, page_url, device, note, request_id, lead_source
            ]
            
            with open(CSV_FILE, "a", newline="", encoding="utf-8-sig") as f:
                writer = csv.writer(f)
                writer.writerow(row)
                
            print(f"[+] Lead Saved! Name: {name}, Phone: {phone}, Inquiry: {inquiry_type}, Unit: {unit_type}, Device: {device}")
            
            self.send_response(200)
            self.send_cors_headers()
            self.send_header('Content-Type', 'application/json; charset=utf-8')
            self.end_headers()
            self.wfile.write(json.dumps({"ok": True, "message": "Saved"}).encode('utf-8'))
        else:
            self.send_response(404)
            self.end_headers()

    def send_cors_headers(self):
        self.send_header("Access-Control-Allow-Origin", "*")
        self.send_header("Access-Control-Allow-Methods", "POST, OPTIONS, GET")
        self.send_header("Access-Control-Allow-Headers", "Content-Type")

def run(server_class=HTTPServer, handler_class=MockAppsScriptHandler):
    init_csv()
    server_address = ('', PORT)
    httpd = server_class(server_address, handler_class)
    print("=" * 60)
    print(f"Mock Google Apps Script Web App running on http://localhost:{PORT}")
    print(f"Mock endpoint: http://localhost:{PORT}/macros/s/mock/exec")
    print(f"Local CSV database: {os.path.abspath(CSV_FILE)}")
    print("Press Ctrl+C to terminate.")
    print("=" * 60)
    try:
        httpd.serve_forever()
    except KeyboardInterrupt:
        print("\nStopping Mock Server.")

if __name__ == "__main__":
    run()
