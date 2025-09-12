import streamlit as st
import pandas as pd
import requests

import json
from streamlit_lottie import st_lottie
import json



def load_lottiefile(filepath: str):
    with open(filepath, "r") as f:
        return json.load(f)

st.set_page_config(page_title=" Uploaded file dashboard.", layout="wide",initial_sidebar_state="collapsed")
st.title("Dashbord for Uploaded Receipts in Database")


with st.container():
    db , list_receipt = st.columns(2)

    with db:
        st.subheader("step 1 : All the uploaded files gets saved to hosted server locally")
        lottie_animation_dbs = load_lottiefile("frontend\static\Database store.json")
        st_lottie(
    lottie_animation_dbs,
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
