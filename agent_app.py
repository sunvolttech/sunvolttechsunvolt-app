import streamlit as st
import psycopg2 
from psycopg2.extras import RealDictCursor
import random

st.set_page_config(page_title="Sunvolt Agent Portal", page_icon="??", layout="wide")

# !!! PRODUCTION NEON CONNECTION STRING !!!
DB_URL = "postgresql://neondb_owner:npg_1CmIlyGAijs2@ep-sparkling-cell-axzagjek-pooler.c-4.us-east-2.aws.neon.tech/neondb?sslmode=require&channel_binding=require"

# --- SMS TWILIO SERVICE OVERLAY CONFIG ---
TWILIO_ACCOUNT_SID = "your_twilio_sid_here"
TWILIO_AUTH_TOKEN = "your_twilio_auth_token_here"
TWILIO_PHONE_NUMBER = "+1234567890"

def get_db_connection():
    return psycopg2.connect(DB_URL)

def send_sms_alert(to_phone, customer_name, paid_amt, remaining_bal):
    try:
        from twilio.rest import Client
        client = Client(TWILIO_ACCOUNT_SID, TWILIO_AUTH_TOKEN)
        msg_body = f"Hello {customer_name.upper()}, Sunvolt has received your payment of N{paid_amt:,.2f}. Your remaining balance is N{remaining_bal:,.2f}. Thank you!"
        formatted_phone = "+234" + to_phone.strip()[1:] if to_phone.strip().startswith("0") else to_phone
        client.messages.create(body=msg_body, from_=TWILIO_PHONE_NUMBER, to=formatted_phone)
        return True
    except:
        return False

# --- LOGIN & PROFILE CAPTURE ---
if 'agent_logged_in' not in st.session_state:
    st.session_state['agent_logged_in'] = False
    st.session_state['agent_name'] = ""
    st.session_state['agent_phone'] = ""
    st.session_state['agent_email'] = ""

if not st.session_state['agent_logged_in']:
    st.markdown("<h2 style='text-align: center;'>?? Sunvolt Agent Registration & Login</h2>", unsafe_allow_html=True)
    st.info("Please enter your official employee credentials to synchronize your handheld agent profile.")
    
    col1, col2 = st.columns(2)
    with col1:
        reg_name = st.text_input("Full Name:")
        reg_phone = st.text_input("Phone Number:")
    with col2:
        reg_email = st.text_input("Email Address:")
        reg_city = st.text_input("Current Operational Town/City (e.g., Kashere):")
        
    if st.button("Verify & Open Dashboard"):
        if reg_name.strip() == "" or reg_phone.strip() == "" or reg_email.strip() == "" or reg_city.strip() == "":
            st.error("Error: Full Name, Phone, Email, and Operational City are mandatory fields!")
        else:
            conn = get_db_connection()
            cursor = conn.cursor()
            cursor.execute("""
                INSERT INTO agent_wallets (agent_email, agent_name, agent_phone, balance, agent_city)
                VALUES (%s, %s, %s, 50000.0, %s) 
                ON CONFLICT (agent_email) DO UPDATE SET agent_name = %s, agent_phone = %s, agent_city = %s
            """, (reg_email.strip().lower(), reg_name.strip(), reg_phone.strip(), reg_city.strip().lower(), reg_name.strip(), reg_phone.strip(), reg_city.strip().lower()))
            conn.commit()
            cursor.close()
            conn.close()
            
            st.session_state['agent_logged_in'] = True
            st.session_state['agent_name'] = reg_name.strip()
            st.session_state['agent_phone'] = reg_phone.strip()
            st.session_state['agent_email'] = reg_email.strip().lower()
            st.success(f"Welcome back, {reg_name.upper()}! Handheld terminal synchronized.")
            st.rerun()
    st.stop()

current_agent_name = st.session_state['agent_name']
current_agent_email = st.session_state['agent_email']

# Fetch current Wallet Balance
conn = get_db_connection()
cursor = conn.cursor()
cursor.execute("SELECT balance FROM agent_wallets WHERE agent_email = %s", (current_agent_email,))
wallet_row = cursor.fetchone()
agent_wallet_balance = wallet_row[0] if wallet_row else 0.0
cursor.close()
conn.close()

# --- SIDEBAR ONLINE DASHBOARD ---
st.sidebar.header("?? AGENT ONLINE DASHBOARD")
st.sidebar.markdown(f"?? **Agent Name:** {current_agent_name.upper()}")
st.sidebar.markdown(f"?? **Agent ID:** {current_agent_email}")
st.sidebar.markdown(f"?? **Agent Wallet:** <h3 style='color:#2ecc71;margin:0;'>N{agent_wallet_balance:,.2f}</h3>", unsafe_allow_html=True)

# Fetch stats
conn = get_db_connection()
cursor = conn.cursor()
cursor.execute("SELECT SUM(CAST(paid_amount AS REAL)), SUM(CAST(balance AS REAL)), COUNT(id) FROM customers")
collected, debt, total_cust = cursor.fetchone()
cursor.execute("SELECT COUNT(id) FROM agent_transfers WHERE status='Accepted'")
my_stock_count = cursor.fetchone()
cursor.close()
conn.close()

collected = collected if collected else 0.0
debt = debt if debt else 0.0
my_stock_count = my_stock_count[0] if my_stock_count else 0

