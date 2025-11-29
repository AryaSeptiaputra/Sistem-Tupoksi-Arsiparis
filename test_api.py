import requests
import json
from datetime import datetime

# --- KONFIGURASI ---
BASE_URL = "http://localhost:5000"  # Sesuaikan port jika beda
ADMIN_NUPTK = "152022190"    # Ganti dengan NUPTK user yang SUDAH ADA di DB
ADMIN_PASSWORD = "aes040904"   # Ganti dengan password user tersebut

# Warna untuk output terminal
GREEN = '\033[92m'
RED = '\033[91m'
RESET = '\033[0m'

class APITester:
    def __init__(self):
        self.session = requests.Session()
        self.token = None
        self.headers = {'Content-Type': 'application/json'}
        
        # Penyimpanan ID sementara untuk testing create -> update -> delete
        self.temp_ids = {
            "classification": None,
            "user": None,
            "incoming": None,
            "outgoing": None
        }

    def log(self, message, success=True):
        status = f"{GREEN}[SUCCESS]{RESET}" if success else f"{RED}[FAILED]{RESET}"
        print(f"{status} {message}")

    def login(self):
        print(f"\n--- 1. TESTING AUTH (LOGIN) ---")
        payload = {"nuptk": ADMIN_NUPTK, "password": ADMIN_PASSWORD}
        try:
            res = self.session.post(f"{BASE_URL}/auth/login", json=payload)
            if res.status_code == 200:
                self.token = res.json().get('access_token')
                self.headers['Authorization'] = f"Bearer {self.token}"
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
        
        # A. CREATE
        payload = {"name": "Surat Undangan Dinas", "code": "UND"}
        res = self.session.post(f"{BASE_URL}/classification/create", json=payload, headers=self.headers)
        if res.status_code == 201:
            data = res.json()
            self.temp_ids['classification'] = data['id']
            self.log(f"Create Classification: {data['name']} (ID: {data['id']})")
        else:
            self.log(f"Create Classification Gagal: {res.text}", success=False)
            return

        # B. GET ALL
        res = self.session.get(f"{BASE_URL}/classification/get_all", headers=self.headers)
        if res.status_code == 200:
            self.log(f"Get All Classifications: {len(res.json())} items found")

        # C. UPDATE
        update_payload = {"id": self.temp_ids['classification'], "name": "Surat Undangan Resmi"}
        res = self.session.post(f"{BASE_URL}/classification/update", json=update_payload, headers=self.headers)
        if res.status_code == 200:
            self.log(f"Update Classification: Berhasil")
        else:
            self.log(f"Update Classification Gagal: {res.text}", success=False)

    def test_user_crud(self):
        print(f"\n--- 3. TESTING USER CRUD ---")
        
        # A. CREATE
        # Note: NUPTK harus unik, kita pakai random string/timestamp dikit biar aman test berkali-kali
        unique_suffix = datetime.now().strftime("%M%S")
        payload = {
            "nuptk": f"999{unique_suffix}",
            "username": f"testuser_{unique_suffix}",
            "password": "PasswordStrong1!",
            "role": "teacher",
            "status": "active"
        }
        res = self.session.post(f"{BASE_URL}/user/create", json=payload, headers=self.headers)
        if res.status_code == 201:
            # Response create user Anda tidak mengembalikan ID, hanya message.
            # Kita perlu cari ID nya via get_by_key untuk tes update/delete
            self.log(f"Create User: {payload['username']}")
            
            # Cari ID user barusan
            search = self.session.post(f"{BASE_URL}/user/get_by_key", json={"key": "nuptk", "value": payload['nuptk']}, headers=self.headers)
            if search.status_code == 200:
                user_data = search.json()[0]
                self.temp_ids['user'] = user_data['id']
        else:
            self.log(f"Create User Gagal: {res.text}", success=False)
            return

        # B. UPDATE
        if self.temp_ids['user']:
            update_payload = {"id": self.temp_ids['user'], "status": "inactive"}
            res = self.session.post(f"{BASE_URL}/user/update", json=update_payload, headers=self.headers)
            if res.status_code == 200:
                self.log("Update User: Berhasil")
            else:
                self.log(f"Update User Gagal: {res.text}", success=False)

    def test_incoming_letter_crud(self):
        print(f"\n--- 4. TESTING INCOMING LETTER ---")
        if not self.temp_ids['classification']:
            self.log("Skip Incoming Letter (No Classification ID)", success=False)
            return

        # A. CREATE
        date_now = datetime.now().date().isoformat() # YYYY-MM-DD
        unique_num = datetime.now().strftime("%H%M%S")
        payload = {
            "number": f"IN-{unique_num}",
            "letter_date": date_now,
            "received_date": date_now,
            "sender": "Dinas Pendidikan",
            "subject": "Undangan Rapat",
            "classification_id": self.temp_ids['classification']
        }
        
        res = self.session.post(f"{BASE_URL}/incoming-letter/create", json=payload, headers=self.headers)
        if res.status_code == 201:
            data = res.json()
            self.temp_ids['incoming'] = data['id']
            self.log(f"Create Incoming Letter: {data['number']}")
        else:
            self.log(f"Create Incoming Letter Gagal: {res.text}", success=False)

        # B. UPDATE
        if self.temp_ids['incoming']:
            update_payload = {"id": self.temp_ids['incoming'], "subject": "Undangan Rapat REVISI"}
            res = self.session.post(f"{BASE_URL}/incoming-letter/update", json=update_payload, headers=self.headers)
            if res.status_code == 200:
                self.log("Update Incoming Letter: Berhasil")

    def test_outgoing_letter_crud(self):
        print(f"\n--- 5. TESTING OUTGOING LETTER ---")
        if not self.temp_ids['classification']:
            self.log("Skip Outgoing Letter (No Classification ID)", success=False)
            return

        # A. CREATE
        date_now = datetime.now().date().isoformat()
        unique_num = datetime.now().strftime("%H%M%S")
        payload = {
            "number": f"OUT-{unique_num}",
            "letter_date": date_now,
            "sent_date": date_now,
            "destination": "Sekolah Cabang",
            "subject": "Pemberitahuan Libur",
            "is_decree": False,
            "classification_id": self.temp_ids['classification']
        }

        res = self.session.post(f"{BASE_URL}/outgoing-letter/create", json=payload, headers=self.headers)
        if res.status_code == 201:
            data = res.json()
            self.temp_ids['outgoing'] = data['id']
            self.log(f"Create Outgoing Letter: {data['number']}")
        else:
            self.log(f"Create Outgoing Letter Gagal: {res.text}", success=False)

    def cleanup(self):
        print(f"\n--- 6. CLEANUP (DELETE DATA) ---")
        
        # 1. Delete Incoming
        if self.temp_ids['incoming']:
            res = self.session.post(f"{BASE_URL}/incoming-letter/delete", json={"id": self.temp_ids['incoming']}, headers=self.headers)
            self.log(f"Delete Incoming: {res.status_code == 200}")

        # 2. Delete Outgoing
        if self.temp_ids['outgoing']:
            res = self.session.post(f"{BASE_URL}/outgoing-letter/delete", json={"id": self.temp_ids['outgoing']}, headers=self.headers)
            self.log(f"Delete Outgoing: {res.status_code == 200}")
            
        # 3. Delete User Test
        if self.temp_ids['user']:
            res = self.session.post(f"{BASE_URL}/user/delete", json={"id": self.temp_ids['user']}, headers=self.headers)
            self.log(f"Delete User Test: {res.status_code == 200}")

        # 4. Delete Classification (Harus terakhir karena dipakai Foreign Key oleh surat)
        if self.temp_ids['classification']:
            res = self.session.post(f"{BASE_URL}/classification/delete", json={"id": self.temp_ids['classification']}, headers=self.headers)
            self.log(f"Delete Classification: {res.status_code == 200}")

if __name__ == "__main__":
    tester = APITester()
    if tester.login():
        tester.test_classification_crud()
        tester.test_user_crud()
        tester.test_incoming_letter_crud()
        tester.test_outgoing_letter_crud()
        tester.cleanup()
    else:
        print("Pengujian dihentikan karena Login Gagal.")