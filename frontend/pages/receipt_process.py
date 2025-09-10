import streamlit as st
import pandas as pd
import requests

st.title("Receipt Processing Software")

# ---------------- Step 1: Fetch all receipts ----------------
response = requests.get("http://localhost:8000/list_receipts/")
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
    response = requests.post(f"http://localhost:8000/process_receipt/{receipt_id}")
    if response.status_code == 200:
        data = response.json().get("data", [])
        if data:
            df_result = pd.DataFrame(data)
            st.subheader(f"Extracted Data for Receipt ID: {receipt_id}")
            st.dataframe(df_result)
        else:
            st.warning("No data returned after processing.")
    else:
        st.error(f"Error: {response.json().get('detail')}")
