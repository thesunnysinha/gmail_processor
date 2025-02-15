# Gmail Email Processor

This project authenticates with **Gmail API** using OAuth, fetches emails, and applies rule-based actions. It uses **SQLAlchemy (SQLite3)** for storage, **Pydantic** for validation, and **Click** for CLI-based execution.

## 🚀 Features

- ✅ **Authenticate using OAuth** (No IMAP)
- ✅ **Fetch emails from Gmail**
- ✅ **Store emails in SQLite3 using SQLAlchemy**
- ✅ **Apply rule-based filtering from a JSON file**
- ✅ **Command-line interface (CLI)**
- ✅ **Modular, maintainable, and scalable**

## 📌 Installation

### 1️⃣ Clone the Repository
```sh
git clone https://github.com/thesunnysinha/gmail_processor.git
cd gmail_processor
```

### 2️⃣ Create a Virtual Environment
```sh
python3 -m venv venv
source venv/bin/activate   # macOS/Linux
venv\Scripts\activate      # Windows
```

### 3️⃣ Install Dependencies
```sh
pip install -r requirements.txt
```

### 4️⃣ Set Up OAuth Credentials
- Go to [Google Cloud Console](https://console.cloud.google.com/)
- Create OAuth 2.0 credentials for Gmail API
- Download `credentials.json` and place it in the project's secret directory.

### 📌 Usage

🔹 **Initialize Database**
```sh
python manage.py migrate
```
🔹 **Authenticate & Fetch Emails**
```sh
python manage.py fetch
```
🔹 **Apply Rules to Emails**
```sh
python manage.py apply_rules
```

### 📌 Running Tests
```sh
pytest tests/
```

### 📌 Example Rule in rules.json
```json
[
    {
        "predicate": "All",
        "conditions": [
            {"field": "From", "predicate": "Contains", "value": "example.com"},
            {"field": "Subject", "predicate": "Contains", "value": "Meeting"}
        ],
        "actions": [
            {"action": "Mark as Read"},
            {"action": "Move Message", "to_mailbox": "Important"}
        ]
    }
]
```

### 📌 Tech Stack
- Python (3.8+)
- SQLAlchemy (ORM)
- Pydantic (Data validation)
- Google API Client (OAuth)
- Click (CLI)
- SQLite3 (Database)
- Pytest (Testing)
- python
