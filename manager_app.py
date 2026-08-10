import streamlit as st
import psycopg2
from psycopg2.extras import RealDictCursor

st.set_page_config(page_title="Sunvolt Executive Suite", page_icon="👑", layout="wide")

# !!! PRODUCTION NEON CONNECTION STRING !!!
DB_URL = "postgresql://neondb_owner:npg_1CmIlyGAijs2@ep-sparkling-cell-axzagjek-pooler.c-4.us-east-2.aws.neon.tech/neondb?sslmode=require&channel_binding=require"

def get_db_connection():
    return psycopg2.connect(DB_URL)

# --- LOGIN WITH DYNAMIC STAFF AUTHENTICATION ---
if 'logged_in' not in st.session_state:
    st.session_state['logged_in'] = False
    st.session_state['staff_name'] = ""
    st.session_state['staff_role'] = ""
    st.session_state['staff_email'] = ""

if not st.session_state['logged_in']:
    st.markdown("<h2 style='text-align: center;'>🔐 Sunvolt Executive Portal Login</h2>", unsafe_allow_html=True)
    st.info("Please verify your official management credentials to access the executive command tools.")
    
    login_email = st.text_input("Enter Your Registered Email Address:")
    login_phone = st.text_input("Enter Your Registered Phone Number:")
    
    if st.button("Authenticate Profile"):
        if login_email.strip() == "" or login_phone.strip() == "":
            st.error("Error: Email and Phone number fields cannot be empty!")
        else:
            conn = get_db_connection()
            cursor = conn.cursor(cursor_factory=RealDictCursor)
            cursor.execute("""
                SELECT * FROM company_staff 
                WHERE LOWER(staff_email) = %s AND staff_phone = %s AND status = 'Active'
            """, (login_email.strip().lower(), login_phone.strip()))
            staff_profile = cursor.fetchone()
            cursor.close()
            conn.close()
            
            if staff_profile:
                st.session_state['logged_in'] = True
                st.session_state['staff_name'] = staff_profile['staff_name']
                st.session_state['staff_role'] = staff_profile['staff_role']
                st.session_state['staff_email'] = staff_profile['staff_email']
                st.success(f"Access Granted! Welcome back, {staff_profile['staff_name'].upper()}.")
                st.rerun()
            else:
                st.error("Access Denied: Invalid parameters or unverified executive profile. Contact Head Office.")
    st.stop()

current_role = st.session_state['staff_role']
current_user = st.session_state['staff_name']
current_email = st.session_state['staff_email']

st.markdown("<h1 style='text-align: center;'>👑 SUNVOLT EXECUTIVE PORTAL</h1>", unsafe_allow_html=True)
st.markdown(f"<p style='text-align: center;'>Authorized Officer: <b>{current_user.upper()}</b> | Security Access Level: <span style='color:#ff6e40;'><b>{current_role.upper()}</b></span></p>", unsafe_allow_html=True)
st.write("---")

# --- EXECUTIVE SIDEBAR ONLINE DASHBOARD ---
st.sidebar.header("📊 BOARD ONLINE DASHBOARD")
conn = get_db_connection()
cursor = conn.cursor()
cursor.execute("SELECT SUM(CAST(paid_amount AS REAL)), SUM(CAST(balance AS REAL)), COUNT(id) FROM customers")
collected, debt, total_cust = cursor.fetchone()
cursor.close()
conn.close()

collected = collected if collected else 0.0
debt = debt if debt else 0.0

st.sidebar.metric(label="💰 Total Cash Collected", value=f"N{collected:,.2f}")
st.sidebar.metric(label="📉 Total Outstandings (Debt)", value=f"N{debt:,.2f}")
st.sidebar.metric(label="👥 Active Accounts", value=f"{total_cust} Customers")

if st.sidebar.button("🔴 Secure Logout"):
    st.session_state['logged_in'] = False
    st.rerun()

# --- EXECUTIVE WORKFLOW INTERFACE BY SYSTEM ROLE ---
if current_role == "Accountant":
    tab_finance = st.tabs(["💰 Financial Ledger Statements"])
    with tab_finance[0]:
        st.subheader("Company Balance Sheets & Profit Ledger")
        gross_profit = collected * 0.25
        expenses = collected * 0.05
        net_profit = gross_profit - expenses
        col_r1, col_r2, col_r3 = st.columns(3)
        with col_r1: st.metric(label="📈 Gross Income Allocation", value=f"N{collected:,.2f}")
        with col_r2: st.metric(label="📉 Operational Deductions", value=f"N{expenses:,.2f}")
        with col_r3: st.metric(label="🏆 Estimated Net Profit", value=f"N{net_profit:,.2f}")

