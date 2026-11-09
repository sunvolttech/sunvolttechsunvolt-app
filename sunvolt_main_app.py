import tkinter as tk
from tkinter import filedialog
import customtkinter as ctk
import psycopg2
import random
from datetime import datetime

NEON_CONNECTION_STRING = "postgresql://neondb_owner:npg_1CmIlyGAijs2@ep-sparkling-cell-axzagjek-pooler.c-4.us-east-2.aws.neon.tech/neondb?sslmode=require&channel_binding=require"

LANG_TEXT = {
    "Hausa": {
        "title": "Sunvolt Tech Hub - Master Pro v9.0",
        "select_lang": "Zaɓi Harshe / Language",
        "login_title": "Shigar da Bayanan Ma'aikaci",
        "select_role": "Zaɓi Matsayinka:",
        "login_btn": "Shiga Manhaja (Login)",
        "reception": "Karɓar Baki (Reception)",
        "engineer": "Babban Engineer (Workbench)",
        "parts": "Kasuwar Kayan Gyara (Parts)",
        "admin": "Allon Ubangida (Admin)",
        "cust_name": "Sunan Abokin Ciniki:",
        "cust_phone": "Lambar Waya:",
        "cust_nin": "Lambar NIN (NIMC):",
        "dev_type": "Nau'in Na'ura:",
        "dev_model": "Kalan Na'ura (Model):",
        "fault": "Matsalar da Aka Faɗa:",
        "total_cost": "Jimillar Kuɗin Gyara (₦):",
        "deposit": "Kuɗin Ajiye (Deposit ₦):",
        "submit_btn": "✓ Tura Wajen Engineer",
        "save_deposit_btn": "💾 Ajiye Deposit",
        "eng_title": "Dandalin Injiniya & Universal IC Lab",
        "pending_jobs": "1. Ayyukan da Ke Jiran Farashi / Deposit:",
        "ready_jobs": "2. Ayyukan da Aka Biya Deposit (Shirye don Gyara):",
        "scan_btn": "🚀 Fara Binciken AI & Gano Wuri",
        "set_price_btn": "💰 Yanke Farashi & Tura (SMS 1)",
        "final_sms_btn": "🔔 Kammala Gyara & Tura Ticket (SMS 2)",
        "view_receipt_btn": "🖨️ Buga Receipt",
        "status": "Sakamakon Binciken AI & Yadda Za a Gyara:",
        "status_idle": "Zaɓi na'ura daga jerin sama sannan ka danna Scan...",
        "status_scanning": "🛡️ AI tana binciken wutar katin, ICs, da firmware...",
        "status_flash": "🔄 Ana auna siginar logic da taswirar PCB...",
        "access_denied": "[⚠️] Kuskure: Ba ka da ikon shiga wannan sashin!",
        "admin_title": "📊 Allon Lissafin Kuɗi na Ubangida (Admin)",
        "total_revenue": "Jimillar Kuɗin da Aka Tara:",
        "total_profit": "Ribar Kamfani (20% Net Profit):",
        "total_completed": "Ayyukan da Aka Kammala:",
        "parts_title": "🛒 Kasuwar Kayan Gyara & Stock Management"
    },
    "English": {
        "title": "Sunvolt Tech Hub - Master Pro v9.0",
        "select_lang": "Select Language / Harshe",
        "login_title": "Staff Authentication Portal",
        "select_role": "Select Your Role:",
        "login_btn": "Authenticate & Login",
        "reception": "Receptionist (Front Desk)",
        "engineer": "Senior Engineer (Workbench)",
        "parts": "Spare Parts Marketplace",
        "admin": "Shop Owner (Admin Dashboard)",
        "cust_name": "Customer Full Name:",
        "cust_phone": "Phone Number:",
        "cust_nin": "NIN Identity (NIMC):",
        "dev_type": "Device Type:",
        "dev_model": "Device Model:",
        "fault": "Reported Fault:",
        "total_cost": "Total Repair Cost (₦):",
        "deposit": "Advance Deposit (₦):",
        "submit_btn": "✓ Forward to Engineer",
        "save_deposit_btn": "💾 Save Deposit",
        "eng_title": "Senior Engineer & Universal IC Programming Lab",
        "pending_jobs": "1. Pending Intake & Deposit Queue:",
        "ready_jobs": "2. Deposit-Paid Devices (Ready for Lab):",
        "scan_btn": "🚀 Run AI Board & Firmware Scan",
        "set_price_btn": "💰 Approve Quote & Send (SMS 1)",
        "final_sms_btn": "🔔 Complete Repair & Send Ticket (SMS 2)",
        "view_receipt_btn": "🖨️ Print Selected Receipt",
        "status": "AI Diagnostic Report & Replacement Guide:",
        "status_idle": "Select a paid device above and click Scan...",
        "status_scanning": "🛡️ AI scanning circuit rails, ICs, and firmware...",
        "status_flash": "🔄 Mapping PCB coordinates & logic states...",
        "access_denied": "[⚠️] Access Denied: Unauthorized role!",
        "admin_title": "📊 Central Financial Owner Dashboard",
        "total_revenue": "Total Accumulated Revenue:",
        "total_profit": "Company Net Profit (20% Yield):",
        "total_completed": "Completed Repairs:",
        "parts_title": "🛒 Spare Parts Marketplace & Inventory"
    }
}

