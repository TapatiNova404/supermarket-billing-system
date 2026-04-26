import streamlit as st
import pandas as pd
import mysql.connector
from mysql.connector import Error
import cv2
import numpy as np
from pyzbar.pyzbar import decode
st.set_page_config(page_title="Supermarket Billing System", page_icon="🛒", layout="wide")

# ==========================================
# Database Connection & Setup
# ==========================================
st.sidebar.header("Database Configuration")
db_host = st.sidebar.text_input("Host", value="localhost")
db_user = st.sidebar.text_input("User", value="root")
db_password = st.sidebar.text_input("Password", value="TapatiPaul@333", type="password")
db_name = st.sidebar.text_input("Database", value="super_market_billing")

def create_db_connection(host, user, password, database=None):
    try:
        if database:
            conn = mysql.connector.connect(host=host, user=user, password=password, database=database)
        else:
            conn = mysql.connector.connect(host=host, user=user, password=password)
        return conn
    except Error as e:
        st.sidebar.error(f"Error connecting to MySQL: {e}")
        return None

def init_db():
    conn = create_db_connection(db_host, db_user, db_password)
    if conn:
        cursor = conn.cursor()
        try:
            cursor.execute(f"CREATE DATABASE IF NOT EXISTS {db_name}")
            cursor.execute(f"USE {db_name}")
            
            # Create Tables
            cursor.execute("""
            CREATE TABLE IF NOT EXISTS cust_details (
                cust_id INT PRIMARY KEY AUTO_INCREMENT,
                cust_name VARCHAR(100) NOT NULL,
                cust_ph_no VARCHAR(15) UNIQUE NOT NULL,
                cust_address VARCHAR(255) NOT NULL
            )
            """)
            
            cursor.execute("""
            CREATE TABLE IF NOT EXISTS product_details (
                p_id INT PRIMARY KEY AUTO_INCREMENT,
                pname VARCHAR(100) NOT NULL,
                p_price DECIMAL(10,2) NOT NULL,
                p_stock INT NOT NULL
            )
            """)
            
            cursor.execute("""
            CREATE TABLE IF NOT EXISTS bill_details (
                sl_no INT PRIMARY KEY AUTO_INCREMENT,
                bill_id INT NOT NULL,
                c_id INT NOT NULL,
                p_id INT NOT NULL,
                p_price DECIMAL(10,2) NOT NULL,
                quantity INT NOT NULL,
                timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
            """)
            
            cursor.execute("""
            CREATE TABLE IF NOT EXISTS audit_table (
                bill_id INT PRIMARY KEY AUTO_INCREMENT,
                c_id INT NOT NULL,
                c_name VARCHAR(100) NOT NULL,
                c_address VARCHAR(255) NOT NULL,
                total_amount_payable DECIMAL(10,2) NOT NULL,
                timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
            """)
            conn.commit()
            st.sidebar.success("Database and Tables initialized successfully!")
        except Error as e:
            st.sidebar.error(f"Database initialization error: {e}")
        finally:
            cursor.close()
            conn.close()

if st.sidebar.button("Initialize/Check Database"):
    init_db()

conn = create_db_connection(db_host, db_user, db_password, db_name)

# ==========================================
# State Management
# ==========================================
if 'cart' not in st.session_state:
    st.session_state.cart = []
if 'current_customer' not in st.session_state:
    st.session_state.current_customer = None
if 'scanned_product_id' not in st.session_state:
    st.session_state.scanned_product_id = None

st.title("🛒 Supermarket Billing System")

if not conn or not conn.is_connected():
    st.warning("Please configure and connect to the database from the sidebar.")
    st.stop()

# ==========================================
# Tabs Setup
# ==========================================
tab1, tab2, tab3, tab4 = st.tabs(["Customer", "Scan & Cart", "Billing & Checkout", "Products Management (Admin)"])

