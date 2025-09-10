import streamlit as st
import requests

API_URL = "http://127.0.0.1:8000"

st.title("Receipt Manager")

menu = ["Upload Receipt", "Validate Receipt", "Process Receipt", "View Receipts"]
choice = st.sidebar.selectbox("Menu", menu)

if choice == "Upload Receipt":
    uploaded_file = st.file_uploader("Upload PDF", type=["pdf"])
    if uploaded_file:
        files = {"file": (uploaded_file.name, uploaded_file, "application/pdf")}
        response = requests.post(f"{API_URL}/upload", files=files)
        st.write(response.json())

elif choice == "Validate Receipt":
    file_id = st.number_input("Enter File ID", min_value=1)
    if st.button("Validate"):
        response = requests.post(f"{API_URL}/validate/{file_id}")
        st.write(response.json())

elif choice == "Process Receipts":
    file_id = st.number_input("Enter File ID", min_value=1)
    if st.button("Process"):
        response = requests.post(f"{API_URL}/process_receipt/{file_id}")
        st.write(response.json())

elif choice == "View Receipts":
    response = requests.get(f"{API_URL}/receipts")
    st.write(response.json())




