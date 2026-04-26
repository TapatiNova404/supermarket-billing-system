# 🛒 Supermarket Billing System

A Streamlit-based **Supermarket Billing System** with **QR code product scanning**, **customer management**, **shopping cart**, **billing**, and **MySQL database integration**.

This project is designed to simulate a real-world supermarket billing workflow where products can be scanned using QR codes, added to a cart, and billed instantly.

---

## 🚀 Features

* 👤 **Customer Management**

  * Search customers by phone number
  * Register new customers
  * Store customer details in MySQL

## 📂 Project Structure

```bash
supermarket-billing-system/
│── supermarket_billing_streamlit.py                         # Main Streamlit billing application
│── qr_generator.py                # QR code generator script for products
│── README.md                      # Project documentation
│── requirements.txt               # Required Python libraries
│
├── qr_codes/                      # Folder containing generated QR code images
│   ├── 1.png
│   ├── 2.png
│   ├── 3.png
│   └── ...
```


* 📷 **QR Code Product Scanning**

  * Scan product QR codes using webcam
  * Decode QR using `pyzbar`
  * Manual product ID entry fallback

* 🛒 **Cart System**

  * Add scanned products to cart
  * Adjust quantity
  * View cart in real time
  * Clear cart when needed

* 🧾 **Billing & Checkout**

  * Generate customer bills
  * Store bill history
  * Update stock after purchase
  * Save final transaction in audit table

* 🗄️ **Database Integration**

  * MySQL database auto setup
  * Creates required tables automatically
  * Stores customers, products, bills, and transaction history

---

## 🛠️ Tech Stack

* **Frontend / App UI:** Streamlit
* **Backend:** Python
* **Database:** MySQL
* **Libraries Used:**

  * `streamlit`
  * `pandas`
  * `mysql-connector-python`
  * `opencv-python`
  * `numpy`
  * `pyzbar`

---

---

## ⚙️ Installation & Setup

### 1️⃣ Clone the Repository

```bash
git clone https://github.com/your-username/supermarket-billing-system.git
cd supermarket-billing-system
```

### 2️⃣ Install Dependencies

```bash
pip install -r requirements.txt
```

### 3️⃣ Install MySQL

Make sure MySQL is installed and running on your system.

Create/update your MySQL credentials in the sidebar when running the app.

### 4️⃣ Run the Streamlit App

```bash
streamlit run app.py
```

---

## 🗃️ Database Tables

The application automatically creates the following tables:

### 1. `cust_details`

Stores customer information.

| Column       | Type         | Description         |
| ------------ | ------------ | ------------------- |
| cust_id      | INT          | Primary Key         |
| cust_name    | VARCHAR(100) | Customer Name       |
| cust_ph_no   | VARCHAR(15)  | Unique Phone Number |
| cust_address | VARCHAR(255) | Customer Address    |

---

### 2. `product_details`

Stores product inventory.

| Column  | Type          | Description     |
| ------- | ------------- | --------------- |
| p_id    | INT           | Primary Key     |
| pname   | VARCHAR(100)  | Product Name    |
| p_price | DECIMAL(10,2) | Product Price   |
| p_stock | INT           | Available Stock |

---

### 3. `bill_details`

Stores item-wise billing details.

| Column    | Type          | Description        |
| --------- | ------------- | ------------------ |
| sl_no     | INT           | Primary Key        |
| bill_id   | INT           | Bill ID            |
| c_id      | INT           | Customer ID        |
| p_id      | INT           | Product ID         |
| p_price   | DECIMAL(10,2) | Product Price      |
| quantity  | INT           | Quantity Purchased |
| timestamp | TIMESTAMP     | Billing Time       |

---

### 4. `audit_table`

Stores final bill summary.

| Column               | Type          | Description       |
| -------------------- | ------------- | ----------------- |
| bill_id              | INT           | Primary Key       |
| c_id                 | INT           | Customer ID       |
| c_name               | VARCHAR(100)  | Customer Name     |
| c_address            | VARCHAR(255)  | Customer Address  |
| total_amount_payable | DECIMAL(10,2) | Final Bill Amount |
| timestamp            | TIMESTAMP     | Transaction Time  |

---

## 📸 How It Works

1. Configure MySQL credentials from the sidebar
2. Initialize database
3. Register or search customer
4. Scan product QR code using webcam
5. Add product to cart
6. Review cart
7. Generate bill
8. Checkout and update stock automatically

---

## 📦 requirements.txt

```txt
streamlit
pandas
mysql-connector-python
opencv-python
numpy
pyzbar
```

---

## 🔐 Important Note

Do **not** upload your real MySQL password publicly on GitHub.

Before uploading, replace this line in your code:

```python
db_password = st.sidebar.text_input("Password", value="your_password_here", type="password")
```

Never expose personal credentials in public repositories.

---

## 📌 Future Improvements

* Admin login authentication
* Printable PDF invoice
* Barcode scanner support
* Sales dashboard with analytics
* Product image support
* Discount & GST calculation

---

## 👩‍💻 Author

Developed by **Tapati Paul**

---

## 📜 License

This project is open-source and free to use for learning purposes.
