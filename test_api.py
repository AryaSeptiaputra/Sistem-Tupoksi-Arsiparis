import requests
import json
from datetime import datetime

BASE_URL = "http://localhost:5000"
# Sesuaikan kredensial ini dengan data seed database Anda
ADMIN_NUPTK = "152022190"
ADMIN_PASSWORD = "aes040904"

GREEN = '\033[92m'
RED = '\033[91m'
RESET = '\033[0m'

class APITester:
    """A class to perform automated integration testing on API endpoints."""
    
    def __init__(self):
        self.session = requests.Session()
        self.token = None
        self.json_headers = {'Content-Type': 'application/json'}
        self.multipart_headers = {}
        
        self.temp_ids = {
            "classification": None,
            "user": None,
            "incoming": None,
            "outgoing": None,
            "report_card": None
        }

    def log(self, message: str, success: bool = True):
        status = f"{GREEN}[SUCCESS]{RESET}" if success else f"{RED}[FAILED]{RESET}"
        print(f"{status} {message}")

    def login(self) -> bool:
        print(f"\n--- 1. TESTING AUTH (LOGIN) ---")
        payload = {"nuptk": ADMIN_NUPTK, "password": ADMIN_PASSWORD}
        try:
            res = self.session.post(f"{BASE_URL}/auth/login", json=payload)
            if res.status_code == 200:
                self.token = res.json().get('access_token')
                auth_header = f"Bearer {self.token}"
                self.json_headers['Authorization'] = auth_header
                self.multipart_headers['Authorization'] = auth_header
                
                self.log(f"Login Berhasil. Token didapatkan.")
                return True
            else:
                self.log(f"Login Gagal: {res.text}", success=False)
                return False
        except Exception as e:
            self.log(f"Koneksi Error: {e}", success=False)
            return False

    def test_classification_crud(self):
        print(f"\n--- 2. TESTING CLASSIFICATION CRUD ---")
        
        payload = {"name": "Surat Undangan Dinas", "code": "UND"}
        res = self.session.post(f"{BASE_URL}/classification/create", json=payload, headers=self.json_headers)
        if res.status_code == 201:
            data = res.json()
            self.temp_ids['classification'] = data['id']
            self.log(f"Create Classification: {data['name']} (ID: {data['id']})")
        else:
            self.log(f"Create Classification Gagal: {res.text}", success=False)
            return

        filter_payload = {"filters": {"code": "UND"}}
        res = self.session.post(f"{BASE_URL}/classification/get_by_keys", json=filter_payload, headers=self.json_headers)
        if res.status_code == 200 and len(res.json()) > 0:
             self.log(f"Get Classification By Keys: Found {len(res.json())} item(s)")
        else:
             self.log(f"Get Classification By Keys Gagal: {res.text}", success=False)

        update_payload = {"id": self.temp_ids['classification'], "name": "Surat Undangan Resmi"}
        res = self.session.post(f"{BASE_URL}/classification/update", json=update_payload, headers=self.json_headers)
        if res.status_code == 200:
            self.log(f"Update Classification: Berhasil")
        else:
            self.log(f"Update Classification Gagal: {res.text}", success=False)

    def test_user_crud(self):
        print(f"\n--- 3. TESTING USER CRUD ---")
        
        unique_suffix = datetime.now().strftime("%M%S")
        payload = {
            "nuptk": f"999{unique_suffix}",
            "username": f"testuser_{unique_suffix}",
            "password": "PasswordStrong1!",
            "role": "teacher",
            "status": "active"
        }
        
        res = self.session.post(f"{BASE_URL}/user/create", json=payload, headers=self.json_headers)
        if res.status_code == 201:
            self.log(f"Create User: {payload['username']}")
            
            search_payload = {"filters": {"nuptk": payload['nuptk']}}
            search = self.session.post(f"{BASE_URL}/user/get_by_keys", json=search_payload, headers=self.json_headers)
            
            if search.status_code == 200 and len(search.json()) > 0:
                user_data = search.json()[0]
                self.temp_ids['user'] = user_data['id']
                self.log(f"Get User By Keys: Found ID {user_data['id']}")
            else:
                self.log(f"Get User By Keys Gagal: {search.text}", success=False)
        else:
            self.log(f"Create User Gagal: {res.text}", success=False)
            return

        if self.temp_ids['user']:
            update_payload = {"id": self.temp_ids['user'], "status": "inactive"}
            res = self.session.post(f"{BASE_URL}/user/update", json=update_payload, headers=self.json_headers)
            if res.status_code == 200:
                self.log("Update User: Berhasil")
            else:
                self.log(f"Update User Gagal: {res.text}", success=False)

    def test_incoming_letter_crud(self):
        print(f"\n--- 4. TESTING INCOMING LETTER ---")
        if not self.temp_ids['classification']:
            self.log("Skip Incoming Letter (No Classification ID)", success=False)
            return

        date_now = datetime.now().date().isoformat()
        unique_num = datetime.now().strftime("%H%M%S")
        
        payload = {
            "number": f"IN-{unique_num}",
            "letter_date": date_now,
            "received_date": date_now,
            "sender": "Dinas Pendidikan",
            "subject": "Undangan Rapat",
            "classification_id": self.temp_ids['classification']
        }
        
        res = self.session.post(f"{BASE_URL}/incoming-letter/create", data=payload, headers=self.multipart_headers)
        
        if res.status_code == 201:
            data = res.json()
            self.temp_ids['incoming'] = data['id']
            self.log(f"Create Incoming Letter: {data['number']}")
        else:
            self.log(f"Create Incoming Letter Gagal: {res.text}", success=False)

        if self.temp_ids['incoming']:
            filter_payload = {"filters": {"number": payload['number']}}
            res = self.session.post(f"{BASE_URL}/incoming-letter/get_by_keys", json=filter_payload, headers=self.json_headers)
            if res.status_code == 200 and len(res.json()) > 0:
                 self.log(f"Get Incoming Letter By Keys: Found {len(res.json())} item(s)")
            else:
                 self.log(f"Get Incoming Letter By Keys Gagal: {res.text}", success=False)

        if self.temp_ids['incoming']:
            update_payload = {"id": self.temp_ids['incoming'], "subject": "Undangan Rapat REVISI"}
            res = self.session.post(f"{BASE_URL}/incoming-letter/update", json=update_payload, headers=self.json_headers)
            if res.status_code == 200:
                self.log("Update Incoming Letter: Berhasil")
            else:
                self.log(f"Update Incoming Letter Gagal: {res.text}", success=False)

    def test_outgoing_letter_crud(self):
        print(f"\n--- 5. TESTING OUTGOING LETTER ---")
        if not self.temp_ids['classification']:
            self.log("Skip Outgoing Letter (No Classification ID)", success=False)
            return

        date_now = datetime.now().date().isoformat()
        unique_num = datetime.now().strftime("%H%M%S")
        
        payload = {
            "number": f"OUT-{unique_num}",
            "letter_date": date_now,
            "sent_date": date_now,
            "destination": "Sekolah Cabang",
            "subject": "Pemberitahuan Libur",
            "is_decree": "false",
            "classification_id": self.temp_ids['classification']
        }

        res = self.session.post(f"{BASE_URL}/outgoing-letter/create", data=payload, headers=self.multipart_headers)
        
        if res.status_code == 201:
            data = res.json()
            self.temp_ids['outgoing'] = data['id']
            self.log(f"Create Outgoing Letter: {data['number']}")
        else:
            self.log(f"Create Outgoing Letter Gagal: {res.text}", success=False)
        
        if self.temp_ids['outgoing']:
            filter_payload = {"filters": {"destination": "Sekolah Cabang"}}
            res = self.session.post(f"{BASE_URL}/outgoing-letter/get_by_keys", json=filter_payload, headers=self.json_headers)
            if res.status_code == 200 and len(res.json()) > 0:
                 self.log(f"Get Outgoing Letter By Keys: Found {len(res.json())} item(s)")

        # ▶️ NOW ADDED: Update Outgoing Letter
        if self.temp_ids['outgoing']:
            update_payload = {
                "id": self.temp_ids['outgoing'],
                "subject": "Pemberitahuan Libur (REVISI)"
            }
            res = self.session.post(f"{BASE_URL}/outgoing-letter/update", json=update_payload, headers=self.json_headers)
            if res.status_code == 200:
                self.log("Update Outgoing Letter: Berhasil")
            else:
                self.log(f"Update Outgoing Letter Gagal: {res.text}", success=False)

    def test_report_card_crud(self):
        print(f"\n--- 6. TESTING REPORT CARD ---")
        
        unique_num = datetime.now().strftime("%H%M%S")
        
        payload = {
            "number": f"RC-{unique_num}",
            "student_name": "Siswa Test API",
            "class_name": "XII-RPL",
            "academic_year": "2024/2025"
        }

        res = self.session.post(f"{BASE_URL}/report-card/create", data=payload, headers=self.multipart_headers)
        
        if res.status_code == 201:
            data = res.json()
            self.temp_ids['report_card'] = data['id']
            self.log(f"Create Report Card: {data['student_name']} (No: {data['number']})")
        else:
            self.log(f"Create Report Card Gagal: {res.text}", success=False)
            return

        if self.temp_ids['report_card']:
            filter_payload = {"filters": {"academic_year": "2024/2025"}}
            res = self.session.post(f"{BASE_URL}/report-card/get_by_keys", json=filter_payload, headers=self.json_headers)
            if res.status_code == 200 and len(res.json()) > 0:
                 self.log(f"Get Report Card By Keys: Found {len(res.json())} item(s)")

        if self.temp_ids['report_card']:
            update_payload = {
                "id": self.temp_ids['report_card'],
                "student_name": "Siswa Test API (Updated)"
            }
            res = self.session.post(f"{BASE_URL}/report-card/update", json=update_payload, headers=self.json_headers)
            if res.status_code == 200:
                self.log("Update Report Card: Berhasil")
            else:
                self.log(f"Update Report Card Gagal: {res.text}", success=False)

    def test_backup_endpoints(self):
        print(f"\n--- 7. TESTING BACKUP ---")
        
        res = self.session.post(f"{BASE_URL}/backup/manual", headers=self.json_headers)
        if res.status_code == 201:
            self.log(f"Manual Backup Triggered: {res.json().get('message')}")
        else:
            self.log(f"Manual Backup Gagal: {res.text}", success=False)

        res = self.session.get(f"{BASE_URL}/backup/logs", headers=self.json_headers)
        if res.status_code == 200:
            logs = res.json()
            self.log(f"Get Backup Logs: Retrieved {len(logs)} logs")
        else:
            self.log(f"Get Backup Logs Gagal: {res.text}", success=False)

    def test_log_endpoints(self):
        print(f"\n--- 8. TESTING LOG ENDPOINTS ---")
        
        res = self.session.get(f"{BASE_URL}/log/get_all", headers=self.json_headers)
        if res.status_code == 200:
            count = len(res.json())
            self.log(f"Get All Logs: Berhasil mengambil {count} log")
        else:
            self.log(f"Get All Logs Gagal: {res.text}", success=False)
            return

        filter_payload = {"filters": {"action": "membuat"}}
        res = self.session.post(f"{BASE_URL}/log/get_by_keys", json=filter_payload, headers=self.json_headers)
        if res.status_code == 200:
            count = len(res.json())
            self.log(f"Get Logs By Keys (Filter 'action'): Found {count} item(s)")
        else:
            self.log(f"Get Logs By Keys Gagal: {res.text}", success=False)

    def cleanup(self):
        print(f"\n--- 9. CLEANUP (DELETE DATA) ---")
        
        def delete_item(endpoint, item_id):
            return self.session.post(f"{BASE_URL}/{endpoint}/delete", json={"id": item_id}, headers=self.json_headers)

        if self.temp_ids['incoming']:
            res = delete_item("incoming-letter", self.temp_ids['incoming'])
            self.log(f"Delete Incoming: {res.status_code == 200}")

        if self.temp_ids['outgoing']:
            res = delete_item("outgoing-letter", self.temp_ids['outgoing'])
            self.log(f"Delete Outgoing: {res.status_code == 200}")

        if self.temp_ids['report_card']:
            res = delete_item("report-card", self.temp_ids['report_card'])
            self.log(f"Delete Report Card: {res.status_code == 200}")

        if self.temp_ids['user']:
            res = delete_item("user", self.temp_ids['user'])
            self.log(f"Delete User Test: {res.status_code == 200}")

        if self.temp_ids['classification']:
            res = delete_item("classification", self.temp_ids['classification'])
            self.log(f"Delete Classification: {res.status_code == 200}")


if __name__ == "__main__":
    tester = APITester()
    if tester.login():
        tester.test_classification_crud()
        tester.test_user_crud()
        tester.test_incoming_letter_crud()
        tester.test_outgoing_letter_crud()
        tester.test_report_card_crud()
        tester.test_backup_endpoints()
        tester.test_log_endpoints()
        tester.cleanup()
    else:
        print("Pengujian dihentikan karena Login Gagal.")
