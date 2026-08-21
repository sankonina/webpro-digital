from fastapi import FastAPI, HTTPException, Form
from fastapi.responses import FileResponse, HTMLResponse
from pydantic import BaseModel
import sqlite3
from datetime import datetime

app = FastAPI()

ADMIN_PASSWORD = "1234"


# =========================
# DATABASE
# =========================

def create_database():

    connection = sqlite3.connect("customers.db")
    cursor = connection.cursor()

    cursor.execute("""
        CREATE TABLE IF NOT EXISTS customers (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT NOT NULL,
            phone TEXT NOT NULL,
            business TEXT,
            service TEXT,
            message TEXT,
            created_at TEXT,
            status TEXT DEFAULT 'חדש'
        )
    """)

    # Check existing columns
    cursor.execute("PRAGMA table_info(customers)")
    columns = [column[1] for column in cursor.fetchall()]

    # Add created_at to an old database
    if "created_at" not in columns:

        cursor.execute(
            "ALTER TABLE customers ADD COLUMN created_at TEXT"
        )

        current_time = datetime.now().strftime(
            "%d/%m/%Y %H:%M"
        )

        cursor.execute(
            """
            UPDATE customers
            SET created_at = ?
            WHERE created_at IS NULL
            """,
            (current_time,)
        )

    # Add status to an old database
    if "status" not in columns:

        cursor.execute(
            """
            ALTER TABLE customers
            ADD COLUMN status TEXT DEFAULT 'חדש'
            """
        )

        cursor.execute(
            """
            UPDATE customers
            SET status = 'חדש'
            WHERE status IS NULL
            """
        )

    connection.commit()
    connection.close()


create_database()


# =========================
# CUSTOMER MODEL
# =========================

class Customer(BaseModel):

    name: str
    phone: str
    business: str = ""
    service: str = ""
    message: str = ""


# =========================
# MAIN WEBSITE
# =========================

@app.get("/")
def home():

    return FileResponse("company-home.html")


@app.get("/company-style.css")
def style():

    return FileResponse("company-style.css")


@app.get("/company.js")
def javascript():

    return FileResponse("company.js")


# =========================
# SAVE CUSTOMER
# =========================

@app.post("/customers")
def save_customer(customer: Customer):

    connection = sqlite3.connect("customers.db")
    cursor = connection.cursor()

    created_at = datetime.now().strftime(
        "%d/%m/%Y %H:%M"
    )

    cursor.execute("""
        INSERT INTO customers
        (
            name,
            phone,
            business,
            service,
            message,
            created_at,
            status
        )
        VALUES (?, ?, ?, ?, ?, ?, ?)
    """, (
        customer.name,
        customer.phone,
        customer.business,
        customer.service,
        customer.message,
        created_at,
        "חדש"
    ))

    connection.commit()
    connection.close()

    return {
        "success": True,
        "message": "הפרטים נשמרו בהצלחה"
    }


# =========================
# ADMIN LOGIN PAGE
# =========================

@app.get("/admin")
def admin_login():

    try:

        with open(
            "admin-login.html",
            "r",
            encoding="utf-8"
        ) as file:

            html = file.read()

        return HTMLResponse(content=html)

    except FileNotFoundError:

        return HTMLResponse(
            content="<h1>admin-login.html לא נמצא</h1>",
            status_code=500
        )


# =========================
# CHECK ADMIN PASSWORD
# =========================

@app.post("/admin/login")
def admin_login_check(password: str = Form(...)):

    if password != ADMIN_PASSWORD:

        raise HTTPException(
            status_code=401,
            detail="סיסמה שגויה"
        )

    return {
        "success": True
    }


# =========================
# ADMIN PAGE
# =========================

@app.get("/admin.html")
def admin_page():

    return FileResponse("admin.html")


# =========================
# GET CUSTOMERS
# =========================

@app.get("/customers-list")
def get_customers(password: str = ""):

    if password != ADMIN_PASSWORD:

        raise HTTPException(
            status_code=401,
            detail="גישה לא מורשית"
        )

    connection = sqlite3.connect("customers.db")

    connection.row_factory = sqlite3.Row

    cursor = connection.cursor()

    cursor.execute("""
        SELECT
            id,
            name,
            phone,
            business,
            service,
            message,
            created_at,
            status
        FROM customers
        ORDER BY id DESC
    """)

    customers = [
        dict(row)
        for row in cursor.fetchall()
    ]

    connection.close()

    return customers


# =========================
# DELETE CUSTOMER
# =========================

@app.delete("/customers/{customer_id}")
def delete_customer(
    customer_id: int,
    password: str = ""
):

    if password != ADMIN_PASSWORD:

        raise HTTPException(
            status_code=401,
            detail="גישה לא מורשית"
        )

    connection = sqlite3.connect("customers.db")

    cursor = connection.cursor()

    cursor.execute(
        """
        DELETE FROM customers
        WHERE id = ?
        """,
        (customer_id,)
    )

    connection.commit()

    deleted = cursor.rowcount

    connection.close()

    if deleted == 0:

        raise HTTPException(
            status_code=404,
            detail="לקוח לא נמצא"
        )

    return {
        "success": True,
        "message": "הלקוח נמחק בהצלחה"
    }


# =========================
# UPDATE CUSTOMER STATUS
# =========================

@app.put("/customers/{customer_id}/status")
def update_customer_status(
    customer_id: int,
    status: str = "",
    password: str = ""
):

    if password != ADMIN_PASSWORD:

        raise HTTPException(
            status_code=401,
            detail="גישה לא מורשית"
        )

    allowed_statuses = [
        "חדש",
        "בטיפול",
        "הושלם"
    ]

    if status not in allowed_statuses:

        raise HTTPException(
            status_code=400,
            detail="סטטוס לא חוקי"
        )

    connection = sqlite3.connect("customers.db")

    cursor = connection.cursor()

    cursor.execute(
        """
        UPDATE customers
        SET status = ?
        WHERE id = ?
        """,
        (
            status,
            customer_id
        )
    )

    connection.commit()

    updated = cursor.rowcount

    connection.close()

    if updated == 0:

        raise HTTPException(
            status_code=404,
            detail="לקוח לא נמצא"
        )

    return {
        "success": True,
        "message": "הסטטוס עודכן בהצלחה"
    }