# Onda Job – Flask + MySQL Application

A full-stack job portal built with **Flask Blueprints** and **MySQL** database (managed via **phpMyAdmin**).

## Project Structure

```
ondajob/
├── run.py                    # Entry point
├── config.py                 # Config with MySQL connection
├── seed.py                   # Seed database with sample data
├── ondajob.sql               # SQL schema (import in phpMyAdmin)
├── requirements.txt
├── .env                      # Database credentials
├── app/
│   ├── __init__.py           # App factory
│   ├── extensions.py         # SQLAlchemy, Migrate, LoginManager
│   ├── models.py             # All database models
│   ├── blueprints/
│   │   ├── main/             # Landing page (/)
│   │   ├── auth/             # Login & Signup (/auth/*)
│   │   ├── jobseeker/        # Job Seeker Dashboard (/jobseeker/*)
│   │   ├── employer/         # Employer Dashboard (/employer/*)
│   │   ├── admin/            # Admin Dashboard (/admin/*)
│   │   ├── jobs/             # Search & Apply (/jobs/*)
│   │   ├── messages/         # Messaging (/messages/*)
│   │   └── resume/           # Resume Builder (/resume/*)
│   ├── static/images/        # Place logo.png here
│   └── templates/
```

## Database Models

| Table          | Description                          |
|----------------|--------------------------------------|
| `users`        | All users (jobseeker/employer/admin) |
| `profiles`     | Job seeker profile details           |
| `experiences`  | Work experience entries              |
| `educations`   | Education entries                    |
| `companies`    | Employer company profiles            |
| `jobs`         | Job listings                         |
| `applications` | Job applications                     |
| `saved_jobs`   | Bookmarked jobs                      |
| `messages`     | User-to-user messages                |
| `notifications`| System notifications                 |
| `reports`      | Flagged content reports              |

## Setup & Run

### 1. Prerequisites
- **Python 3.8+**
- **XAMPP / WAMP / MAMP** (for MySQL + phpMyAdmin)

### 2. Create Database
**Option A — phpMyAdmin:**
1. Open phpMyAdmin (`http://localhost/phpmyadmin`)
2. Click "Import" → select `ondajob.sql` → click "Go"

**Option B — MySQL CLI:**
```bash
mysql -u root < ondajob.sql
```

### 3. Install & Run
```bash
# Create virtual environment
python -m venv venv
source venv/bin/activate  # Windows: venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt

# (Optional) Seed sample data
python seed.py

# Run the app
python run.py
```

### 4. Access
- **App:** http://localhost:5000
- **phpMyAdmin:** http://localhost/phpmyadmin

### 5. Default Accounts (after seeding)
| Role       | Email               | Password      |
|------------|---------------------|---------------|
| Admin      | admin@ondajob.com   | admin123      |
| Job Seeker | juan@email.com      | password123   |
| Employer   | hr@techcorp.ph      | password123   |

## API Routes

### Public
- `GET /` — Landing page
- `GET /auth/login` — Login
- `POST /auth/login` — Process login
- `GET /auth/signup` — Signup
- `POST /auth/signup` — Process registration
- `GET /auth/logout` — Logout
- `GET /jobs/search` — Search jobs (with filters)

### Job Seeker (requires login)
- `GET /jobseeker/dashboard` — Dashboard
- `POST /jobs/apply/<id>` — Apply to a job
- `POST /jobs/save/<id>` — Save/unsave a job
- `GET /resume/builder` — Resume builder
- `POST /resume/save` — Save resume
- `POST /resume/add-experience` — Add work experience
- `POST /resume/add-education` — Add education
- `GET /messages/` — Messages inbox
- `POST /messages/send` — Send a message

### Employer (requires login)
- `GET /employer/dashboard` — Dashboard
- `POST /employer/post-job` — Post a new job

### Admin (requires admin role)
- `GET /admin/dashboard` — Admin dashboard
- `POST /admin/toggle-user/<id>` — Activate/suspend user

## Database Configuration

Edit `.env` or `config.py`:
```
DATABASE_URL=mysql+pymysql://username:password@localhost/ondajob
```

Examples:
```
# XAMPP (default, no password)
mysql+pymysql://root:@localhost/ondajob

# With password
mysql+pymysql://root:mypassword@localhost/ondajob

# Custom port
mysql+pymysql://root:@localhost:3307/ondajob
```