st.sidebar.metric(label="Total Cash Collected (Sunvolt)", value=f"N{collected:,.2f}")
st.sidebar.metric(label="Total Outstandings (Debt)", value=f"N{debt:,.2f}")
st.sidebar.metric(label="Active Network Customers", value=f"{total_cust} Accounts")
st.sidebar.metric(label="Your Handheld Stock Units", value=f"{my_stock_count} Units")

if st.sidebar.button("?? Secure Logout From Profile"):
    st.session_state['agent_logged_in'] = False
    st.rerun()

st.markdown("<h1 style='text-align: center;'>?? SUNVOLT AGENT PORTAL</h1>", unsafe_allow_html=True)
st.write("---")

tab_pricing, tab_stock, tab_register, tab_payment = st.tabs([
    "?? Pricing Group (Office Price)", "?? Stock Allocations & Accepts", "?? Step-by-Step Register", "?? Collect Repayment"
])

# --- 1. PRICING GROUP (OFFICE VIEW ONLY) ---
with tab_pricing:
    st.subheader("?? Head Office Global Pricing Catalog")
    st.caption("This panel reflects the live system valuation set by Senior Management.")
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT item_name, price FROM pricing_groups")
    global_prices = cursor.fetchall()
    cursor.close()
    conn.close()
    if not global_prices:
        st.info("No corporate asset catalog configuration published from Head Office yet.")
    else:
        for item, prc in global_prices:
            st.markdown(f"?? **Product Category:** {item} | **Standard Corporate Price:** <b>N{prc:,.2f}</b>", unsafe_allow_html=True)

# --- 2. STOCK & ACCEPTS ---
with tab_stock:
    st.subheader("?? Accept Dispatched Inventory from Store Keeper")
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT id, item_name, unit_number FROM agent_transfers WHERE status='Pending'")
    pending_transfers = cursor.fetchall()
    cursor.close()
    conn.close()
    if not pending_transfers:
        st.success("? Clean Queue: No pending equipment allocations to accept at the moment.")
    else:
        for tid, titem, tunit in pending_transfers:
            col_x, col_y = st.columns(2)
            with col_x: st.warning(f"?? **{titem}** | Unit Serial Number: `{tunit}`")
            with col_y:
                if st.button(f"Accept Unit Allocation: {tunit}", key=f"acc_{tid}"):
                    conn = get_db_connection()
                    cursor = conn.cursor()
                    cursor.execute("UPDATE agent_transfers SET status='Accepted' WHERE id=%s", (tid,))
                    conn.commit()
                    cursor.close()
                    conn.close()
                    st.success("Inventory Unit accepted successfully!")
                    st.rerun()
    st.write("---")
    st.subheader("?? Handheld Live Inventory Reserves")
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT item_name, unit_number FROM agent_transfers WHERE status='Accepted'")
    my_units = cursor.fetchall()
    cursor.close()
    conn.close()
    if not my_units:
        st.info("Your handheld deployment inventory is currently empty.")
    else:
        for m_item, m_unit in my_units:
            st.code(f"Solar Asset: {m_item} | Box Unit Serial Number: {m_unit}", language="markdown")

# --- 3. STEP-BY-STEP CUSTOMER REGISTER ---
with tab_register:
    st.subheader("?? New Customer Enrollment KYC Verification Workflow")
    if 'reg_step' not in st.session_state: st.session_state['reg_step'] = 1
    if 'temp_cust_name' not in st.session_state: st.session_state['temp_cust_name'] = ""
    if 'temp_cust_phone' not in st.session_state: st.session_state['temp_cust_phone'] = ""
    if 'temp_cust_nin' not in st.session_state: st.session_state['temp_cust_nin'] = ""
    if 'otp_sent' not in st.session_state: st.session_state['otp_sent'] = False
    if 'generated_otp' not in st.session_state: st.session_state['generated_otp'] = ""
    if 'otp_verified' not in st.session_state: st.session_state['otp_verified'] = False

    if st.session_state['reg_step'] == 1:
        st.markdown("#### Phase 1: Capture Client Core Identification Data")
        c_name = st.text_input("Customer Full Name:")
        c_phone = st.text_input("Customer Contact Phone Number:")
        c_nin = st.text_input("National Identity Number (NIN):")
        if st.button("Proceed to Next Phase ??"):
            if c_name.strip() == "" or c_phone.strip() == "" or c_nin.strip() == "":
                st.error("Error: Client Name, Phone, and NIN details are mandatory!")
            else:
                st.session_state['temp_cust_name'] = c_name
                st.session_state['temp_cust_phone'] = c_phone
                st.session_state['temp_cust_nin'] = c_nin
                st.session_state['reg_step'] = 2
                st.rerun()

    elif st.session_state['reg_step'] == 2:
        st.markdown("#### Phase 2: Telecommunication OTP Security Verification")
        st.write(f"Activation code will be pushed to: **{st.session_state['temp_cust_phone']}**")
        
        # Wuri na musamman da zai ri?a canzawa ta atomatik (Maballin zai ?ace akwati ya fito)
        otp_box = st.empty()
        
        if not st.session_state['otp_sent']:
            if st.button("Transmit OTP Verification Token", type="primary"):
                st.session_state['generated_otp'] = str(random.randint(100000, 999999))
                st.session_state['otp_sent'] = True
                st.rerun()
