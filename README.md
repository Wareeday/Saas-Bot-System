# SaaS Bot System

[![License](https://img.shields.io/badge/License-MIT-blue.svg)](LICENSE)
[![Python](https://img.shields.io/badge/Python-3.9+-blue.svg)](https://www.python.org/)
[![FastAPI](https://img.shields.io/badge/FastAPI-0.100+-green.svg)](https://fastapi.tiangolo.com/)
[![React](https://img.shields.io/badge/React-18+-blue.svg)](https://reactjs.org/)

A production-ready, fully asynchronous web automation SaaS platform designed for scalable task execution, user management, and real-time monitoring. Built with modern technologies to handle complex web automation workflows efficiently and securely.

## 🚀 Features

- **Asynchronous Task Execution**: Leverages Celery and Redis for distributed, non-blocking task processing
- **Web Automation**: Powered by Playwright for reliable browser automation across multiple tasks
- **RESTful API**: FastAPI-based backend with automatic OpenAPI documentation
- **Real-time Dashboard**: React-based frontend for task monitoring and management
- **User Authentication**: JWT-based auth with role-based access control
- **Scheduled Tasks**: Cron-based scheduling for recurring automation jobs
- **Comprehensive Monitoring**: Flower dashboard for Celery task insights
- **Database Integration**: PostgreSQL with async SQLAlchemy for data persistence
- **Containerized Deployment**: Docker Compose setup for easy development and production deployment

## 🏗️ Architecture

```
┌─────────────┐     HTTP     ┌────────────────┐    Celery tasks    ┌─────────────────┐
│  React UI   │ ──────────▶  │  FastAPI (8000) │ ────────────────▶  │  Celery Worker  │
│  (port 3000)│              │  + APScheduler  │                    │  (Playwright)   │
└─────────────┘              └────────────────┘                    └─────────────────┘
                                      │                                      │
                               ┌──────┴──────┐                    ┌─────────┴────────┐
                               │  PostgreSQL  │                    │      Redis        │
                               │  (port 5432) │                    │  (broker+results) │
                               └─────────────┘                    └───────────────────┘
```

## 📋 Table of Contents

- [Prerequisites](#prerequisites)
- [Quick Start](#quick-start)
- [Services](#services)
- [API Reference](#api-reference)
- [Task Types & Payloads](#task-types--payloads)
- [Scheduling Tasks](#scheduling-tasks-cron)
- [Local Development](#local-development-without-docker)
- [Environment Variables](#environment-variables)
- [Deployment](#deployment)
- [Contributing](#contributing)
- [License](#license)

## 📋 Prerequisites

- Docker and Docker Compose
- Git
- (For local development) Python 3.9+, Node.js 16+, npm

---

## 🛠️ Services

| Service  | Port | Technology Stack | Description |
|----------|------|------------------|-------------|
| backend  | 8000 | FastAPI, Uvicorn | REST API server with built-in scheduler |
| worker   | —    | Celery, Playwright | Asynchronous task executor for web automation |
| flower   | 5555 | Flower | Celery monitoring and administration dashboard |
| frontend | 3000 | React, Vite | User dashboard for task management |
| db       | 5432 | PostgreSQL | Primary database for application data |
| redis    | 6379 | Redis | Message broker and result backend for Celery |

---

## 🚀 Quick Start

### 1. Clone the Repository

```bash
git clone https://github.com/Wareeday/Saas-Bot-System.git 
cd saas-bot-system
```

### 2. Environment Configuration

```bash
cp .env.example .env  # Copy the example environment file
# Edit .env with your configuration (database credentials, secrets, etc.)
```

### 3. Launch the Application

```bash
docker compose up --build
```

### 4. Access the Application

- **Dashboard**: http://localhost:3000
- **API Documentation**: http://localhost:8000/docs
- **Celery Monitoring**: http://localhost:5555

---

## 📚 API Reference

### Authentication Endpoints

| Method | Endpoint | Description | Request Body |
|--------|----------|-------------|--------------|
| POST | `/api/auth/register` | Register a new user | `{username, email, password}` |
| POST | `/api/auth/token` | Obtain JWT access token | `{username, password}` |
| GET | `/api/auth/me` | Get current user information | — |

### Account Management

| Method | Endpoint | Description | Request Body |
|--------|----------|-------------|--------------|
| GET | `/api/accounts` | List user accounts | Query parameters for filtering |
| POST | `/api/accounts` | Create a new account | Account creation payload |
| GET | `/api/accounts/{id}` | Retrieve account details | — |
| PATCH | `/api/accounts/{id}` | Update account information | Partial account update |
| DELETE | `/api/accounts/{id}` | Delete an account | — |

### Task Management

| Method | Endpoint | Description | Request Body |
|--------|----------|-------------|--------------|
| GET | `/api/tasks` | List tasks with pagination | Query parameters |
| POST | `/api/tasks` | Create and optionally execute a task | Task creation payload |
| GET | `/api/tasks/stats` | Get task status statistics | — |
| GET | `/api/tasks/{id}` | Get detailed task information | — |
| PATCH | `/api/tasks/{id}` | Update task configuration | Partial task update |
| POST | `/api/tasks/{id}/run` | Manually trigger task execution | — |
| POST | `/api/tasks/{id}/cancel` | Cancel a running task | — |
| DELETE | `/api/tasks/{id}` | Delete a task | — |

---

## 🤖 Task Types & Payloads

### Navigation Task
**Type**: `navigate`

```json
{
  "url": "https://example.com"
}
```

### Login Automation
**Type**: `login`

```json
{
  "url": "https://example.com/login",
  "username_selector": "#username",
  "password_selector": "#password",
  "submit_selector": "button[type=submit]",
  "username": "myuser",
  "password": "mypassword",
  "success_selector": ".dashboard"
}
```

### Data Scraping
**Type**: `scrape`

```json
{
  "url": "https://example.com",
  "selectors": {
    "title": "h1",
    "price": ".price-tag",
    "description": "#desc"
  }
}
```

### Form Filling
**Type**: `form_fill`

```json
{
  "url": "https://example.com/form",
  "fields": [
    { "selector": "#name", "value": "John", "type": "text" },
    { "selector": "#country", "value": "US", "type": "select" },
    { "selector": "#agree", "value": true, "type": "checkbox" }
  ],
  "submit_selector": "button[type=submit]"
}
```

### Element Clicking
**Type**: `click`

```json
{
  "url": "https://example.com",
  "selector": ".btn-primary",
  "wait_after_ms": 2000
}
```

### Screenshot Capture
**Type**: `screenshot`

```json
{
  "url": "https://example.com",
  "path": "/tmp/screenshot.png"
}
```

---

## ⏰ Scheduling Tasks (Cron)

Tasks can be scheduled for recurring execution using cron expressions. Set the `schedule_cron` field when creating a task:

```json
{
  "name": "Daily data scrape",
  "task_type": "scrape",
  "payload": {
    "url": "https://example.com",
    "selectors": { "price": ".price" }
  },
  "schedule_cron": "0 9 * * *",
  "run_now": false
}
```

Common cron patterns:
- `0 9 * * *`: Daily at 9:00 AM
- `*/30 * * * *`: Every 30 minutes
- `0 0 * * 1`: Weekly on Mondays at midnight

---

## 💻 Local Development (without Docker)

### Backend Setup

```bash
cd backend
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
pip install -r requirements.txt
playwright install chromium
uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
```

### Worker Setup (Separate Terminal)

```bash
cd backend
source venv/bin/activate  # On Windows: venv\Scripts\activate
celery -A app.workers.worker.celery_app worker --loglevel=info -Q bot_tasks
```

### Frontend Setup (Separate Terminal)

```bash
cd frontend
npm install
npm run dev
```

---

## ⚙️ Environment Variables

| Variable | Default | Description |
|----------|---------|-------------|
| `SECRET_KEY` | *(required in production)* | JWT token signing secret |
| `DATABASE_URL` | `postgresql+asyncpg://postgres:postgres@db:5432/saas_bot` | PostgreSQL connection string |
| `REDIS_URL` | `redis://redis:6379/0` | Redis connection URL |
| `BOT_HEADLESS` | `true` | Run browser in headless mode |
| `BOT_TIMEOUT_MS` | `30000` | Browser action timeout in milliseconds |
| `BOT_MAX_RETRIES` | `3` | Maximum retry attempts for failed tasks |
| `LOG_LEVEL` | `INFO` | Application logging level |
| `LOG_JSON` | `true` | Enable JSON-structured logging |

## 🚢 Deployment

### Production Considerations

1. **Security**: Use strong secrets for `SECRET_KEY` and database credentials
2. **Scaling**: Adjust Celery worker count based on load
3. **Monitoring**: Set up proper logging and monitoring for production
4. **Database**: Use connection pooling and backup strategies
5. **Reverse Proxy**: Configure nginx or similar for SSL termination

### Docker Production Deployment

```bash
# Build for production
docker compose -f docker-compose.prod.yml up --build -d
```

## 🤝 Contributing

1. Fork the repository
2. Create a feature branch: `git checkout -b feature/amazing-feature`
3. Commit your changes: `git commit -m 'Add amazing feature'`
4. Push to the branch: `git push origin feature/amazing-feature`
5. Open a Pull Request

### Development Guidelines

- Follow PEP 8 for Python code
- Use ESLint for JavaScript/React code
- Write tests for new features
- Update documentation for API changes

## 📄 License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## 📞 Support

For questions or issues, please open an issue on GitHub or contact the development team.

---

*Built with ❤️ using FastAPI, React, and modern web technologies.*