# ==========================================
# 1. Customer Section
# ==========================================
with tab1:
    st.header("Customer Details")
    phone_search = st.text_input("Search Customer by Phone Number", placeholder="e.g., 9876543210")
    
    if st.button("Search Customer"):
        if phone_search:
            cursor = conn.cursor(dictionary=True)
            cursor.execute("SELECT * FROM cust_details WHERE cust_ph_no = %s", (phone_search,))
            customer = cursor.fetchone()
            cursor.close()
            
            if customer:
                st.success(f"Customer Found: {customer['cust_name']}")
                st.session_state.current_customer = customer
            else:
                st.warning("Customer not found. Please register below.")
                st.session_state.current_customer = None
        else:
            st.error("Please enter a phone number.")
            
    if st.session_state.current_customer:
        st.info(f"Current Active Customer: **{st.session_state.current_customer['cust_name']}** (ID: {st.session_state.current_customer['cust_id']})")
        if st.button("Clear Current Customer"):
            st.session_state.current_customer = None
            st.session_state.cart = []
            st.rerun()

    st.markdown("---")
    st.subheader("Register New Customer")
    with st.form("register_customer"):
        new_name = st.text_input("Name")
        new_phone = st.text_input("Phone Number")
        new_address = st.text_area("Address")
        submit_reg = st.form_submit_button("Register")
        
        if submit_reg:
            if new_name and new_phone and new_address:
                cursor = conn.cursor()
                try:
                    cursor.execute("INSERT INTO cust_details (cust_name, cust_ph_no, cust_address) VALUES (%s, %s, %s)", 
                                   (new_name, new_phone, new_address))
                    conn.commit()
                    st.success("Customer registered successfully! You can now search for them.")
                except Error as e:
                    st.error(f"Error registering customer: {e}")
                finally:
                    cursor.close()
            else:
                st.error("Please fill all fields.")

# ==========================================
# 2. Scan & Cart Section
# ==========================================
with tab2:
    st.header("Scan Products & Add to Cart")
    if not st.session_state.current_customer:
        st.warning("Please select or register a customer in the 'Customer' tab first.")
    else:
        col1, col2 = st.columns(2)
        
        with col1:
            st.subheader("QR Scanner")
            
            qr_text = None
            
            camera_image = st.camera_input("Take a picture of the QR code to scan")
            if camera_image is not None:
                # Convert the file to an opencv image.
                file_bytes = np.asarray(bytearray(camera_image.read()), dtype=np.uint8)
                opencv_image = cv2.imdecode(file_bytes, 1)

                # Decode QR code using pyzbar (much more reliable than cv2)
                decoded_objects = decode(opencv_image)
                
                if decoded_objects:
                    qr_text = decoded_objects[0].data.decode('utf-8')
                    st.success(f"QR Code detected!")
                else:
                    st.warning("Could not detect a QR code. Make sure it's clearly visible and in focus.")
            
            # Manual entry fallback
            manual_id = st.text_input("Or enter Product ID manually:")
            if st.button("Use Manual ID"):
                qr_text = manual_id
                
            if qr_text:
                st.session_state.scanned_product_id = qr_text
                
        with col2:
            st.subheader("Product Details")
            if st.session_state.scanned_product_id:
                try:
                    # Extract just the first word/number in case the QR has extra text like '3 Sugar 1kg'
                    scanned_text = str(st.session_state.scanned_product_id).strip()
                    p_id_str = scanned_text.split()[0] if scanned_text else ""
                    p_id = int(p_id_str)
                    
                    cursor = conn.cursor(dictionary=True)
                    cursor.execute("SELECT * FROM product_details WHERE p_id = %s", (p_id,))
                    product = cursor.fetchone()
                    cursor.close()
                    
                    if product:
                        st.success("Product Found!")
                        st.write(f"**Name:** {product['p_name']}")
                        st.write(f"**Price:** ₹{product['p_price']}")
                        st.write(f"**Available Stock:** {product['p_stock']}")
                        
                        qty = st.number_input("Quantity", min_value=1, max_value=product['p_stock'], value=1)
                        if st.button("Add to Cart"):
                            if product['p_stock'] >= qty:
                                # Check if already in cart
                                item_exists = False
                                for item in st.session_state.cart:
                                    if item['p_id'] == product['p_id']:
                                        item['quantity'] += qty
                                        item_exists = True
                                        break
                                
                                if not item_exists:
                                    st.session_state.cart.append({
                                        'p_id': product['p_id'],
                                        'p_name': product['p_name'],
                                        'p_price': product['p_price'],
                                        'quantity': qty
                                    })
                                st.success(f"Added {qty} x {product['p_name']} to cart.")
                                st.session_state.scanned_product_id = None # reset
                                st.rerun()
                            else:
                                st.error("Insufficient stock!")
                    else:
                        st.error("Product ID not found in database.")
                except (ValueError, IndexError):
                    st.error(f"Invalid QR code format. Expected a Product ID number, but got: '{st.session_state.scanned_product_id}'")
            else:
                st.info("Scan a QR code or enter an ID to view details.")
                
        st.markdown("---")
        st.subheader("Current Cart")
        if st.session_state.cart:
            cart_df = pd.DataFrame(st.session_state.cart)
            cart_df['Total'] = cart_df['p_price'] * cart_df['quantity']
            st.dataframe(cart_df, use_container_width=True)
            
            if st.button("Clear Cart"):
                st.session_state.cart = []
                st.rerun()
        else:
            st.info("Cart is empty.")

