import streamlit as st
import requests
from streamlit_lottie import st_lottie
import json

from config import DB_PATH
import sqlite3, json
from datetime import datetime
import httpx
from pathlib import Path

import asyncio
#API_URL = "http://127.0.0.1:8000"   #(For Local testing)
API_URL = "https://receipt-automation-backend-6nbp.onrender.com"   #for productionsetup deployment!)

response = requests.get(f"{API_URL}/receipts")
data = response.json()




# -----------------------------
# 🔹 Path Helpers (Cross-Platform)
# -----------------------------
BASE_DIR = Path(__file__).resolve().parent

def static_file(filename: str) -> str:
    """Return absolute path to a file in static/ folder"""
    return str(BASE_DIR / "static" / filename)


# ---------------------------

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

st.set_page_config(page_title= "Home",page_icon="./static/home.png",initial_sidebar_state="expanded",layout="wide")


st.title("Autonomous Receipt Management ")



with st.container():
    st.markdown("""
            
            
     Receipt Automation system that allows users to upload scanned receipts (PDF files only--- currently.)
     The backend validates files, runs OCR + layout analysis, extracts structured fields (date, merchant, total, line items, taxes, payment method), 
    stores metadata and parsed results into a lightweight SQLite database.       
            
            
            
            """)
    col1,col2 = st.columns(2)
    with col1:
        #st.image("frontend\static\dashboard.png")
        lottie_upload = load_lottiefile(static_file("Accounting.json"))
        st_lottie(lottie_upload, height=400, width=620, key="validate_process_anim")
        

    with col2:
        st.header("""Automate Accounts""")
        st.subheader("The software under the hood utilizes Machine Learning ,Nantural Language Processing , Near Entity Relationship(NLP -NER) "
        "-- small Language Models  - enabled with complex data parsing technique, it can extract meningful results of your expenses at various outlets.")
        

        st.text("""
         – Receipt Management System. A full-stack receipt automation system that allows users to upload, process, and manage receipts.
            """)

        st.text("""Backend (FastAPI) – Handles file uploads, validation, receipt extraction, and database operations.Frontend (Streamlit/React) – Provides an interface for uploading receipts, viewing processed data, and managing receipts.
            SQLite Database – Stores metadata for uploaded receipts.
                                
                    """)
        
        

# Two columns layout
col1, col2 = st.columns(2)

uploaded_id = st.session_state.get("uploaded_id")  # store last uploaded file ID

async def upload_file(file):
    async with httpx.AsyncClient() as client:
        files = {"file": (file.name, file, "application/pdf")}
        response = await client.post(f"{API_URL}/upload", files=files)
        return response.json()

async def validate_file(file_id: int):
    async with httpx.AsyncClient() as client:
        response = await client.post(f"{API_URL}/validate/{file_id}")
        return response.json()



with st.sidebar:
    st.markdown("### 🌟 Quick Actions Navbar :  Some pages are currently underdevelopment")
    lottie_sidebar = load_lottiefile("frontend/static/uploading.json")
    st_lottie(lottie_sidebar, height=250, width=250, key="sidebar_anim")








menu = ["Receipt Automation Upload",  "Process Receipt", "View Receipts"]
choice = st.sidebar.selectbox("Menu", menu)
file_uploader , validator = st.columns(2)

if choice == "Receipt Automation Upload":
    
# ---- LEFT COLUMN: Upload ----
    with st.container():
        with col1:
            st.subheader("Upload Receipt")
            uploaded_file = st.file_uploader("Upload PDF", type=["pdf"])
            uploaded_id = st.session_state.get("uploaded_id") 
            if uploaded_file and st.button("Upload"):
                with st.spinner("Uploading..."):
                    result = asyncio.run(upload_file(uploaded_file))
                    st.success("File Uploaded Successfully 🎉")
                    st.json(result)

                    # Save file_id to session state
                    if "id" in result:
                        st.session_state.uploaded_id = result["id"]
                

        # ---- RIGHT COLUMN: Validate ----
        with col2:
            st.subheader("Validate Receipt")

            if uploaded_id:  # auto-fill with last uploaded file_id
                st.write(f"Last uploaded file ID: **{uploaded_id}**")

            file_id = st.number_input("Enter File ID", min_value=1, value=uploaded_id or 1)

            if st.button("Validate"):
                with st.spinner("Validating..."):
                    result = asyncio.run(validate_file(file_id))
                    st.success("Validation Completed ✅")
                    st.json(result)

if choice == "Process Receipts":
    file_id = st.number_input("Enter File ID", min_value=1)
    if st.button("Process"):
        response = requests.post(f"{API_URL}/process_receipt/{file_id}")
        st.write(response.json())

if choice == "View Receipts":
    response = requests.get(f"{API_URL}/receipts")
    st.write(response.json())










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
    cursor.execute("""
        INSERT INTO processed_receipts (receipt_id, processed_at, response_json)
        VALUES (?, ?, ?)
    """, (receipt_id, datetime.utcnow().isoformat(), json.dumps(response_json)))
    conn.commit()
    conn.close()
    print(f"[DEBUG] Saved receipt_id={receipt_id} into {DB_PATH}")








#######################################################################
############################################

