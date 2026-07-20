# 🩸 Blood Connect

![Python](https://img.shields.io/badge/Python-3.11+-3776AB?logo=python&logoColor=white)
![Flask](https://img.shields.io/badge/Flask-3.x-000000?logo=flask)
![SQLAlchemy](https://img.shields.io/badge/SQLAlchemy-2.x-D71F00?logo=sqlalchemy&logoColor=white)
![Bootstrap](https://img.shields.io/badge/Bootstrap-5-7952B3?logo=bootstrap&logoColor=white)
![Jinja](https://img.shields.io/badge/Jinja2-Templates-B41717?logo=jinja&logoColor=white)
![SQLite](https://img.shields.io/badge/SQLite-Local-003B57?logo=sqlite&logoColor=white)
![PostgreSQL](https://img.shields.io/badge/PostgreSQL-Production-4169E1?logo=postgresql&logoColor=white)
![Pytest](https://img.shields.io/badge/Pytest-Tested-0A9EDC?logo=pytest&logoColor=white)
![Render](https://img.shields.io/badge/Render-Deployed-46E3B7?logo=render&logoColor=black)
![Neon](https://img.shields.io/badge/Neon-PostgreSQL-00E699)
![Brevo](https://img.shields.io/badge/Brevo-SMTP-009FE3)

A security-focused full-stack web application built with Flask for managing blood donations and blood requests.

A security-focused full-stack web application built with Flask for managing blood donations and blood requests.

The platform allows users to submit donation and request operations while administrators validate and manage the complete workflow through a dedicated admin dashboard.

# ✨ Features

### 👤 User Features

* Secure authentication system
* Email verification
* Password reset via timed tokens
* Blood donation and request management
* Eligibility tracking system
* Optional email notifications
* Personal statistics dashboard
* Profile management

#### User Interface

> 📷 _Authentication page_ 
![Authentication page](/app/static/screenshots/authentication_page.png)

> 📷 _User dashboard_
![User dashboard](/app/static/screenshots/user_dashboard.png)

> 📷 _User donation/request page_
![User donation page](/app/static/screenshots/user_donation_page.png)
![User request page](/app/static/screenshots/user_request_page.png)

> 📷 _User Settings_
![User settings](/app/static/screenshots/user_settings.png)

### 👑 Admin Features

* Administrative analytics dashboard
* Donation/request approval workflow
* User ban/reactivation system
* CSV export tools
* Database cleanup utilities

#### Admin Interface

> 📷 _Admin dashboard_
![Admin dashboard](/app/static/screenshots/admin_dashboard.png)

> 📷 _Operations management_
![Donation management](/app/static/screenshots/donation_management.png)
![Request management](/app/static/screenshots/request_management.png)
![User management](/app/static/screenshots/user_management.png)

> 📷 _Admin settings_
![Admin settings](/app/static/screenshots/admin_settings.png)

# 🔄 Core Workflow

* Users create blood donations or blood requests
* All operations start in a `Pending` state
* Administrators validate and complete operations
* Approved donations become searchable
* Automated notifications update users during the workflow


# 🧱 Architecture

The application follows a service-layer architecture:

```text
Routes → Services → Models → Database
```

Core backend logic is isolated inside dedicated service classes for maintainability and scalability.

# 🔐 Security

The project was developed with a security-oriented mindset and includes protections against common web attacks.

Implemented protections include:

* Password hashing with bcrypt
* CSRF protection
* Rate limiting
* RBAC authorization
* Timed email tokens
* Secure session handling
* SQL injection prevention
* Input validation
* Business logic abuse prevention

See:

* SECURITY.md
* ROADMAP.md


# 🧪 Running Tests

```bash
pytest
```

# 🚀 Quick Local Setup

## Requirements

* Python 3.11+
* Mailpit
* pip


## Installation

```bash
git clone <repository-url>
cd Blood-Connect

python -m venv .venv

# Windows
.\.venv\Scripts\Activate.ps1

# Linux/macOS
source .venv/bin/activate

pip install -r requirements.txt
```

## Environment Variables

Create a `.env` file:

```env
SECRET_KEY=your_secret_key
PYTHONPATH=.
```

## Initialize Database

```bash
python create_admin.py
python seed_data.py
```

## Start Mailpit (Local Email Testing)

The application uses Mailpit during local development to capture and inspect outgoing emails without sending them to real recipients.

1. Download the appropriate Mailpit release for your operating system from the official website:
   https://mailpit.axllent.org/

2. Extract the downloaded archive.

3. Open a terminal inside the extracted folder and start Mailpit:

```bash
./mailpit
```

Windows:

```bash
.\mailpit.exe
```

Once started, Mailpit exposes:

**SMTP Server**

```text
localhost:1025
```

Used by the Flask application to send emails locally.

**Web Interface**

```text
http://localhost:8025
```

Used to view captured emails such as:

* Account verification emails
* Password reset emails
* Donation and request notifications
* Thank-you emails

Keep Mailpit running while testing email-related features locally.

## Run Application

```bash
flask --app run.py run
```

# 📂 Project Structure

```tree
Blood-Connect/
│
├── app/
│   ├── admin/
│   │   └── routes.py
│   │
│   ├── auth/
│   │   └── routes.py
│   │
│   ├── blood_operations/
│   │   └── routes.py
│   │
│   ├── config/
│   │   └── rules.py
│   │
│   ├── main/
│   │   └── routes.py
│   │
│   ├── services/
│   │   ├── admin_service.py
│   │   ├── auth_service.py
│   │   ├── blood_service.py
│   │   ├── email_service.py
│   │   └── main_service.py
│   │
│   ├── static/
│   │
│   ├── templates/
│   ├── __init__.py
│   ├── extensions.py
│   ├── forms.py
│   ├── models.py
│   ├── security.py
│   └── time_limit.py
│
├── instance/
│   └── BloodConnect.db
│   
├── tests/
│   ├── conftest.py
│   ├── test_admin_service.py
│   ├── test_auth_service.py
│   ├── test_blood_service.py
│   └── test_main_service.py
│   
├── .env
├── config.py
├── create_admin.py
├── create_db.py
├── README.md
├── requirements.txt
├── run.py
└── seed_data.py
```

# 🧠 Tech Stack

### Backend

* Flask
* SQLAlchemy
* Flask-Login
* Flask-WTF
* Flask-Mail
* Flask-Limiter

### Frontend

* HTML5
* Bootstrap 5
* Jinja2

### Database

* SQLite (Local Development)
* PostgreSQL (Production)

### Infrastructure & Deployment

* Render - Cloud hosting platform for the web application
* Neon - Serverless PostgreSQL database for production data
* Brevo - Transactional email service (SMTP) for automated notifications


# 👨‍💻 Author 

Portfolio project focused on:

* Secure Flask backend development
* Authentication systems
* RBAC authorization
* Web application architecture
* Security-oriented backend engineering

## ⚖️ License

This project is licensed under the MIT License.