# ==========================================
# 3. Billing & Checkout Section
# ==========================================
with tab3:
    st.header("Billing & Checkout")
    if not st.session_state.current_customer:
        st.warning("Please select a customer first.")
    elif not st.session_state.cart:
        st.warning("Cart is empty.")
    else:
        cust = st.session_state.current_customer
        st.write(f"**Customer:** {cust['cust_name']} | **Phone:** {cust['cust_ph_no']}")
        
        cart_df = pd.DataFrame(st.session_state.cart)
        cart_df['Total'] = cart_df['p_price'] * cart_df['quantity']
        
        st.table(cart_df[['p_name', 'p_price', 'quantity', 'Total']])
        
        grand_total = float(cart_df['Total'].sum())
        st.subheader(f"Grand Total: ₹{grand_total:.2f}")
        
        if st.button("Generate Bill & Checkout"):
            cursor = conn.cursor()
            try:
                # 1. Insert into audit_table to get bill_id
                cursor.execute("""
                    INSERT INTO audit_table (c_id, c_name, c_address, total_amount_payable) 
                    VALUES (%s, %s, %s, %s)
                """, (cust['cust_id'], cust['cust_name'], cust['cust_address'], grand_total))
                bill_id = cursor.lastrowid
                
                # 2. Insert items into bill_details and update stock
                for item in st.session_state.cart:
                    # Insert bill detail
                    cursor.execute("""
                        INSERT INTO bill_details (bill_id, c_id, p_id, p_price, quantity)
                        VALUES (%s, %s, %s, %s, %s)
                    """, (bill_id, cust['cust_id'], item['p_id'], item['p_price'], item['quantity']))
                    
                    # Update stock
                    cursor.execute("""
                        UPDATE product_details 
                        SET p_stock = p_stock - %s 
                        WHERE p_id = %s
                    """, (item['quantity'], item['p_id']))
                
                conn.commit()
                st.success(f"Bill Generated Successfully! Bill ID: {bill_id}")
                st.balloons()
                
                # Clear cart
                st.session_state.cart = []
            except Error as e:
                conn.rollback()
                st.error(f"Checkout failed: {e}")
            finally:
                cursor.close()

# ==========================================
# 4. Products Management (Admin/Test Setup)
# ==========================================
with tab4:
    st.header("Manage Products")
    st.info("Use this section to add initial products for testing.")
    
    with st.form("add_product"):
        p_name = st.text_input("Product Name")
        p_price = st.number_input("Price", min_value=0.01, step=0.5)
        p_stock = st.number_input("Initial Stock", min_value=1, step=1)
        add_btn = st.form_submit_button("Add Product")
        
        if add_btn:
            if p_name:
                cursor = conn.cursor()
                try:
                    cursor.execute("INSERT INTO product_details (pname, p_price, p_stock) VALUES (%s, %s, %s)",
                                   (p_name, p_price, p_stock))
                    conn.commit()
                    st.success("Product added successfully!")
                except Error as e:
                    st.error(f"Failed to add product: {e}")
                finally:
                    cursor.close()
            else:
                st.error("Product name is required.")
                
    st.subheader("Current Inventory")
    cursor = conn.cursor(dictionary=True)
    cursor.execute("SELECT * FROM product_details")
    products = cursor.fetchall()
    cursor.close()
    
    if products:
        st.dataframe(pd.DataFrame(products), use_container_width=True)
    else:
        st.write("No products in inventory.")
