import requests
import json
from datetime import datetime

BASE_URL = "http://localhost:5000"
ADMIN_NUPTK = "152022190"
ADMIN_PASSWORD = "aes040904"

GREEN = '\033[92m'
RED = '\033[91m'
RESET = '\033[0m'

class APITester:
    """A class to perform automated integration testing on API endpoints.

    This class handles the authentication and sequential execution of CRUD 
    operations across various modules (User, Classification, Letters, Reports, Logs).
    It maintains a session and temporary IDs to ensure data continuity during tests.

    Attributes:
        session (requests.Session): The HTTP session used for persistent connections.
        token (str): The JWT access token obtained after login.
        headers (dict): HTTP headers including Content-Type and Authorization.
        temp_ids (dict): A storage dictionary to hold IDs of created records 
            (classification, user, incoming, outgoing, report_card) for later 
            updates or cleanup.
    """
    
    def __init__(self):
        """Initializes the APITester with a session and empty state."""
        self.session = requests.Session()
        self.token = None
        self.headers = {'Content-Type': 'application/json'}
        
        self.temp_ids = {
            "classification": None,
            "user": None,
            "incoming": None,
            "outgoing": None,
            "report_card": None
        }

    def log(self, message: str, success: bool = True):
        """Prints a formatted log message to the terminal.

        Args:
            message (str): The message content to display.
            success (bool, optional): If True, prints in green (SUCCESS). 
                If False, prints in red (FAILED). Defaults to True.
        """
        status = f"{GREEN}[SUCCESS]{RESET}" if success else f"{RED}[FAILED]{RESET}"
        print(f"{status} {message}")

    def login(self) -> bool:
        """Authenticates the admin user to obtain a JWT Token.

        Sends a POST request to the auth/login endpoint. If successful, 
        it stores the access token in the `headers` attribute for subsequent requests.

        Returns:
            bool: True if login is successful and token is stored, False otherwise.
        """
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
        """Executes the CRUD test cycle for Classification.

        Steps:
        1. Creates a new classification.
        2. Retrieves classifications using filters (get_by_keys).
        3. Updates the created classification.
        
        Side Effects:
            Updates `self.temp_ids['classification']` with the new ID.
        """
        print(f"\n--- 2. TESTING CLASSIFICATION CRUD ---")
        
        # 1. Create
        payload = {"name": "Surat Undangan Dinas", "code": "UND"}
        res = self.session.post(f"{BASE_URL}/classification/create", json=payload, headers=self.headers)
        if res.status_code == 201:
            data = res.json()
            self.temp_ids['classification'] = data['id']
            self.log(f"Create Classification: {data['name']} (ID: {data['id']})")
        else:
            self.log(f"Create Classification Gagal: {res.text}", success=False)
            return

        # 2. Get By Keys (New Feature)
        filter_payload = {"filters": {"code": "UND"}}
        res = self.session.post(f"{BASE_URL}/classification/get_by_keys", json=filter_payload, headers=self.headers)
        if res.status_code == 200 and len(res.json()) > 0:
             self.log(f"Get Classification By Keys: Found {len(res.json())} item(s)")
        else:
             self.log(f"Get Classification By Keys Gagal: {res.text}", success=False)

        # 3. Update
        update_payload = {"id": self.temp_ids['classification'], "name": "Surat Undangan Resmi"}
        res = self.session.post(f"{BASE_URL}/classification/update", json=update_payload, headers=self.headers)
        if res.status_code == 200:
            self.log(f"Update Classification: Berhasil")
        else:
            self.log(f"Update Classification Gagal: {res.text}", success=False)

    def test_user_crud(self):
        """Executes the CRUD test cycle for User management.

        Steps:
        1. Creates a new user with a unique NUPTK/Username.
        2. Verifies creation by searching via `get_by_keys`.
        3. Updates the user's status.
        
        Side Effects:
            Updates `self.temp_ids['user']` with the new User ID.
        """
        print(f"\n--- 3. TESTING USER CRUD ---")
        
        unique_suffix = datetime.now().strftime("%M%S")
        payload = {
            "nuptk": f"999{unique_suffix}",
            "username": f"testuser_{unique_suffix}",
            "password": "PasswordStrong1!",
            "role": "teacher",
            "status": "active"
        }
        
        # 1. Create
        res = self.session.post(f"{BASE_URL}/user/create", json=payload, headers=self.headers)
        if res.status_code == 201:
            self.log(f"Create User: {payload['username']}")
            
            # 2. Get By Keys
            search_payload = {"filters": {"nuptk": payload['nuptk']}}
            search = self.session.post(f"{BASE_URL}/user/get_by_keys", json=search_payload, headers=self.headers)
            
            if search.status_code == 200 and len(search.json()) > 0:
                user_data = search.json()[0]
                self.temp_ids['user'] = user_data['id']
                self.log(f"Get User By Keys: Found ID {user_data['id']}")
            else:
                self.log(f"Get User By Keys Gagal: {search.text}", success=False)
        else:
            self.log(f"Create User Gagal: {res.text}", success=False)
            return

        # 3. Update
        if self.temp_ids['user']:
            update_payload = {"id": self.temp_ids['user'], "status": "inactive"}
            res = self.session.post(f"{BASE_URL}/user/update", json=update_payload, headers=self.headers)
            if res.status_code == 200:
                self.log("Update User: Berhasil")
            else:
                self.log(f"Update User Gagal: {res.text}", success=False)

    def test_incoming_letter_crud(self):
        """Executes the CRUD test cycle for Incoming Letters.
        
        Requires:
            A valid classification ID in `self.temp_ids`.

        Steps:
        1. Creates an incoming letter linked to the classification.
        2. Retrieves the letter using `get_by_keys`.
        3. Updates the subject of the letter.
        """
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
        
        # 1. Create
        res = self.session.post(f"{BASE_URL}/incoming-letter/create", json=payload, headers=self.headers)
        if res.status_code == 201:
            data = res.json()
            self.temp_ids['incoming'] = data['id']
            self.log(f"Create Incoming Letter: {data['number']}")
        else:
            self.log(f"Create Incoming Letter Gagal: {res.text}", success=False)

        # 2. Get By Keys
        if self.temp_ids['incoming']:
            filter_payload = {"filters": {"number": payload['number']}}
            res = self.session.post(f"{BASE_URL}/incoming-letter/get_by_keys", json=filter_payload, headers=self.headers)
            if res.status_code == 200 and len(res.json()) > 0:
                 self.log(f"Get Incoming Letter By Keys: Found {len(res.json())} item(s)")
            else:
                 self.log(f"Get Incoming Letter By Keys Gagal: {res.text}", success=False)

        # 3. Update
        if self.temp_ids['incoming']:
            update_payload = {"id": self.temp_ids['incoming'], "subject": "Undangan Rapat REVISI"}
            res = self.session.post(f"{BASE_URL}/incoming-letter/update", json=update_payload, headers=self.headers)
            if res.status_code == 200:
                self.log("Update Incoming Letter: Berhasil")

    def test_outgoing_letter_crud(self):
        """Executes the CRUD test cycle for Outgoing Letters.

        Requires:
            A valid classification ID in `self.temp_ids`.

        Steps:
        1. Creates an outgoing letter.
        2. Retrieves the letter using `get_by_keys` filter (destination).
        """
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
            "is_decree": False,
            "classification_id": self.temp_ids['classification']
        }

        # 1. Create
        res = self.session.post(f"{BASE_URL}/outgoing-letter/create", json=payload, headers=self.headers)
        if res.status_code == 201:
            data = res.json()
            self.temp_ids['outgoing'] = data['id']
            self.log(f"Create Outgoing Letter: {data['number']}")
        else:
            self.log(f"Create Outgoing Letter Gagal: {res.text}", success=False)
        
        # 2. Get By Keys
        if self.temp_ids['outgoing']:
            filter_payload = {"filters": {"destination": "Sekolah Cabang"}}
            res = self.session.post(f"{BASE_URL}/outgoing-letter/get_by_keys", json=filter_payload, headers=self.headers)
            if res.status_code == 200 and len(res.json()) > 0:
                 self.log(f"Get Outgoing Letter By Keys: Found {len(res.json())} item(s)")

    def test_report_card_crud(self):
        """Executes the CRUD test cycle for Report Cards (Raport).

        Steps:
        1. Creates a new report card.
        2. Retrieves it using `get_by_keys` (academic_year).
        3. Updates the student name.
        """
        print(f"\n--- 6. TESTING REPORT CARD ---")
        
        unique_num = datetime.now().strftime("%H%M%S")
        payload = {
            "number": f"RC-{unique_num}",
            "student_name": "Siswa Test API",
            "class_name": "XII-RPL",
            "academic_year": "2024/2025"
        }

        # 1. Create
        res = self.session.post(f"{BASE_URL}/report-card/create", json=payload, headers=self.headers)
        if res.status_code == 201:
            data = res.json()
            self.temp_ids['report_card'] = data['id']
            self.log(f"Create Report Card: {data['student_name']} (No: {data['number']})")
        else:
            self.log(f"Create Report Card Gagal: {res.text}", success=False)
            return

        # 2. Get By Keys
        if self.temp_ids['report_card']:
            filter_payload = {"filters": {"academic_year": "2024/2025"}}
            res = self.session.post(f"{BASE_URL}/report-card/get_by_keys", json=filter_payload, headers=self.headers)
            if res.status_code == 200 and len(res.json()) > 0:
                 self.log(f"Get Report Card By Keys: Found {len(res.json())} item(s)")

        # 3. Update
        if self.temp_ids['report_card']:
            update_payload = {
                "id": self.temp_ids['report_card'],
                "student_name": "Siswa Test API (Updated)"
            }
            res = self.session.post(f"{BASE_URL}/report-card/update", json=update_payload, headers=self.headers)
            if res.status_code == 200:
                self.log("Update Report Card: Berhasil")
            else:
                self.log(f"Update Report Card Gagal: {res.text}", success=False)

    def test_log_endpoints(self):
        """Tests the Logging endpoints (Audit Trail).

        Steps:
        1. Fetches all logs (`get_all`).
        2. Filters logs by action text (`get_by_keys`) to verify recent activities.
        """
        print(f"\n--- 7. TESTING LOG ENDPOINTS ---")
        
        # 1. Get All Logs
        res = self.session.get(f"{BASE_URL}/log/get_all", headers=self.headers)
        if res.status_code == 200:
            count = len(res.json())
            self.log(f"Get All Logs: Berhasil mengambil {count} log")
        else:
            self.log(f"Get All Logs Gagal: {res.text}", success=False)
            return

        # 2. Get Logs By Keys (Filter by Action contains 'membuat')
        # Note: We look for logs created in previous steps
        filter_payload = {"filters": {"action": "membuat"}} 
        res = self.session.post(f"{BASE_URL}/log/get_by_keys", json=filter_payload, headers=self.headers)
        if res.status_code == 200:
            count = len(res.json())
            self.log(f"Get Logs By Keys (Filter 'action'): Found {count} item(s)")
        else:
            self.log(f"Get Logs By Keys Gagal: {res.text}", success=False)

    def cleanup(self):
        """Cleans up test data by deleting created records.
        
        It attempts to delete records in reverse order of dependency:
        1. Incoming Letters
        2. Outgoing Letters
        3. Report Cards
        4. Users
        5. Classifications
        """
        print(f"\n--- 8. CLEANUP (DELETE DATA) ---")
        
        if self.temp_ids['incoming']:
            res = self.session.post(f"{BASE_URL}/incoming-letter/delete", json={"id": self.temp_ids['incoming']}, headers=self.headers)
            self.log(f"Delete Incoming: {res.status_code == 200}")

        if self.temp_ids['outgoing']:
            res = self.session.post(f"{BASE_URL}/outgoing-letter/delete", json={"id": self.temp_ids['outgoing']}, headers=self.headers)
            self.log(f"Delete Outgoing: {res.status_code == 200}")

        if self.temp_ids['report_card']:
            res = self.session.post(f"{BASE_URL}/report-card/delete", json={"id": self.temp_ids['report_card']}, headers=self.headers)
            self.log(f"Delete Report Card: {res.status_code == 200}")

        if self.temp_ids['user']:
            res = self.session.post(f"{BASE_URL}/user/delete", json={"id": self.temp_ids['user']}, headers=self.headers)
            self.log(f"Delete User Test: {res.status_code == 200}")

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
        tester.test_report_card_crud()
        tester.test_log_endpoints()
        tester.cleanup()
    else:
        print("Pengujian dihentikan karena Login Gagal.")