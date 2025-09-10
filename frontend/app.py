import streamlit as st
import requests


from config import DB_PATH
import sqlite3, json
from datetime import datetime
import httpx
import asyncio
#API_URL = "http://127.0.0.1:8000"
API_URL = "https://receipt-automation-backend-6nbp.onrender.com:8000"

response = requests.get(f"{API_URL}/")
data = response.json()

st.set_page_config(page_title= "Home",page_icon="./static/home.png",initial_sidebar_state="expanded",layout="wide")


st.title("Autonomous Receipt Management ")


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


menu = ["Upload Receipt", "Validate Receipt", "Process Receipt", "View Receipts"]
choice = st.sidebar.selectbox("Menu", menu)
file_uploader , validator = st.columns(2)

if choice == "Upload Receipt":
    
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
