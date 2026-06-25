# Smart Visitor Entry & Exit Management System

A production-ready Streamlit web application for managing visitor entry and exit with QR codes, admin approval workflow, and comprehensive reporting.

---

## 🚀 Quick Start

### 1. Install dependencies
```bash
pip install -r requirements.txt
```

### 2. Run the app
```bash
streamlit run app.py
```

### 3. Access
Open your browser at: **http://localhost:8501**

---

## 🔐 Default Admin Login

| Field    | Value       |
|----------|-------------|
| Username | `admin`     |
| Password | `Admin@123` |

> **You will be prompted to change the password on first login.**

---

## 📁 Project Structure

```
vms/
├── app.py                  ← Main Streamlit application
├── requirements.txt        ← Python dependencies
├── .streamlit/
│   └── config.toml        ← Theme & server config
├── modules/
│   ├── __init__.py
│   ├── database.py        ← SQLite CRUD, schema, auth
│   ├── qr_utils.py        ← QR generation, badge, PDF pass
│   └── reports.py         ← Excel / CSV / PDF reports
└── data/                  ← Auto-created on first run
    ├── vms.db             ← SQLite database
    ├── visitors/          ← Visitor records (CSV backup)
    ├── photos/            ← Visitor photographs
    ├── logs/              ← Application logs
    ├── approvals/         ← Approval documents
    ├── exports/           ← Generated reports
    └── backups/           ← Database backups
```

---

## ✨ Features

### Visitor Self-Registration
- Unique auto-generated Visitor Number (VIS-00001, VIS-00002…)
- QR code generated on submission (for entry & exit)
- Photo upload
- ID verification fields
- Emergency contact capture
- Nigeria timezone (Africa/Lagos) timestamps

### Admin Portal
- Secure login with bcrypt-hashed passwords
- Role-based access: Super Admin, Security Officer, Receptionist
- Force password change on first login

### Approval Workflow
- View pending visitors with all details & photos
- One-click Approve / Reject / Request More Info
- Comments field for approval notes
- Audit trail of all approval actions

### Visitor Pass & Badge
- PNG badge with photo, QR code, and status
- PDF visitor pass (A6 size, printable)
- Downloadable directly from the browser

### Exit Management
- QR code scan or manual Visitor Number entry
- Automatic duration calculation
- Duplicate exit prevention
- Exit timestamp in Africa/Lagos timezone

### Dashboard Analytics
- Live stats: Today's visitors, Inside, Approved, Pending, Rejected, Checked Out
- 30-day visit trend (area chart)
- Visits by department (horizontal bar)
- Peak hours chart (today)
- Recent visitor table

### Reporting
- Periods: Today, This Week, This Month, Custom Range
- Filters: Status, Department
- Export: Excel (.xlsx), CSV, PDF (landscape A4)
- Color-coded status rows in PDF

### Audit Trail
- All logins, logouts, registrations, approvals, check-outs, report downloads
- User, action, details, timestamp, IP address

---

## 🎨 Status Color Coding

| Status       | Color  |
|-------------|--------|
| Approved    | 🟢 Green  |
| Pending     | 🟡 Yellow |
| Rejected    | 🔴 Red    |
| Checked Out | 🔵 Blue   |

---

## 🛠️ Tech Stack

| Layer     | Technology                         |
|-----------|------------------------------------|
| Frontend  | Streamlit + custom CSS             |
| Backend   | Python 3.11+                       |
| Database  | SQLite (WAL mode)                  |
| Auth      | bcrypt password hashing            |
| QR Codes  | qrcode + pyzbar + opencv           |
| Charts    | Plotly                             |
| Reports   | ReportLab (PDF) + openpyxl (Excel) |
| Timezone  | pytz (Africa/Lagos)                |
| Images    | Pillow                             |

---

## 📋 Database Schema

- **visitors** — all visitor records and status
- **approvals** — approval/rejection history
- **departments** — department list
- **hosts** — people who can be visited
- **admins** — admin accounts with hashed passwords
- **audit_logs** — full activity trail

---

## 🔒 Security Notes

- Passwords hashed with bcrypt (cost factor 12)
- Session-based authentication
- Role-based access control
- Input validation on all forms
- Duplicate exit prevention
- Audit trail for all sensitive actions