elif current_role in ["Senior Manager", "Auditor"]:
    # Anan ne aka gyara ainihin raba shafukan daki-daki da lambobi [0], [1], [2], [3]
    tab_titles = ["📋 Customer Verification", "🏷️ Pricing Group Manager", "💼 Agent Wallets", "👥 Company Staff Registry"]
    tabs = st.tabs(tab_titles)
    
    # 1. CUSTOMER VERIFICATION
    with tabs[0]:
        st.subheader("Pending Customer Enrollment Verifications")
        conn = get_db_connection()
        cursor = conn.cursor(cursor_factory=RealDictCursor)
        cursor.execute("SELECT * FROM approvals WHERE status='Pending'")
        pending_custs = cursor.fetchall()
        conn.close()
        
        if not pending_custs:
            st.info("No customer accounts awaiting executive validation.")
        else:
            for cust in pending_custs:
                st.write(f"👤 **Draft Customer:** {cust['name'].upper()} | Catalog: {cust['item_name']} | Serial Number: `{cust['serial_number']}` | Downpayment: N{float(cust['paid_amount']):,.2f}")
                if current_role == "Senior Manager":
                    if st.button(f"Approve Enrollment: {cust['name']}", key=f"c_ap_{cust['id']}"):
                        conn = get_db_connection()
                        cursor = conn.cursor()
                        cursor.execute("""
                        INSERT INTO customers (name, phone, nin, photo_path, address, serial_number, unit, payment_type, total_price, paid_amount, balance)
                        VALUES (%s, '080', '123', 'p.jpg', 'Addr', %s, %s, 'Easy Buy', %s, %s, %s)
                        """, (cust['name'], cust['serial_number'], cust['unit'], str(float(cust['paid_amount'])+float(cust['balance'])), cust['paid_amount'], cust['balance']))
                        cursor.execute("UPDATE approvals SET status='Approved' WHERE id=%s", (cust['id'],))
                        cursor.execute("DELETE FROM agent_transfers WHERE unit_number = %s", (cust['unit'],))
                        conn.commit()
                        cursor.close()
                        conn.close()
                        st.success(f"Customer {cust['name'].upper()} verified and added!"); st.rerun()
                else:
                    st.info("👁️ View-Only Audit Mode Restricted")

    # 2. PRICING GROUP MANAGER
    with tabs[1]:
        st.subheader("🏷️ Global System Pricing Group Configuration")
        if current_role == "Senior Manager":
            with st.form("add_price_form"):
                new_item = st.text_input("Enter Solar Product Catalog Specification:")
                new_price = st.number_input("Set Company Standard Rate (N):", min_value=0.0, step=1000.0)
                submit_price = st.form_submit_button("Publish Product Rate")
                
                if submit_price and new_item.strip() != "":
                    conn = get_db_connection()
                    cursor = conn.cursor()
                    cursor.execute("""
                        INSERT INTO pricing_groups (item_name, price)
                        VALUES (%s, %s)
                        ON CONFLICT (item_name) DO UPDATE SET price = EXCLUDED.price
                    """, (new_item.strip(), new_price))
                    conn.commit()
                    cursor.close()
                    conn.close()
                    st.success("New product pricing tier distributed to all nodes!")
                    st.rerun()
        
        st.write("---")
        conn = get_db_connection()
        cursor = conn.cursor()
        cursor.execute("SELECT id, item_name, price FROM pricing_groups")
        all_prices = cursor.fetchall()
        cursor.close()
        conn.close()
        
        for pid, name, prc in all_prices:
            col_p1, col_p2 = st.columns(2)
            with col_p1: st.markdown(f"🔹 **{name}** — Configured Value: **N{prc:,.2f}**")
            with col_p2:
                if current_role == "Senior Manager" and st.button("Remove Category", key=f"del_{pid}"):
                    conn = get_db_connection()
                    cursor = conn.cursor()
                    cursor.execute("DELETE FROM pricing_groups WHERE id = %s", (pid,))
                    conn.commit()
                    cursor.close()
                    conn.close()
                    st.success("Configuration purged."); st.rerun()

    # 3. AGENT WALLETS MANAGEMENT
    with tabs[2]:
        st.subheader("💼 Registered Distribution Agent Funding Desk")
        if current_role == "Senior Manager":
            conn = get_db_connection()
            cursor = conn.cursor()
            cursor.execute("SELECT agent_email, agent_name FROM agent_wallets")
            all_agents_list = cursor.fetchall()
            cursor.close()
            conn.close()
            
            if all_agents_list:
                agent_opts = {f"{name} ({email})": email for email, name in all_agents_list}
                selected_ag_str = st.selectbox("Select Target Distribution Agent:", list(agent_opts.keys()))
                fund_amount = st.number_input("Enter Capital Allocation Amount (N):", min_value=100.0, step=500.0)
                
                if st.button("Top-up Agent Vault Wallet"):
                    target_email = agent_opts[selected_ag_str]
                    conn = get_db_connection()
                    cursor = conn.cursor()
                    cursor.execute("UPDATE agent_wallets SET balance = balance + %s WHERE agent_email = %s", (fund_amount, target_email))
                    conn.commit()
                    cursor.close()
                    conn.close()
                    st.success(f"Transferred N{fund_amount:,.2f} to {selected_ag_str}!"); st.rerun()
        
        st.write("---")
