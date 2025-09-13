import os
from pathlib import Path
import json
import sqlite3
import asyncio
from datetime import datetime

import streamlit as st
import requests
import httpx
from streamlit_lottie import st_lottie

from config import DB_PATH


# -----------------------------
# 🔹 Path Helpers (Cross-Platform)
# -----------------------------
BASE_DIR = Path(__file__).resolve().parent

def static_file(filename: str) -> str:
    """Return absolute path to a file in static/ folder"""
    return str(BASE_DIR / "static" / filename)


# -----------------------------
# 🔹 API Settings
# -----------------------------
API_URL = "https://receipt-automation-backend-6nbp.onrender.com"

# Test backend connection (optional)
try:
    response = requests.get(f"{API_URL}/receipts", timeout=10)
    data = response.json()
except Exception as e:
    data = {"error": str(e)}


# -----------------------------
# 🔹 Utilities
# -----------------------------
def load_lottiefile(filepath: str):
    """Load a Lottie animation JSON file"""
    with open(filepath, "r") as f:
        return json.load(f)


async def upload_file(file):
    async with httpx.AsyncClient() as client:
        files = {"file": (file.name, file, "application/pdf")}
        response = await client.post(f"{API_URL}/upload", files=files)
        return response.json()


async def validate_file(file_id: int):
    async with httpx.AsyncClient() as client:
        response = await client.post(f"{API_URL}/validate/{file_id}")
        return response.json()


def save_processed_result(receipt_id, response_json):
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS processed_receipts (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            receipt_id INTEGER NOT NULL,
            processed_at TEXT NOT NULL,
            response_json TEXT NOT NULL
        )
    """)
    cursor.execute("""x
        INSERT INTO processed_receipts (receipt_id, processed_at, response_json)
        VALUES (?, ?, ?)
    """, (receipt_id, datetime.utcnow().isoformat(), json.dumps(response_json)))
    conn.commit()
    conn.close()
    print(f"[DEBUG] Saved receipt_id={receipt_id} into {DB_PATH}")


# -----------------------------
# 🔹 Streamlit Page Config
# -----------------------------
st.set_page_config(
    page_title="Home",
    page_icon=static_file("home.png"),
    initial_sidebar_state="expanded",
    layout="wide"
)


# -----------------------------
# 🔹 UI: Home Page
# -----------------------------
st.title("Autonomous Receipt Management ")

with st.container():
    st.markdown("""
    Receipt Automation system that allows users to upload scanned receipts (PDF files only).
    The backend validates files, runs OCR + layout analysis, extracts structured fields (date, merchant, total, line items, taxes, payment method),
    and stores metadata and parsed results into a lightweight SQLite database.
    """)
    col1, col2 = st.columns(2)

    with col1:
        lottie_upload = load_lottiefile(static_file("Accounting.json"))
        st_lottie(lottie_upload, height=400, width=620, key="validate_process_anim")

    with col2:
        st.header("Automate Accounts")
        st.subheader("The software uses ML, NLP, and NER models for data parsing, extracting meaningful results of your expenses.")
        st.text("""
        – Receipt Management System. A full-stack automation system to upload, process, and manage receipts.
        Backend (FastAPI) – Handles file uploads, validation, receipt extraction, and DB ops.
        Frontend (Streamlit/React) – Upload and view processed receipts.
        SQLite Database – Stores metadata for uploaded receipts.
        """)


# -----------------------------
# 🔹 Sidebar
# -----------------------------
with st.sidebar:
    st.markdown("### 🌟 Quick Actions Navbar")
    lottie_sidebar = load_lottiefile(static_file("uploading.json"))
    st_lottie(lottie_sidebar, height=250, width=250, key="sidebar_anim")

menu = ["Receipt Automation Upload", "Process Receipts", "View Receipts"]
choice = st.sidebar.selectbox("Menu", menu)


# -----------------------------
# 🔹 Upload & Validate
# -----------------------------
col1, col2 = st.columns(2)
uploaded_id = st.session_state.get("uploaded_id")

if choice == "Receipt Automation Upload":
    with col1:
        st.subheader("Upload Receipt")
        uploaded_file = st.file_uploader("Upload PDF", type=["pdf"])
        uploaded_id = st.session_state.get("uploaded_id")

        if uploaded_file and st.button("Upload"):
            with st.spinner("Uploading..."):
                result = asyncio.run(upload_file(uploaded_file))
                st.success("File Uploaded Successfully 🎉")
                st.json(result)

                if "id" in result:
                    st.session_state.uploaded_id = result["id"]

    with col2:
        st.subheader("Validate Receipt")

        if uploaded_id:
            st.write(f"Last uploaded file ID: **{uploaded_id}**")

        file_id = st.number_input("Enter File ID", min_value=1, value=uploaded_id or 1)

        if st.button("Validate"):
            with st.spinner("Validating..."):
                result = asyncio.run(validate_file(file_id))
                st.success("Validation Completed ✅")
                st.json(result)


# -----------------------------
# 🔹 Process Receipts
# -----------------------------
if choice == "Process Receipts":
    file_id = st.number_input("Enter File ID", min_value=1)
    if st.button("Process"):
        response = requests.post(f"{API_URL}/process_receipt/{file_id}")
        st.write(response.json())


# -----------------------------
# 🔹 View Receipts
# -----------------------------
if choice == "View Receipts":
    response = requests.get(f"{API_URL}/receipts")
    st.write(response.json())
