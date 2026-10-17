import os
import streamlit as st

INCOME_FILE = "income.txt"
EXPENSE_FILE = "expense.txt"
USERS_FILE = "users.txt"  # New file database to hold custom accounts

# Create files if they don't exist
for f in [INCOME_FILE, EXPENSE_FILE, USERS_FILE]:
    if not os.path.exists(f):
        open(f, "w").close()

st.set_page_config(page_title="Multi-User Shop Tracker", layout="centered")

# --- DATABASE HELPER FUNCTIONS ---
def get_all_users():
    """Reads users.txt and returns a dictionary of {user_id: password}."""
    user_db = {}
    with open(USERS_FILE, "r") as f:
        for line in f:
            if line.strip():
                parts = line.strip().split(",")
                if len(parts) == 2:
                    user_db[parts[0]] = parts[1]
    return user_db

def create_new_user(user_id, password):
    """Appends a new user account profile to users.txt."""
    with open(USERS_FILE, "a") as f:
        f.write(f"{user_id},{password}\n")

# --- SESSION INITIALIZATION ---
if "logged_in" not in st.session_state:
    st.session_state.logged_in = False
if "current_user" not in st.session_state:
    st.session_state.current_user = ""

# --- 1. WELCOME SCREEN (LOGIN / SIGNUP SYSTEM LIKE INSTAGRAM) ---
if not st.session_state.logged_in:
    st.title("📱 Shop Budget Web App")
    
    # Create two visual tabs at the top of the box
    tab_login, tab_signup = st.tabs(["🔐 Log In", "🆕 Create Account (Sign Up)"])
    
    # TAB A: THE LOGIN FORM
    with tab_login:
        st.subheader("Login to your Account")
        login_user = st.text_input("User ID / Username:", key="log_user")
        login_pass = st.text_input("Password:", type="password", key="log_pass")
        
        if st.button("Sign In"):
            users = get_all_users()
            if login_user in users and users[login_user] == login_pass:
                st.session_state.logged_in = True
                st.session_state.current_user = login_user
                st.success(f"Welcome back, {login_user}!")
                st.rerun()
            else:
                st.error("Incorrect User ID or Password!")

    # TAB B: THE SIGNUP FORM (LIKE INSTAGRAM SIGN UP)
    with tab_signup:
        st.subheader("Register a New Profile")
        new_user = st.text_input("Choose a unique User ID:", key="sign_user")
        new_pass = st.text_input("Create a secure Password:", type="password", key="sign_pass")
        confirm_pass = st.text_input("Confirm Password:", type="password", key="sign_confirm")
        
        if st.button("Register Now"):
            users = get_all_users()
            if not new_user or not new_pass:
                st.error("Fields cannot be empty!")
            elif " " in new_user:
                st.error("User ID cannot contain spaces!")
            elif new_user in users:
                st.error("This User ID is already taken! Try another name.")
            elif new_pass != confirm_pass:
                st.error("Passwords do not match!")
            else:
                create_new_user(new_user, new_pass)
                st.success("🎉 Account created successfully! Go to the 'Log In' tab to log in.")

# --- 2. THE DASHBOARD ---
else:
    # personalized header title showing exactly who logged in
    st.title(f"📊 Dashboard for: {st.session_state.current_user}")
    
    if st.sidebar.button("Log Out"):
        st.session_state.logged_in = False
        st.session_state.current_user = ""
        st.rerun()

    col1, col2 = st.columns(2)
    
    with col1:
        st.subheader("Log Income")
        inc_source = st.text_input("Source (e.g., Shop Sales):", key="inc_src")
        inc_amount = st.text_input("Amount ($):", key="inc_amt")
        if st.button("➕ Save Income"):
            if inc_source and inc_amount:
                try:
                    float(inc_amount)
                    # We save the username next to the data line so entries don't mix up
                    with open(INCOME_FILE, "a") as file:
                        file.write(f"{st.session_state.current_user},{inc_source},{inc_amount}\n")
                    st.success(f"Logged ${inc_amount}")
                    st.rerun()
                except ValueError:
                    st.error("Enter a valid number")

    with col2:
        st.subheader("Log Expense")
        exp_cat = st.text_input("Category (e.g., Salary):", key="exp_ct")
        exp_amount = st.text_input("Amount ($):", key="exp_amt")
        if st.button("➖ Save Expense"):
            if exp_cat and exp_amount:
                try:
                    float(exp_amount)
                    with open(EXPENSE_FILE, "a") as file:
                        file.write(f"{st.session_state.current_user},{exp_cat},{exp_amount}\n")
                    st.success(f"Logged ${exp_amount}")
                    st.rerun()
                except ValueError:
                    st.error("Enter a valid number")

    st.divider()
    st.subheader("Your Financial Summary")
    
    total_income = 0.0
    total_expense = 0.0

    # Read Income File and only grab data matching the current user
    with open(INCOME_FILE, "r") as file:
        for line in file:
            if line.strip():
                parts = line.strip().split(",")
                if len(parts) == 3 and parts[0] == st.session_state.current_user:
                    total_income += float(parts[2])
            
    # Read Expense File and only grab data matching the current user
    with open(EXPENSE_FILE, "r") as file:
        for line in file:
            if line.strip():
                parts = line.strip().split(",")
                if len(parts) == 3 and parts[0] == st.session_state.current_user:
                    total_expense += float(parts[2])

    net_balance = total_income - total_expense
    
    m1, m2, m3 = st.columns(3)
    m1.metric("Total Income", f"${total_income:.2f}")
    m2.metric("Total Expenses", f"${total_expense:.2f}")
    m3.metric("Net Balance", f"${net_balance:.2f}")
    
    if net_balance >= 0:
        st.success("Current Standing: PROFIT 👍")
    else:
        st.error("Current Standing: LOSS 👎")