SUNVOLT_JOB_QUEUE = []
SUNVOLT_HISTORY_ARCHIVE = []
SUNVOLT_ADMIN_FINANCES = {"total_revenue": 0.0, "total_profit": 0.0, "total_completed": 0}
SUNVOLT_PARTS_INVENTORY = [
    {"name": "Infinix / Tecno OLED Display Screen", "price": 18500, "stock": 12},
    {"name": "High-Voltage Inverter Mosfet (IRF3205 - 5pcs)", "price": 4500, "stock": 30},
    {"name": "Solar Charge Controller 60A Main Control IC", "price": 7200, "stock": 15},
    {"name": "Industrial Sewing Machine Servo IPM Module", "price": 14000, "stock": 8},
    {"name": "Universal SMPS PWM Controller (UC3842) + PC817", "price": 3500, "stock": 40},
    {"name": "Winbond 25Q64 / 25Q128 Blank BIOS Flash IC", "price": 2500, "stock": 25}
]
class SunvoltApp(ctk.CTk):
    def __init__(self):
        super().__init__()
        ctk.set_appearance_mode("dark")
        ctk.set_default_color_theme("blue")
        self.current_lang = "Hausa"
        self.user_role = "receptionist"
        self.title(LANG_TEXT[self.current_lang]["title"])
        self.geometry("1300x770")
        self.initialize_neon_database()
        
        self.grid_columnconfigure(1, weight=1)
        self.grid_rowconfigure(0, weight=1)
        
        self.sidebar_frame = ctk.CTkFrame(self, width=240, corner_radius=0, fg_color="#111111")
        self.sidebar_frame.grid(row=0, column=0, sticky="nsew")
        
        self.logo_label = ctk.CTkLabel(self.sidebar_frame, text="⚡ SUNVOLT", font=ctk.CTkFont(size=24, weight="bold"), text_color="#FFB300")
        self.logo_label.grid(row=0, column=0, padx=20, pady=(25, 20))
        
        self.role_badge = ctk.CTkLabel(self.sidebar_frame, text="LOCK", font=ctk.CTkFont(size=12, weight="bold"), text_color="#FF3D00")
        self.role_badge.grid(row=1, column=0, padx=20, pady=(0, 20))
        
        self.btn_reception = ctk.CTkButton(self.sidebar_frame, text=LANG_TEXT[self.current_lang]["reception"], fg_color="transparent", text_color="white", hover_color="#222222", anchor="w", command=self.show_reception_view)
        self.btn_reception.grid(row=2, column=0, padx=20, pady=8, sticky="ew")
        
        self.btn_engineer = ctk.CTkButton(self.sidebar_frame, text=LANG_TEXT[self.current_lang]["engineer"], fg_color="transparent", text_color="white", hover_color="#222222", anchor="w", command=self.show_engineer_view)
        self.btn_engineer.grid(row=3, column=0, padx=20, pady=8, sticky="ew")

        self.btn_parts = ctk.CTkButton(self.sidebar_frame, text=LANG_TEXT[self.current_lang]["parts"], fg_color="transparent", text_color="white", hover_color="#222222", anchor="w", command=self.show_parts_view)
        self.btn_parts.grid(row=4, column=0, padx=20, pady=8, sticky="ew")

        self.btn_admin = ctk.CTkButton(self.sidebar_frame, text=LANG_TEXT[self.current_lang]["admin"], fg_color="transparent", text_color="white", hover_color="#222222", anchor="w", command=self.show_admin_view)
        self.btn_admin.grid(row=5, column=0, padx=20, pady=8, sticky="ew")
        
        self.lang_label = ctk.CTkLabel(self.sidebar_frame, text=LANG_TEXT[self.current_lang]["select_lang"], font=ctk.CTkFont(size=12))
        self.lang_label.grid(row=6, column=0, padx=20, pady=(100, 5))
        
        self.lang_menu = ctk.CTkOptionMenu(self.sidebar_frame, values=["Hausa", "English"], button_color="#FFB300", dropdown_hover_color="#FFB300", command=self.change_language)
        self.lang_menu.grid(row=7, column=0, padx=20, pady=10, sticky="ew")
        
        self.main_frame = ctk.CTkFrame(self, corner_radius=10, fg_color="#1A1A1A")
        self.main_frame.grid(row=0, column=1, padx=20, pady=20, sticky="nsew")
        self.main_frame.grid_columnconfigure(0, weight=1)
        self.main_frame.grid_rowconfigure(0, weight=1)
        self.show_login_view()

    def change_language(self, new_lang):
        self.current_lang = new_lang
        self.title(LANG_TEXT[self.current_lang]["title"])
        self.btn_reception.configure(text=LANG_TEXT[self.current_lang]["reception"])
        self.btn_engineer.configure(text=LANG_TEXT[self.current_lang]["engineer"])
        self.btn_parts.configure(text=LANG_TEXT[self.current_lang]["parts"])
        self.btn_admin.configure(text=LANG_TEXT[self.current_lang]["admin"])
        self.lang_label.configure(text=LANG_TEXT[self.current_lang]["select_lang"])
        if hasattr(self, 'current_view'):
            if self.current_view == "login": self.show_login_view()
            elif self.current_view == "reception": self.show_reception_view()
            elif self.current_view == "engineer": self.show_engineer_view()
            elif self.current_view == "parts": self.show_parts_view()
            elif self.current_view == "admin": self.show_admin_view()

    def clear_main_frame(self):
        for widget in self.main_frame.winfo_children(): widget.destroy()

    def show_login_view(self):
        self.current_view = "login"
        self.clear_main_frame()
        t = LANG_TEXT[self.current_lang]
        login_box = ctk.CTkFrame(self.main_frame, width=450, height=350, fg_color="#111111", corner_radius=12)
        login_box.grid(row=0, column=0, padx=20, pady=20)
        login_box.grid_propagate(False)
        ctk.CTkLabel(login_box, text=t["login_title"], font=ctk.CTkFont(size=18, weight="bold"), text_color="#FFB300").pack(pady=(40, 20))
        ctk.CTkLabel(login_box, text=t["select_role"], font=ctk.CTkFont(size=13)).pack(pady=5)
        self.login_role_menu = ctk.CTkOptionMenu(login_box, width=280, values=["Receptionist", "Senior Engineer", "Shop Owner (Admin)"], button_color="#FFB300")
        self.login_role_menu.pack(pady=15)
        ctk.CTkButton(login_box, text=t["login_btn"], fg_color="#FFB300", text_color="black", hover_color="#FFA000", width=180, height=38, font=ctk.CTkFont(weight="bold"), command=self.action_login).pack(pady=25)

    def action_login(self):
        role = self.login_role_menu.get()
        if role == "Receptionist":
            self.user_role = "receptionist"
            self.role_badge.configure(text="🔒 FRONT DESK ONLY", text_color="#FF9100")
            self.show_reception_view()
        elif role == "Senior Engineer":
            self.user_role = "engineer"
            self.role_badge.configure(text="🔓 ENGINEER ACCESS", text_color="#00E676")
            self.show_engineer_view()
        else:
            self.user_role = "admin"
            self.role_badge.configure(text="👑 SHOP OWNER (ADMIN)", text_color="#D500F9")
            self.show_admin_view()

    def show_reception_view(self):
        self.current_view = "reception"
        self.clear_main_frame()
        t = LANG_TEXT[self.current_lang]
        if self.user_role == "engineer":
            ctk.CTkLabel(self.main_frame, text=t["access_denied"], font=ctk.CTkFont(size=16, weight="bold"), text_color="#FF3D00").grid(row=0, column=0, padx=40, pady=40, sticky="w")
            return
        self.main_frame.grid_rowconfigure(0, weight=0)
        self.main_frame.grid_columnconfigure(0, weight=1)
        self.main_frame.grid_columnconfigure(1, weight=1)
        
        left_frame = ctk.CTkFrame(self.main_frame, fg_color="transparent")
        left_frame.grid(row=0, column=0, padx=20, pady=20, sticky="nsew")
        ctk.CTkLabel(left_frame, text=t["reception"], font=ctk.CTkFont(size=20, weight="bold"), text_color="#FFB300").pack(anchor="w", pady=(10, 15))
        
        ctk.CTkLabel(left_frame, text=t["cust_name"]).pack(anchor="w", pady=2)
        self.entry_name = ctk.CTkEntry(left_frame, width=340, fg_color="#2B2B2B")
        self.entry_name.pack(anchor="w", pady=5)
        ctk.CTkLabel(left_frame, text=t["cust_phone"]).pack(anchor="w", pady=2)
        self.entry_phone = ctk.CTkEntry(left_frame, width=340, fg_color="#2B2B2B")
        self.entry_phone.pack(anchor="w", pady=5)
        ctk.CTkLabel(left_frame, text=t["cust_nin"]).pack(anchor="w", pady=2)
        self.entry_nin = ctk.CTkEntry(left_frame, width=340, fg_color="#2B2B2B")
        self.entry_nin.pack(anchor="w", pady=5)
        ctk.CTkLabel(left_frame, text=t["dev_type"]).pack(anchor="w", pady=2)
        self.menu_dev_type = ctk.CTkOptionMenu(left_frame, width=340, values=["Phone", "Laptop", "Inverter", "Charge_Controller", "Sewing_Machine", "Universal_Unknown"])
        self.menu_dev_type.pack(anchor="w", pady=5)
        ctk.CTkLabel(left_frame, text=t["dev_model"]).pack(anchor="w", pady=2)
        self.entry_model = ctk.CTkEntry(left_frame, width=340, fg_color="#2B2B2B")
        self.entry_model.pack(anchor="w", pady=5)
        ctk.CTkLabel(left_frame, text=t["fault"]).pack(anchor="w", pady=2)
        self.txt_fault = ctk.CTkEntry(left_frame, width=340, height=50, fg_color="#2B2B2B")
        self.txt_fault.pack(anchor="w", pady=5)
        ctk.CTkButton(left_frame, text=t["submit_btn"], fg_color="#FFB300", text_color="black", hover_color="#FFA000", width=200, height=38, font=ctk.CTkFont(weight="bold"), command=self.action_submit_order).pack(anchor="w", pady=15)
        
        right_frame = ctk.CTkFrame(self.main_frame, fg_color="#111111", corner_radius=10, width=420)
        right_frame.grid(row=0, column=1, padx=20, pady=40, sticky="nsew")
        right_frame.pack_propagate(False)
        ctk.CTkLabel(right_frame, text="💰 Step 3: Collect Deposit", font=ctk.CTkFont(size=16, weight="bold"), text_color="#00E676").pack(anchor="w", padx=20, pady=15)
        self.lbl_selected_job_info = ctk.CTkLabel(right_frame, text="No active quote from Engineer yet.", font=ctk.CTkFont(size=13), justify="left")
        self.lbl_selected_job_info.pack(anchor="w", padx=20, pady=10)
        ctk.CTkLabel(right_frame, text=t["deposit"]).pack(anchor="w", padx=20, pady=2)
        self.entry_deposit = ctk.CTkEntry(right_frame, width=340, fg_color="#2B2B2B")
        self.entry_deposit.pack(anchor="w", padx=20, pady=5)
        ctk.CTkButton(right_frame, text=t["save_deposit_btn"], fg_color="#00E676", text_color="black", hover_color="#00C853", width=200, height=38, font=ctk.CTkFont(weight="bold"), command=self.action_save_deposit).pack(anchor="w", padx=20, pady=20)
        self.refresh_reception_deposit_view()
    def show_engineer_view(self):
        t = LANG_TEXT[self.current_lang]
        if self.user_role == "receptionist":
            self.clear_main_frame()
            ctk.CTkLabel(self.main_frame, text=t["access_denied"], font=ctk.CTkFont(size=16, weight="bold"), text_color="#FF3D00").grid(row=0, column=0, padx=40, pady=40, sticky="w")
            return
        self.current_view = "engineer"
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
            ("📋 1. Pending & Quotes", "intake"),
            ("🔬 2. AI Diagnostics & Board Map", "lab"),
            ("🧬 3. Universal IC Programmer", "programmer"),
            ("🧾 4. Receipts & History", "history")
        ]
        for idx, (label, key) in enumerate(sub_pages):
            btn = ctk.CTkButton(nav_bar, text=label, width=215, height=34, fg_color="#2B2B2B", text_color="white", font=ctk.CTkFont(size=12, weight="bold"), command=lambda k=key: self.switch_engineer_subpage(k))
            btn.grid(row=0, column=idx, padx=5, pady=6)
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
            ctk.CTkLabel(self.eng_content_area, text=t["pending_jobs"], font=ctk.CTkFont(size=14, weight="bold"), text_color="#FFB300").pack(anchor="w", padx=25, pady=(20, 8))
            self.pending_listbox = tk.Listbox(self.eng_content_area, width=88, height=9, bg="#1E1E1E", fg="white", bd=0, font=("Helvetica", 11))
            self.pending_listbox.pack(anchor="w", padx=25, pady=5)
            self.pending_listbox.bind('<<ListboxSelect>>', self.on_select_pending_job)
            
            self.lbl_intake_details = ctk.CTkLabel(self.eng_content_area, text="Select a new device above to inspect fault & set repair quotation.", font=ctk.CTkFont(size=13), text_color="#B0BEC5")
            self.lbl_intake_details.pack(anchor="w", padx=25, pady=12)
            
            quote_row = ctk.CTkFrame(self.eng_content_area, fg_color="transparent")
            quote_row.pack(anchor="w", padx=25, pady=10)
            ctk.CTkLabel(quote_row, text=t["total_cost"], font=ctk.CTkFont(size=13, weight="bold")).pack(side="left", padx=(0, 10))
            self.entry_final_cost = ctk.CTkEntry(quote_row, width=200, placeholder_text="e.g. 15000", fg_color="#2B2B2B")
            self.entry_final_cost.pack(side="left", padx=(0, 15))
            ctk.CTkButton(quote_row, text=t["set_price_btn"], fg_color="#FF9100", text_color="black", hover_color="#FF6D00", width=240, height=36, font=ctk.CTkFont(weight="bold"), command=self.action_engineer_set_price).pack(side="left")

        elif page_key == "lab":
            self.eng_content_area.grid_columnconfigure(0, weight=3)
            self.eng_content_area.grid_columnconfigure(1, weight=2)
            
            lab_left = ctk.CTkFrame(self.eng_content_area, fg_color="transparent")
            lab_left.grid(row=0, column=0, padx=15, pady=10, sticky="nsew")
            
            hw_frame = ctk.CTkFrame(lab_left, fg_color="#1A1A1A", corner_radius=8)
            hw_frame.pack(anchor="w", pady=(5, 6))
            self.selected_hw_mode = "Phone"
            self.board_image_path = None
            self.hw_buttons = {}
            hw_modes = [("📱 Phone", "Phone"), ("💻 Laptop", "Laptop"), ("⚡ Inverter", "Inverter"), ("☀️ CC", "Charge_Controller"), ("🧵 Sewing", "Sewing_Machine"), ("🌐 Universal", "Universal_Unknown")]
            for idx, (label_txt, mode_key) in enumerate(hw_modes):
                btn = ctk.CTkButton(hw_frame, text=label_txt, width=90, height=28, fg_color="#FFB300" if mode_key == "Phone" else "#2B2B2B", text_color="black" if mode_key == "Phone" else "white", font=ctk.CTkFont(size=11, weight="bold"), command=lambda m=mode_key: self.select_hardware_mode(m))
                btn.grid(row=0, column=idx, padx=3, pady=5)
                self.hw_buttons[mode_key] = btn

            probe_frame = ctk.CTkFrame(lab_left, fg_color="#1A1A1A", corner_radius=8)
            probe_frame.pack(anchor="w", pady=(0, 6))
            ctk.CTkButton(probe_frame, text="📸 Upload Board Photo", width=150, height=28, fg_color="#37474F", font=ctk.CTkFont(size=11, weight="bold"), command=self.action_upload_board_photo).grid(row=0, column=0, padx=5, pady=5)
            self.entry_voltage_probe = ctk.CTkEntry(probe_frame, width=390, height=28, placeholder_text="Multimeter / Symptom (e.g. 12V In / 0V Out, IC dead)...", fg_color="#2B2B2B", font=ctk.CTkFont(size=11))
            self.entry_voltage_probe.grid(row=0, column=1, padx=5, pady=5)

            ctk.CTkLabel(lab_left, text=t["ready_jobs"], font=ctk.CTkFont(size=12, weight="bold"), text_color="#00E676").pack(anchor="w", pady=(2, 2))
            self.ready_listbox = tk.Listbox(lab_left, width=74, height=3, bg="#1E1E1E", fg="white", bd=0, font=("Helvetica", 10))
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
            ctk.CTkButton(lab_btns, text=t["scan_btn"], fg_color="#2296F3", text_color="white", width=240, height=36, font=ctk.CTkFont(weight="bold"), command=self.simulate_usb_scan).pack(side="left", padx=(0, 12))
            ctk.CTkButton(lab_btns, text=t["final_sms_btn"], fg_color="#4CAF50", text_color="white", width=270, height=36, font=ctk.CTkFont(weight="bold"), command=self.action_send_final_sms).pack(side="left")

            # --- GEFEN DAMA: TASWIRAR GANO WURI A JIKIN BOARD (VISUAL PCB LOCATOR) ---
            lab_right = ctk.CTkFrame(self.eng_content_area, fg_color="#1A1A1A", corner_radius=8)
            lab_right.grid(row=0, column=1, padx=15, pady=15, sticky="nsew")
            ctk.CTkLabel(lab_right, text="🗺️ PCB Component Visual Locator", font=ctk.CTkFont(size=13, weight="bold"), text_color="#00E676").pack(pady=(10, 5))
            self.pcb_canvas = tk.Canvas(lab_right, width=320, height=310, bg="#0B3B24", highlightthickness=2, highlightbackground="#FFB300")
            self.pcb_canvas.pack(pady=8, padx=12)
            self.draw_base_pcb_map()
            self.lbl_pcb_coords = ctk.CTkLabel(lab_right, text="Awaiting AI Scan to pinpoint faulty IC / FET...", font=ctk.CTkFont(size=11), text_color="#B0BEC5")
            self.lbl_pcb_coords.pack(pady=5)

        elif page_key == "programmer":
            self.build_universal_programmer_ui()

        elif page_key == "history":
            self.eng_content_area.grid_columnconfigure(0, weight=1)
            self.eng_content_area.grid_columnconfigure(1, weight=1)
            
            hist_left = ctk.CTkFrame(self.eng_content_area, fg_color="transparent")
            hist_left.grid(row=0, column=0, padx=25, pady=20, sticky="nsew")
            ctk.CTkLabel(hist_left, text="📚 Completed Repairs Archive (History):", font=ctk.CTkFont(size=14, weight="bold"), text_color="#FFB300").pack(anchor="w", pady=(0, 8))
            self.history_listbox = tk.Listbox(hist_left, width=48, height=16, bg="#1E1E1E", fg="white", bd=0, font=("Helvetica", 11))
            self.history_listbox.pack(anchor="w", pady=5)
            self.history_listbox.bind('<<ListboxSelect>>', self.on_select_history_job)
            ctk.CTkButton(hist_left, text=t["view_receipt_btn"], fg_color="#9C27B0", text_color="white", width=250, height=38, font=ctk.CTkFont(weight="bold"), command=self.action_trigger_print_view).pack(anchor="w", pady=12)

            hist_right = ctk.CTkFrame(self.eng_content_area, width=380, height=430, fg_color="#F5F5F5", corner_radius=6)
            hist_right.grid(row=0, column=1, padx=25, pady=20, sticky="ne")
            hist_right.pack_propagate(False)
            self.txt_receipt = tk.Text(hist_right, width=44, height=22, bg="#F5F5F5", fg="black", bd=0, font=("Courier", 10))
            self.txt_receipt.pack(pady=10, padx=10)
            self.txt_receipt.insert(tk.END, "Select a completed job from History on the left\nto view or print its official thermal receipt.")

        self.refresh_all_engineer_lists()
    def draw_base_pcb_map(self, highlight_x=None, highlight_y=None, label=""):
        if not hasattr(self, 'pcb_canvas'):
            return
        self.pcb_canvas.delete("all")
        # Zana layukan circuit (PCB Traces)
        for i in range(20, 310, 35):
            self.pcb_canvas.create_line(15, i, 305, i, fill="#145A32", width=1)
            self.pcb_canvas.create_line(i, 15, i, 295, fill="#145A32", width=1)
        # Zana sassan katin (ICs, Mosfets, Capacitors)
        self.pcb_canvas.create_rectangle(45, 45, 115, 115, fill="#1C2833", outline="#95A5A6", width=2)
        self.pcb_canvas.create_text(80, 80, text="MAIN MCU\n/ CPU", fill="white", font=("Arial", 8, "bold"))
        
        self.pcb_canvas.create_rectangle(195, 45, 275, 105, fill="#1C2833", outline="#95A5A6", width=2)
        self.pcb_canvas.create_text(235, 75, text="POWER / FET\nSTAGE", fill="white", font=("Arial", 8, "bold"))
        
        self.pcb_canvas.create_rectangle(45, 195, 125, 260, fill="#1C2833", outline="#95A5A6", width=2)
        self.pcb_canvas.create_text(85, 227, text="BIOS / FLASH\nEEPROM", fill="white", font=("Arial", 8, "bold"))
        
        self.pcb_canvas.create_rectangle(195, 195, 275, 260, fill="#1C2833", outline="#95A5A6", width=2)
        self.pcb_canvas.create_text(235, 227, text="CHARGING /\nDRIVER IC", fill="white", font=("Arial", 8, "bold"))

        # Idan AI ta gano matsala, ta haska jan da'ira a wurin
        if highlight_x and highlight_y:
            self.pcb_canvas.create_oval(highlight_x-28, highlight_y-28, highlight_x+28, highlight_y+28, outline="#FF1744", width=4)
            self.pcb_canvas.create_oval(highlight_x-12, highlight_y-12, highlight_x+12, highlight_y+12, fill="#FF1744", outline="white")
            self.pcb_canvas.create_text(highlight_x, highlight_y+38, text=f"⚠ FAULT: {label}", fill="#FFEB3B", font=("Arial", 9, "bold"))

    def build_universal_programmer_ui(self):
        self.eng_content_area.grid_columnconfigure(0, weight=1)
        self.eng_content_area.grid_columnconfigure(1, weight=2)
        
        prog_left = ctk.CTkFrame(self.eng_content_area, fg_color="#1A1A1A", corner_radius=8)
        prog_left.grid(row=0, column=0, padx=20, pady=15, sticky="nsew")
        
        ctk.CTkLabel(prog_left, text="🧬 Universal IC & Firmware Lab", font=ctk.CTkFont(size=15, weight="bold"), text_color="#00E676").pack(anchor="w", padx=15, pady=(15, 5))
        ctk.CTkLabel(prog_left, text="Select IC Family / Chip Architecture:", font=ctk.CTkFont(size=12)).pack(anchor="w", padx=15, pady=(8, 2))
        
        self.ic_family_menu = ctk.CTkOptionMenu(
            prog_left, width=280, button_color="#FFB300", text_color="black",
            values=[
                "SPI Flash / Laptop & Inverter BIOS (25Qxx)",
                "Serial EEPROM / TV & Car ECU (24Cxx / 93Cxx)",
                "Microchip PIC / Atmel AVR MCU (PIC16F / ATmega)",
                "ARM Cortex / STM32 / Charge Controller MCU",
                "Inverter DSP / Pure Sine Wave MCU (dsPIC / EG8010)",
                "Smartphone eMMC / UFS Storage & Boot Repair"
            ],
            command=self.update_programmer_guide
        )
        self.ic_family_menu.pack(anchor="w", padx=15, pady=5)
        
        ctk.CTkLabel(prog_left, text="Chip Part Number (e.g. W25Q64, PIC16F877A):", font=ctk.CTkFont(size=12)).pack(anchor="w", padx=15, pady=(8, 2))
        self.entry_chip_part = ctk.CTkEntry(prog_left, width=280, placeholder_text="Enter IC number...", fg_color="#2B2B2B")
        self.entry_chip_part.pack(anchor="w", padx=15, pady=5)
        
        ctk.CTkButton(prog_left, text="📂 Load Firmware (.BIN / .HEX)", width=280, height=34, fg_color="#37474F", font=ctk.CTkFont(weight="bold"), command=self.action_load_firmware_file).pack(anchor="w", padx=15, pady=10)
        ctk.CTkButton(prog_left, text="⚡ Generate Wiring & Flash Guide", width=280, height=38, fg_color="#00E676", text_color="black", font=ctk.CTkFont(weight="bold"), command=lambda: self.update_programmer_guide(self.ic_family_menu.get())).pack(anchor="w", padx=15, pady=5)

        prog_right = ctk.CTkFrame(self.eng_content_area, fg_color="#1A1A1A", corner_radius=8)
        prog_right.grid(row=0, column=1, padx=15, pady=15, sticky="nsew")
        ctk.CTkLabel(prog_right, text="🛠️ Required Programmer Hardware, Pinout & Step-by-Step Guide:", font=ctk.CTkFont(size=14, weight="bold"), text_color="#FFB300").pack(anchor="w", padx=20, pady=(15, 8))
        
        self.txt_prog_guide = tk.Text(prog_right, width=68, height=22, bg="#111111", fg="#E0F2F1", bd=0, font=("Consolas", 10))
        self.txt_prog_guide.pack(padx=20, pady=8, fill="both", expand=True)
        self.update_programmer_guide("SPI Flash / Laptop & Inverter BIOS (25Qxx)")

    def action_load_firmware_file(self):
        fw_path = filedialog.askopenfilename(title="Select Firmware Binary or Hex File", filetypes=[("Firmware Files", "*.bin *.hex *.rom *.img")])
        if fw_path:
            fname = fw_path.split("/")[-1]
            self.txt_prog_guide.insert(tk.END, f"\n[✓] FIRMWARE LOADED: {fname} — Ready to write to chip!\n")
    def update_programmer_guide(self, ic_type):
        chip = self.entry_chip_part.get().strip() if hasattr(self, 'entry_chip_part') and self.entry_chip_part.get().strip() else "Selected Chip"
        guides = {
            "SPI Flash / Laptop & Inverter BIOS (25Qxx)": (
                f"TARGET CHIP: {chip} (8-Pin SOIC8 / DIP8 SPI Flash)\n"
                "================================================================\n"
                "1. REQUIRED HARDWARE TOOLS (KAYAN AIKI):\n"
                "   • CH341A USB Programmer OR XGecu T48 / TL866II Plus\n"
                "   • SOIC8 Test Clip (for in-circuit) OR Hot Air Rework Station\n\n"
                "2. PINOUT WIRING (YADDA ZA A HAƊA ƘAFAFUN IC):\n"
                "   • Pin 1 (/CS)  --> Programmer CS   | Pin 8 (VCC) --> 3.3V\n"
                "   • Pin 2 (DO)   --> Programmer MISO | Pin 7 (/HOLD)-> 3.3V\n"
                "   • Pin 4 (GND)  --> Programmer GND  | Pin 5 (DI)  --> MOSI\n\n"
                "3. STEP-BY-STEP PROGRAMMING (MATAKAN YIN PROGRAMMING):\n"
                "   Step 1: Desolder the 8-pin chip using Hot Air at 320°C.\n"
                "   Step 2: Align Pin 1 dot on the chip with Pin 1 on ZIF socket.\n"
                "   Step 3: Click 'Detect / Read' and SAVE a backup file first.\n"
                "   Step 4: Click 'Erase' -> 'Blank Check' -> Load clean .BIN.\n"
                "   Step 5: Click 'Program / Write' and 'Verify' (100% OK)."
            ),
            "Serial EEPROM / TV & Car ECU (24Cxx / 93Cxx)": (
                f"TARGET CHIP: {chip} (I2C / Microwire Serial EEPROM)\n"
                "================================================================\n"
                "1. REQUIRED HARDWARE TOOLS:\n"
                "   • XGecu T48 / TL866II Plus OR RT809F / RT809H Programmer\n"
                "   • SOP8 to DIP8 Adapter Socket\n\n"
                "2. PINOUT WIRING:\n"
                "   • Pins 1,2,3 (A0-A2) --> GND | Pin 4 --> GND | Pin 8 --> 5.0V\n"
                "   • Pin 5 (SDA) --> Data       | Pin 6 (SCL) --> Clock\n\n"
                "3. STEP-BY-STEP PROGRAMMING:\n"
                "   Step 1: Clean solder flux off chip legs with Isopropyl Alcohol.\n"
                "   Step 2: Select exact part number (e.g., 24C02, 24C64, 93C46).\n"
                "   Step 3: Read & Backup existing data, then write clean .BIN/.HEX."
            ),
            "Microchip PIC / Atmel AVR MCU (PIC16F / ATmega)": (
                f"TARGET CHIP: {chip} (Inverter & Charge Controller MCU)\n"
                "================================================================\n"
                "1. REQUIRED HARDWARE TOOLS:\n"
                "   • PICkit 3 / PICkit 4 (Microchip PIC) OR USBasp (Atmel AVR)\n"
                "   • 5-Pin ICSP Header Dupont Jumper Wires\n\n"
                "2. ICSP PINOUT WIRING:\n"
                "   • Pin 1: MCLR / VPP (Reset)   | Pin 2: VDD (+5V Target Power)\n"
                "   • Pin 3: VSS (Ground)         | Pin 4: PGD (Data) | Pin 5: PGC\n\n"
                "3. STEP-BY-STEP PROGRAMMING:\n"
                "   Step 1: Connect the 5 ICSP wires to the board's ICSP header.\n"
                "   Step 2: Open MPLAB IPE (for PIC) or AVRDUDESS (for AVR).\n"
                "   Step 3: Load the .HEX firmware file and click 'Program'."
            ),
            "ARM Cortex / STM32 / Charge Controller MCU": (
                f"TARGET CHIP: {chip} (MPPT Solar & Sewing Machine Servo MCU)\n"
                "================================================================\n"
                "1. REQUIRED HARDWARE TOOLS:\n"
                "   • ST-Link V2 USB Debugger (SWD Interface)\n"
                "   • 4 Female-to-Female Jumper Wires\n\n"
                "2. SWD PINOUT WIRING:\n"
                "   • SWDIO --> Board SWDIO | SWCLK --> Board SWCLK\n"
                "   • GND   --> Board GND   | 3.3V  --> Board 3.3V\n\n"
                "3. STEP-BY-STEP PROGRAMMING:\n"
                "   Step 1: Launch STM32CubeProgrammer on PC.\n"
                "   Step 2: Click 'Connect', load .BIN/.HEX, and click 'Download'."
            ),
            "Inverter DSP / Pure Sine Wave MCU (dsPIC / EG8010)": (
                f"TARGET CHIP: {chip} (Pure Sine Wave Inverter Control Board)\n"
                "================================================================\n"
                "1. REQUIRED HARDWARE TOOLS:\n"
                "   • PICkit 3 / ICD3 Programmer (dsPIC30F2010 / dsPIC33)\n"
                "   • USB-to-TTL Serial Adapter (for EGS002 / EG8010)\n\n"
                "2. STEP-BY-STEP PROGRAMMING:\n"
                "   Step 1: Disconnect high-voltage battery & AC mains first!\n"
                "   Step 2: Supply 5V logic power to the control card.\n"
                "   Step 3: Flash Sine-Wave PWM .HEX file & verify 50Hz output."
            ),
            "Smartphone eMMC / UFS Storage & Boot Repair": (
                f"TARGET CHIP: {chip} (Mobile Dead-Boot & PAYG Unlock)\n"
                "================================================================\n"
                "1. REQUIRED HARDWARE TOOLS:\n"
                "   • EasyJTAG Plus / UFI Box / Medusa Pro II\n"
                "   • ISP Pinout Adapter (CMD, CLK, DAT0, GND) OR BGA Socket\n\n"
                "2. STEP-BY-STEP PROGRAMMING:\n"
                "   Step 1: Solder thin 0.1mm jumper wires to CLK, CMD, DAT0, GND.\n"
                "   Step 2: Identify eMMC/UFS, write Dump/Preloader & repair boot."
            )
        }
        self.txt_prog_guide.delete("1.0", tk.END)
        self.txt_prog_guide.insert(tk.END, guides.get(ic_type, ""))

    def select_hardware_mode(self, mode_key):
        self.selected_hw_mode = mode_key
        for key, btn in self.hw_buttons.items():
            btn.configure(fg_color="#FFB300" if key == mode_key else "#2B2B2B", text_color="black" if key == mode_key else "white")
        self.lbl_status_text.configure(text=f"Mode Set: [{mode_key}] Analyzer Ready.\nSelect paid device & click Run AI Scan.", text_color="#00E676")

    def action_upload_board_photo(self):
        file_path = filedialog.askopenfilename(title="Select PCB / Circuit Board Photo", filetypes=[("Image Files", "*.png *.jpg *.jpeg *.bmp")])
        if file_path:
            self.board_image_path = file_path
            short_name = file_path.split("/")[-1]
            self.lbl_status_text.configure(text=f"📸 Board Image Loaded: [{short_name}]\nAI Vision ready to inspect burnt traces & ICs.", text_color="#00E676")

    def show_parts_view(self):
        self.current_view = "parts"
        self.clear_main_frame()
        t = LANG_TEXT[self.current_lang]
        if self.user_role == "receptionist":
            ctk.CTkLabel(self.main_frame, text=t["access_denied"], font=ctk.CTkFont(size=16, weight="bold"), text_color="#FF3D00").grid(row=0, column=0, padx=40, pady=40, sticky="w")
            return
        self.main_frame.grid_rowconfigure(0, weight=0)
        self.main_frame.grid_rowconfigure(1, weight=0)
        self.main_frame.grid_rowconfigure(2, weight=1)
        self.main_frame.grid_columnconfigure(0, weight=1)
        
        ctk.CTkLabel(self.main_frame, text=t["parts_title"], font=ctk.CTkFont(size=20, weight="bold"), text_color="#00E676").grid(row=0, column=0, padx=30, pady=(20, 10), sticky="w")
        
        top_bar = ctk.CTkFrame(self.main_frame, fg_color="#111111", corner_radius=8)
        top_bar.grid(row=1, column=0, padx=30, pady=(0, 10), sticky="ew")
        
        self.entry_part_search = ctk.CTkEntry(top_bar, width=260, placeholder_text="🔍 Search IC, Mosfet, Screen...", fg_color="#2B2B2B")
        self.entry_part_search.pack(side="left", padx=10, pady=10)
        ctk.CTkButton(top_bar, text="Search", width=80, fg_color="#2296F3", command=self.refresh_parts_list).pack(side="left", padx=(0, 20))
        
        self.entry_new_part_name = ctk.CTkEntry(top_bar, width=220, placeholder_text="New Part Name...", fg_color="#2B2B2B")
        self.entry_new_part_name.pack(side="left", padx=5)
        self.entry_new_part_price = ctk.CTkEntry(top_bar, width=100, placeholder_text="Price (₦)", fg_color="#2B2B2B")
        self.entry_new_part_price.pack(side="left", padx=5)
        ctk.CTkButton(top_bar, text="+ Add Stock", width=110, fg_color="#00E676", text_color="black", font=ctk.CTkFont(weight="bold"), command=self.action_add_new_part).pack(side="left", padx=10)
        
        self.parts_scroll_frame = ctk.CTkScrollableFrame(self.main_frame, fg_color="#111111", corner_radius=8)
        self.parts_scroll_frame.grid(row=2, column=0, padx=30, pady=(0, 20), sticky="nsew")
        self.refresh_parts_list()

    def refresh_parts_list(self):
        for w in self.parts_scroll_frame.winfo_children():
            w.destroy()
        query = self.entry_part_search.get().lower().strip() if hasattr(self, 'entry_part_search') else ""
        for item in SUNVOLT_PARTS_INVENTORY:
            if query and query not in item["name"].lower():
                continue
            row_f = ctk.CTkFrame(self.parts_scroll_frame, height=52, fg_color="#1E1E1E", corner_radius=6)
            row_f.pack(fill="x", padx=10, pady=5)
            ctk.CTkLabel(row_f, text=f"{item['name']}   |   ₦ {item['price']:,}   |   In Stock: {item['stock']}", font=ctk.CTkFont(size=13, weight="bold")).pack(side="left", padx=15, pady=10)
            ctk.CTkButton(row_f, text="Order Part", width=110, fg_color="#FFB300", text_color="black", font=ctk.CTkFont(weight="bold"), command=lambda i=item: self.action_order_spare_part(i)).pack(side="right", padx=15)

    def action_add_new_part(self):
        name = self.entry_new_part_name.get().strip()
        price_str = self.entry_new_part_price.get().strip()
        if name and price_str.isdigit():
            SUNVOLT_PARTS_INVENTORY.insert(0, {"name": name, "price": int(price_str), "stock": 10})
            self.entry_new_part_name.delete(0, tk.END)
            self.entry_new_part_price.delete(0, tk.END)
    def show_admin_view(self):
        self.current_view = "admin"
        self.clear_main_frame()
        t = LANG_TEXT[self.current_lang]
        if self.user_role != "admin":
            ctk.CTkLabel(self.main_frame, text=t["access_denied"], font=ctk.CTkFont(size=16, weight="bold"), text_color="#FF3D00").grid(row=0, column=0, padx=40, pady=40, sticky="w")
            return
        ctk.CTkLabel(self.main_frame, text=t["admin_title"], font=ctk.CTkFont(size=22, weight="bold"), text_color="#D500F9").pack(anchor="w", padx=40, pady=(30, 20))
        for label_key, val_str, col in [
            ("total_revenue", f"₦ {SUNVOLT_ADMIN_FINANCES['total_revenue']:,}.00", "#FFB300"),
            ("total_profit", f"₦ {SUNVOLT_ADMIN_FINANCES['total_profit']:,}.00", "#00E676"),
            ("total_completed", str(int(SUNVOLT_ADMIN_FINANCES['total_completed'])), "#2296F3")
        ]:
            box = ctk.CTkFrame(self.main_frame, width=500, height=95, fg_color="#111111", corner_radius=10)
            box.pack(anchor="w", padx=40, pady=12)
            box.pack_propagate(False)
            ctk.CTkLabel(box, text=t[label_key], font=ctk.CTkFont(size=14)).pack(anchor="w", padx=20, pady=(12, 4))
            ctk.CTkLabel(box, text=val_str, font=ctk.CTkFont(size=22, weight="bold"), text_color=col).pack(anchor="w", padx=20)

    def action_submit_order(self):
        name = self.entry_name.get() or "Aliyu Ibrahim Kano"
        phone = self.entry_phone.get() or "08062571997"
        nin = self.entry_nin.get() or "12345678901 (VERIFIED)"
        dtype = self.menu_dev_type.get()
        model = self.entry_model.get() or "Infinix Hot 30"
        fault = self.txt_fault.get() or "EasyBuy PAYG Lock Bypass"
        ticket_id = f"SVT-{random.randint(1000, 9999)}"
        new_job = {
            "ticket_id": ticket_id, "name": name, "phone": phone, "nin": nin,
            "type": dtype, "model": model, "fault": fault, "deposit": "0",
            "cost": "0", "balance": "0", "stage": "1",
            "date": datetime.now().strftime("%Y-%m-%d %H:%M")
        }
        SUNVOLT_JOB_QUEUE.append(new_job)
        self.save_to_neon_db(new_job)
        for entry in [self.entry_name, self.entry_phone, self.entry_nin, self.entry_model, self.txt_fault]:
            entry.delete(0, tk.END)
        print(f"[Reception] Device routed to Engineer under Ticket #{ticket_id}.")

    def refresh_reception_deposit_view(self):
        self.active_deposit_job = next((j for j in SUNVOLT_JOB_QUEUE if j["stage"] == "3"), None)
        if self.active_deposit_job:
            j = self.active_deposit_job
            info = f"Customer: {j['name']}\nDevice: {j['type']} ({j['model']})\nQuoted Cost: ₦{j['cost']}.00"
            self.lbl_selected_job_info.configure(text=info, text_color="#00E676")
        else:
            self.lbl_selected_job_info.configure(text="No active quote from Engineer yet.", text_color="white")

    def action_save_deposit(self):
        if not getattr(self, 'active_deposit_job', None):
            return
        dep_val = self.entry_deposit.get() or "5000"
        self.active_deposit_job["deposit"] = dep_val
        try:
            self.active_deposit_job["balance"] = int(self.active_deposit_job["cost"]) - int(dep_val)
        except ValueError:
            self.active_deposit_job["balance"] = 10000
        self.active_deposit_job["stage"] = "4"
        self.update_neon_db(self.active_deposit_job)
        self.entry_deposit.delete(0, tk.END)
        print(f"[Reception] Deposit ₦{dep_val} saved for #{self.active_deposit_job['ticket_id']}.")
        self.refresh_reception_deposit_view()

    def refresh_all_engineer_lists(self):
        self.pending_jobs_cache = [j for j in SUNVOLT_JOB_QUEUE if j["stage"] in ("1", "3")]
        self.ready_jobs_cache = [j for j in SUNVOLT_JOB_QUEUE if j["stage"] == "4"]
        
        if hasattr(self, 'pending_listbox'):
            self.pending_listbox.delete(0, tk.END)
            for j in self.pending_jobs_cache:
                tag = " [Awaiting Quote]" if j["stage"] == "1" else f" [Quoted: ₦{j['cost']} - Awaiting Deposit]"
                self.pending_listbox.insert(tk.END, f" #{j['ticket_id']} | {j['name']} | {j['type']} ({j['model']}){tag}")
                
        if hasattr(self, 'ready_listbox'):
            self.ready_listbox.delete(0, tk.END)
            for j in self.ready_jobs_cache:
                self.ready_listbox.insert(tk.END, f" #{j['ticket_id']} | {j['name']} | {j['type']} ({j['model']}) | Deposit: ₦{j['deposit']} [READY]")
                
        if hasattr(self, 'history_listbox'):
            self.history_listbox.delete(0, tk.END)
            for j in SUNVOLT_HISTORY_ARCHIVE:
                self.history_listbox.insert(tk.END, f" #{j['ticket_id']} - {j['name']} ({j['model']}) - ₦{j['cost']}")

    def on_select_pending_job(self, event):
        if not self.pending_listbox.curselection():
            return
        idx = self.pending_listbox.curselection()[0]
        self.selected_pending_job = self.pending_jobs_cache[idx]
        j = self.selected_pending_job
        self.lbl_intake_details.configure(text=f"Selected: {j['name']} | Device: {j['type']} ({j['model']}) | Reported Fault: {j['fault']}", text_color="#FFB300")

    def on_select_ready_job(self, event):
        if not self.ready_listbox.curselection():
            return
        idx = self.ready_listbox.curselection()[0]
        self.selected_ready_job = self.ready_jobs_cache[idx]
        j = self.selected_ready_job
        self.lbl_status_text.configure(text=f"Loaded in Lab: {j['name']} ({j['model']})\nFault: {j['fault']} | Ready for AI Scan.", text_color="white")

    def on_select_history_job(self, event):
        if not self.history_listbox.curselection():
            return
        idx = self.history_listbox.curselection()[0]
        self.selected_history_job = SUNVOLT_HISTORY_ARCHIVE[idx]
        self.action_trigger_print_view()

    def simulate_usb_scan(self):
        if not hasattr(self, 'selected_ready_job'):
            self.lbl_status_text.configure(text="[⚠️] Please select a Deposit-Paid device from list #2 above!", text_color="#FF3D00")
            return
        self.lbl_status_text.configure(text=LANG_TEXT[self.current_lang]["status_scanning"], text_color="#FFB300")
        self.update()
        self.after(1500, self.simulate_flashing)

    def simulate_flashing(self):
        self.lbl_status_text.configure(text=LANG_TEXT[self.current_lang]["status_flash"], text_color="#2296F3")
        self.update()
        self.after(1500, self.finish_simulation)

    def finish_simulation(self):
        mode = getattr(self, 'selected_hw_mode', 'Phone')
        probe_data = self.entry_voltage_probe.get().strip().lower()
        
        # Gano ko matsalar IC Programming ce (Firmware Corruption) ko Hardware Short
        is_programming_fault = any(k in probe_data for k in ["dead", "boot", "bios", "program", "firmware", "stuck", "logo", "hang"]) or random.choice([True, False])
        
        if is_programming_fault:
            comp = "Winbond 25Q64 BIOS / Main MCU Firmware" if mode in ["Laptop", "Inverter", "Charge_Controller"] else "System Flash / EEPROM IC (U402)"
            hx, hy, zone = 85, 227, "Bottom-Left (BIOS / EEPROM Zone)"
            steps = (
                "1. DIAGNOSIS: IC has clean 3.3V/5V power but zero clock/logic output (Corrupted Firmware).\n"
                "2. ACTION: Go to Tab '🧬 3. Universal IC Programmer', use CH341A / XGecu T48, erase & write clean .BIN/.HEX file."
            )
            tag = "🧬 IC PROGRAMMING FAULT"
        else:
            if mode == "Inverter":
                comp, hx, hy, zone = "IRF3205 Power Mosfet Q4", 235, 75, "Top-Right (Power FET Stage)"
                steps = "1. Desolder Q4 & gate resistor (10R) at 360°C.\n2. Clean pads with wick, apply fresh thermal paste & solder matched IRF3205."
            elif mode == "Charge_Controller":
                comp, hx, hy, zone = "60A Schottky Diode D3", 235, 75, "Top-Right (PV Input Stage)"
                steps = "1. Remove shorted D3 diode from heatsink.\n2. Check buck inductor L1 for continuity & solder new 60A diode."
            elif mode == "Sewing_Machine":
                comp, hx, hy, zone = "Servo IPM Driver Module U3", 235, 227, "Bottom-Right (Motor Driver Stage)"
                steps = "1. Unscrew IPM heatsink & desolder 15 pins using solder sucker.\n2. Mount new IPM module with silicone insulator & resolder."
            elif mode == "Laptop":
                comp, hx, hy, zone = "BQ24780S Charging IC", 235, 227, "Bottom-Right (Charging IC Stage)"
                steps = "1. Apply flux & lift QFN IC with Hot Air at 340°C.\n2. Tin pads evenly, align Pin 1 dot, reflow & clean with IPA."
            elif mode == "Universal_Unknown":
                comp, hx, hy, zone = "UC3842 PWM Controller + PC817", 235, 75, "Top-Right (Primary SMPS Stage)"
                steps = "1. Replace 8-pin UC3842 PWM IC & 4-pin PC817 optocoupler.\n2. Test output voltage with series bulb before full load."
            else:
                comp, hx, hy, zone = "Qualcomm PM8150 Power IC", 80, 80, "Top-Left (Main PMIC Zone)"
                steps = "1. Shield nearby CPU, apply flux & lift PMIC at 350°C.\n2. Reball/align new PM8150 IC, reflow & check boot current."
            tag = "🔧 HARDWARE COMPONENT FAULT"

        self.draw_base_pcb_map(hx, hy, comp)
        if hasattr(self, 'lbl_pcb_coords'):
            self.lbl_pcb_coords.configure(text=f"📍 Location: {zone}\nPart: {comp}", text_color="#FFEB3B")

        res = (
            f"[{tag}] — {comp}\n"
            f"• Board Location: {zone}\n"
            f"• Replacement / Fix Steps:\n{steps}"
        )
        self.lbl_status_text.configure(text=res, text_color="#4CAF50")

    def action_engineer_set_price(self):
        if not hasattr(self, 'selected_pending_job'):
            self.lbl_intake_details.configure(text="[⚠️] Please select a pending job from the list above first!", text_color="#FF3D00")
            return
        j = self.selected_pending_job
        cost_val = self.entry_final_cost.get() or "15000"
        j['cost'] = cost_val
        j['stage'] = "3"
        self.update_neon_db(j)
        self.entry_final_cost.delete(0, tk.END)
        print(f">>> SMS 1 Sent to {j['phone']}: 'Sunvolt Repair Quote: ₦{cost_val}. Please pay deposit at front desk.'")
        self.refresh_all_engineer_lists()
        self.lbl_intake_details.configure(text=f"[✓] Quote ₦{cost_val} sent to {j['name']} (SMS 1) & Front Desk!", text_color="#00E676")
        delattr(self, 'selected_pending_job')

    def action_send_final_sms(self):
        if not hasattr(self, 'selected_ready_job'):
            self.lbl_status_text.configure(text="[⚠️] Select a Deposit-Paid device from list #2 first!", text_color="#FF3D00")
            return
        j = self.selected_ready_job
        j["stage"] = "5"
        self.update_neon_db(j)
        print(f">>> SMS 2 Sent to {j['phone']}: 'Repair Complete! Ticket: #{j['ticket_id']} Cost: ₦{j['cost']}. Pickup within 24h or ₦500 fine applies.'")
        try:
            earned = float(j['cost'])
            SUNVOLT_ADMIN_FINANCES["total_revenue"] += earned
            SUNVOLT_ADMIN_FINANCES["total_profit"] += (earned * 0.20)
            SUNVOLT_ADMIN_FINANCES["total_completed"] += 1
        except ValueError:
            pass
        SUNVOLT_JOB_QUEUE.remove(j)
        SUNVOLT_HISTORY_ARCHIVE.insert(0, j)
        self.selected_history_job = j
        self.refresh_all_engineer_lists()
        self.lbl_status_text.configure(text=f"[⚡] Repair Completed! Ticket #{j['ticket_id']} archived in History tab.", text_color="#4CAF50")
        delattr(self, 'selected_ready_job')

    def action_trigger_print_view(self):
        pr_j = getattr(self, 'selected_history_job', None)
        if not pr_j:
            self.txt_receipt.delete("1.0", tk.END)
            self.txt_receipt.insert(tk.END, "No completed job selected from History list yet.")
            return
        receipt_text = (
            "======================================\n"
            "           SUNVOLT TECH HUB\n"
            "    Affordable Electronics & Repair\n"
            "======================================\n"
            f"Date:            {pr_j.get('date', '2026-11-09')}\n"
            f"Ticket ID:       #{pr_j['ticket_id']}\n"
            f"Customer:        {pr_j['name']}\n"
            f"Phone:           {pr_j['phone']}\n"
            f"NIN:             {pr_j['nin']}\n"
            "--------------------------------------\n"
            f"Device:          {pr_j['type']} ({pr_j['model']})\n"
            f"Fault:           {pr_j['fault']}\n"
            "--------------------------------------\n"
            f"Total Cost:      ₦{pr_j['cost']}.00\n"
            f"Deposit Paid:    ₦{pr_j['deposit']}.00\n"
            f"Balance Due:     ₦{pr_j['balance']}.00\n"
            "--------------------------------------\n"
            "* WARNING: Test device before leaving.\n"
            "* NOTICE: Pickup within 24h or ₦500\n"
            "  late pickup fine applies.\n"
            "======================================\n"
        )
        self.txt_receipt.delete("1.0", tk.END)
        self.txt_receipt.insert(tk.END, receipt_text)

    def save_to_neon_db(self, job):
        try:
            conn = psycopg2.connect(NEON_CONNECTION_STRING)
            cur = conn.cursor()
            cur.execute("INSERT INTO users (full_name, phone_number, nin_number) VALUES (%s, %s, %s)", (job['name'], job['phone'], job['nin']))
            cur.execute("INSERT INTO repairs_orders (ticket_id, device_type, device_model, cost, deposit_paid, balance_due) VALUES (%s, %s, %s, %s, %s, %s)", (job['ticket_id'], job['type'], job['model'], 0, 0, 0))
            conn.commit()
            cur.close()
            conn.close()
            print(f"[✓] Saved #{job['ticket_id']} to Neon Cloud!")
        except Exception as e:
            print(f"[!] Neon Save Error: {e}")

    def save_part_order_to_neon(self, item):
        try:
            conn = psycopg2.connect(NEON_CONNECTION_STRING)
            cur = conn.cursor()
            cur.execute("INSERT INTO parts_orders (part_name, price) VALUES (%s, %s)", (item['name'], float(item['price'])))
            conn.commit()
            cur.close()
            conn.close()
        except Exception as e:
            print(f"[!] Neon Part Order Error: {e}")

    def update_neon_db(self, job):
        try:
            conn = psycopg2.connect(NEON_CONNECTION_STRING)
            cur = conn.cursor()
            cur.execute("UPDATE repairs_orders SET cost=%s, deposit_paid=%s, balance_due=%s WHERE ticket_id=%s", (float(job['cost']), float(job['deposit']), float(job['balance']), job['ticket_id']))
            conn.commit()
            cur.close()
            conn.close()
        except Exception as e:
            print(f"[!] Neon Update Error: {e}")

    def initialize_neon_database(self):
        if "PASSWORD_DINA" in NEON_CONNECTION_STRING:
            return
        try:
            conn = psycopg2.connect(NEON_CONNECTION_STRING)
            cur = conn.cursor()
            cur.execute("CREATE TABLE IF NOT EXISTS users (user_id UUID PRIMARY KEY DEFAULT gen_random_uuid(), full_name VARCHAR(255), phone_number VARCHAR(50), nin_number VARCHAR(50));")
            cur.execute("CREATE TABLE IF NOT EXISTS repairs_orders (order_id UUID PRIMARY KEY DEFAULT gen_random_uuid(), ticket_id VARCHAR(50), device_type VARCHAR(100), device_model VARCHAR(255), cost DECIMAL(10,2), deposit_paid DECIMAL(10,2), balance_due DECIMAL(10,2));")
            cur.execute("CREATE TABLE IF NOT EXISTS parts_orders (order_id UUID PRIMARY KEY DEFAULT gen_random_uuid(), part_name VARCHAR(255), price DECIMAL(10,2), ordered_at TIMESTAMP DEFAULT NOW());")
            conn.commit()
            cur.close()
            conn.close()
            print("[✓] Connected to Neon Cloud Database!")
        except Exception as e:
            print(f"[!] Neon Connection Error: {e}")

if __name__ == "__main__":
    app = SunvoltApp()
    app.mainloop()
