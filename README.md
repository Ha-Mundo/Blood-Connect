# 🩸 Blood Donation Portal

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

### 👑 Admin Features

* Donation/request approval workflow
* User ban/reactivation system
* CSV export tools
* Database cleanup utilities
* Administrative analytics dashboard


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
cd Blood-Donation-Portal

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
python create_db.py
python create_admin.py
python seed_data.py
```

## Start Mailpit

```bash
mailpit
```

SMTP:

```text
localhost:1025
```

Web UI:

```text
http://localhost:8025
```

## Run Application

```bash
flask --app run.py run
```

# 📂 Project Structure

```tree
Blood-Donation-Portal/
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
│   └── BloodDonationSystem.db
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

* SQLite

# ⚖️ License

This project is licensed under the MIT License.


# 👨‍💻 Author

Portfolio project focused on:

* Secure Flask backend development
* Authentication systems
* RBAC authorization
* Web application architecture
* Security-oriented backend engineering
