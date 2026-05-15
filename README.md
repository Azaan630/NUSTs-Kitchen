# NUST's Kitchen - Mess Management System

NUST's Kitchen is a comprehensive mess management solution designed to streamline dining hall operations. It provides a robust backend API, a user-friendly interface for diners, and a data-driven dashboard for administrators.

## 🚀 Tech Stack

- **Backend:** [FastAPI](https://fastapi.tiangolo.com/) (Python)
- **Database:** [MySQL 8.0](https://www.mysql.com/)
- **Main Frontend:** [Flet](https://flet.dev/) (Python-based Flutter framework)
- **Admin Dashboard:** [Streamlit](https://streamlit.io/)
- **Containerization:** [Docker](https://www.docker.com/) & [Docker Compose](https://docs.docker.com/compose/)
- **Reports:** ReportLab (PDF Generation)

## ✨ Features

- **User Roles & Permissions:** Secure access control for diners and administrators.
- **Menu Scheduling:** Dynamic management and automation of daily meal schedules.
- **Polls & Feedback:** Interactive polling system to gather diner preferences.
- **PDF Report Generation:** Automated generation of printable menus and reports.
- **Admin Analytics:** Visualized insights into mess usage and user feedback.
- **Dockerized Workflow:** Easy deployment using multi-container orchestration.

## 📁 Project Structure

```text
DB_Project/
├── backend/            # FastAPI source code, models, and DAOs
├── db/                 # Database initialization scripts (init.sql)
├── frontend_main/      # User-facing application (Flet)
├── frontend_admin/     # Administrator dashboard (Streamlit)
├── docker-compose.yml  # Multi-container orchestration
└── .env                # Environment configuration
```

## 🛠️ Installation & Setup

### Using Docker (Recommended)

1. **Clone the repository:**
   ```bash
   git clone https://github.com/AzaanNust/DB_Project.git
   cd DB_Project
   ```

2. **Configure Environment Variables:**
   Create a `.env` file in the root directory and add your database credentials.

3. **Spin up the containers:**
   ```bash
   docker-compose up --build
   ```

4. **Access the services:**
   - **Backend API:** `http://localhost:8000`
   - **Main App (Flet):** `http://localhost:8550`
   - **Admin Dashboard (Streamlit):** `http://localhost:8501`

### Manual Setup (Development)

Each component (`backend`, `frontend_main`, `frontend_admin`) contains its own `requirements.txt`. You can set up virtual environments for each and run them locally:

- **Backend:** `uvicorn main:app --reload`
- **User App:** `python main.py`
- **Admin:** `streamlit run Home.py`

## 📜 License

This project is licensed under the MIT License.

---
*Developed as part of a Database Systems course project.*
