import os
import sqlite3
from datetime import datetime
from zoneinfo import ZoneInfo
from fastapi.responses import FileResponse
import psycopg2
from psycopg2.extras import RealDictCursor

from fastapi import FastAPI, HTTPException, Form
from fastapi.responses import FileResponse, HTMLResponse
from pydantic import BaseModel


app = FastAPI()
@app.get("/google95eac2fcd01cf588.html", include_in_schema=False)
def google_verification():
    return FileResponse(
        "google95eac2fcd01cf588.html",
        media_type="text/html"
    )
@app.get("/robots.txt", include_in_schema=False)
def robots_txt():
    return FileResponse(
        "robots.txt",
        media_type="text/plain"
    )
@app.get("/sitemap.xml", include_in_schema=False)
def sitemap_xml():
    return FileResponse(
        "sitemap.xml",
        media_type="application/xml"
    )
# ==================================================
# SETTINGS
# ==================================================

DATABASE_URL = os.getenv("DATABASE_URL")

# מקומית אפשר להמשיך עם 1234 עד שנגדיר סיסמה ב-Render
ADMIN_PASSWORD = os.getenv("ADMIN_PASSWORD", "1234")

USE_POSTGRES = bool(DATABASE_URL)


# ==================================================
# DATABASE CONNECTION
# ==================================================

def get_connection():

    if USE_POSTGRES:

        return psycopg2.connect(
            DATABASE_URL,
            cursor_factory=RealDictCursor
        )

    return sqlite3.connect(
        "customers.db"
    )


# ==================================================
# DATABASE INITIALIZATION
# ==================================================

def create_database():

    connection = get_connection()
    cursor = connection.cursor()

    if USE_POSTGRES:

        cursor.execute("""
            CREATE TABLE IF NOT EXISTS customers (
                id SERIAL PRIMARY KEY,
                name TEXT NOT NULL,
                phone TEXT NOT NULL,
                business TEXT DEFAULT '',
                service TEXT DEFAULT '',
                message TEXT DEFAULT '',
                created_at TEXT,
                status TEXT DEFAULT 'חדש'
            )
        """)

    else:

        cursor.execute("""
            CREATE TABLE IF NOT EXISTS customers (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                name TEXT NOT NULL,
                phone TEXT NOT NULL,
                business TEXT DEFAULT '',
                service TEXT DEFAULT '',
                message TEXT DEFAULT '',
                created_at TEXT,
                status TEXT DEFAULT 'חדש'
            )
        """)

        # תאימות למסד SQLite ישן
        cursor.execute("PRAGMA table_info(customers)")

        columns = [
            column[1]
            for column in cursor.fetchall()
        ]

        if "created_at" not in columns:

            cursor.execute(
                "ALTER TABLE customers ADD COLUMN created_at TEXT"
            )

        if "status" not in columns:

            cursor.execute(
                "ALTER TABLE customers ADD COLUMN status TEXT DEFAULT 'חדש'"
            )

    connection.commit()
    cursor.close()
    connection.close()


create_database()


# ==================================================
# CUSTOMER MODEL
# ==================================================

class Customer(BaseModel):

    name: str
    phone: str
    business: str = ""
    service: str = ""
    message: str = ""


# ==================================================
# WEBSITE FILES
# ==================================================

@app.get("/")
def home():

    return FileResponse(
        "company-home.html"
    )


@app.get("/company-style.css")
def style():

    return FileResponse(
        "company-style.css"
    )


@app.get("/company.js")
def javascript():

    return FileResponse(
        "company.js"
    )


# ==================================================
# SAVE CUSTOMER
# ==================================================

@app.post("/customers")
def save_customer(customer: Customer):

    connection = get_connection()
    cursor = connection.cursor()

    israel_time = datetime.now(
        ZoneInfo("Asia/Jerusalem")
    )

    created_at = israel_time.strftime(
        "%d/%m/%Y %H:%M"
    )

    if USE_POSTGRES:

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
            VALUES (%s, %s, %s, %s, %s, %s, %s)
        """, (
            customer.name,
            customer.phone,
            customer.business,
            customer.service,
            customer.message,
            created_at,
            "חדש"
        ))

    else:

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

    cursor.close()
    connection.close()

    return {
        "success": True,
        "message": "הפרטים נשמרו בהצלחה"
    }
    if USE_POSTGRES:

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
            VALUES (%s, %s, %s, %s, %s, %s, %s)
        """, (
            customer.name,
            customer.phone,
            customer.business,
            customer.service,
            customer.message,
            created_at,
            "חדש"
        ))

    else:

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

    cursor.close()
    connection.close()

    return {
        "success": True,
        "message": "הפרטים נשמרו בהצלחה"
    }


# ==================================================
# ADMIN LOGIN PAGE
# ==================================================

@app.get("/admin")
def admin_login():

    try:

        with open(
            "admin-login.html",
            "r",
            encoding="utf-8"
        ) as file:

            html = file.read()

        return HTMLResponse(
            content=html
        )

    except FileNotFoundError:

        return HTMLResponse(
            content="<h1>admin-login.html לא נמצא</h1>",
            status_code=500
        )


# ==================================================
# ADMIN LOGIN CHECK
# ==================================================

@app.post("/admin/login")
def admin_login_check(
    password: str = Form(...)
):

    if password != ADMIN_PASSWORD:

        raise HTTPException(
            status_code=401,
            detail="סיסמה שגויה"
        )

    return {
        "success": True
    }


# ==================================================
# ADMIN PAGE
# ==================================================

@app.get("/admin.html")
def admin_page():

    return FileResponse(
        "admin.html"
    )


# ==================================================
# GET CUSTOMERS
# ==================================================

@app.get("/customers-list")
def get_customers(
    password: str = ""
):

    if password != ADMIN_PASSWORD:

        raise HTTPException(
            status_code=401,
            detail="גישה לא מורשית"
        )

    connection = get_connection()

    if USE_POSTGRES:

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

        customers = cursor.fetchall()

    else:

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

        rows = cursor.fetchall()

        columns = [
            "id",
            "name",
            "phone",
            "business",
            "service",
            "message",
            "created_at",
            "status"
        ]

        customers = [
            dict(
                zip(columns, row)
            )
            for row in rows
        ]

    cursor.close()
    connection.close()

    return customers


# ==================================================
# DELETE CUSTOMER
# ==================================================

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

    connection = get_connection()
    cursor = connection.cursor()

    if USE_POSTGRES:

        cursor.execute(
            """
            DELETE FROM customers
            WHERE id = %s
            """,
            (customer_id,)
        )

    else:

        cursor.execute(
            """
            DELETE FROM customers
            WHERE id = ?
            """,
            (customer_id,)
        )

    deleted = cursor.rowcount

    connection.commit()

    cursor.close()
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


# ==================================================
# UPDATE STATUS
# ==================================================

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

    connection = get_connection()
    cursor = connection.cursor()

    if USE_POSTGRES:

        cursor.execute(
            """
            UPDATE customers
            SET status = %s
            WHERE id = %s
            """,
            (
                status,
                customer_id
            )
        )

    else:

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

    updated = cursor.rowcount

    connection.commit()

    cursor.close()
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


# ==================================================
# HEALTH CHECK
# ==================================================

@app.get("/health")
def health():

    return {
        "status": "ok",
        "database": "postgresql" if USE_POSTGRES else "sqlite"
    }