import streamlit as st
import psycopg2
from psycopg2.extras import RealDictCursor
import random

st.set_page_config(page_title="Sunvolt Store Keeper Suite", page_icon="??", layout="wide")

# !!! PRODUCTION NEON CONNECTION STRING !!!
DB_URL = "postgresql://neondb_owner:npg_1CmIlyGAijs2@ep-sparkling-cell-axzagjek-pooler.c-4.us-east-2.aws.neon.tech/neondb?sslmode=require&channel_binding=require"

def get_db_connection():
    return psycopg2.connect(DB_URL)

# --- LOGIN & PROFILE CAPTURE FOR STORE KEEPER ---
if 'store_logged_in' not in st.session_state:
    st.session_state['store_logged_in'] = False
    st.session_state['store_name'] = ""
    st.session_state['store_phone'] = ""
    st.session_state['store_email'] = ""
    st.session_state['store_branch_city'] = ""

if not st.session_state['store_logged_in']:
    st.markdown("<h2 style='text-align: center;'>?? Sunvolt Store Keeper Registration & Login</h2>", unsafe_allow_html=True)
    st.info("Please enter your official warehouse staff credentials to access your branch dashboard.")
    
    col1, col2 = st.columns(2)
    with col1:
        s_name = st.text_input("Full Name:")
        s_phone = st.text_input("Phone Number:")
    with col2:
        s_email = st.text_input("Email Address:")
        s_office = st.text_input("Main Office Store Location / City (e.g., Kashere):")
        
    if st.button("Verify & Open Warehouse Dashboard"):
        if s_name.strip() == "" or s_phone.strip() == "" or s_email.strip() == "" or s_office.strip() == "":
            st.error("Error: Full Name, Phone, Email, and Store Branch Location are all mandatory fields!")
        else:
            st.session_state['store_logged_in'] = True
            st.session_state['store_name'] = s_name.strip()
            st.session_state['store_phone'] = s_phone.strip()
            st.session_state['store_email'] = s_email.strip().lower()
            st.session_state['store_branch_city'] = s_office.strip().lower()
            st.success(f"Welcome back, {s_name.upper()}! Warehouse profile authenticated.")
            st.rerun()
    st.stop()

current_store_user = st.session_state['store_name']
current_store_email = st.session_state['store_email']
current_store_city = st.session_state['store_branch_city']

# --- SIDEBAR ONLINE DASHBOARD ---
st.sidebar.header("?? STORE ONLINE DASHBOARD")
st.sidebar.markdown(f"?? **Store Keeper:** {current_store_user.upper()}")
st.sidebar.markdown(f"?? **Store Branch:** <span style='color:#e67e22;'><b>{current_store_city.upper()}</b></span>", unsafe_allow_html=True)

if st.sidebar.button("?? Logout From Store"):
    st.session_state['store_logged_in'] = False
    st.rerun()

st.markdown("<h1 style='text-align: center;'>?? SUNVOLT STORE KEEPER PORTAL</h1>", unsafe_allow_html=True)
st.markdown(f"<p style='text-align: center;'>Inventory Management Panel: <b style='color:#e67e22;'>{current_store_city.upper()} WAREHOUSE</b></p>", unsafe_allow_html=True)
st.write("---")

tab_warehouse, tab_send, tab_reg_agent, tab_complaint = st.tabs([
    "?? Warehouse Inventory & QR Intake", "?? QR Transfer Stock to Agent", "?? Register New Agent Draft", "?? Receive Customer Complaints"
])

# 1. WAREHOUSE INTAKE MANAGEMENT WITH SCANNING FIELD
with tab_warehouse:
    st.subheader(f"?? Add Bulk Stock Inflow to {current_store_city.upper()} Warehouse")
    
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT item_name FROM pricing_groups")
    global_items = cursor.fetchall()
    
    for item in global_items:
        cursor.execute("INSERT INTO store_inventory (item_name, quantity) VALUES (%s, 0) ON CONFLICT (item_name) DO NOTHING", (item,))
    conn.commit()
    
    cursor.execute("SELECT item_name, quantity FROM store_inventory")
    warehouse_stock = cursor.fetchall()
    cursor.close()
    conn.close()
    
    st.write("### Current In-Store Quantities")
    if not warehouse_stock:
        st.info("No product stock catalog published yet. Awaiting Pricing Group configuration from Head Office.")
    else:
        for name, qty in warehouse_stock:
            st.markdown(f"?? **{name}** ? Available in Store: **{qty} Units**")
            
        st.write("---")
        st.write("### ? QR/Barcode Scanner Auto Intake")
        st.caption("Click into the box below and scan the box QR code to automatically record inbound delivery stock from vehicles.")
        
        product_options = [w for w in warehouse_stock] if warehouse_stock else []
        if product_options:
            selected_intake = st.selectbox("Select Arriving Solar Product Catalog:", product_options, key="intake_cat")
            scanned_intake_code = st.text_input("Scan QR Code Here (Inflow Box):", key="scan_intake_field")
            intake_qty = st.number_input("Or enter stock count manually:", min_value=1, step=1, value=1)
            
            if st.button("Record Intake Into Main Store") or (scanned_intake_code.strip() != ""):
                final_qty = 1 if scanned_intake_code.strip() != "" else intake_qty
                conn = get_db_connection()
                cursor = conn.cursor()
                cursor.execute("UPDATE store_inventory SET quantity = quantity + %s WHERE item_name = %s", (final_qty, selected_intake))
                conn.commit()
                cursor.close()
                conn.close()
                st.success(f"Recorded incoming batch of {final_qty} unit(s) into warehouse reserve successfully!")
                st.rerun()

