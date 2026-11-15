import os
import json
import tkinter as tk
from tkinter import filedialog
import customtkinter as ctk
import serial.tools.list_ports
from fpdf import FPDF

ctk.set_appearance_mode("dark")
ctk.set_default_color_theme("blue")

SUNVOLT_JOB_QUEUE = []
SUNVOLT_HISTORY_ARCHIVE = []
SUNVOLT_ADMIN_FINANCES = {"total_revenue": 0.0, "total_profit": 0.0, "total_completed": 0, "total_parts_cost": 0.0}
SUNVOLT_SPARE_PARTS = [
    {"name": "Infinix / Tecno OLED Display", "price": 18500, "stock": 6},
    {"name": "IRF3205 N-Channel Mosfet (10pcs)", "price": 4500, "stock": 15},
    {"name": "EGS002 Pure Sine SPWM Module", "price": 6500, "stock": 8},
    {"name": "W25Q64 BIOS Flash Chip (5pcs)", "price": 3000, "stock": 12},
    {"name": "Samsung Type-C Charging Board", "price": 5500, "stock": 10}
]
DATA_FILE_PATH = os.path.join(os.path.expanduser("~"), "sunvolt_local_data.json")
SUNVOLT_API_CONFIG = {"gemini_key": "", "termii_key": "", "sender_id": "SUNVOLT", "neon_url": "", "eng_pin": "2222", "admin_pin": "9999"}


def save_sunvolt_local_data():
    try:
        payload = {
            "jobs": SUNVOLT_JOB_QUEUE,
            "history": SUNVOLT_HISTORY_ARCHIVE,
            "finances": SUNVOLT_ADMIN_FINANCES,
            "parts": SUNVOLT_SPARE_PARTS,
            "config": SUNVOLT_API_CONFIG
        }
        with open(DATA_FILE_PATH, "w", encoding="utf-8") as f:
            json.dump(payload, f, indent=2)
    except Exception:
        pass

def load_sunvolt_local_data():
    if not os.path.exists(DATA_FILE_PATH):
        save_sunvolt_local_data()
        return
    try:
        with open(DATA_FILE_PATH, "r", encoding="utf-8") as f:
            data = json.load(f)
        SUNVOLT_JOB_QUEUE.clear()
        SUNVOLT_JOB_QUEUE.extend(data.get("jobs", []))
        SUNVOLT_HISTORY_ARCHIVE.clear()
        SUNVOLT_HISTORY_ARCHIVE.extend(data.get("history", []))
        SUNVOLT_ADMIN_FINANCES.update(data.get("finances", {}))
        if data.get("parts"):
            SUNVOLT_SPARE_PARTS.clear()
            SUNVOLT_SPARE_PARTS.extend(data.get("parts", []))
        SUNVOLT_API_CONFIG.update(data.get("config", {}))
        if SUNVOLT_API_CONFIG.get("gemini_key"):
            os.environ["GEMINI_API_KEY"] = SUNVOLT_API_CONFIG["gemini_key"]
        if SUNVOLT_API_CONFIG.get("neon_url"):
            os.environ["NEON_DATABASE_URL"] = SUNVOLT_API_CONFIG["neon_url"]
    except Exception:
        pass

load_sunvolt_local_data()

LANG_TEXT = {
    "HA": {
        "app_title": "SUNVOLT TECH HUB — KASHERE",
        "nav_rec": "🛎️ Reception (Intake)",
        "nav_eng": "🛠️ Senior Engineer Lab",
        "nav_parts": "🛒 Spare Parts Market",
        "nav_imei": "🛡️ EasyBuy / IMEI Check",
        "nav_admin": "👑 Shop Owner (Admin)",
        "rec_title": "🛎️ SHAFIN KARƁAR KAYA (RECEPTION INTAKE)",
        "eng_title": "🛠️ DAKIN GYARA NA BABBAN ENGINEER",
        "access_denied": "⛔ HANA SHIGA: Wannan shafin na Babban Engineer ko Ubangida ne kawai!",
        "pending_jobs": "📋 Sabbin Kayayyakin da Suka Shigo Daga Reception:",
        "ready_jobs": "✅ Kayayyakin da Aka Tsaida Farashi (A Shirye Don Gyara):",
        "total_cost": "Kuɗin Gyara (₦):",
        "set_price_btn": "💰 Tsaida Farashi & Tura SMS",
        "scan_btn": "🔍 Bincika Board / USB (AI Scan)",
        "final_sms_btn": "✅ Kammala Gyara & Tura SMS",
        "status": "📊 Sakamakon Binciken AI & Matsalar Kati:",
        "status_idle": "A shirye don bincike. Zaɓi kaya a sama ko ka danna 'AI Scan'.",
        "admin_title": "👑 ALLON UBANGIDA (SHOP OWNER DASHBOARD)",
        "total_revenue": "💰 Jimillar Kuɗin Shiga (Total Revenue):",
        "total_profit": "📈 Tsantsar Riba (20% Net Profit):",
        "total_completed": "✅ Adadin Gyaran da Aka Kammala:"
    },
    "EN": {
        "app_title": "SUNVOLT TECH HUB — KASHERE",
        "nav_rec": "🛎️ Reception (Intake)",
        "nav_eng": "🛠️ Senior Engineer Lab",
        "nav_parts": "🛒 Spare Parts Market",
        "nav_imei": "🛡️ EasyBuy / IMEI Check",
        "nav_admin": "👑 Shop Owner (Admin)",
        "rec_title": "🛎️ CUSTOMER DEVICE INTAKE (RECEPTION)",
        "eng_title": "🛠️ SENIOR ENGINEER DIAGNOSTIC & PCB LAB",
        "access_denied": "⛔ ACCESS DENIED: Restricted to Senior Engineer or Admin!",
        "pending_jobs": "📋 New Intake Devices Awaiting Quote:",
        "ready_jobs": "✅ Approved Jobs (Ready for Repair):",
        "total_cost": "Repair Quote (₦):",
        "set_price_btn": "💰 Approve Quote & Send SMS",
        "scan_btn": "🔍 Run AI Board / USB Scan",
        "final_sms_btn": "✅ Complete Repair & Send SMS",
        "status": "📊 Live AI Diagnostics & Hardware Report:",
        "status_idle": "System idle. Select an approved device or click 'Run AI Scan'.",
        "admin_title": "👑 SHOP OWNER FINANCIAL DASHBOARD",
        "total_revenue": "💰 Total Gross Revenue:",
        "total_profit": "📈 Net Company Profit (20%):",
        "total_completed": "✅ Total Completed Repairs:"
    }
}


