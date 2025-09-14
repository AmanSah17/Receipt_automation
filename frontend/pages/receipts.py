import streamlit as st
import pandas as pd
import requests
import sqlite3
from datetime import datetime
import json
import os

from app import API_URL

st.set_page_config(layout="wide",initial_sidebar_state="collapsed")
st.title("Receipt Processing Service")

DB_PATH = "processed_receipts.db"













# ---------------- Create DB schema if not exists ----------------
def init_db():
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
    conn.commit()
    conn.close()

def save_processed_result(receipt_id, response_json):
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    cursor.execute("""
        INSERT INTO processed_receipts (receipt_id, processed_at, response_json)
        VALUES (?, ?, ?)
    """, (receipt_id, datetime.utcnow().isoformat(), json.dumps(response_json)))
    conn.commit()
    conn.close()

def get_all_processed():
    conn = sqlite3.connect(DB_PATH)
    df = pd.read_sql_query("SELECT * FROM processed_receipts", conn)
    conn.close()
    return df

# Initialize DB
init_db()

# ---------------- Step 1: Fetch all receipts ----------------
response = requests.get(f"{API_URL}/list_receipts/")
if response.status_code == 200:
    receipts = response.json().get("data", [])
    df_receipts = pd.DataFrame(receipts)
    st.subheader("All Receipts in DB")
    st.dataframe(df_receipts)
else:
    st.error("Failed to fetch receipts from backend.")

# ---------------- Step 2: User selects/enters ID ----------------
receipt_id = st.number_input("Enter Receipt ID to Process:", min_value=1, step=1)

if st.button("Process Receipt"):
    response = requests.post(f"{API_URL}/process_receipt/{receipt_id}")
    st.balloons()
    if response.status_code == 200:
        data = response.json().get("data", [])
        if data:
            df_result = pd.DataFrame(data)
            st.subheader(f"Extracted Data for Receipt ID: {receipt_id}")
            st.dataframe(df_result)

            # Save to local DB
            save_processed_result(receipt_id, data)
            st.success(f"Saved results for Receipt ID {receipt_id} to local DB ✅")
        else:
            st.warning("No data returned after processing.")
    else:
        st.error(f"Error: {response.json().get('detail')}")



# ---------------- Step 3: Show logs ----------------
if st.button("Show Processed database"):

    st.subheader("Processed Receipts saved to the receipt processed database !")
    st.balloons()
    st.dataframe(get_all_processed())



