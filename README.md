# TaskMaster Pro API 🚀

A professional-grade Task Management System built with **FastAPI**, **SQLite**, and a modern **Bootstrap 5** frontend. 

## ✨ Features

- **Secure Authentication:** JWT-based Login/Registration with Bcrypt password hashing.
- **Account Recovery:** Self-service "Forgot Password" feature using a secure Recovery Key.
- **Data Persistence:** SQLite database with SQLAlchemy ORM.
- **User Profiles:** Edit profile details (Name, Age, Profession) with email validation.
- **Data Privacy:** Users can only view, edit, and delete their *own* tasks.
- **Modern UI:** Responsive Dashboard, Modals, and visual feedback using Bootstrap 5.

## 🛠️ Tech Stack

- **Backend:** Python 3.11+, FastAPI, Uvicorn
- **Database:** SQLite, SQLAlchemy
- **Security:** Python-Jose (JWT), Passlib (Bcrypt)
- **Frontend:** HTML5, JavaScript (Fetch API), Bootstrap 5

## 🚀 How to Run Locally (bash/Terminal)

1. **Clone the repository**
    ```bash
    git clone https://github.com/officialakash96/fastapi-task-tracker.git
    cd fastapi-task-tracker


2. **Create a Virtual Environment**
    ```bash
    python3 -m venv venv
    source venv/bin/activate  # On Windows: venv\Scripts\activate

3. **Install Dependencies**
    ```bash
    pip install -r requirements.txt

4. **Start the Server**
    ```bash
    uvicorn main:app --reload

5. **Access the app**
    ```
    Dashboard: Open http://127.0.0.1:8000 in your browser.
    API Docs: Open http://127.0.0.1:8000/docs

----------------------
📸 Screenshots (Dashboard and Login screen)
<img width="405" height="481" alt="image" src="https://github.com/user-attachments/assets/43c76f42-b257-4362-a54b-795a88aa69ec" />
<img width="1316" height="379" alt="image" src="https://github.com/user-attachments/assets/1558e346-49e2-46e5-be4e-29305b531e03" />


----------------------
Created by Akash Singh
