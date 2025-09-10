import streamlit as st


st.set_page_config(layout="centered",page_icon="./static/home.png",initial_sidebar_state="collapsed")




st.title("Receipt Automation Expenditure Tracker")





with st.container():
    st.markdown("""
            
            
     Receipt Automation system that allows users to upload scanned receipts (PDF files only--- currently.)
     The backend validates files, runs OCR + layout analysis, extracts structured fields (date, merchant, total, line items, taxes, payment method), 
    stores metadata and parsed results into a lightweight SQLite database.       
            
            
            
            """)
    col1,col2 = st.columns(2)
    with col1:
        st.image("frontend\static\dashboard.png")

    with col2:
        st.markdown("""
        This web app demonstrates the **Receipt Automation** project. 
                    Users can:


        - Upload scanned receipts (PDF files only !)
                    
                    """)
        
        


        st.markdown("""
        - Validate & process them via OCR + NLP
        - Extract structured fields (merchant, date, total, line items)
        - Store results in an SQLite database
        - Retrieve and review receipts via REST API


    


        ---
        
        """)


with st.container():
    dev , details = st.columns(2)


    with dev:


        st.markdown("""
                **Developer:** Aman Sah \n
                **Email:** [amansah1717@gmail.com](mailto:amansah1717@gmail.com)
                **GitHub:** [github.com/Amansah17](https://github.com/Amansah17)
                **Portfolio:** [sahaman-smarted.onrender.com](https://sahaman-smarted.onrender.com/)
                **LinkedIn:** [linkedin.com/in/aman-sah-8a320b14b](https://www.linkedin.com/in/aman-sah-8a320b14b/)

        """)


    with details:
        st.markdown("Github url: ------------------")
        st.markdown("youtube -----------")
