import streamlit as st


st.set_page_config(layout="centered",page_icon="./static/home.png",initial_sidebar_state="collapsed")

st.title("Expenditure Tracker")


st.title("About Receipt Automation")
st.markdown("""
This web app demonstrates the **Receipt Automation** project. Users can:


- Upload scanned receipts (PDF/Images)
- Validate & process them via OCR + spaCy NLP
- Extract structured fields (merchant, date, total, line items)
- Store results in an SQLite database
- Retrieve and review receipts via REST API


**Tech stack:** FastAPI (backend), SQLite (database), Tesseract/EasyOCR (OCR), spaCy (NLP), Streamlit (UI).


---
**Developer:** Aman Sah
**Email:** [amansah1717@gmail.com](mailto:amansah1717@gmail.com)
**GitHub:** [github.com/Amansah17](https://github.com/Amansah17)
**Portfolio:** [sahaman-smarted.onrender.com](https://sahaman-smarted.onrender.com/)
**LinkedIn:** [linkedin.com/in/aman-sah-8a320b14b](https://www.linkedin.com/in/aman-sah-8a320b14b/)
""")