class SunvoltApp(ctk.CTk):
    def __init__(self):
        super().__init__()
        self.title("⚡ SUNVOLT TECH HUB — Kashere Engineering & Repair OS")
        self.geometry("1180x720")
        self.current_lang = "HA"
        self.user_role = "admin"
        self.ticket_counter = 101
        self.selected_hw_mode = "Phone"
        self.board_image_path = None
        self.current_pcb_title = "PURE SINE WAVE INVERTER BOARD (PCB REV 4.2)"
        self.current_pcb_mode = "inverter"

        self.initialize_neon_database()

        self.grid_columnconfigure(1, weight=1)
        self.grid_rowconfigure(0, weight=1)

        # Sidebar
        self.sidebar_frame = ctk.CTkFrame(self, width=230, corner_radius=0, fg_color="#0D1117")
        self.sidebar_frame.grid(row=0, column=0, sticky="nsew")
        self.sidebar_frame.grid_rowconfigure(9, weight=1)

        self.logo_label = ctk.CTkLabel(self.sidebar_frame, text="⚡ SUNVOLT", font=ctk.CTkFont(size=24, weight="bold"), text_color="#FFB300")
        self.logo_label.grid(row=0, column=0, padx=20, pady=(20, 4))
        ctk.CTkLabel(self.sidebar_frame, text="Kashere Hardware & Mobile Lab", font=ctk.CTkFont(size=11), text_color="#8B949E").grid(row=1, column=0, padx=20, pady=(0, 15))

        ctk.CTkLabel(self.sidebar_frame, text="👤 Active Role:", font=ctk.CTkFont(size=11, weight="bold")).grid(row=2, column=0, padx=20, pady=(5, 2), sticky="w")
        self.role_menu = ctk.CTkOptionMenu(self.sidebar_frame, values=["Admin (Shop Owner)", "Senior Engineer", "Receptionist"], command=self.change_user_role)
        self.role_menu.grid(row=3, column=0, padx=20, pady=(0, 15))

        t = LANG_TEXT[self.current_lang]
        self.btn_nav_rec = ctk.CTkButton(self.sidebar_frame, text=t["nav_rec"], anchor="w", command=self.show_reception_view)
        self.btn_nav_rec.grid(row=4, column=0, padx=20, pady=6, sticky="ew")

        self.btn_nav_eng = ctk.CTkButton(self.sidebar_frame, text=t["nav_eng"], anchor="w", fg_color="#FFB300", text_color="black", font=ctk.CTkFont(weight="bold"), command=self.show_engineer_view)
        self.btn_nav_eng.grid(row=5, column=0, padx=20, pady=6, sticky="ew")

        self.btn_nav_parts = ctk.CTkButton(self.sidebar_frame, text=t["nav_parts"], anchor="w", command=self.show_marketplace_view)
        self.btn_nav_parts.grid(row=6, column=0, padx=20, pady=6, sticky="ew")

        self.btn_nav_imei = ctk.CTkButton(self.sidebar_frame, text=t["nav_imei"], anchor="w", command=self.show_imei_view)
        self.btn_nav_imei.grid(row=7, column=0, padx=20, pady=6, sticky="ew")

        self.btn_nav_admin = ctk.CTkButton(self.sidebar_frame, text=t["nav_admin"], anchor="w", fg_color="#6A1B9A", command=self.show_admin_view)
        self.btn_nav_admin.grid(row=8, column=0, padx=20, pady=6, sticky="ew")
        self.btn_nav_settings = ctk.CTkButton(self.sidebar_frame, text="⚙️ API & SMS Settings", anchor="w", fg_color="#37474F", command=self.show_settings_view)
        self.btn_nav_settings.grid(row=9, column=0, padx=20, pady=6, sticky="ew")

        self.lang_switch = ctk.CTkSegmentedButton(self.sidebar_frame, values=["HA", "EN"], command=self.toggle_language)
        self.lang_switch.set("HA")
        self.lang_switch.grid(row=10, column=0, padx=20, pady=15)

        self.main_frame = ctk.CTkFrame(self, corner_radius=0, fg_color="#161B22")
        self.main_frame.grid(row=0, column=1, sticky="nsew")

        self.show_engineer_view()
        self.protocol("WM_DELETE_WINDOW", self.on_app_close)

    def on_app_close(self):
        save_sunvolt_local_data()
        self.destroy()

    def initialize_neon_database(self):
        self.neon_connected = False
        try:
            import psycopg2
            db_url = os.environ.get("NEON_DATABASE_URL", "")
            if db_url:
                conn = psycopg2.connect(db_url)
                cur = conn.cursor()
                cur.execute("CREATE TABLE IF NOT EXISTS repair_jobs (ticket_id TEXT PRIMARY KEY, customer TEXT, phone TEXT, model TEXT, fault TEXT, quote REAL, status TEXT);")
                cur.execute("CREATE TABLE IF NOT EXISTS parts_orders (id SERIAL PRIMARY KEY, part_name TEXT, price REAL, ordered_at TIMESTAMP DEFAULT NOW());")
                conn.commit()
                cur.close()
                conn.close()
                self.neon_connected = True
        except Exception:
            self.neon_connected = False

    def save_part_order_to_neon(self, item):
        try:
            import psycopg2
            db_url = os.environ.get("NEON_DATABASE_URL", "")
            if db_url:
                conn = psycopg2.connect(db_url)
                cur = conn.cursor()
                cur.execute("INSERT INTO parts_orders (part_name, price) VALUES (%s, %s);", (item["name"], item["price"]))
                conn.commit()
                cur.close()
                conn.close()
        except Exception:
            pass

    def clear_main_frame(self):
        for widget in self.main_frame.winfo_children():
            widget.destroy()

    def change_user_role(self, choice):
        if "Receptionist" in choice:
            self.user_role = "receptionist"
            self.show_reception_view()
            return
        req_pin = SUNVOLT_API_CONFIG.get("eng_pin", "2222") if "Engineer" in choice else SUNVOLT_API_CONFIG.get("admin_pin", "9999")
        dialog = ctk.CTkInputDialog(text=f"🔐 Shigar da Lambar Sirri (PIN) don shiga {choice}:", title="SUNVOLT SECURITY LOCK")
        entered = dialog.get_input()
        if entered == req_pin:
            if "Engineer" in choice:
                self.user_role = "engineer"
                self.show_engineer_view()
            else:
                self.user_role = "admin"
                self.show_admin_view()
        else:
            self.role_menu.set("Receptionist")
            self.user_role = "receptionist"
            self.show_reception_view()

    def toggle_language(self, lang):
        self.current_lang = lang
        t = LANG_TEXT[lang]
        self.btn_nav_rec.configure(text=t["nav_rec"])
        self.btn_nav_eng.configure(text=t["nav_eng"])
        self.btn_nav_parts.configure(text=t["nav_parts"])
        self.btn_nav_imei.configure(text=t["nav_imei"])
        self.btn_nav_admin.configure(text=t["nav_admin"])
        self.show_engineer_view()

    # ==================== 1. RECEPTION VIEW ====================
    def show_reception_view(self):
        self.clear_main_frame()
        t = LANG_TEXT[self.current_lang]
        ctk.CTkLabel(self.main_frame, text=t["rec_title"], font=ctk.CTkFont(size=20, weight="bold"), text_color="#00E676").pack(anchor="w", padx=30, pady=(15, 8))

        wrap = ctk.CTkFrame(self.main_frame, fg_color="transparent")
        wrap.pack(fill="both", expand=True, padx=30, pady=5)
        wrap.grid_columnconfigure(0, weight=1)
        wrap.grid_columnconfigure(1, weight=1)

        # Left: Vertical Intake Form (Akwatunan Shigar da Bayanai a Tsaye)
        form = ctk.CTkFrame(wrap, fg_color="#111111", corner_radius=10)
        form.grid(row=0, column=0, padx=(0, 12), pady=5, sticky="nsew")

        ctk.CTkLabel(form, text="📝 Sabon Rajistar Kaya (Vertical Form):", font=ctk.CTkFont(size=14, weight="bold"), text_color="#FFB300").pack(anchor="w", padx=20, pady=(14, 8))

        self.entry_cust_name = ctk.CTkEntry(form, width=380, placeholder_text="1. Sunan Kwastoma (Customer Name)...")
        self.entry_cust_name.pack(anchor="w", padx=20, pady=6)

        self.entry_cust_phone = ctk.CTkEntry(form, width=380, placeholder_text="2. Lambar Waya (Phone e.g. 0803...)")
        self.entry_cust_phone.pack(anchor="w", padx=20, pady=6)

        self.entry_dev_model = ctk.CTkEntry(form, width=380, placeholder_text="3. Sunan Na'ura (Samsung, Inverter 3.5kVA...)")
        self.entry_dev_model.pack(anchor="w", padx=20, pady=6)

        self.entry_dev_imei = ctk.CTkEntry(form, width=380, placeholder_text="4. IMEI / Serial Number / NIN Check...")
        self.entry_dev_imei.pack(anchor="w", padx=20, pady=6)

        self.entry_dev_fault = ctk.CTkEntry(form, width=380, placeholder_text="5. Matsalar Na'urar (Fault Description)...")
        self.entry_dev_fault.pack(anchor="w", padx=20, pady=6)
        self.entry_deposit = ctk.CTkEntry(form, width=380, placeholder_text="6. Deposit Paid (₦) — Rubuta 0 idan bai bada ba...")
        self.entry_deposit.pack(anchor="w", padx=20, pady=6)

        ctk.CTkButton(form, text="📥 Yi Rajista & Tura Zuwa Babban Engineer", width=380, height=40, fg_color="#00E676", text_color="black", font=ctk.CTkFont(weight="bold"), command=self.action_submit_order).pack(anchor="w", padx=20, pady=(12, 8))

        self.lbl_rec_feedback = ctk.CTkLabel(form, text="", font=ctk.CTkFont(size=12, weight="bold"), text_color="#FFB300", wraplength=380, justify="left")
        self.lbl_rec_feedback.pack(anchor="w", padx=20, pady=(2, 12))

        # Right: Live Engineer Status & Rejected Jobs Board + Delete Button
        board = ctk.CTkFrame(wrap, fg_color="#111111", corner_radius=10)
        board.grid(row=0, column=1, padx=(12, 0), pady=5, sticky="nsew")

        ctk.CTkLabel(board, text="📡 Sakamakon Babban Engineer (Live Status & Rejects):", font=ctk.CTkFont(size=14, weight="bold"), text_color="#64FFDA").pack(anchor="w", padx=20, pady=(14, 8))

        self.rec_status_listbox = tk.Listbox(board, width=54, height=13, bg="#1E1E1E", fg="white", bd=0, font=("Helvetica", 10))
        self.rec_status_listbox.pack(anchor="w", padx=20, pady=6)

        btn_bar = ctk.CTkFrame(board, fg_color="transparent")
        btn_bar.pack(anchor="w", padx=20, pady=10)
        ctk.CTkButton(btn_bar, text="🔄 Refresh Status", width=150, height=34, fg_color="#2296F3", font=ctk.CTkFont(weight="bold"), command=self.refresh_reception_status_list).pack(side="left", padx=(0, 10))
        ctk.CTkButton(btn_bar, text="🗑️ Delete Selected", width=150, height=34, fg_color="#D50000", font=ctk.CTkFont(weight="bold"), command=self.action_delete_reception_item).pack(side="left")

        self.refresh_reception_status_list()
    def refresh_reception_status_list(self):
        if not hasattr(self, 'rec_status_listbox') or not self.rec_status_listbox.winfo_exists():
            return
        self.rec_status_listbox.delete(0, tk.END)
        self.rec_all_items_cache = []
        active_id = getattr(self, 'active_workbench_ticket_id', None)
        for j in SUNVOLT_JOB_QUEUE:
            self.rec_all_items_cache.append(("queue", j))
            is_active = " 🔧 [ANA DUBAWA YANZU]" if j["ticket_id"] == active_id else ""
            if j["status"] == "Rejected":
                self.rec_status_listbox.insert(tk.END, f"❌ REJECTED #{j['ticket_id']} | {j['model']} — Dalili: {j.get('reject_reason', 'Unrepairable')}")
            elif j["status"] == "Approved":
                self.rec_status_listbox.insert(tk.END, f"💰 APPROVED #{j['ticket_id']} | {j['model']} — Kuɗi: ₦{j['quote']:,.0f}{is_active}")
            else:
                self.rec_status_listbox.insert(tk.END, f"⏳ PENDING #{j['ticket_id']} | {j['model']} ({j['customer']}){is_active}")
        for j in SUNVOLT_HISTORY_ARCHIVE:
            self.rec_all_items_cache.append(("history", j))
            self.rec_status_listbox.insert(tk.END, f"✅ COMPLETED #{j['ticket_id']} | {j['model']} — An Gama (₦{j['quote']:,.0f})")

    def action_delete_reception_item(self):
        sel = self.rec_status_listbox.curselection()
        if not sel:
            return
        idx = sel
        src, job = self.rec_all_items_cache[idx]
        if src == "queue" and job in SUNVOLT_JOB_QUEUE:
            SUNVOLT_JOB_QUEUE.remove(job)
        elif src == "history" and job in SUNVOLT_HISTORY_ARCHIVE:
            SUNVOLT_HISTORY_ARCHIVE.remove(job)
        self.refresh_reception_status_list()
        self.lbl_rec_feedback.configure(text=f"🗑️ An goge #{job['ticket_id']} daga allon Reception.", text_color="#FF9100")

    def action_submit_order(self):
        name = self.entry_cust_name.get().strip() or "Walk-in Customer"
        phone = self.entry_cust_phone.get().strip() or "08000000000"
        model = self.entry_dev_model.get().strip() or "Unknown Device"
        imei = self.entry_dev_imei.get().strip() or "N/A"
        fault = self.entry_dev_fault.get().strip() or "General Hardware Check"
        try:
            dep_val = float(self.entry_deposit.get().strip() or "0")
        except ValueError:
            dep_val = 0.0

        tid = f"SV-{self.ticket_counter}"
        self.ticket_counter += 1
        dep_note = f"Deposit: ₦{dep_val:,.0f}" if dep_val > 0 else "No Deposit (₦0)"
        job = {
            "ticket_id": tid, "customer": name, "phone": phone,
            "model": model, "imei": imei, "fault": fault,
            "deposit": dep_val, "quote": 0.0, "status": "Pending"
        }
        SUNVOLT_JOB_QUEUE.append(job)
        save_sunvolt_local_data()
        self.lbl_rec_feedback.configure(
            text=f"✅ An yi rajistar #{tid} ({model}) | {dep_note} — An tura wa Babban Engineer!",
            text_color="#00E676"
        )
        for entry in (self.entry_cust_name, self.entry_cust_phone, self.entry_dev_model, self.entry_dev_imei, self.entry_dev_fault, self.entry_deposit):
            entry.delete(0, tk.END)
        self.refresh_reception_status_list()

    # ==================== 2. SENIOR ENGINEER LAB (5 TABS) ====================
    def show_engineer_view(self):
        t = LANG_TEXT[self.current_lang]
        if self.user_role == "receptionist":
            self.clear_main_frame()
            ctk.CTkLabel(self.main_frame, text=t["access_denied"], font=ctk.CTkFont(size=16, weight="bold"), text_color="#FF3D00").grid(row=0, column=0, padx=40, pady=40, sticky="w")
            return
        self.clear_main_frame()
        self.main_frame.grid_rowconfigure(0, weight=0)
        self.main_frame.grid_rowconfigure(1, weight=0)
        self.main_frame.grid_rowconfigure(2, weight=1)
        self.main_frame.grid_columnconfigure(0, weight=1)

        ctk.CTkLabel(self.main_frame, text=t["eng_title"], font=ctk.CTkFont(size=20, weight="bold"), text_color="#FFB300").grid(row=0, column=0, padx=25, pady=(12, 6), sticky="w")

        nav_bar = ctk.CTkFrame(self.main_frame, fg_color="#111111", corner_radius=8)
        nav_bar.grid(row=1, column=0, padx=25, pady=(0, 8), sticky="w")

        self.eng_sub_buttons = {}
        sub_pages = [
            ("📋 1. Pending", "intake"),
            ("🔬 2. AI Diagnostics", "lab"),
            ("🧬 3. IC Programmer", "programmer"),
            ("🧾 4. Receipts", "history"),
            ("📐 5. PCB Studio", "pcb_studio")
        ]
        for idx, (label, key) in enumerate(sub_pages):
            btn = ctk.CTkButton(nav_bar, text=label, width=165, height=34, fg_color="#2B2B2B", text_color="white", font=ctk.CTkFont(size=12, weight="bold"), command=lambda k=key: self.switch_engineer_subpage(k))
            btn.grid(row=0, column=idx, padx=4, pady=6)
            self.eng_sub_buttons[key] = btn

        self.eng_content_area = ctk.CTkFrame(self.main_frame, fg_color="#111111", corner_radius=10)
        self.eng_content_area.grid(row=2, column=0, padx=25, pady=(0, 18), sticky="nsew")
        self.switch_engineer_subpage("intake")

    def switch_engineer_subpage(self, page_key):
        t = LANG_TEXT[self.current_lang]
        for k, btn in self.eng_sub_buttons.items():
            btn.configure(fg_color="#FFB300" if k == page_key else "#2B2B2B", text_color="black" if k == page_key else "white")

        for w in self.eng_content_area.winfo_children():
            w.destroy()

        if page_key == "intake":
            ctk.CTkLabel(self.eng_content_area, text=t["pending_jobs"], font=ctk.CTkFont(size=14, weight="bold"), text_color="#FFB300").pack(anchor="w", padx=25, pady=(15, 5))
            self.pending_listbox = tk.Listbox(self.eng_content_area, width=88, height=7, bg="#1E1E1E", fg="white", bd=0, exportselection=False, font=("Helvetica", 11))
            self.pending_listbox.pack(anchor="w", padx=25, pady=5)
            self.pending_listbox.bind('<<ListboxSelect>>', self.on_select_pending_job)

            self.lbl_intake_details = ctk.CTkLabel(self.eng_content_area, text="Zaɓi kaya a sama don tsaida farashi, Reject, ko goge shi.", font=ctk.CTkFont(size=13), text_color="#B0BEC5")
            self.lbl_intake_details.pack(anchor="w", padx=25, pady=8)

            quote_row = ctk.CTkFrame(self.eng_content_area, fg_color="transparent")
            quote_row.pack(anchor="w", padx=25, pady=6)
            ctk.CTkLabel(quote_row, text=t["total_cost"], font=ctk.CTkFont(size=13, weight="bold")).pack(side="left", padx=(0, 10))
            self.entry_final_cost = ctk.CTkEntry(quote_row, width=180, placeholder_text="e.g. 15000", fg_color="#2B2B2B")
            self.entry_final_cost.pack(side="left", padx=(0, 12))
            ctk.CTkButton(quote_row, text=t["set_price_btn"], fg_color="#FF9100", text_color="black", width=230, height=36, font=ctk.CTkFont(weight="bold"), command=self.action_engineer_set_price).pack(side="left")

            reject_row = ctk.CTkFrame(self.eng_content_area, fg_color="#1A1A1A", corner_radius=8)
            reject_row.pack(anchor="w", padx=25, pady=(10, 5))
            ctk.CTkLabel(reject_row, text="Reject Reason:", font=ctk.CTkFont(size=12, weight="bold"), text_color="#FF3D00").pack(side="left", padx=10, pady=8)
            self.entry_reject_reason = ctk.CTkEntry(reject_row, width=250, placeholder_text="e.g. Dead CPU / Burnt PCB...", fg_color="#2B2B2B")
            self.entry_reject_reason.pack(side="left", padx=6, pady=8)
            ctk.CTkButton(reject_row, text="❌ Reject", fg_color="#D50000", text_color="white", width=110, height=34, font=ctk.CTkFont(weight="bold"), command=self.action_engineer_reject_job).pack(side="left", padx=6, pady=8)
            ctk.CTkButton(reject_row, text="🗑️ Delete Job", fg_color="#424242", text_color="white", width=110, height=34, font=ctk.CTkFont(weight="bold"), command=self.action_delete_pending_job).pack(side="left", padx=(0, 10), pady=8)

        elif page_key == "lab":
            lab_wrap = ctk.CTkFrame(self.eng_content_area, fg_color="transparent")
            lab_wrap.pack(fill="both", expand=True, padx=10, pady=10)
            lab_wrap.grid_columnconfigure(0, weight=3)
            lab_wrap.grid_columnconfigure(1, weight=2)

            lab_left = ctk.CTkFrame(lab_wrap, fg_color="transparent")
            lab_left.grid(row=0, column=0, padx=10, pady=5, sticky="nsew")

            hw_frame = ctk.CTkFrame(lab_left, fg_color="#1A1A1A", corner_radius=8)
            hw_frame.pack(anchor="w", pady=(5, 6))
            self.hw_buttons = {}
            hw_modes = [("📱 Phone", "Phone"), ("💻 Laptop", "Laptop"), ("⚡ Inverter", "Inverter"), ("☀️ CC", "Charge_Controller"), ("🧵 Sewing", "Sewing_Machine"), ("🌐 Universal", "Universal_Unknown")]
            for idx, (label_txt, mode_key) in enumerate(hw_modes):
                btn = ctk.CTkButton(hw_frame, text=label_txt, width=90, height=28, fg_color="#FFB300" if mode_key == self.selected_hw_mode else "#2B2B2B", text_color="black" if mode_key == self.selected_hw_mode else "white", font=ctk.CTkFont(size=11, weight="bold"), command=lambda m=mode_key: self.select_hardware_mode(m))
                btn.grid(row=0, column=idx, padx=3, pady=5)
                self.hw_buttons[mode_key] = btn

            probe_frame = ctk.CTkFrame(lab_left, fg_color="#1A1A1A", corner_radius=8)
            probe_frame.pack(anchor="w", pady=(0, 6))
            ctk.CTkButton(probe_frame, text="📸 Upload Board Photo", width=150, height=28, fg_color="#37474F", font=ctk.CTkFont(size=11, weight="bold"), command=self.action_upload_board_photo).grid(row=0, column=0, padx=5, pady=5)
            self.entry_voltage_probe = ctk.CTkEntry(probe_frame, width=390, height=28, placeholder_text="Multimeter / Symptom (e.g. 12V In / 0V Out, IC dead)...", fg_color="#2B2B2B", font=ctk.CTkFont(size=11))
            self.entry_voltage_probe.grid(row=0, column=1, padx=5, pady=5)

            ctk.CTkLabel(lab_left, text=t["ready_jobs"], font=ctk.CTkFont(size=12, weight="bold"), text_color="#00E676").pack(anchor="w", pady=(2, 2))
            self.ready_listbox = tk.Listbox(lab_left, width=74, height=3, bg="#1E1E1E", fg="white", bd=0, exportselection=False, font=("Helvetica", 10))
            self.ready_listbox.pack(anchor="w", pady=3)
            self.ready_listbox.bind('<<ListboxSelect>>', self.on_select_ready_job)

            self.status_frame = ctk.CTkFrame(lab_left, width=560, height=155, fg_color="#1A1A1A", corner_radius=8)
            self.status_frame.pack(anchor="w", pady=6)
            self.status_frame.pack_propagate(False)
            ctk.CTkLabel(self.status_frame, text=t["status"], font=ctk.CTkFont(size=12, weight="bold"), text_color="#FFB300").grid(row=0, column=0, padx=12, pady=(5, 2), sticky="w")
            self.lbl_status_text = ctk.CTkLabel(self.status_frame, text=t["status_idle"], font=ctk.CTkFont(size=11), justify="left", anchor="nw")
            self.lbl_status_text.grid(row=1, column=0, padx=12, pady=2, sticky="nw")

            lab_btns = ctk.CTkFrame(lab_left, fg_color="transparent")
            lab_btns.pack(anchor="w", pady=6)
            ctk.CTkButton(lab_btns, text=t["scan_btn"], fg_color="#2296F3", text_color="white", width=175, height=34, font=ctk.CTkFont(size=11, weight="bold"), command=self.simulate_usb_scan).pack(side="left", padx=(0, 6))
            ctk.CTkButton(lab_btns, text=t["final_sms_btn"], fg_color="#4CAF50", text_color="white", width=195, height=34, font=ctk.CTkFont(size=11, weight="bold"), command=self.action_send_final_sms).pack(side="left", padx=(0, 6))
            ctk.CTkButton(lab_btns, text="🗑️ Delete", fg_color="#D50000", text_color="white", width=95, height=34, font=ctk.CTkFont(size=11, weight="bold"), command=self.action_delete_ready_job).pack(side="left")

            lab_right = ctk.CTkFrame(lab_wrap, fg_color="#1A1A1A", corner_radius=8)
            lab_right.grid(row=0, column=1, padx=10, pady=10, sticky="nsew")
            hdr_lab = ctk.CTkFrame(lab_right, fg_color="transparent")
            hdr_lab.pack(fill="x", padx=12, pady=(8, 4))
            ctk.CTkLabel(hdr_lab, text="🗺️ PCB Fault Locator", font=ctk.CTkFont(size=13, weight="bold"), text_color="#00E676").pack(side="left")
            ctk.CTkButton(hdr_lab, text="🔍 Zoom Scan", width=105, height=26, fg_color="#2296F3", font=ctk.CTkFont(size=11, weight="bold"), command=self.action_open_fullscreen_ai_diag).pack(side="right")

            self.pcb_canvas = tk.Canvas(lab_right, width=320, height=310, bg="#0B3B24", highlightthickness=2, highlightbackground="#FFB300")
            self.pcb_canvas.pack(pady=8, padx=12)
            self.draw_base_pcb_map()
            self.lbl_pcb_coords = ctk.CTkLabel(lab_right, text="Awaiting AI Scan to pinpoint faulty IC / FET...", font=ctk.CTkFont(size=11), text_color="#B0BEC5")
            self.lbl_pcb_coords.pack(pady=5)

        elif page_key == "programmer":
            prog_wrap = ctk.CTkFrame(self.eng_content_area, fg_color="transparent")
            prog_wrap.pack(fill="both", expand=True, padx=12, pady=12)
            prog_wrap.grid_columnconfigure(0, weight=1)
            prog_wrap.grid_columnconfigure(1, weight=2)

            prog_left = ctk.CTkFrame(prog_wrap, fg_color="#1A1A1A", corner_radius=8)
            prog_left.grid(row=0, column=0, padx=(0, 10), pady=5, sticky="nsew")

            ctk.CTkLabel(prog_left, text="🧬 Universal IC & Mobile Lab", font=ctk.CTkFont(size=15, weight="bold"), text_color="#00E676").pack(anchor="w", padx=15, pady=(12, 6))
            ctk.CTkLabel(prog_left, text="🔍 Smart Auto-Detect (IC # or Phone):", font=ctk.CTkFont(size=11, weight="bold"), text_color="#FFB300").pack(anchor="w", padx=15, pady=(4, 2))

            detect_row = ctk.CTkFrame(prog_left, fg_color="transparent")
            detect_row.pack(anchor="w", padx=15, pady=4)
            self.entry_chip_part = ctk.CTkEntry(detect_row, width=180, placeholder_text="W25Q64, iPhone, Samsung...", fg_color="#2B2B2B")
            self.entry_chip_part.pack(side="left", padx=(0, 6))
            ctk.CTkButton(detect_row, text="Detect", width=75, fg_color="#2296F3", font=ctk.CTkFont(size=11, weight="bold"), command=self.action_auto_detect_chip).pack(side="left")

            ctk.CTkLabel(prog_left, text="Or Select Category Manually:", font=ctk.CTkFont(size=11)).pack(anchor="w", padx=15, pady=(8, 2))
            self.ic_family_menu = ctk.CTkOptionMenu(
                prog_left, width=265, button_color="#FFB300", text_color="black",
                values=[
                    "Smartphone USB Flash (MTK / Qualcomm / SPD)",
                    "Samsung Download Mode / Odin & Knox KG Guide",
                    "Apple iPhone / iPad USB Restore & DFU Mode",
                    "Keypad / Feature Phones (Itel / Nokia SPD & RDA)",
                    "Smartphone EasyBuy / MDM Clearance Protocol",
                    "SPI Flash / Laptop, TV & Inverter BIOS (25Qxx)",
                    "Serial EEPROM / TV & Car ECU (24Cxx / 93Cxx)",
                    "Microchip PIC / Atmel AVR MCU (PIC16F / ATmega)",
                    "ARM Cortex / STM32 / Charge Controller MCU",
                    "Inverter DSP & IGBT Gate Drivers (dsPIC / IR2110 / SG3525)",
                    "Smartphone eMMC / UFS Direct Chip-Off Repair"
                ],
                command=self.update_programmer_guide
            )
            self.ic_family_menu.pack(anchor="w", padx=15, pady=4)

            ctk.CTkButton(prog_left, text="📂 Load Firmware (.BIN / .HEX)", width=265, height=34, fg_color="#37474F", font=ctk.CTkFont(size=11, weight="bold"), command=self.action_load_firmware_file).pack(anchor="w", padx=15, pady=10)
            ctk.CTkButton(prog_left, text="⚡ Generate Wiring & Flash Guide", width=265, height=38, fg_color="#00E676", text_color="black", font=ctk.CTkFont(weight="bold"), command=lambda: self.update_programmer_guide(self.ic_family_menu.get())).pack(anchor="w", padx=15, pady=4)

            prog_right = ctk.CTkFrame(prog_wrap, fg_color="#1A1A1A", corner_radius=8)
            prog_right.grid(row=0, column=1, padx=(10, 0), pady=5, sticky="nsew")
            ctk.CTkLabel(prog_right, text="🛠️ Required Tools, USB/Pinout Wiring & Safety Protocol:", font=ctk.CTkFont(size=13, weight="bold"), text_color="#FFB300").pack(anchor="w", padx=15, pady=(12, 6))

            self.txt_prog_guide = tk.Text(prog_right, bg="#111111", fg="#E0F2F1", bd=0, font=("Consolas", 10))
            self.txt_prog_guide.pack(padx=15, pady=(4, 15), fill="both", expand=True)
            self.update_programmer_guide("Smartphone USB Flash (MTK / Qualcomm / SPD)")

        elif page_key == "history":
            hist_wrap = ctk.CTkFrame(self.eng_content_area, fg_color="transparent")
            hist_wrap.pack(fill="both", expand=True, padx=15, pady=15)
            hist_wrap.grid_columnconfigure(0, weight=1)
            hist_wrap.grid_columnconfigure(1, weight=1)

            hist_left = ctk.CTkFrame(hist_wrap, fg_color="transparent")
            hist_left.grid(row=0, column=0, padx=10, pady=5, sticky="nsew")
            ctk.CTkLabel(hist_left, text="📚 Completed Repairs Archive (History):", font=ctk.CTkFont(size=14, weight="bold"), text_color="#FFB300").pack(anchor="w", pady=(0, 8))
            search_row = ctk.CTkFrame(hist_left, fg_color="transparent")
            search_row.pack(anchor="w", pady=(0, 6))
            self.entry_hist_search = ctk.CTkEntry(search_row, width=265, placeholder_text="🔍 Search Name, Phone, or Ticket #...")
            self.entry_hist_search.pack(side="left", padx=(0, 6))
            ctk.CTkButton(search_row, text="Search", width=85, fg_color="#2296F3", font=ctk.CTkFont(weight="bold"), command=self.action_filter_history_list).pack(side="left")

            self.history_listbox = tk.Listbox(hist_left, width=48, height=13, bg="#1E1E1E", fg="white", bd=0, exportselection=False, font=("Helvetica", 11))
            self.history_listbox.pack(anchor="w", pady=5)
            self.history_listbox.bind('<<ListboxSelect>>', self.on_select_history_job)

            btn_row = ctk.CTkFrame(hist_left, fg_color="transparent")
            btn_row.pack(anchor="w", pady=10)
            ctk.CTkButton(btn_row, text="👁️ Preview", fg_color="#9C27B0", text_color="white", width=105, height=38, font=ctk.CTkFont(weight="bold"), command=self.action_trigger_print_view).pack(side="left", padx=(0, 8))
            ctk.CTkButton(btn_row, text="📄 Export PDF", fg_color="#2296F3", text_color="white", width=115, height=38, font=ctk.CTkFont(weight="bold"), command=self.action_export_receipt_pdf).pack(side="left", padx=(0, 8))
            ctk.CTkButton(btn_row, text="🖨️ Print Now", fg_color="#00E676", text_color="black", width=115, height=38, font=ctk.CTkFont(weight="bold"), command=self.action_direct_print_receipt).pack(side="left")

            self.lbl_print_status = ctk.CTkLabel(hist_left, text="", font=ctk.CTkFont(size=12, weight="bold"), text_color="#00E676")
            self.lbl_print_status.pack(anchor="w", pady=4)

            hist_right = ctk.CTkFrame(hist_wrap, width=380, height=430, fg_color="#F5F5F5", corner_radius=6)
            hist_right.grid(row=0, column=1, padx=10, pady=5, sticky="ne")
            hist_right.pack_propagate(False)
            self.txt_receipt = tk.Text(hist_right, width=44, height=22, bg="#F5F5F5", fg="black", bd=0, font=("Courier", 10))
            self.txt_receipt.pack(pady=10, padx=10)
            self.txt_receipt.insert(tk.END, "Select a completed job from History on the left\nto preview, export PDF, or send to Printer.")

        elif page_key == "pcb_studio":
            studio_wrap = ctk.CTkFrame(self.eng_content_area, fg_color="transparent")
            studio_wrap.pack(fill="both", expand=True, padx=10, pady=10)
            studio_wrap.grid_columnconfigure(0, weight=2)
            studio_wrap.grid_columnconfigure(1, weight=3)

            st_left = ctk.CTkFrame(studio_wrap, fg_color="#1A1A1A", corner_radius=8)
            st_left.grid(row=0, column=0, padx=(0, 8), pady=4, sticky="nsew")

            ctk.CTkLabel(st_left, text="📐 Custom Circuit & PCB Generator", font=ctk.CTkFont(size=14, weight="bold"), text_color="#FFB300").pack(anchor="w", padx=12, pady=(10, 4))
            top_ctrl = ctk.CTkFrame(st_left, fg_color="transparent")
            top_ctrl.pack(anchor="w", padx=12, pady=4)
            self.entry_pcb_design = ctk.CTkEntry(top_ctrl, width=155, placeholder_text="Inverter, MPPT, ATS...", fg_color="#2B2B2B")
            self.entry_pcb_design.pack(side="left", padx=(0, 5))
            ctk.CTkButton(top_ctrl, text="⚡ Generate", width=95, fg_color="#00E676", text_color="black", font=ctk.CTkFont(weight="bold"), command=self.action_generate_custom_pcb).pack(side="left", padx=(0, 5))
            ctk.CTkButton(top_ctrl, text="💾 Export PCB", width=95, fg_color="#FFB300", text_color="black", font=ctk.CTkFont(weight="bold"), command=self.action_export_pcb_manufacturing_files).pack(side="left")

            self.pcb_preset_menu = ctk.CTkOptionMenu(
                st_left, width=355, button_color="#2296F3",
                values=[
                    "Pure Sine Wave Inverter Board (12V/24V to 220V)",
                    "MPPT / PWM Solar Charge Controller Board (12V/24V 60A)",
                    "Smart 3-Stage 12V/24V Lead-Acid & Lithium Battery Charger",
                    "Automatic Changeover / ATS Relay Control Board",
                    "12V / 5V High-Current SMPS Power Supply Board"
                ],
                command=self.action_generate_custom_pcb
            )
            self.pcb_preset_menu.pack(anchor="w", padx=12, pady=6)

            self.txt_pcb_steps = tk.Text(st_left, bg="#111111", fg="#E0F2F1", bd=0, font=("Consolas", 9), height=16)
            self.txt_pcb_steps.pack(fill="both", expand=True, padx=12, pady=(4, 10))

            st_right = ctk.CTkFrame(studio_wrap, fg_color="#1A1A1A", corner_radius=8)
            st_right.grid(row=0, column=1, padx=(8, 0), pady=4, sticky="nsew")
            hdr_r = ctk.CTkFrame(st_right, fg_color="transparent")
            hdr_r.pack(fill="x", padx=12, pady=(8, 2))
            ctk.CTkLabel(hdr_r, text="🖼️ PCB Blueprint:", font=ctk.CTkFont(size=12, weight="bold"), text_color="#00E676").pack(side="left", padx=(0, 10))
            ctk.CTkButton(hdr_r, text="🔍 Zoom Full Screen", width=135, height=26, fg_color="#2296F3", font=ctk.CTkFont(size=11, weight="bold"), command=self.action_open_fullscreen_pcb).pack(side="left")

            self.studio_canvas = tk.Canvas(st_right, width=440, height=340, bg="#052214", highlightthickness=2, highlightbackground="#FFB300")
            self.studio_canvas.pack(padx=10, pady=6, fill="both", expand=True)
            self.action_generate_custom_pcb("Pure Sine Wave Inverter Board (12V/24V to 220V)")

        self.refresh_all_engineer_lists()

    def refresh_all_engineer_lists(self):
        self.pending_jobs_cache = [item for item in SUNVOLT_JOB_QUEUE if item.get("status") == "Pending"]
        self.ready_jobs_cache = [item for item in SUNVOLT_JOB_QUEUE if item.get("status") == "Approved"]
        if hasattr(self, 'pending_listbox') and self.pending_listbox.winfo_exists():
            self.pending_listbox.delete(0, tk.END)
            for item in self.pending_jobs_cache:
                dep = item.get('deposit', 0.0)
                dep_tag = f"Deposit: ₦{dep:,.0f}" if dep > 0 else "No Deposit"
                self.pending_listbox.insert(tk.END, f"#{item['ticket_id']} | {item['model']} ({item['customer']}) — {dep_tag} | Fault: {item['fault']}")
        if hasattr(self, 'ready_listbox') and self.ready_listbox.winfo_exists():
            self.ready_listbox.delete(0, tk.END)
            for item in self.ready_jobs_cache:
                self.ready_listbox.insert(tk.END, f"#{item['ticket_id']} | {item['model']} — Quote: ₦{item['quote']:,}")
        if hasattr(self, 'history_listbox') and self.history_listbox.winfo_exists():
            self.history_listbox.delete(0, tk.END)
            for item in SUNVOLT_HISTORY_ARCHIVE:
                self.history_listbox.insert(tk.END, f"#{item['ticket_id']} | {item['model']} ({item['customer']}) — ₦{item['quote']:,}")

    def on_select_pending_job(self, event):
        sel = self.pending_listbox.curselection()
        if sel:
            self.selected_pending_job = self.pending_jobs_cache[sel[0]]
            j = self.selected_pending_job
            self.active_workbench_ticket_id = j["ticket_id"]
            self.lbl_intake_details.configure(
                text=f"🔧 ACTIVE ON WORKBENCH #{j['ticket_id']}: {j['model']} | Customer: {j['customer']} ({j['phone']}) | Fault: {j['fault']}",
                text_color="#00E676"
            )
            self.refresh_reception_status_list()

    def on_select_ready_job(self, event):
        sel = self.ready_listbox.curselection()
        if sel:
            self.selected_ready_job = self.ready_jobs_cache[sel[0]]
            j = self.selected_ready_job
            self.active_workbench_ticket_id = j["ticket_id"]
            if hasattr(self, 'lbl_status_text'):
                self.lbl_status_text.configure(
                    text=f"🔧 ACTIVE DEVICE ON WORKBENCH: #{j['ticket_id']} — {j['model']} ({j['customer']})\n• Reported Fault: {j['fault']} | Approved Quote: ₦{j['quote']:,.0f}\n• Danna 'AI Scan' don duba wannan na'urar kafin na gaba.",
                    text_color="#64FFDA"
                )
            self.refresh_reception_status_list()
    def action_filter_history_list(self):
        q = self.entry_hist_search.get().strip().lower()
        self.history_listbox.delete(0, tk.END)
        self.filtered_history_cache = []
        for item in SUNVOLT_HISTORY_ARCHIVE:
            blob = f"{item['ticket_id']} {item['customer']} {item['phone']} {item['model']}".lower()
            if not q or q in blob:
                self.filtered_history_cache.append(item)
                self.history_listbox.insert(tk.END, f"#{item['ticket_id']} | {item['model']} ({item['customer']}) — ₦{item['quote']:,}")

    def on_select_history_job(self, event):
        sel = self.history_listbox.curselection()
        if sel:
            j = SUNVOLT_HISTORY_ARCHIVE[sel]
            self.selected_history_job = j
            receipt = (
                "==========================================\n"
                "     SUNVOLT TECH HUB — KASHERE, GOMBE    \n"
                "==========================================\n"
                f"Ticket ID:   {j['ticket_id']}\n"
                f"Customer:    {j['customer']} ({j['phone']})\n"
                f"Device:      {j['model']}\n"
                f"Fault Fixed: {j['fault']}\n"
                f"Total Paid:  NGN {j['quote']:,.2f}\n"
                "Status:      COMPLETED & TESTED OK\n"
                "==========================================\n"
                "   Thank you for trusting Sunvolt Tech!   \n"
            )
            self.txt_receipt.delete("1.0", tk.END)
            self.txt_receipt.insert(tk.END, receipt)

    def action_engineer_set_price(self):
        if not hasattr(self, 'selected_pending_job'):
            if getattr(self, 'pending_jobs_cache', None):
                self.selected_pending_job = self.pending_jobs_cache
            else:
                return
        try:
            price = float(self.entry_final_cost.get().strip())
        except ValueError:
            self.lbl_intake_details.configure(text="⚠️ Shigar da lambar kuɗi mai kyau (e.g. 15000)!", text_color="#FF3D00")
            return
        j = self.selected_pending_job
        j["quote"] = price
        j["status"] = "Approved"
        self.entry_final_cost.delete(0, tk.END)
        self.refresh_all_engineer_lists()
        self.lbl_intake_details.configure(text=f"✅ An tsaida ₦{price:,.0f} don #{j['ticket_id']} kuma an tura SMS ga {j['customer']}!", text_color="#00E676")
        delattr(self, 'selected_pending_job')

    def action_engineer_reject_job(self):
        if not hasattr(self, 'selected_pending_job'):
            if getattr(self, 'pending_jobs_cache', None):
                self.selected_pending_job = self.pending_jobs_cache
            else:
                return
        j = self.selected_pending_job
        reason = self.entry_reject_reason.get().strip() or "Unrepairable Board"
        j["status"] = "Rejected"
        j["reject_reason"] = reason
        self.entry_reject_reason.delete(0, tk.END)
        self.refresh_all_engineer_lists()
        self.lbl_intake_details.configure(text=f"❌ REJECTED #{j['ticket_id']}: {reason} (An mayar allon Reception).", text_color="#FF5252")
        delattr(self, 'selected_pending_job')

    def action_delete_pending_job(self):
        if not hasattr(self, 'selected_pending_job'):
            if getattr(self, 'pending_jobs_cache', None):
                self.selected_pending_job = self.pending_jobs_cache
            else:
                return
        j = self.selected_pending_job
        if j in SUNVOLT_JOB_QUEUE:
            SUNVOLT_JOB_QUEUE.remove(j)
        self.refresh_all_engineer_lists()
        self.lbl_intake_details.configure(text=f"🗑️ An goge #{j['ticket_id']} daga jerin ayyuka.", text_color="#FF9100")
        delattr(self, 'selected_pending_job')

    def action_delete_ready_job(self):
        if not hasattr(self, 'selected_ready_job'):
            if getattr(self, 'ready_jobs_cache', None):
                self.selected_ready_job = self.ready_jobs_cache
            else:
                return
        j = self.selected_ready_job
        if j in SUNVOLT_JOB_QUEUE:
            SUNVOLT_JOB_QUEUE.remove(j)
        self.refresh_all_engineer_lists()
        self.lbl_status_text.configure(text=f"🗑️ An goge #{j['ticket_id']} daga Lab.", text_color="#FF9100")
        delattr(self, 'selected_ready_job')

    def select_hardware_mode(self, mode_key):
        self.selected_hw_mode = mode_key
        for k, btn in self.hw_buttons.items():
            btn.configure(fg_color="#FFB300" if k == mode_key else "#2B2B2B", text_color="black" if k == mode_key else "white")

    def action_upload_board_photo(self):
        path = filedialog.askopenfilename(title="Select Board Photo", filetypes=[("Images", "*.png *.jpg *.jpeg")])
        if path:
            self.board_image_path = path
            self.lbl_status_text.configure(text=f"📸 Loaded Board Photo: {os.path.basename(path)}\nRubuta aunin Multimeter a sama sannan ka danna 'AI Scan'.", text_color="#64FFDA")
    def action_open_fullscreen_ai_diag(self):
        win = ctk.CTkToplevel(self)
        win.title("SUNVOLT AI DIAGNOSTICS — FULL SCREEN PCB & REPORT VIEW")
        win.geometry("960x620")
        win.attributes("-topmost", True)
        win.grid_columnconfigure(0, weight=1)
        win.grid_columnconfigure(1, weight=1)
        win.grid_rowconfigure(0, weight=1)

        live_text = self.lbl_status_text.cget("text") if hasattr(self, 'lbl_status_text') else ""
        info = getattr(self, 'last_ai_diag_data', None)
        if not info and live_text and "System idle" not in live_text and "A shirye don bincike" not in live_text:
            info = {"hx": 160, "hy": 140, "part": "AI FAULT SCAN", "ref": "PCB-TARGET", "meter": "ANALYZED", "report": live_text}
        elif not info:
            info = {"hx": None, "hy": None, "part": "", "ref": "", "meter": "", "report": live_text or "Danna 'AI Scan' da farko don ganin cikakken rahoto."}

        big_c = tk.Canvas(win, width=460, height=580, bg="#062918", highlightthickness=2, highlightbackground="#FFB300")
        big_c.grid(row=0, column=0, padx=12, pady=12, sticky="nsew")
        self.draw_base_pcb_map(info["hx"], info["hy"], info["part"], info["ref"], info["meter"], target_canvas=big_c, w=460, h=580)

        txt_full = tk.Text(win, bg="#111111", fg="#E0F2F1", font=("Consolas", 11), wrap="word", bd=0)
        txt_full.grid(row=0, column=1, padx=(0, 12), pady=12, sticky="nsew")
        txt_full.insert(tk.END, info["report"])

    def draw_base_pcb_map(self, hx=None, hy=None, part_code="", board_ref="", meter_val="", target_canvas=None, w=320, h=310):
        c = target_canvas if target_canvas else getattr(self, 'pcb_canvas', None)
        if not c:
            return
        sx, sy = w / 320.0, h / 310.0
        c.delete("all")
        c.configure(bg="#062918")
        c.create_rectangle(6*sx, 6*sy, 314*sx, 304*sy, outline="#FFB300", width=2)
        for i in range(20, 305, 22):
            c.create_line(10*sx, i*sy, 310*sx, i*sy, fill="#0D4228", width=1)
            c.create_line(i*sx, 10*sy, i*sx, 300*sy, fill="#0D4228", width=1)

        c.create_rectangle(22*sx, 25*sy, 95*sx, 85*sy, fill="#1B2631", outline="#40C4FF", width=1)
        c.create_text(58*sx, 55*sy, text="F1 / D1\nPOWER IN", fill="#40C4FF", font=("Arial", 7, "bold"))

        c.create_rectangle(115*sx, 95*sy, 205*sx, 185*sy, fill="#111827", outline="#FFB300", width=2)
        c.create_text(160*sx, 140*sy, text="U1: MAIN CPU /\nPWM CONTROLLER", fill="#FFB300", font=("Arial", 7, "bold"))

        c.create_rectangle(215*sx, 35*sy, 295*sx, 125*sy, fill="#1C2833", outline="#00E676", width=1)
        c.create_text(255*sx, 80*sy, text="Q1-Q4: FET /\nDRIVER BANK", fill="#00E676", font=("Arial", 7, "bold"))

        c.create_rectangle(25*sx, 200*sy, 120*sx, 275*sy, fill="#1C2833", outline="#CE93D8", width=1)
        c.create_text(72*sx, 237*sy, text="U2: BIOS / PMIC\n& 3.3V RAIL", fill="#CE93D8", font=("Arial", 7, "bold"))

        c.create_rectangle(195*sx, 200*sy, 295*sx, 275*sy, fill="#1C2833", outline="#FFAB40", width=1)
        c.create_text(245*sx, 237*sy, text="L1 / C1-C4\nOUTPUT STAGE", fill="#FFAB40", font=("Arial", 7, "bold"))

        c.create_line(95*sx, 55*sy, 160*sx, 55*sy, 160*sx, 95*sy, fill="#FF5252", width=2)
        c.create_line(205*sx, 120*sy, 255*sx, 120*sy, 255*sx, 125*sy, fill="#00E676", width=2)
        c.create_line(115*sx, 160*sy, 72*sx, 160*sy, 72*sx, 200*sy, fill="#CE93D8", width=2)
        c.create_line(160*sx, 185*sy, 160*sx, 237*sy, 195*sx, 237*sy, fill="#FFAB40", width=2)

        if hx and hy:
            c.create_oval((hx-32)*sx, (hy-32)*sy, (hx+32)*sx, (hy+32)*sy, outline="#FF1744", width=3)
            c.create_oval((hx-12)*sx, (hy-12)*sy, (hx+12)*sx, (hy+12)*sy, fill="#D50000", outline="#FFEB3B", width=2)
            box_y = (268 if hy < 180 else 18) * sy
            c.create_rectangle(14*sx, box_y, 306*sx, box_y + 30*sy, fill="#B71C1C", outline="#FFEB3B", width=1)
            c.create_text(160*sx, box_y + 15*sy, text=f"FAULT [{board_ref}]: {part_code} | {meter_val}", fill="#FFEB3B", font=("Arial", 7, "bold"))

    def simulate_usb_scan(self):
        probe = (self.entry_voltage_probe.get().strip() if hasattr(self, 'entry_voltage_probe') else "").lower()
        mode = self.selected_hw_mode
        api_key = os.environ.get("GEMINI_API_KEY", "").strip()
        if getattr(self, 'board_image_path', None) and os.path.exists(self.board_image_path) and api_key:
            try:
                from google import genai
                from PIL import Image
                self.lbl_status_text.configure(text="⏳ Gemini Vision AI na duba hoton katin (Scanning every SMD component)...", text_color="#64FFDA")
                self.update_idletasks()
                client = genai.Client(api_key=api_key)
                img = Image.open(self.board_image_path)
                prompt = (
                    f"You are an expert hardware repair engineer inspecting a {mode} PCB photo. "
                    f"Technician multimeter/symptom note: '{probe or 'Visual & fault inspection'}'. "
                    "Identify every visible burnt, cracked, shorted, or suspect component (ICs, Mosfets, SMD resistors, capacitors, diodes, traces). "
                    "Give exact part codes, board reference numbers (e.g., Q1, R12, U4), expected multimeter readings, and step-by-step fix instructions concisely."
                )
                response = client.models.generate_content(model="gemini-2.5-flash", contents=[img, prompt])
                ai_reply = response.text.strip()
                self.draw_base_pcb_map(160, 140, "AI VISION SCAN", "PHOTO-PCB", "VERIFIED")
                if hasattr(self, 'lbl_pcb_coords'):
                    self.lbl_pcb_coords.configure(text="📸 Gemini Vision AI: Complete Board Photo Analyzed!", text_color="#00E676")
                self.lbl_status_text.configure(text=ai_reply[:650], text_color="#00E676")
                return
            except Exception as e:
                self.lbl_status_text.configure(text=f"⚠️ Offline Fallback ({e}): Running local database...", text_color="#FF9100")

        if mode == "Inverter":
            if "overload" in probe or "beep" in probe or "feedback" in probe:
                hx, hy, ref, part, meter = 160, 140, "U3 / R14", "LM358 Op-Amp & 0.01Ω Shunt", "Pin 1 High (4.8V)"
                diag = "Overload / Short-Circuit Sense Fault: LM358 comparator or current shunt resistor drifted."
                steps = "1. Replace LM358 (U3) & check 10kΩ feedback resistors.\n2. Verify 2.5V reference on Pin 3 before loading."
            elif "no wave" in probe or "0v" in probe or "driver" in probe:
                hx, hy, ref, part, meter = 160, 140, "U1 (EGS002)", "EG8010 + IR2110 SPWM Module", "0V AC / No 50Hz Gate"
                diag = "SPWM Driver Failure: EGS002 oscillator dead or 5V/12V supply missing."
                steps = "1. Check 12V & 5V pins on EGS002 header.\n2. Replace EGS002 board & inspect 10Ω gate resistors."
            else:
                hx, hy, ref, part, meter = 255, 80, "Q1-Q8 / U4", "IRF3205 / HY4008 Mosfet + IR2110", "0.00Ω Drain-Source Short"
                diag = "H-Bridge Power Stage Short: Blown N-Channel Mosfets & damaged IR2110 gate driver."
                steps = "1. Desolder all shorted IRF3205/HY4008 Mosfets.\n2. Replace IR2110 driver & burnt 10Ω gate resistors first!"

        elif mode == "Laptop":
            if "bios" in probe or "no display" in probe or "fan" in probe:
                hx, hy, ref, part, meter = 72, 237, "U12 (SOIC-8)", "Winbond W25Q64FV BIOS IC", "3.3V OK / Corrupt Data"
                diag = "Corrupted SPI BIOS Firmware: Board powers on (fan spins) but fails POST/Display."
                steps = "1. Desolder W25Q64 (U12) & backup old dump.\n2. Flash verified .BIN firmware in Tab 3 (IC Programmer)."
            elif "charge" in probe or "battery" in probe or "19v" in probe:
                hx, hy, ref, part, meter = 58, 55, "PQ1 / PU4", "BQ24780S Charging IC & Input FET", "19V Blocked at 2nd FET"
                diag = "19V Input Rail Blocked: Shorted input Mosfet or dead BQ24780S charge controller."
                steps = "1. Check ACDET (2.6V) & CMSRC on BQ24780S.\n2. Replace shorted N-Channel input Mosfet."
            else:
                hx, hy, ref, part, meter = 72, 237, "PU5 (TPS51125)", "3.3V / 5V Always-On Step-Down IC", "0V on L3/L5 Coils"
                diag = "Dead Motherboard (No 3.3V/5V ALW): Primary step-down PWM controller or filter cap shorted."
                steps = "1. Inject 1V on 3.3V coil to find hot tantalum capacitor.\n2. Replace TPS51125 PWM controller IC."

        elif mode == "Charge_Controller":
            if "overcharge" in probe or "high" in probe or "16v" in probe:
                hx, hy, ref, part, meter = 255, 80, "Q1, Q2", "IRF3205 / STP80NF70 Buck Mosfets", "Gate-Drain Leaking"
                diag = "Uncontrolled Battery Overcharging: Buck switching Mosfets shorted straight through."
                steps = "1. Replace shorted Buck Mosfets (Q1/Q2) & IR2104 driver.\n2. Check voltage divider resistors (100kΩ / 10kΩ) to MCU."
            else:
                hx, hy, ref, part, meter = 58, 55, "F1 / D2 / U1", "60A Blade Fuse, MBR20100 & LM2596", "0V LCD / Reverse Polarity"
                diag = "Dead Charge Controller: Blown input protection diode/fuse or dead 5V buck regulator."
                steps = "1. Replace 60A fuse & shorted Schottky diode.\n2. Verify 5.0V output from LM2596 to PIC/STM32 MCU."

        elif mode == "Sewing_Machine":
            hx, hy, ref, part, meter = 255, 80, "IPM1 / Q3", "FSBB20CH60 IGBT Module & 310V Bus", "Short on U/V/W Motor Pins"
            diag = "Servo Motor Driver Fault: Blown 3-phase IGBT module or burnt 22Ω emitter shunt."
            steps = "1. Check 310V DC on main 450V capacitor.\n2. Replace IGBT module & optical gate drivers (TLP250)."

        else:  # Phone / Universal
            if "charge" in probe or "usb" in probe or "not charging" in probe:
                hx, hy, ref, part, meter = 58, 55, "U401 / OVP", "BQ25601 / SMB1351 Charging IC", "5.1V In / 0.0A Bat"
                diag = "Charging Circuit Fault: Damaged OVP protection IC or BQ25601 charge manager."
                steps = "1. Bypass or replace OVP 9-ball IC near USB flex.\n2. Replace BQ25601 Charging IC & check VBUS line."
            elif "network" in probe or "sim" in probe or "service" in probe:
                hx, hy, ref, part, meter = 245, 237, "U802 / PA", "WTR2965 RF Transceiver & 4G PA", "No Baseband / 1.8V Low"
                diag = "RF / Baseband Failure: Cracked solder joints under WTR2965 or dead Power Amplifier."
                steps = "1. Check 1.0V & 1.8V RF supply caps around WTR2965.\n2. Reball or replace WTR2965 RF IC."
            else:
                hx, hy, ref, part, meter = 72, 237, "U201 (PMIC)", "MT6357CRV / PM8953 Power IC", "VPH_PWR Short (0.04Ω)"
                diag = "Dead Boot / Primary Short: Shorted capacitor on VPH_PWR rail or dead PMIC."
                steps = "1. Apply rosin smoke & inject 3.8V/2A on VPH_PWR to spot hot cap.\n2. Replace shorted filter cap or reball/replace PMIC."

        self.draw_base_pcb_map(hx, hy, part, ref, meter)
        if hasattr(self, 'lbl_pcb_coords'):
            self.lbl_pcb_coords.configure(text=f"📍 Board Ref: {ref} | Part: {part}\n⚡ Multimeter: {meter}", text_color="#FFEB3B")

        report = (
            f"[AI DIAGNOSTICS — {mode.upper()}] Symptom: {probe or 'Full Board Scan'}\n"
            f"• Faulty Part: {part} (Location: {ref})\n"
            f"• Root Cause:  {diag}\n"
            f"• Fix Steps:\n{steps}"
        )
        self.lbl_status_text.configure(text=report, text_color="#00E676")

    def action_send_final_sms(self):
        if not hasattr(self, 'selected_ready_job'):
            if getattr(self, 'ready_jobs_cache', None):
                self.selected_ready_job = self.ready_jobs_cache
            else:
                return
        j = self.selected_ready_job
        j["status"] = "Completed"
        earned = float(j["quote"])
        SUNVOLT_ADMIN_FINANCES["total_revenue"] += earned
        SUNVOLT_ADMIN_FINANCES["total_profit"] += (earned * 0.20)
        SUNVOLT_ADMIN_FINANCES["total_completed"] += 1
        SUNVOLT_JOB_QUEUE.remove(j)
        SUNVOLT_HISTORY_ARCHIVE.append(j)
        self.refresh_all_engineer_lists()
        self.lbl_status_text.configure(text=f"✅ COMPLETED #{j['ticket_id']}! An tura SMS na ƙarshe ga {j['customer']} ({j['phone']}).", text_color="#00E676")
        delattr(self, 'selected_ready_job')

    # ==================== 3. IC PROGRAMMER & PCB STUDIO ====================
    def action_auto_detect_chip(self):
        q = self.entry_chip_part.get().strip().lower()
        if not q:
            return
        if any(k in q for k in ["iphone", "ipad", "apple", "ios"]):
            cat = "Apple iPhone / iPad USB Restore & DFU Mode"
        elif any(k in q for k in ["samsung", "galaxy", "odin", "knox"]):
            cat = "Samsung Download Mode / Odin & Knox KG Guide"
        elif any(k in q for k in ["keypad", "itel 2160", "nokia 105", "feature"]):
            cat = "Keypad / Feature Phones (Itel / Nokia SPD & RDA)"
        elif any(k in q for k in ["25q", "bios", "winbond", "tv"]):
            cat = "SPI Flash / Laptop, TV & Inverter BIOS (25Qxx)"
        elif any(k in q for k in ["24c", "93c", "eeprom", "ecu"]):
            cat = "Serial EEPROM / TV & Car ECU (24Cxx / 93Cxx)"
        elif any(k in q for k in ["pic", "avr", "atmega"]):
            cat = "Microchip PIC / Atmel AVR MCU (PIC16F / ATmega)"
        elif any(k in q for k in ["stm32", "arm"]):
            cat = "ARM Cortex / STM32 / Charge Controller MCU"
        elif any(k in q for k in ["dspic", "eg8010", "ir2110", "sg3525", "igbt"]):
            cat = "Inverter DSP & IGBT Gate Drivers (dsPIC / IR2110 / SG3525)"
        else:
            cat = "Smartphone USB Flash (MTK / Qualcomm / SPD)"
        self.ic_family_menu.set(cat)
        self.update_programmer_guide(cat)

    def update_programmer_guide(self, ic_type):
        chip = self.entry_chip_part.get().strip() if hasattr(self, 'entry_chip_part') and self.entry_chip_part.get().strip() else "Target Device / IC"
        guides = {
            "Smartphone USB Flash (MTK / Qualcomm / SPD)": f"TARGET PHONE: {chip}\n1. TOOLS: USB Cable + PC + UnlockTool / SP Flash Tool\n2. BOOT: Hold Vol+ & Vol- -> Plug USB -> Click Flash.",
            "Samsung Download Mode / Odin & Knox KG Guide": f"TARGET SAMSUNG: {chip}\n1. TOOLS: Odin3 v3.14 + SamFw Tool\n2. DOWNLOAD MODE: Hold Vol+ & Vol- -> Plug USB -> Press Vol+.",
            "Apple iPhone / iPad USB Restore & DFU Mode": f"TARGET APPLE: {chip}\n1. TOOLS: Lightning/Type-C Cable + 3uTools / iTunes\n2. RECOVERY: Quick Vol+, quick Vol-, hold Power until PC icon.",
            "Keypad / Feature Phones (Itel / Nokia SPD & RDA)": f"TARGET KEYPAD: {chip}\n1. TOOLS: Miracle Box / CM2 SPD\n2. BOOT: Hold Center OK or '0' -> Plug USB -> Read/Format.",
            "Smartphone EasyBuy / MDM Clearance Protocol": f"TARGET MDM: {chip}\n1. Connect Wi-Fi after full payment for OTA unlock.\n2. Flash stock ROM only after verifying receipt.",
            "SPI Flash / Laptop, TV & Inverter BIOS (25Qxx)": f"TARGET SPI: {chip}\n1. TOOLS: CH341A / XGecu T48 + SOIC8 Clip\n2. PINOUT: 1:CS | 2:MISO | 4:GND | 5:MOSI | 8:3.3V.",
            "Serial EEPROM / TV & Car ECU (24Cxx / 93Cxx)": f"TARGET EEPROM: {chip}\n1. TOOLS: XGecu T48 / RT809H\n2. PINOUT: 4:GND | 5:SDA | 6:SCL | 8:5V.",
            "Microchip PIC / Atmel AVR MCU (PIC16F / ATmega)": f"TARGET MCU: {chip}\n1. TOOLS: PICkit 3 / USBasp\n2. ICSP: 1:MCLR | 2:5V | 3:GND | 4:PGD | 5:PGC.",
            "ARM Cortex / STM32 / Charge Controller MCU": f"TARGET ARM: {chip}\n1. TOOLS: ST-Link V2\n2. SWD: SWDIO, SWCLK, GND, 3.3V -> Flash via STM32Cube.",
            "Inverter DSP & IGBT Gate Drivers (dsPIC / IR2110 / SG3525)": f"TARGET INVERTER: {chip}\n1. Check SG3525 PWM & IR2110 gate drivers + 10R resistors before replacing blown Mosfets/IGBTs.",
            "Smartphone eMMC / UFS Direct Chip-Off Repair": f"TARGET BGA: {chip}\n1. TOOLS: EasyJTAG Plus / UFI Box -> Solder CLK, CMD, DAT0, GND."
        }
        if hasattr(self, 'txt_prog_guide'):
            self.txt_prog_guide.delete("1.0", tk.END)
            self.txt_prog_guide.insert(tk.END, guides.get(ic_type, ""))

    def render_detailed_pcb_on_canvas(self, c, w, h, title, mode):
        c.delete("all")
        c.configure(bg="#052214")
        c.create_rectangle(8, 8, w-8, h-8, outline="#FFB300", width=2)
        for gx in range(20, w-15, 18):
            c.create_line(gx, 12, gx, h-12, fill="#0A3620", width=1)
        for gy in range(20, h-15, 18):
            c.create_line(12, gy, w-12, gy, fill="#0A3620", width=1)
        for hx, hy in [(18, 18), (w-18, 18), (18, h-18), (w-18, h-18)]:
            c.create_oval(hx-5, hy-5, hx+5, hy+5, fill="#020D08", outline="#FFB300", width=2)

        c.create_text(w//2, 22, text=title, fill="#64FFDA", font=("Arial", 9, "bold"))
        c.create_line(28, 42, w-28, 42, fill="#FF5252", width=3)
        c.create_text(58, 33, text="+12V/+24V VCC TRACK", fill="#FF5252", font=("Arial", 7, "bold"))
        c.create_line(28, h-32, w-28, h-32, fill="#40C4FF", width=3)
        c.create_text(52, h-21, text="GND COPPER PLANE", fill="#40C4FF", font=("Arial", 7, "bold"))

        ic_x1, ic_y1, ic_x2, ic_y2 = 38, 85, 102, h-75
        c.create_rectangle(ic_x1, ic_y1, ic_x2, ic_y2, fill="#111827", outline="white", width=2)
        ic_name = "U1:EG8010" if mode == "inverter" else ("U1:STM32" if mode == "mppt" else ("U1:UC3842" if mode == "charger" else "U1:NE555"))
        c.create_text((ic_x1+ic_x2)//2, (ic_y1+ic_y2)//2, text=ic_name, fill="#FFB300", font=("Arial", 8, "bold"), angle=90)

        step_y = max(22, (ic_y2 - ic_y1 - 20) // 6)
        for idx in range(6):
            py = ic_y1 + 15 + (idx * step_y)
            c.create_oval(ic_x1-7, py-3, ic_x1, py+3, fill="#FFB300", outline="")
            c.create_oval(ic_x2, py-3, ic_x2+7, py+3, fill="#FFB300", outline="")
            c.create_line(ic_x2+7, py, ic_x2+35, py, fill="#00E676", width=2)
            rx1, rx2 = ic_x2+35, ic_x2+65
            c.create_rectangle(rx1, py-5, rx2, py+5, fill="#D7CCC8", outline="#FFB300")
            c.create_line(rx1+6, py-5, rx1+6, py+5, fill="#D50000", width=2)
            c.create_line(rx1+14, py-5, rx1+14, py+5, fill="#1A237E", width=2)
            c.create_line(rx1+22, py-5, rx1+22, py+5, fill="#FFB300", width=2)
            c.create_text((rx1+rx2)//2, py-10, text=f"R{idx+1}:10Ω", fill="white", font=("Arial", 6))
            c.create_line(rx2, py, rx2+32, py, fill="#00E676", width=2)
            c.create_oval(rx2+30, py-3, rx2+36, py+3, fill="#FFB300", outline="")

        cap_x = ic_x2 + 105
        for cidx, cy in enumerate(range(75, 150, 45)):
            c.create_oval(cap_x-12, cy-12, cap_x+12, cy+12, fill="#0D47A1", outline="#90CAF9", width=2)
            c.create_line(cap_x, 42, cap_x, cy-12, fill="#FF5252", width=2)
            c.create_line(cap_x, cy+12, cap_x, h-32, fill="#40C4FF", width=1)
            c.create_text(cap_x, cy, text=f"C{cidx+1}", fill="white", font=("Arial", 7, "bold"))

        c.create_rectangle(cap_x-16, 165, cap_x+16, 182, fill="#111111", outline="white")
        c.create_line(cap_x+10, 165, cap_x+10, 182, fill="#B0BEC5", width=3)
        c.create_text(cap_x, 190, text="D1:1N4148", fill="white", font=("Arial", 6))

        sw_x = cap_x + 35
        if mode == "ats":
            for ridx, ry in enumerate(range(65, 220, 100)):
                c.create_rectangle(sw_x, ry, sw_x+75, ry+75, fill="#0D47A1", outline="white", width=2)
                c.create_text(sw_x+37, ry+37, text=f"RL{ridx+1}: 60A\nRELAY", fill="white", font=("Arial", 7, "bold"))
                c.create_line(sw_x+75, ry+37, w-75, ry+37, fill="#FF5252", width=3)
        else:
            for qidx, qy in enumerate(range(65, 220, 55)):
                c.create_rectangle(sw_x, qy, sw_x+48, qy+36, fill="#212121", outline="#00E676", width=2)
                c.create_rectangle(sw_x, qy-6, sw_x+48, qy, fill="#B0BEC5", outline="")
                qlbl = f"Q{qidx+1}:3205" if mode != "charger" else f"Q{qidx+1}:20N60"
                c.create_text(sw_x+24, qy+18, text=qlbl, fill="#00E676", font=("Arial", 6, "bold"))
                c.create_line(sw_x+48, qy+18, w-85, qy+18, fill="#FF5252", width=2)

        mag_x = w - 62
        c.create_oval(mag_x-26, 75, mag_x+26, 127, fill="#3E2723", outline="#FF8F00", width=4)
        mag_lbl = "T1:TOROID" if mode == "inverter" else ("L1:BUCK" if mode == "mppt" else ("T1:EE42" if mode == "charger" else "MOV"))
        c.create_text(mag_x, 101, text=mag_lbl, fill="#FFEB3B", font=("Arial", 6, "bold"))

        c.create_rectangle(mag_x-26, 155, mag_x+26, 225, fill="#2E7D32", outline="white", width=2)
        c.create_oval(mag_x-14, 175, mag_x-4, 185, fill="#B0BEC5", outline="black")
        c.create_oval(mag_x+4, 175, mag_x+14, 185, fill="#B0BEC5", outline="black")
        c.create_text(mag_x, 208, text="J1: OUT", fill="white", font=("Arial", 7, "bold"))

    def action_open_fullscreen_pcb(self):
        win = ctk.CTkToplevel(self)
        win.title("SUNVOLT PCB STUDIO — FULL SCREEN COPPER & COMPONENT VIEW")
        win.geometry("920x620")
        win.attributes("-topmost", True)
        big_canvas = tk.Canvas(win, width=890, height=590, bg="#052214")
        big_canvas.pack(padx=12, pady=12, fill="both", expand=True)
        self.render_detailed_pcb_on_canvas(big_canvas, 890, 590, self.current_pcb_title, self.current_pcb_mode)
        if getattr(self, 'current_ai_pcb_design', None):
            self.render_ai_custom_pcb(big_canvas, 890, 590, self.current_ai_pcb_design)
        else:
            self.render_detailed_pcb_on_canvas(big_canvas, 890, 590, self.current_pcb_title, self.current_pcb_mode)

    def action_generate_custom_pcb(self, preset_name=None):
        if preset_name and hasattr(self, 'entry_pcb_design'):
            self.entry_pcb_design.delete(0, tk.END)
            self.entry_pcb_design.insert(0, preset_name)
        query = preset_name if preset_name else (self.entry_pcb_design.get().strip() if hasattr(self, 'entry_pcb_design') else "")
        if not query and hasattr(self, 'pcb_preset_menu'):
            query = self.pcb_preset_menu.get()

        api_key = os.environ.get("GEMINI_API_KEY", "").strip()
        if api_key and query:
            try:
                from google import genai
                if hasattr(self, 'txt_pcb_steps'):
                    self.txt_pcb_steps.delete("1.0", tk.END)
                    self.txt_pcb_steps.insert(tk.END, f"⏳ Gemini AI Hardware Architect na zana taswirar '{query}'...\n")
                    self.update_idletasks()
                client = genai.Client(api_key=api_key)
                prompt = (
                    f"Design a real, workable single-layer electronics PCB for: '{query}'. "
                    "Return ONLY valid JSON (no markdown) with this exact structure: "
                    '{"title": "BOARD NAME", "bom": "Complete BOM & step-by-step assembly text", '
                    '"parts": [{"ref": "U1", "type": "ic", "label": "EG8010", "x": 80, "y": 170}, '
                    '{"ref": "R1", "type": "resistor", "label": "10R", "x": 160, "y": 110}, '
                    '{"ref": "C1", "type": "capacitor", "label": "2200uF", "x": 220, "y": 90}, '
                    '{"ref": "Q1", "type": "mosfet", "label": "IRF3205", "x": 290, "y": 140}, '
                    '{"ref": "T1", "type": "coil", "label": "TOROID", "x": 370, "y": 160}], '
                    '"traces": [[80, 170, 160, 110], [160, 110, 290, 140], [290, 140, 370, 160]]}. '
                    "Include 10 to 16 realistic parts (ICs, resistors, capacitors, diodes, mosfets/relays, coils, terminals) within x:45..395, y:55..285."
                )
                resp = client.models.generate_content(model="gemini-2.5-flash", contents=prompt)
                raw = resp.text.strip().removeprefix("```json").removeprefix("```").removesuffix("```").strip()
                design = json.loads(raw)
                self.current_pcb_title = design.get("title", query.upper())
                self.current_ai_pcb_design = design
                if hasattr(self, 'txt_pcb_steps'):
                    self.txt_pcb_steps.delete("1.0", tk.END)
                    self.txt_pcb_steps.insert(tk.END, f"📐 {self.current_pcb_title}\n=========================================\n{design.get('bom', '')}")
                if hasattr(self, 'studio_canvas'):
                    self.render_ai_custom_pcb(self.studio_canvas, 440, 340, design)
                return
            except Exception:
                pass

        # Fallback Offline Templates if no Internet / API Key
        q = query.lower()
        if "mppt" in q or "solar" in q:
            title, mode = "MPPT SOLAR CHARGE CONTROLLER (PCB REV 2.4)", "mppt"
            guide = "1. PARTS: STM32/PIC16F877A, IR2104, 2x IRF3205, 47uH Toroid, MBR20100CT.\n2. STEPS: Solder 5V regulator -> MCU -> Driver & Mosfets -> Flash .HEX."
        elif "charger" in q or "battery" in q:
            title, mode = "SMART 12V/24V BATTERY CHARGER (PCB REV 1.8)", "charger"
            guide = "1. PARTS: UC3842 PWM, 20N60 FET, EE42 Core, PC817, LM358, TL431.\n2. STEPS: Keep 220V & 12V tracks 6mm apart -> Wind EE42 -> Set 14.4V."
        elif "ats" in q or "changeover" in q:
            title, mode = "AUTOMATIC CHANGEOVER ATS BOARD (PCB REV 3.0)", "ats"
            guide = "1. PARTS: NE555 Timer, LM393, 2x BC547, 2x 12V 60A Relays, 1N4007.\n2. STEPS: Build 12V supply -> 10s NE555 delay -> Wire 60A relays."
        else:
            title, mode = "PURE SINE WAVE INVERTER BOARD (PCB REV 4.2)", "inverter"
            guide = "1. PARTS: EGS002 (EG8010+IR2110), 8x IRF3205, 10R Resistors, Toroid.\n2. STEPS: Tin power tracks -> Solder EGS002 -> Check 50Hz wave -> Mount FETs."

        self.current_pcb_title = title
        self.current_pcb_mode = mode
        self.current_ai_pcb_design = None
        if hasattr(self, 'txt_pcb_steps'):
            self.txt_pcb_steps.delete("1.0", tk.END)
            self.txt_pcb_steps.insert(tk.END, f"📐 {title}\n=========================================\n{guide}")
        if hasattr(self, 'studio_canvas'):
            self.render_detailed_pcb_on_canvas(self.studio_canvas, 440, 340, title, mode)

    def render_ai_custom_pcb(self, c, w, h, design):
        c.delete("all")
        c.configure(bg="#052214")
        sx, sy = w / 440.0, h / 340.0
        c.create_rectangle(8, 8, w-8, h-8, outline="#FFB300", width=2)
        for gx in range(20, w-15, 18):
            c.create_line(gx, 12, gx, h-12, fill="#0A3620", width=1)
        for gy in range(20, h-15, 18):
            c.create_line(12, gy, w-12, gy, fill="#0A3620", width=1)
        c.create_text(w//2, 20, text=design.get("title", "AI CUSTOM PCB"), fill="#64FFDA", font=("Arial", 8, "bold"))

        for tr in design.get("traces", []):
            if len(tr) == 4:
                c.create_line(tr*sx, tr*sy, tr*sx, tr*sy, fill="#00E676", width=2)

        for p in design.get("parts", []):
            px, py = p.get("x", 100) * sx, p.get("y", 100) * sy
            ptype = p.get("type", "").lower()
            lbl = f"{p.get('ref','')}:{p.get('label','')}"
            if "ic" in ptype:
                c.create_rectangle(px-24, py-32, px+24, py+32, fill="#111827", outline="white", width=2)
                c.create_text(px, py, text=lbl, fill="#FFB300", font=("Arial", 6, "bold"))
            elif "mosfet" in ptype or "relay" in ptype:
                c.create_rectangle(px-20, py-16, px+20, py+16, fill="#212121", outline="#00E676", width=2)
                c.create_text(px, py, text=lbl, fill="#00E676", font=("Arial", 6, "bold"))
            elif "capacitor" in ptype:
                c.create_oval(px-12, py-12, px+12, py+12, fill="#0D47A1", outline="#90CAF9", width=2)
                c.create_text(px, py+18, text=lbl, fill="white", font=("Arial", 6))
            elif "coil" in ptype:
                c.create_oval(px-20, py-20, px+20, py+20, fill="#3E2723", outline="#FF8F00", width=3)
                c.create_text(px, py, text=lbl, fill="#FFEB3B", font=("Arial", 6, "bold"))
            else:
                c.create_rectangle(px-14, py-5, px+14, py+5, fill="#D7CCC8", outline="#FFB300")
                c.create_text(px, py-11, text=lbl, fill="white", font=("Arial", 6))

    def action_export_pcb_manufacturing_files(self):
        title = self.current_pcb_title
        safe_name = "".join(c if c.isalnum() else "_" for c in title)[:25]
        desktop = os.path.join(os.path.expanduser("~"), "Desktop")
        pdf_path = os.path.join(desktop, f"{safe_name}_PRINT_READY.pdf")
        gerber_path = os.path.join(desktop, f"{safe_name}_TOP_COPPER.gbr")

        gerber_code = (
            f"G04 SUNVOLT TECH HUB — RS-274X GERBER FILE ({title})*\n"
            "%FSLAX26Y26*%\n%MOMM*%\n%LPD*%\n"
            "%ADD10C,1.500*%\n%ADD11R,2.000X2.000*%\n"
            "G54D10*\nX1000000Y1000000D03*\nX5000000Y1000000D03*\n"
            "G54D11*\nX2500000Y2500000D01*\nX4500000Y2500000D01*\n"
            "M02*\n"
        )
        with open(gerber_path, "w", encoding="utf-8") as gf:
            gf.write(gerber_code)

        pdf = FPDF()
        pdf.add_page()
        pdf.set_font("Helvetica", "B", 14)
        pdf.cell(0, 10, f"SUNVOLT PCB MANUFACTURING PACK: {title}", ln=True)
        pdf.set_font("Helvetica", "", 10)
        pdf.cell(0, 7, "1:1 Scale Copper Etching Mask (Print on Glossy Paper for Toner Transfer)", ln=True)
        pdf.ln(4)

        start_y = pdf.get_y()
        pdf.set_draw_color(0, 0, 0)
        pdf.set_fill_color(0, 0, 0)
        pdf.set_line_width(0.8)
        pdf.rect(20, start_y, 120, 75)
        pdf.line(25, start_y + 10, 135, start_y + 10)
        pdf.line(25, start_y + 65, 135, start_y + 65)
        for py in range(int(start_y + 20), int(start_y + 58), 6):
            pdf.ellipse(35, py, 2.5, 2.5, style="F")
            pdf.ellipse(52, py, 2.5, 2.5, style="F")
            pdf.line(54, py + 1.2, 85, py + 1.2)
        for qy in range(int(start_y + 18), int(start_y + 60), 16):
            pdf.rect(85, qy, 8, 8, style="F")
            pdf.line(93, qy + 4, 125, qy + 4)
        pdf.ellipse(115, start_y + 22, 16, 16)
        pdf.set_y(start_y + 82)

        if hasattr(self, 'txt_pcb_steps'):
            bom_text = self.txt_pcb_steps.get("1.0", tk.END).encode('latin-1', 'replace').decode('latin-1')
            pdf.multi_cell(0, 6, bom_text)
        pdf.output(pdf_path)

        if hasattr(self, 'txt_pcb_steps'):
            self.txt_pcb_steps.insert("1.0", f"[✅ OPENED ON SCREEN & SAVED TO DESKTOP]:\n• Print PDF: {pdf_path}\n• Gerber:    {gerber_path}\n================================================================\n")

        try:
            os.startfile(pdf_path)
        except Exception:
            pass

    def action_load_firmware_file(self):
        fw_path = filedialog.askopenfilename(title="Select Firmware File", filetypes=[("Firmware Files", "*.bin *.hex *.pac *.img"), ("All Files", "*.*")])
        if fw_path and hasattr(self, 'txt_prog_guide'):
            short_fw = os.path.basename(fw_path)
            size_kb = round(os.path.getsize(fw_path) / 1024, 1)
            self.txt_prog_guide.insert("1.0", f"[📂 FIRMWARE LOADED]: {short_fw} ({size_kb} KB) — Ready to Flash!\n----------------------------------------------------------------\n")
    def action_trigger_print_view(self):
        content = self.txt_receipt.get("1.0", tk.END).strip()
        if not content or "Select a completed job" in content:
            self.lbl_print_status.configure(text="⚠️ Zaɓi wani gyara daga jerin History da farko!", text_color="#FF9100")
            return
        win = ctk.CTkToplevel(self)
        win.title("SUNVOLT RECEIPT — PRINT PREVIEW")
        win.geometry("440x520")
        win.attributes("-topmost", True)
        paper = tk.Text(win, bg="#FFFFFF", fg="#000000", font=("Courier", 11), bd=10, relief="flat")
        paper.pack(fill="both", expand=True, padx=15, pady=(15, 8))
        paper.insert(tk.END, content)
        paper.configure(state="disabled")
        ctk.CTkButton(win, text="🖨️ Send to Printer / Export PDF", height=36, fg_color="#00E676", text_color="black", font=ctk.CTkFont(weight="bold"), command=lambda: [win.destroy(), self.action_export_receipt_pdf()]).pack(pady=(0, 12))

    def action_export_receipt_pdf(self):
        if not hasattr(self, 'selected_history_job'):
            return
        j = self.selected_history_job
        desktop = os.path.join(os.path.expanduser("~"), "Desktop")
        pdf_path = os.path.join(desktop, f"Receipt_{j['ticket_id']}.pdf")
        pdf = FPDF()
        pdf.add_page()
        pdf.set_font("Courier", "", 11)
        pdf.multi_cell(0, 6, self.txt_receipt.get("1.0", tk.END).encode('latin-1', 'replace').decode('latin-1'))
        pdf.output(pdf_path)
        self.lbl_print_status.configure(text=f"✅ Receipt PDF saved to Desktop: Receipt_{j['ticket_id']}.pdf")
        try:
            os.startfile(pdf_path)
        except Exception:
            pass

    def action_direct_print_receipt(self):
        self.action_export_receipt_pdf()

    def show_marketplace_view(self):
        self.clear_main_frame()
        t = LANG_TEXT[self.current_lang]
        if self.user_role == "receptionist":
            ctk.CTkLabel(self.main_frame, text=t["access_denied"], font=ctk.CTkFont(size=16, weight="bold"), text_color="#FF3D00").pack(padx=40, pady=40)
            return
        ctk.CTkLabel(self.main_frame, text="🛒 SUNVOLT SPARE PARTS & INVENTORY MANAGER", font=ctk.CTkFont(size=20, weight="bold"), text_color="#FFB300").pack(anchor="w", padx=30, pady=(16, 8))

        add_bar = ctk.CTkFrame(self.main_frame, fg_color="#111111", corner_radius=8)
        add_bar.pack(fill="x", padx=30, pady=(0, 8))
        self.new_part_name = ctk.CTkEntry(add_bar, width=260, placeholder_text="Part Name (e.g. Tecno Screen)...")
        self.new_part_name.pack(side="left", padx=8, pady=10)
        self.new_part_price = ctk.CTkEntry(add_bar, width=120, placeholder_text="Price (₦)...")
        self.new_part_price.pack(side="left", padx=6, pady=10)
        self.new_part_qty = ctk.CTkEntry(add_bar, width=90, placeholder_text="Qty...")
        self.new_part_qty.pack(side="left", padx=6, pady=10)
        ctk.CTkButton(add_bar, text="➕ Add / Restock", width=140, fg_color="#2296F3", font=ctk.CTkFont(weight="bold"), command=self.action_add_or_restock_part).pack(side="left", padx=8, pady=10)

        self.parts_container = ctk.CTkScrollableFrame(self.main_frame, fg_color="transparent")
        self.parts_container.pack(fill="both", expand=True, padx=30, pady=6)
        self.refresh_parts_list()

    def action_add_or_restock_part(self):
        name = self.new_part_name.get().strip()
        if not name:
            return
        try:
            price = int(float(self.new_part_price.get().strip() or "0"))
            qty = int(self.new_part_qty.get().strip() or "1")
        except ValueError:
            return
        for item in SUNVOLT_SPARE_PARTS:
            if item["name"].lower() == name.lower():
                item["stock"] += qty
                if price > 0:
                    item["price"] = price
                save_sunvolt_local_data()
                self.refresh_parts_list()
                return
        SUNVOLT_SPARE_PARTS.append({"name": name, "price": price, "stock": qty})
        save_sunvolt_local_data()
        self.refresh_parts_list()

    def refresh_parts_list(self):
        for w in self.parts_container.winfo_children():
            w.destroy()
        for item in SUNVOLT_SPARE_PARTS:
            row = ctk.CTkFrame(self.parts_container, fg_color="#111111", corner_radius=8)
            row.pack(fill="x", pady=6)
            ctk.CTkLabel(row, text=f"{item['name']}  |  ₦{item['price']:,}  |  Stock: {item['stock']}", font=ctk.CTkFont(size=13, weight="bold")).pack(side="left", padx=15, pady=12)
            ctk.CTkButton(row, text="🛒 Order Part", width=130, fg_color="#00E676", text_color="black", font=ctk.CTkFont(weight="bold"), command=lambda i=item: self.action_order_spare_part(i)).pack(side="right", padx=15, pady=8)

    def action_order_spare_part(self, item):
        if item["stock"] > 0:
            item["stock"] -= 1
            SUNVOLT_ADMIN_FINANCES["total_parts_cost"] += float(item["price"])
            self.refresh_parts_list()
            self.save_part_order_to_neon(item)

    def show_imei_view(self):
        self.clear_main_frame()
        ctk.CTkLabel(self.main_frame, text="🛡️ EASYBUY / KNOX GUARD / IMEI & USB SECURITY CHECK", font=ctk.CTkFont(size=20, weight="bold"), text_color="#00E676").pack(anchor="w", padx=30, pady=(20, 10))
        box = ctk.CTkFrame(self.main_frame, fg_color="#111111", corner_radius=10)
        box.pack(fill="x", padx=30, pady=10)

        self.entry_imei_check = ctk.CTkEntry(box, width=280, placeholder_text="Shigar da IMEI (15 digits) ko Serial...")
        self.entry_imei_check.pack(side="left", padx=(15, 8), pady=15)

        ctk.CTkButton(box, text="🔍 Check IMEI", width=120, height=36, fg_color="#2296F3", font=ctk.CTkFont(weight="bold"), command=self.action_check_imei).pack(side="left", padx=6, pady=15)
        ctk.CTkButton(box, text="🔌 Scan USB Port", width=140, height=36, fg_color="#00E676", text_color="black", font=ctk.CTkFont(weight="bold"), command=self.action_scan_live_usb_imei_tab).pack(side="left", padx=6, pady=15)
        ctk.CTkButton(box, text="🔐 Dead Boot & Lock Guide", width=175, height=36, fg_color="#6A1B9A", font=ctk.CTkFont(weight="bold"), command=self.action_show_dead_security_guide).pack(side="left", padx=6, pady=15)

        self.lbl_imei_result = ctk.CTkLabel(self.main_frame, text="Jona wayar iPhone, Samsung, ko Infinix a USB sannan ka danna '🔌 Scan USB Port' ko ka duba IMEI.", font=ctk.CTkFont(size=12), justify="left")
        self.lbl_imei_result.pack(anchor="w", padx=30, pady=15)

    def action_scan_live_usb_imei_tab(self):
        ports = list(serial.tools.list_ports.comports())
        if not ports:
            self.lbl_imei_result.configure(
                text="⚠️ BABU WAYAR DA AKA GANI A USB (No USB Device Detected):\n• Duba kebul ɗin USB ko ka riƙe maɓallan Boot (Vol+ & Vol-) sannan ka sake soka kebul ɗin.",
                text_color="#FF9100"
            )
            return
        details = "\n".join([f"   • Port: {p.device}  |  Device: {p.description}  |  HWID: {p.hwid}" for p in ports])
        self.lbl_imei_result.configure(
            text=f"✅ LIVE USB CONNECTION DETECTED ({len(ports)} Device):\n{details}\n\n👉 Wayar ta haɗu da kwamfuta! Za ka iya duba FRP, MDM/EasyBuy, ko Flash a Tab 3 (IC Programmer).",
            text_color="#00E676"
        )

    def action_check_imei(self):
        imei = self.entry_imei_check.get().strip()
        if len(imei) == 15 and imei.isdigit():
            self.lbl_imei_result.configure(text=f"✅ IMEI {imei}: VALID FORMAT — Ready for ownership & finance verification.", text_color="#00E676")
        else:
            self.lbl_imei_result.configure(text="⚠️ Shigar da cikakkun lambobin IMEI guda 15 (Dial *#06#).", text_color="#FF9100")

    def action_show_dead_security_guide(self):
        ports = list(serial.tools.list_ports.comports())
        live_port = ", ".join([f"{p.device} ({p.description})" for p in ports]) if ports else "None detected yet"
        apple_note = "\n🍏 APPLE iPHONE/iPAD DETECTED ON USB! (Open Tab 3 -> Apple iOS Guide)" if "apple" in live_port.lower() else ""
        guide = f"🔐 DEAD BOOT & SECURITY PROTOCOL\n• Live USB Port: [{live_port}]{apple_note}\n1. Verify receipt/box.\n2. Samsung FRP: *#0*# -> SamFw ADB.\n3. MTK/Qualcomm: Vol+ & Vol- -> USB."
        self.lbl_imei_result.configure(text=guide, text_color="#E1BEE7")

    def show_admin_view(self):
        self.clear_main_frame()
        t = LANG_TEXT[self.current_lang]
        if self.user_role != "admin":
            ctk.CTkLabel(self.main_frame, text=t["access_denied"], font=ctk.CTkFont(size=16, weight="bold"), text_color="#FF3D00").pack(padx=40, pady=40)
            return
        ctk.CTkLabel(self.main_frame, text=t["admin_title"], font=ctk.CTkFont(size=22, weight="bold"), text_color="#D500F9").pack(anchor="w", padx=35, pady=(16, 8))

        exp_bar = ctk.CTkFrame(self.main_frame, fg_color="#111111", corner_radius=8)
        exp_bar.pack(anchor="w", padx=35, pady=(0, 10))
        self.entry_exp_note = ctk.CTkEntry(exp_bar, width=250, placeholder_text="Expense Note (Fuel, Data, Rent)...")
        self.entry_exp_note.pack(side="left", padx=10, pady=10)
        self.entry_exp_amt = ctk.CTkEntry(exp_bar, width=130, placeholder_text="Amount (₦)...")
        self.entry_exp_amt.pack(side="left", padx=6, pady=10)
        ctk.CTkButton(exp_bar, text="💸 Record Expense", width=150, fg_color="#FF5252", font=ctk.CTkFont(weight="bold"), command=self.action_record_shop_expense).pack(side="left", padx=10, pady=10)

        rev = SUNVOLT_ADMIN_FINANCES.get("total_revenue", 0.0)
        parts_spent = SUNVOLT_ADMIN_FINANCES.get("total_parts_cost", 0.0)
        expenses = SUNVOLT_ADMIN_FINANCES.get("total_expenses", 0.0)
        net_profit = max(0.0, SUNVOLT_ADMIN_FINANCES.get("total_profit", 0.0) - expenses)

        cards = [
            (t["total_revenue"], f"₦ {rev:,.2f}", "#FFB300"),
            ("📈 Tsantsar Riba (Net Profit After Expenses):", f"₦ {net_profit:,.2f}", "#00E676"),
            ("🛒 Kuɗin Sayen Kayan Gyara (Parts Cost):", f"₦ {parts_spent:,.2f}", "#FF9100"),
            ("💸 Kuɗin Fita na Shago (Shop Expenses):", f"₦ {expenses:,.2f}", "#FF5252"),
            (t["total_completed"], str(int(SUNVOLT_ADMIN_FINANCES.get("total_completed", 0))), "#2296F3")
        ]
        for label_str, val_str, col in cards:
            box = ctk.CTkFrame(self.main_frame, width=560, height=68, fg_color="#111111", corner_radius=10)
            box.pack(anchor="w", padx=35, pady=5)
            box.pack_propagate(False)
            ctk.CTkLabel(box, text=label_str, font=ctk.CTkFont(size=12)).pack(anchor="w", padx=18, pady=(8, 0))
            ctk.CTkLabel(box, text=val_str, font=ctk.CTkFont(size=18, weight="bold"), text_color=col).pack(anchor="w", padx=18)

    def action_record_shop_expense(self):
        try:
            amt = float(self.entry_exp_amt.get().strip())
            if amt > 0:
                SUNVOLT_ADMIN_FINANCES["total_expenses"] = SUNVOLT_ADMIN_FINANCES.get("total_expenses", 0.0) + amt
                save_sunvolt_local_data()
                self.show_admin_view()
        except ValueError:
            pass

    def send_customer_sms_alert(self, phone, message):
        clean_phone = phone.strip()
        if clean_phone.startswith("0") and len(clean_phone) == 11:
            clean_phone = "234" + clean_phone[1:]
        t_key = SUNVOLT_API_CONFIG.get("termii_key", "").strip()
        sender = SUNVOLT_API_CONFIG.get("sender_id", "SUNVOLT").strip() or "SUNVOLT"
        if t_key and clean_phone.isdigit():
            try:
                import urllib.request
                url = "https://termii.com"
                body = json.dumps({
                    "to": clean_phone,
                    "from": sender,
                    "sms": message,
                    "type": "plain",
                    "channel": "generic",
                    "api_key": t_key
                }).encode("utf-8")
                req = urllib.request.Request(url, data=body, headers={"Content-Type": "application/json"})
                urllib.request.urlopen(req, timeout=8)
                return "✅ Real SMS Sent via Termii!"
            except Exception as e:
                return f"⚠️ SMS Network Error ({e})"
        return "ℹ️ Saved Locally (Add Termii API Key in Settings for Live SMS)"

    def show_settings_view(self):
        self.clear_main_frame()
        if self.user_role != "admin":
            ctk.CTkLabel(self.main_frame, text="⛔ HANA SHIGA: Admin ne kawai zai iya saita API Keys!", font=ctk.CTkFont(size=16, weight="bold"), text_color="#FF3D00").pack(padx=40, pady=40)
            return
        ctk.CTkLabel(self.main_frame, text="⚙️ SUNVOLT API, SMS & CLOUD DATABASE SETTINGS", font=ctk.CTkFont(size=20, weight="bold"), text_color="#64FFDA").pack(anchor="w", padx=35, pady=(20, 10))

        box = ctk.CTkFrame(self.main_frame, fg_color="#111111", corner_radius=10)
        box.pack(fill="x", padx=35, pady=10)

        ctk.CTkLabel(box, text="1. Google Gemini Vision & PCB AI Key (://google.com):", font=ctk.CTkFont(size=12, weight="bold"), text_color="#FFB300").pack(anchor="w", padx=20, pady=(14, 2))
        self.set_gemini = ctk.CTkEntry(box, width=540, placeholder_text="AIzaSy...", show="*")
        self.set_gemini.insert(0, SUNVOLT_API_CONFIG.get("gemini_key", ""))
        self.set_gemini.pack(anchor="w", padx=20, pady=(0, 10))

        ctk.CTkLabel(box, text="2. Termii Live SMS API Key (termii.com):", font=ctk.CTkFont(size=12, weight="bold"), text_color="#00E676").pack(anchor="w", padx=20, pady=(4, 2))
        self.set_termii = ctk.CTkEntry(box, width=540, placeholder_text="TL...", show="*")
        self.set_termii.insert(0, SUNVOLT_API_CONFIG.get("termii_key", ""))
        self.set_termii.pack(anchor="w", padx=20, pady=(0, 10))

        ctk.CTkLabel(box, text="3. SMS Sender ID (e.g. SUNVOLT or N-Alert):", font=ctk.CTkFont(size=12, weight="bold")).pack(anchor="w", padx=20, pady=(4, 2))
        self.set_sender = ctk.CTkEntry(box, width=260)
        self.set_sender.insert(0, SUNVOLT_API_CONFIG.get("sender_id", "SUNVOLT"))
        self.set_sender.pack(anchor="w", padx=20, pady=(0, 10))

        ctk.CTkLabel(box, text="4. Neon Cloud Database URL (Optional Multi-PC Sync):", font=ctk.CTkFont(size=12, weight="bold"), text_color="#CE93D8").pack(anchor="w", padx=20, pady=(4, 2))
        self.set_neon = ctk.CTkEntry(box, width=540, placeholder_text="postgresql://user:pass@ep-...neon.tech/neondb")
        self.set_neon.insert(0, SUNVOLT_API_CONFIG.get("neon_url", ""))
        self.set_neon.pack(anchor="w", padx=20, pady=(0, 14))

        ctk.CTkButton(box, text="💾 Save All Keys & Auto-Backup Data", width=300, height=40, fg_color="#00E676", text_color="black", font=ctk.CTkFont(weight="bold"), command=self.action_save_api_settings).pack(anchor="w", padx=20, pady=(4, 15))
        self.lbl_set_status = ctk.CTkLabel(self.main_frame, text=f"📁 Local Auto-Save File: {DATA_FILE_PATH}", font=ctk.CTkFont(size=12), text_color="#B0BEC5")
        self.lbl_set_status.pack(anchor="w", padx=35, pady=6)
        b_row = ctk.CTkFrame(box, fg_color="transparent")
        b_row.pack(anchor="w", padx=20, pady=(4, 15))
        ctk.CTkButton(b_row, text="💾 Save All Settings", width=180, height=38, fg_color="#00E676", text_color="black", font=ctk.CTkFont(weight="bold"), command=self.action_save_api_settings).pack(side="left", padx=(0, 10))
        ctk.CTkButton(b_row, text="📤 Export Backup", width=165, height=38, fg_color="#2296F3", font=ctk.CTkFont(weight="bold"), command=self.action_export_backup_file).pack(side="left", padx=(0, 10))
        ctk.CTkButton(b_row, text="📥 Restore Backup", width=165, height=38, fg_color="#FFB300", text_color="black", font=ctk.CTkFont(weight="bold"), command=self.action_restore_backup_file).pack(side="left")

    def action_save_api_settings(self):
        SUNVOLT_API_CONFIG["gemini_key"] = self.set_gemini.get().strip()
        SUNVOLT_API_CONFIG["termii_key"] = self.set_termii.get().strip()
        SUNVOLT_API_CONFIG["sender_id"] = self.set_sender.get().strip() or "SUNVOLT"
        SUNVOLT_API_CONFIG["neon_url"] = self.set_neon.get().strip()
        if SUNVOLT_API_CONFIG["gemini_key"]:
            os.environ["GEMINI_API_KEY"] = SUNVOLT_API_CONFIG["gemini_key"]
        if SUNVOLT_API_CONFIG["neon_url"]:
            os.environ["NEON_DATABASE_URL"] = SUNVOLT_API_CONFIG["neon_url"]
            self.initialize_neon_database()
        save_sunvolt_local_data()
        self.lbl_set_status.configure(text="✅ An adana dukan API Keys & Local Auto-Save lafiya ƙalau!", text_color="#00E676")
    def action_export_backup_file(self):
        save_sunvolt_local_data()
        dest = filedialog.asksaveasfilename(defaultextension=".json", initialfile="Sunvolt_Backup.json", filetypes=[("JSON Backup", "*.json")])
        if dest and os.path.exists(DATA_FILE_PATH):
            import shutil
            shutil.copy2(DATA_FILE_PATH, dest)
            self.lbl_set_status.configure(text=f"✅ Backup Saved: {dest}", text_color="#00E676")

    def action_restore_backup_file(self):
        src = filedialog.askopenfilename(title="Select Sunvolt Backup File", filetypes=[("JSON Backup", "*.json")])
        if src:
            import shutil
            shutil.copy2(src, DATA_FILE_PATH)
            load_sunvolt_local_data()
            self.lbl_set_status.configure(text="✅ All Shop Data Restored Successfully!", text_color="#00E676")
# ==================== V2026 ENTERPRISE OVERRIDES (NO EDITING NEEDED) ====================
def _sv_patch_sunvolt_v2026():
    
    def new_set_hw_mode(self, mode):
        self.selected_hw_mode = mode
        colors = {"Phone": "#00897B", "Laptop": "#1E88E5", "Inverter": "#F57C00", "Charge_Controller": "#43A047", "Sun_King": "#FFB300", "Sewing_Machine": "#8E24AA", "Universal_Unknown": "#D81B60"}
        if hasattr(self, 'hw_mode_buttons'):
            for m, btn in self.hw_mode_buttons.items():
                btn.configure(fg_color=colors.get(m, "#00897B") if m == mode else "#2B2B2B", text_color="black" if (m == mode and m == "Sun_King") else "white")

    _orig_switch = SunvoltApp.switch_engineer_subpage
    def new_switch_engineer_subpage(self, page_key):
        _orig_switch(self, page_key)
        if page_key == "lab" and hasattr(self, 'hw_mode_buttons') and "Sun_King" not in self.hw_mode_buttons:
            parent_row = list(self.hw_mode_buttons.values()).master
            for b in self.hw_mode_buttons.values():
                b.destroy()
            self.hw_mode_buttons.clear()
            row2 = ctk.CTkFrame(parent_row.master, fg_color="transparent")
            row2.pack(anchor="w", pady=(2, 4), after=parent_row)
            row1_modes = [("📱 Phone", "Phone"), ("💻 Laptop", "Laptop"), ("⚡ Inverter", "Inverter"), ("☀️ CC", "Charge_Controller")]
            row2_modes = [("🔋 Sun King", "Sun_King"), ("🧵 Sewing", "Sewing_Machine"), ("🌐 Universal", "Universal_Unknown")]
            for lbl, mode_val in row1_modes:
                btn = ctk.CTkButton(parent_row, text=lbl, width=95, height=28, fg_color="#2B2B2B", font=ctk.CTkFont(size=11, weight="bold"), command=lambda m=mode_val: self.set_hw_mode(m))
                btn.pack(side="left", padx=3)
                self.hw_mode_buttons[mode_val] = btn
            for lbl, mode_val in row2_modes:
                btn = ctk.CTkButton(row2, text=lbl, width=115, height=28, fg_color="#2B2B2B", font=ctk.CTkFont(size=11, weight="bold"), command=lambda m=mode_val: self.set_hw_mode(m))
                btn.pack(side="left", padx=3)
                self.hw_mode_buttons[mode_val] = btn
            self.set_hw_mode(getattr(self, 'selected_hw_mode', 'Phone'))

    def new_open_fullscreen_pcb(self):
        win = ctk.CTkToplevel(self)
        win.title("SUNVOLT PCB STUDIO — HIGH-DENSITY SCROLLABLE & DRAGGABLE BLUEPRINT (100–200+ PARTS)")
        win.geometry("1020x660")
        win.attributes("-topmost", True)
        top = ctk.CTkFrame(win, fg_color="#111111", corner_radius=6)
        top.pack(fill="x", padx=12, pady=(10, 4))
        ctk.CTkLabel(top, text=f"📐 {getattr(self, 'current_pcb_title', 'PCB BLUEPRINT')}  |  🖱️ Riƙe Mouse ka ja (Click & Drag) ko yi amfani da Scrollbars!", font=ctk.CTkFont(size=12, weight="bold"), text_color="#64FFDA").pack(side="left", padx=12, pady=6)
        box = tk.Frame(win, bg="#041E11")
        box.pack(fill="both", expand=True, padx=12, pady=(0, 12))
        hbar = tk.Scrollbar(box, orient="horizontal")
        hbar.pack(side="bottom", fill="x")
        vbar = tk.Scrollbar(box, orient="vertical")
        vbar.pack(side="right", fill="y")
        big_w, big_h = 2000, 1400
        big_c = tk.Canvas(box, bg="#041E11", scrollregion=(0, 0, big_w, big_h), xscrollcommand=hbar.set, yscrollcommand=vbar.set, highlightthickness=2, highlightbackground="#FFB300")
        big_c.pack(side="left", fill="both", expand=True)
        hbar.config(command=big_c.xview)
        vbar.config(command=big_c.yview)
        big_c.bind("<ButtonPress-1>", lambda e: big_c.scan_mark(e.x, e.y))
        big_c.bind("<B1-Motion>", lambda e: big_c.scan_dragto(e.x, e.y, gain=1))
        if getattr(self, 'current_ai_pcb_design', None) and hasattr(self, 'render_ai_custom_pcb'):
            self.render_ai_custom_pcb(big_c, big_w, big_h, self.current_ai_pcb_design)
        else:
            self.render_detailed_pcb_on_canvas(big_c, big_w, big_h, getattr(self, 'current_pcb_title', 'PCB'), getattr(self, 'current_pcb_mode', 'inverter'))

    SunvoltApp.set_hw_mode = new_set_hw_mode
    SunvoltApp.switch_engineer_subpage = new_switch_engineer_subpage
    SunvoltApp.action_open_fullscreen_pcb = new_open_fullscreen_pcb
    _orig_rec = SunvoltApp.show_reception_view
    def new_show_reception_view(self):
            _orig_rec = SunvoltApp.show_reception_view
    def new_show_reception_view(self):
        _orig_rec(self)
        if hasattr(self, 'rec_status_listbox') and not hasattr(self, 'dep_choice'):
            right_panel = self.rec_status_listbox.master
            dep_box = ctk.CTkFrame(right_panel, fg_color="#1B2631", corner_radius=8)
            dep_box.pack(fill="x", padx=15, pady=(6, 10))
            ctk.CTkLabel(dep_box, text="💰 Karɓar Deposit (Bayan Engineer Ya Sa Farashi):", font=ctk.CTkFont(size=12, weight="bold"), text_color="#FFB300").pack(anchor="w", padx=10, pady=(6, 2))
            row = ctk.CTkFrame(dep_box, fg_color="transparent")
            row.pack(fill="x", padx=10, pady=(2, 8))
            self.dep_choice = ctk.CTkSegmentedButton(row, values=["❌ No Deposit", "✅ Paid Deposit"], command=self.toggle_deposit_input)
            self.dep_choice.set("❌ No Deposit")
            self.dep_choice.pack(side="left", padx=(0, 6))
            self.entry_deposit = ctk.CTkEntry(row, width=115, placeholder_text="Amount (₦)...", state="disabled", fg_color="#1E1E1E")
            self.entry_deposit.pack(side="left", padx=(0, 6))
            ctk.CTkButton(row, text="💾 Save", width=70, fg_color="#00E676", text_color="black", font=ctk.CTkFont(weight="bold"), command=self.action_save_post_quote_deposit).pack(side="left")

    def new_toggle_deposit(self, choice):
        if "Paid" in choice:
            self.entry_deposit.configure(state="normal", fg_color="#2B2B2B", placeholder_text="Kuɗi (₦)...")
        else:
            self.entry_deposit.delete(0, tk.END)
            self.entry_deposit.configure(state="disabled", fg_color="#1E1E1E", placeholder_text="Amount (₦)...")

    def new_save_post_quote_deposit(self):
        sel = self.rec_status_listbox.curselection()
        if not sel:
            self.lbl_rec_feedback.configure(text="⚠️ Danna na'urar da Engineer ya sa wa farashi a jerin dama da farko!", text_color="#FF9100")
            return
        idx = sel
        if idx >= len(SUNVOLT_JOB_QUEUE):
            self.lbl_rec_feedback.configure(text="⚠️ Wannan aikin an riga an kammala shi!", text_color="#FF9100")
            return
        job = SUNVOLT_JOB_QUEUE[idx]
        if job.get("status") != "Approved":
            self.lbl_rec_feedback.configure(text="⚠️ Sai Babban Engineer ya sa farashi (APPROVED) tukuna kafin a karɓi Deposit!", text_color="#FF9100")
            return
        dep_val = 0.0
        if "Paid" in self.dep_choice.get():
            try:
                dep_val = float(self.entry_deposit.get().strip() or "0")
            except ValueError:
                dep_val = 0.0
        job["deposit"] = dep_val
        save_sunvolt_local_data()
        bal = max(0.0, job.get("quote", 0.0) - dep_val)
        msg = f"✅ #{job['ticket_id']}: Deposit ₦{dep_val:,.0f} | Ragowar Bashi (Balance): ₦{bal:,.0f}" if dep_val > 0 else f"ℹ️ #{job['ticket_id']}: No Deposit (₦0) — Balance: ₦{job.get('quote', 0.0):,.0f}"
        self.lbl_rec_feedback.configure(text=msg, text_color="#00E676")
        self.refresh_reception_status_list()

    SunvoltApp.show_reception_view = new_show_reception_view
    SunvoltApp.toggle_deposit_input = new_toggle_deposit
    SunvoltApp.action_save_post_quote_deposit = new_save_post_quote_deposit
    _orig_init = SunvoltApp.__init__
    def new_init(self, *args, **kwargs):
        _orig_init(self, *args, **kwargs)
        if hasattr(self, 'sidebar_frame') and not hasattr(self, 'btn_nav_help'):
            self.sidebar_frame.grid_rowconfigure(10, weight=0)
            self.sidebar_frame.grid_rowconfigure(11, weight=1)
            self.btn_nav_help = ctk.CTkButton(self.sidebar_frame, text="📖 Jagora & AI Help", anchor="w", fg_color="#00897B", text_color="white", font=ctk.CTkFont(weight="bold"), command=self.show_user_guide_view)
            self.btn_nav_help.grid(row=10, column=0, padx=20, pady=6, sticky="ew")
            if hasattr(self, 'lang_switch'):
                self.lang_switch.grid(row=11, column=0, padx=20, pady=15, sticky="s")

    def new_show_user_guide(self):
        self.clear_main_frame()
        is_en = (getattr(self, 'current_lang', 'HA') == "EN")
        title_txt = "📖 SUNVOLT TECH HUB — COMPLETE USER GUIDE & AI ASSISTANT" if is_en else "📖 SUNVOLT TECH HUB — CIKAKKEN LITTAFIN JAGORA & AI HELP"
        ph_txt = "🔍 Ask anything about this app (e.g. Gerber, PIN, Deposit, Sun King, AI Scan)..." if is_en else "🔍 Rubuta abin da ya kulle maka kai (misali: PIN, Gerber, Deposit, Sun King, AI Scan)..."
        btn_txt = "💡 Ask Guide" if is_en else "💡 Nemi Bayani"

        ctk.CTkLabel(self.main_frame, text=title_txt, font=ctk.CTkFont(size=19, weight="bold"), text_color="#64FFDA").pack(anchor="w", padx=30, pady=(16, 6))
        ask_bar = ctk.CTkFrame(self.main_frame, fg_color="#111111", corner_radius=8)
        ask_bar.pack(fill="x", padx=30, pady=(0, 10))
        self.entry_help_query = ctk.CTkEntry(ask_bar, width=520, placeholder_text=ph_txt)
        self.entry_help_query.pack(side="left", padx=12, pady=12)
        ctk.CTkButton(ask_bar, text=btn_txt, width=180, height=36, fg_color="#00E676", text_color="black", font=ctk.CTkFont(weight="bold"), command=self.action_ask_manual_help).pack(side="left", padx=6, pady=12)

        self.txt_user_manual = tk.Text(self.main_frame, bg="#111111", fg="#E0F2F1", font=("Consolas", 10), wrap="word", bd=10, relief="flat")
        self.txt_user_manual.pack(fill="both", expand=True, padx=30, pady=(0, 18))

        manual_body = (
            "=================================================================================\n"
            "          ⚡ SUNVOLT TECH HUB — CIKAKKEN JAGORAR AIKI (USER GUIDE) ⚡             \n"
            "=================================================================================\n\n"
            "1. 🛎️ RECEPTION (KARƁAR KAYA & DEPOSIT):\n"
            "   • Rajista (Hagu): Cika suna, lambar waya, na'ura, IMEI, da matsala sannan ka tura.\n"
            "   • Deposit (Dama): Bayan Babban Engineer ya sa farashi ('💰 APPROVED'), zaɓi na'urar\n"
            "     a gefen dama, danna '✅ Paid Deposit' (ko '❌ No Deposit') sannan ka danna '💾 Save'.\n\n"
            "2. 🛠️ SENIOR ENGINEER LAB (DAKIN GYARA — SHAFUKA 5):\n"
            "   • Tab 1 (📋 Pending): Danna sunan kaya don kulle shi a teburinka, sa farashi ('Approve')\n"
            "     ko ka ƙi karɓa ('Reject') tare da dalili.\n"
            "   • Tab 2 (🔬 AI Diagnostics): Zaɓi nau'in na'ura (Phone, Laptop, Inv, CC, SunKing,\n"
            "     Sew, Univ), ɗora hoton kati ('Upload Board Photo') + aunin Multimeter -> 'AI Scan'.\n"
            "   • Tab 3 (🧬 IC Programmer): Rubuta lambar IC (e.g. W25Q64) ko waya (iPhone, Samsung)\n"
            "     ka danna 'Detect' don ganin Pinout da hanyar Flashing.\n"
            "   • Tab 4 (🧾 Receipts): Danna '👁️ Preview', 'Export PDF', ko '🖨️ Print Now' don rasiti.\n"
            "   • Tab 5 (📐 PCB Studio): Rubuta sunan kowane kati -> '⚡ Generate' -> '🔍 Zoom'\n"
            "     (2000x1400 Scrollable & Draggable) ko '💾 Export PCB' (PDF & Gerber .gbr).\n\n"
            "3. 🛒 SPARE PARTS, 🛡️ IMEI/USB CHECK, 👑 ADMIN & ⚙️ SETTINGS:\n"
            "   • Admin Dashboard: Yana lissafa jimillar kuɗin shiga, riba, da adana komai ta atomatik.\n"
            "   • Settings: Saka Gemini AI Key, Termii SMS Key, da Neon Cloud URL a nan.\n"
        )
        self.txt_user_manual.insert(tk.END, manual_body)

    def new_ask_help(self):
        q = self.entry_help_query.get().strip()
        if not q:
            return
        ql = q.lower()
        if "deposit" in ql or "kudi" in ql:
            ans = "💰 DEPOSIT: Bayan Engineer ya sa farashi ('APPROVED'), danna na'urar a gefen dama na Reception, zaɓi '✅ Paid Deposit' ka rubuta kuɗin -> '💾 Save'."
        elif "pcb" in ql or "gerber" in ql:
            ans = "📐 PCB STUDIO: Shiga Tab 5, rubuta sunan katin -> '⚡ Generate'. Danna '🔍 Zoom Full Screen' don jawo babban zanen 2000x1400, ko '💾 Export PCB' don Gerber & PDF."
        elif "sun king" in ql or "sunking" in ql or "solar" in ql:
            ans = "🔋 SUN KING: Shiga Tab 2 (AI Diagnostics), danna maɓallin '🔋 SunKing', ɗora hoton katin + aunin Multimeter (3.2V Bat) -> 'AI Scan'."
        elif "flash" in ql or "ic" in ql:
            ans = "🧬 FLASHING & IC: Shiga Tab 3 (IC Programmer), rubuta sunan wayar ko lambar IC (e.g. W25Q64) -> 'Detect' don ganin Pinout da kayan Flashing."
        else:
            ans = f"💡 BAYANI GAME DA '{q.upper()}': Duba cikakken tsarin shafuka da ke ƙasa, ko ka saka Gemini API Key a Settings don amsoshin AI kai tsaye!"

        api_key = os.environ.get("GEMINI_API_KEY", "").strip()
        if api_key:
            try:
                from google import genai
                client = genai.Client(api_key=api_key)
                live_menus = [w.cget("text") for w in self.sidebar_frame.winfo_children() if isinstance(w, ctk.CTkButton)]
                prompt = f"You are the built-in user guide assistant for 'Sunvolt Tech Hub'. Active menus: {live_menus}. Answer clearly in Hausa & English: {q}"
                resp = client.models.generate_content(model="gemini-2.5-flash", contents=prompt)
                ans = f"🤖 AI GUIDE ANSWER:\n{resp.text.strip()}"
            except Exception:
                pass
        self.txt_user_manual.insert("1.0", f"\n================ AMSAR TAMBAYARKA ================\n{ans}\n==================================================\n\n")

    SunvoltApp.__init__ = new_init
    SunvoltApp.show_user_guide_view = new_show_user_guide
    SunvoltApp.action_ask_manual_help = new_ask_help

_sv_patch_sunvolt_v2026()


if __name__ == "__main__":
    app = SunvoltApp()
    app.mainloop()
