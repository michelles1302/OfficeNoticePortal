# Cloud-Based Office Notice Portal

A secure web application developed using Flask for managing office notices within an organization. Administrators can create and manage notices, while employees can securely log in, view notices, search notices, and track read status.

---

## Features

### Administrator
- Secure Login
- Dashboard
- Create, Edit and Delete Notices
- Publish Notices
- Manage Users

### Employee
- Secure Login
- View Notice Feed
- Search & Filter Notices
- View Notice Details
- Mark Notices as Read
- Update Profile

---

## Technology Stack

**Frontend**
- HTML5
- CSS3
- Bootstrap 5
- JavaScript

**Backend**
- Python
- Flask
- Flask SQLAlchemy
- Flask Login
- Flask Bcrypt

**Database**
- SQLite (Development)
- PostgreSQL (Production)

---

## Project Structure

```text
office_notice_portal/
│
├── app/
│   ├── blueprints/
│   ├── models/
│   ├── services/
│   ├── static/
│   └── templates/
│
├── instance/
├── uploads/
├── config.py
├── run.py
├── requirements.txt
└── README.md
```

---

## Installation

1. Create a virtual environment

```bash
python -m venv venv
```

2. Activate it

```bash
venv\Scripts\activate
```

3. Install dependencies

```bash
pip install -r requirements.txt
```

4. Seed the database

```bash
python seed.py
```

5. Run the application

```bash
python run.py
```

Open:

```
http://127.0.0.1:5000
```

---

## Default Login

**Admin**

Email:
```
admin@noticeportal.com
```

Password:
```
AdminPassword123
```

---

## Future Enhancements

- AWS EC2 Deployment
- AWS RDS Integration
- AWS S3 File Storage
- Email Notifications
- Reports and Analytics

---

## Author

**Michelle**