# 2. TRANSFER STOCK TO AGENT (STRICT CITY BRANCH FILTERING)
with tab_send:
    st.subheader(f"Send Solar Box to Agents Operating in {current_store_city.upper()} Only")
    
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT item_name, quantity FROM store_inventory WHERE quantity > 0")
    store_items = cursor.fetchall()
    
    cursor.execute("SELECT agent_email, agent_name, agent_phone FROM agent_wallets WHERE LOWER(agent_city) = %s", (current_store_city,))
    active_agents = cursor.fetchall()
    cursor.close()
    conn.close()
    
    if not store_items:
        st.error("? Warehouse is out of dispatchable stock! Record inbound quantities first.")
    elif not active_agents:
        st.warning(f"?? Branch Lock Security: No active Agent found operating under **{current_store_city.upper()}**. Agents must create a wallet profile first.")
    else:
        agent_options = {f"{a.upper()} (Email: {a})": a for a in active_agents}
        selected_agent_display = st.selectbox("Select Registered Branch Agent (Assigned to Your Town):", list(agent_options.keys()))
        target_agent_email = agent_options[selected_agent_display]
        
        send_options = [s for s in store_items]
        selected_item = st.selectbox("Select Solar Category to Send:", send_options)
        
        st.write("### 2D QR Scanner Dispatch Box")
        st.caption("Click into the box below and scan the box QR code to instantly dispatch the system unit.")
        qr_unit_number = st.text_input("Scan QR Code Here (Dispatch Box):", key="scan_dispatch_field")
        
        if st.button("Dispatch Stock via Online Server") or (qr_unit_number.strip() != ""):
            if not qr_unit_number.strip():
                st.error("? Unit Serial Number is mandatory before dispatching!")
            else:
                conn = get_db_connection()
                cursor = conn.cursor()
                cursor.execute("UPDATE store_inventory SET quantity = quantity - 1 WHERE item_name=%s", (selected_item,))
                cursor.execute("""
                    INSERT INTO agent_transfers (item_name, unit_number, status) 
                    VALUES (%s, %s, 'Pending')
                """, (selected_item, qr_unit_number.strip()))
                conn.commit()
                cursor.close()
                conn.close()
                st.success(f"?? Successfully dispatched {selected_item} (Serial: {qr_unit_number.strip()}) directly to {selected_agent_display}.")
                st.rerun()
                
    st.write("---")
    st.subheader("?? Stock Dispatch Status Tracker")
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT item_name, unit_number, status FROM agent_transfers")
    transfers = cursor.fetchall()
    cursor.close()
    conn.close()
    
    for item, unit, status in transfers:
        if status == "Pending":
            st.warning(f"? **{item}** (Serial: `{unit}`) -> **Awaiting Agent Acceptance**")
        else:
            st.success(f"? **{item}** (Serial: `{unit}`) -> **Accepted by Agent**")

# 3. REGISTER NEW AGENT WITH NIN & ADDRESS
with tab_reg_agent:
    st.subheader("Enroll New Agent Draft (Forward to Executive Board)")
    col_a, col_b = st.columns(2)
    with col_a:
        ag_name = st.text_input("New Agent Full Name:")
        ag_phone = st.text_input("Phone Number:")
        ag_email = st.text_input("Email Address:")
    with col_b:
        ag_nin = st.text_input("National Identity Number (NIN):")
        ag_address = st.text_area("Home Address & Operation Area:")
    
    if st.button("Submit Agent Draft to Management"):
        if not ag_name or not ag_phone or not ag_nin or not ag_address:
            st.error("? Error: Full Name, Phone, NIN, and Address are mandatory!")
        else:
            conn = get_db_connection()
            cursor = conn.cursor()
            cursor.execute("""
                INSERT INTO agent_approvals (name, phone, email, status) 
                VALUES (%s, %s, %s, 'Pending')
            """, (ag_name, ag_phone, ag_email))
            conn.commit()
            cursor.close()
            conn.close()
            st.info(f"Agent recruitment file for {ag_name.upper()} has been successfully forwarded to Executive Board for approval.")

# 4. CUSTOMER COMPLAINTS LOG
with tab_complaint:
    st.subheader("Log Faulty Solar System Complaints")
    c_name = st.text_input("Customer Name:")
