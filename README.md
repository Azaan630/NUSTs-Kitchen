# NUST's Kitchen — Smart Mess Management

> *"With great food, comes great responsibility!"*

A full-stack, role-based mess management platform purpose-built for NUST hostels — handling menu planning, billing, inventory, voting, and analytics in one unified system.

---

## 🧱 Architecture

```
┌─────────────────────┐     ┌──────────────────┐     ┌───────────┐
│   Flet Frontend     │────▶│   FastAPI Backend │────▶│  MySQL 8  │
│  (Python/Flutter)   │◀────│   (REST + Auth)  │◀────│  (Aiven)  │
└─────────────────────┘     └──────────────────┘     └───────────┘
        │                          │
        ▼                          ▼
   Google OAuth                Gmail SMTP
```

---

## ✨ Features

### 🍽️ Menu & Scheduling
- **7-Day Weekly Menu** — Breakfast, Lunch, Dinner for a full week
- **Meal-Type Grouping** — Items organized and colored by meal slot
- **Drag-Drop Admin** — Add/remove items to any schedule slot
- **Interactive Food Cards** — Click any item to see image, price, ingredients & cooking steps
- **Menu Polls** — Students vote on upcoming meals; most votes win

### 💰 Billing & Payments
- **Auto Monthly Bills** — Per-student billing with mess-off day deductions
- **Payment Tracking** — Collected vs outstanding with partial payment support
- **Overdue Alerts** — Bills past due date auto-flagged in red
- **Transaction History** — Full audit of all payments (Cash, Card, Online)
- **CSV & PDF Export** — Download bills and student lists

### 📦 Inventory & Recipes
- **20+ Ingredients** — Real-time stock tracking with unit cost profiling
- **Low-Stock Alerts** — Items below threshold highlighted for quick restocking
- **Cost Analysis** — Per-item cost calculated from ingredient quantities & prices
- **15 Food Items** — Each with image, price, and full cooking steps
- **Recipe CRUD** — Staff/Admin can add, edit, delete recipe ingredients
- **Recipe Detail Pages** — Full-page recipe view with centered image, ingredients, and step-by-step instructions

### ⭐ Ratings & Voting
- **5-Star Ratings** — Students rate dishes after meals
- **Live Average Triggers** — DB triggers auto-update rating averages
- **Rating Analytics** — Bar/line charts showing trends and top dishes
- **Active Polls** — Real-time voting with live results

### 📋 Mess-Off Management
- **Request System** — Students apply for mess-off with date ranges
- **Approve/Reject** — Staff review and respond to requests
- **Auto Emails** — Registration, approval, deletion, and bill notifications via Gmail SMTP
- **Status Tracking** — Pending, Approved, Rejected, Cancelled

### 📊 Admin Dashboard
- **Live Stats** — Students, Staff, Food Items, Ingredients, Active Mess-Offs, Unpaid Bills
- **Bar Charts** — Avg ratings per item, stock levels
- **Line Charts** — Price trends, menu ratings, billing trends, daily activity, cost profiles
- **Pie Chart** — Student vs Staff population
- **Non-duplicate X-Axis** — Smart label truncation with auto-suffix for unique names

### 👥 User Management
- **3 Roles** — Admin, Staff, Student with permission-gated endpoints
- **Google OAuth** — Sign in with your NUST SEECS Google account
- **Registration Requests** — New users apply; admin approves or rejects
- **Staff Categories** — Head Chef, Chef, Server, Cleaner with salaries & hours
- **Multivalued Contacts** — Staff can have multiple phone numbers

### 📧 Automated Emails (Gmail SMTP)
- Registration request received
- Registration approved — welcome email
- Account deleted — removal notification
- Bill issued — amount, month, due date
- Feedback submitted — stored in DB, viewable in Admin panel

### 🎨 UI/UX
- **Dark/Light Theme** — Toggle with smooth transition
- **Glassmorphism Landing** — Gradient hero with animated logo splash
- **15 Flip Cards** — Feature highlights with tap-to-flip reveal
- **Bounce Arrow** — Scroll indicator at hero bottom
- **Responsive** — Mobile-first with adaptive layouts
- **Floating Feedback** — Popup form on every page, saved to DB
- **Animated Charts** — All admin charts have entry animations

---

## 🛠 Tech Stack

