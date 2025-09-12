
# 📑 Automate Accounts – Receipt Management System

A full-stack receipt automation system that allows users to **upload, process, and manage receipts**.  
The system consists of:

- **Backend (FastAPI)** – Handles file uploads, validation, receipt extraction, and database operations.
- **Frontend (Streamlit/React)** – Provides an interface for uploading receipts, viewing processed data, and managing receipts.
- **SQLite Database** – Stores metadata for uploaded receipts.

---

## ⚡ Features

- ✅ Upload PDF receipts
- ✅ Validate uploaded files
- ✅ Extract & process receipt details
- ✅ Store receipt metadata in SQLite
- ✅ View all receipts in a list
- ✅ View details of a specific receipt
- ✅ Async & fast reload API endpoints

---

## 🏗 Project Structure

```

automate-accounts/
│
├── config.py                  # Configuration (DB path, constants, etc.)
├── processed\_receipts.db      # SQLite database
│
├── backend/
│   └── main.py                # FastAPI backend (API endpoints)
│
├── frontend/
│   ├── app.py                 # Streamlit / Frontend entry
│   └── pages/
│       ├── upload.py          # Upload receipts page
│       └── receipts.py        # List & view receipts
│
└── README.md                  # Project documentation

````

---

## ⚙️ Installation

### 1. Clone the repository
```bash
git clone https://github.com/AmanSah17/Receipt_automation.git
cd automate-accounts
````

### 2. Create and activate virtual environment

```bash
python -m venv .venv
source .venv/bin/activate   # Linux / macOS
.venv\Scripts\activate      # Windows
```

### 3. Install dependencies

```bash
pip install -r requirements.txt
```

---

## ▶️ Running the Project

### 1. Start the Backend (FastAPI)

```bash
cd backend
uvicorn main:app --reload --host 0.0.0.0 --port 8000
```

This runs the API on `http://localhost:8000`

### 2. Start the Frontend

 using **Streamlit**:

```bash
cd frontend
streamlit run app.py
```


---

## 🌐 API Endpoints

### Receipts

* `GET /receipts` → List all receipts
* `GET /receipts/{id}` → Retrieve details of a specific receipt
* `POST /upload` → Upload a receipt file
* `POST /process` → Extract and process a receipt

---

## 🧪 Example Usage with cURL

### 1. Upload a Receipt

```bash
curl -X POST "http://localhost:8000/upload" \
  -F "file=@sample_receipt.pdf"
```

**Response:**

```json
{
  "id": 1,
  "file_name": "20250910_101751623699.pdf",
  "file_path": "./uploads/20250910_101751623699.pdf",
  "is_valid": true,
  "invalid_reason": null,
  "is_processed": false
}
```

---

### 2. List All Receipts

```bash
curl -X GET "http://localhost:8000/receipts"
```

**Response:**

```json
[
  {
    "id": 1,
    "file_name": "20250910_101751623699.pdf",
    "is_valid": true,
    "is_processed": false
  }
]
```

---

### 3. Get Details of a Specific Receipt

```bash
curl -X GET "http://localhost:8000/receipts/1"
```

**Response:**

```json
{
  "id": 1,
  "file_name": "20250910_101751623699.pdf",
  "file_path": "./uploads/20250910_101751623699.pdf",
  "is_valid": true,
  "invalid_reason": null,
  "is_processed": false
}
```

---

### 4. Process a Receipt

```bash
curl -X POST "http://localhost:8000/process" \
  -H "Content-Type: application/json" \
  -d '{"id": 1}'
```

**Response:**

```json
{
  "id": 1,
  "status": "processed",
  "details": {
    "vendor": "Amazon",
    "total_amount": "₹1999",
    "date": "2025-09-10"
  }
}
```

---

## 📸 Screenshots

### Upload Page

!(<img src="frontend\static\file_upload.png" alt="Upload and Validation Page" width="400"/>
)

### Receipt List Page

![Receipts Screenshot](Images\receipts.png)

---

## ⚡ Common Issues

### ❌ Connection refused: `http://localhost:8000`

* Ensure backend is running:

  ```bash
  uvicorn backend.main:app --reload --host 0.0.0.0 --port 8000
  ```
* If deployed (e.g., Render, Railway, etc.), replace
  `http://localhost:8000` with your backend’s **public URL** in the frontend code:

  ```python
  BASE_URL = "https://your-backend.onrender.com"
  ```

---

## 🚀 Deployment

### Backend

Deploy FastAPI to:

* [Render](https://render.com/)
* [Railway](https://railway.app/)
* [Heroku](https://www.heroku.com/)

### Frontend

Deploy to:

* [Vercel](https://vercel.com/)
* [Netlify](https://www.netlify.com/)
* [Streamlit Cloud](https://streamlit.io/cloud) (if using Streamlit)

---

## 📜 License

Apache License © 2025 \[Aman Sah ]

---

## 🤝 Contributing

Pull requests are welcome!
For major changes, please open an issue first to discuss what you’d like to change.

---

## 🧑‍💻 Author

Developed by **[Mr. Aman Sah](https://github.com/AmanSah17/)** 








