# NUST's Kitchen - Mess Management System

NUST's Kitchen is a comprehensive mess management solution designed to streamline dining hall operations. It provides a robust backend API, a user-friendly interface for diners, and a data-driven dashboard for administrators.

## 🚀 Tech Stack

- **Backend:** [FastAPI](https://fastapi.tiangolo.com/) (Python)
- **Database:** [MySQL 8.0](https://www.mysql.com/)
- **Main Frontend:** [Flet](https://flet.dev/) (Python-based Flutter framework)
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
├── docker-compose.yml  # Multi-container orchestration
└── .env                # Environment configuration
```

# 🔗 Link: [NUST's Kitchen](https://nusts-kitchen-production-6c2e.up.railway.app)

## 📜 License

This project is licensed under the MIT License.

---
*Developed as part of a Database Systems course project.*
