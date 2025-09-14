import streamlit as st
import pandas as pd
import requests
from pathlib import Path
import json
from streamlit_lottie import st_lottie
import json
from utils import  extract_text_pdfplumber, extract_receipt_data 

BASE_DIR = Path(__file__).resolve().parent

def static_file(filename: str) -> str:
    """Return absolute path to a file in static/ folder"""
    return str(BASE_DIR / "static" / filename)
# -----------------------------
# 🔹 Path Helpers (Cross-Platform)
# -----------------------------
BASE_DIR = Path(__file__).resolve().parent

def load_lottiefile(filepath: str):
    """Load a Lottie animation JSON file"""
    with open(filepath, "r") as f:
        return json.load(f)

st.set_page_config(page_title="dashboard.", layout="wide",initial_sidebar_state="collapsed")
st.title("Dashbord for Uploaded Receipts in Database")


with st.container():
    db , list_receipt = st.columns(2)

    with db:
        st.subheader("step 1 : All the uploaded files gets saved to hosted server locally")
        lottie_anim_dbs = load_lottiefile(static_file("Accounting.json"))
        #st_lottie(lottie_upload, height=400, width=620, key="validate_process_anim")
        st_lottie(
    lottie_anim_dbs,
    speed=1,
    reverse=False,
    loop=True,
    quality="high",
    height=400,
    width=400,
    key="lottie_animation",
)
        



    with list_receipt:



        # ---------------- Step 1: Fetch all receipts ----------------
        response = requests.get("http://localhost:8000/list_receipts/")
        if response.status_code == 200:
            receipts = response.json().get("data", [])
            df_receipts = pd.DataFrame(receipts)
            st.subheader("All Uploaded Receipts files present in DB")
            st.dataframe(df_receipts)
        else:
            st.error("Failed to fetch receipts from backend.")

        # ---------------- Step 2: User selects/enters ID ----------------
        receipt_id = st.number_input("Enter Receipt ID to Process:", min_value=1, step=1)







        if st.button("Process Receipt"):
            response = requests.post(f"http://localhost:8000/process_receipt/{receipt_id}")
            if response.status_code == 200:
                data = response.json().get("data", [20])
                if data:
                    df_result = pd.DataFrame(data)
                    st.subheader(f"Extracted Data for Receipt ID: {receipt_id}")
                    st.dataframe(df_result)
                else:
                    st.warning("No data returned after processing.")
            else:
                st.error(f"Error: Please validate the file first .")