| Layer | Technology |
|-------|-----------|
| Backend | FastAPI (Python) |
| Database | MySQL 8.0 (Aiven) |
| Frontend | Flet 0.85.3 (Python → Flutter) |
| Auth | Google OAuth 2.0 |
| Email | Gmail SMTP (TLS, port 587) |
| Hosting | Azure Container Apps |
| CI/CD | GitHub Actions → GHCR |
| PDF | ReportLab |
| Charts | flet_charts (BarChart, LineChart, PieChart) |
| Icons | Material Icons (Rounded) |

---

## 📁 Project Structure

```
.
├── backend/
│   ├── main.py              # FastAPI app + all endpoints
│   ├── auth.py              # API key verification + email extraction
│   ├── database.py          # MySQL connection pool + runtime seeder
│   ├── seed.sql             # Minimal auto-init (3 core users + table safety)
│   ├── email_utils.py       # Gmail SMTP email templates + sender
│   ├── dao/                 # Data access objects
│   │   ├── base.py          # BaseDAO (_fetchall, _fetchone, _execute)
│   │   ├── queries.py       # All SQL queries
│   │   ├── user_dao.py      # User CRUD
│   │   ├── food_dao.py      # Food items, ingredients, recipes
│   │   ├── menu_dao.py      # Menu schedule
│   │   ├── bill_dao.py      # Bills & transactions
│   │   ├── poll_dao.py      # Voting & polls
│   │   └── registration_dao.py
│   └── models.py            # Pydantic models
├── db/
│   ├── init.sql             # Full schema (17 tables, views, procedures, triggers)
│   ├── migration.sql        # Column additions (Image_Path, Profile_Picture)
│   └── seed.sql             # Comprehensive seed data (run in MySQL Workbench)
├── frontend_main/
│   ├── main.py              # Flet app entry, landing page, auth flow
│   ├── mock_data.py         # Guest mode data (mirrors seed.sql)
│   └── pages/
│       ├── admin_page.py    # Admin dashboard (13 tabs)
│       ├── staff_page.py    # Staff portal (4 tabs)
│       ├── home_page.py     # Student menu view
│       ├── profile_page.py  # Student profile + bills
│       ├── voting_page.py   # Poll voting
│       ├── mess_off_page.py # Mess-off requests
│       └── api_client.py    # Shared HTTP client with API key
├── .github/workflows/
│   └── deploy.yml           # GitHub Actions → build & push to GHCR
├── docker-compose.yml
├── run_init.py              # Schema deployment script
└── .env                     # Environment variables
```

---

## 🔑 Environment Variables

### Backend
| Variable | Description |
|----------|-------------|
| `DB_HOST` | MySQL host |
| `DB_USER` | MySQL user |
| `DB_PASSWORD` | MySQL password |
| `DB_NAME` | MySQL database name |
| `DB_PORT` | MySQL port (default 3306) |
| `BACKEND_API_KEY` | Shared API key between frontend & backend |
| `GMAIL_APP_PASSWORD` | Gmail app password for SMTP emails |
| `GMAIL_USER` | Gmail address (default: zainif63@gmail.com) |

### Frontend
| Variable | Description |
|----------|-------------|
| `BACKEND_URL` | Backend URL |
| `PUBLIC_BACKEND_URL` | Public backend URL for PDF/CSV downloads |
| `BACKEND_API_KEY` | Same key as backend |
| `GOOGLE_CLIENT_ID` | Google OAuth client ID |
| `GOOGLE_CLIENT_SECRET` | Google OAuth client secret |
| `OAUTH_REDIRECT_URL` | OAuth callback URL |

---

## 🔄 CI/CD — GitHub Actions

Every push to `main` triggers `.github/workflows/deploy.yml` which:

1. **Builds** both Docker images (`backend` from `./backend`, `flet-app` from `./frontend_main`)
2. **Tags** each with `:latest` and the commit SHA (for rollbacks)
3. **Pushes** to GitHub Container Registry (GHCR) — free, no external registry needed

Images land at:
- `ghcr.io/Azaan630/nust-kitchen-backend:latest`
- `ghcr.io/Azaan630/nust-kitchen-flet-app:latest`

Azure Container Apps pulls directly from GHCR on each deployment. Just set `GITHUB_TOKEN` as the registry password.

### One-Time Setup
```bash
# Enable package permissions
GitHub Repo → Settings → Actions → General → Workflow permissions → Read and write packages
```

---

## 📜 License

MIT License

---

*Built with ❤️ at NUST SEECS*
