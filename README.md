# MedhaAI Backend

MedhaAI Backend is a Python-based backend application built using **FastAPI and PostgreSQL**. It provides REST APIs for authentication, user management, billing, institute management, AI-powered functionality, and usage tracking.

The backend integrates Firebase Authentication for user identity verification and Google Gemini for AI-powered processing.

## 🚀 Technologies Used

| Technology | Purpose |
|---|---|
| Python | Backend programming language |
| FastAPI | REST API framework |
| PostgreSQL | Relational database |
| SQLAlchemy | Database ORM |
| Docker | Database containerization |
| Firebase Authentication | User authentication and token verification |
| Firebase Web API | Firebase authentication configuration |
| Google Gemini API | AI-powered functionality |
| Uvicorn | ASGI server |
| Pydantic | Data validation and request schemas |
| Psycopg | PostgreSQL database connectivity |

## 📁 Project Structure

```text
MedhaAI-Backend/
│
├── app/
│   │
│   ├── config/
│   │   └── ai.py
│   │
│   ├── database/
│   │   └── connection.py
│   │
│   ├── models/
│   │   └── user.py
│   │
│   ├── routers/
│   │   ├── auth.py
│   │   ├── billing.py
│   │   ├── admin.py
│   │   ├── institute.py
│   │   ├── ai.py
│   │   └── usage.py
│   │
│   ├── schemas/
│   │   ├── auth.py
│   │   ├── billing.py
│   │   ├── admin.py
│   │   ├── institute.py
│   │   └── ai.py
│   │
│   └── services/
│       ├── auth_service.py
│       ├── billing_service.py
│       ├── admin_service.py
│       ├── institute_service.py
│       ├── ai_service.py
│       ├── usage_service.py
│       └── firebase_service.py
│
├── main.py
├── requirements.txt
├── .env
├── .gitignore
└── README.md
```

## ⚙️ Getting Started

Follow these steps to set up the project locally.

### 1. Clone the Repository

```bash
git clone <YOUR_GITHUB_REPOSITORY_URL>
```

Navigate to the project directory:

```bash
cd MedhaAI-Backend
```

### 2. Create a Virtual Environment

Create a Python virtual environment:

```bash
python -m venv venv
```

Activate the virtual environment on Windows:

```powershell
venv\Scripts\Activate.ps1
```

### 3. Install Dependencies

Install the required Python packages:

```bash
pip install -r requirements.txt
```

## 🗄️ PostgreSQL Database Setup

MedhaAI uses PostgreSQL as its relational database.

You can run PostgreSQL locally or through Docker.

### Option 1: Using Docker (Recommended)

Make sure Docker Desktop is installed and running.

Create a PostgreSQL container:

```bash
docker run --name postgres-db -e POSTGRES_USER=postgres -e POSTGRES_PASSWORD=your_password -e POSTGRES_DB=medha_ai -p 5432:5432 -v postgres_data:/var/lib/postgresql/data -d postgres:17
```

This command:

- Creates a PostgreSQL 17 container.
- Creates a database named `medha_ai`.
- Configures the PostgreSQL username and password.
- Maps port `5432` to your local machine.
- Creates a persistent Docker volume named `postgres_data`.

Check whether the container is running:

```bash
docker ps
```

To stop the container:

```bash
docker stop postgres-db
```

To start it again:

```bash
docker start postgres-db
```

### Option 2: Using PostgreSQL Locally

If PostgreSQL is already installed, create a database using:

```sql
CREATE DATABASE medha_ai;
```

You can manage and inspect the database using DBeaver or the PostgreSQL command-line tool.

### Database Initialization

Creating the database does not automatically create all application tables, relationships, or SQL functions.

The required database schema and initialization SQL scripts must be executed separately.

If the project uses predefined tables, stored procedures, or PostgreSQL functions, make sure the corresponding SQL definitions are available to the developer setting up the project.

The application will only work fully when the required database objects have been initialized.

## 🔑 Environment Configuration

Create a `.env` file in the root directory of the project.

Add the required configuration variables:

```env
# PostgreSQL Database
DATABASE_URL=postgresql://postgres:your_password@localhost:5432/medha_ai

# Firebase Configuration
FIREBASE_WEB_API_KEY=your_firebase_web_api_key

# Google Gemini AI
GEMINI_API_KEY=your_gemini_api_key
```

Replace the placeholder values with your actual configuration.

**Firebase Configuration:**

- `FIREBASE_WEB_API_KEY` is used for Firebase-related authentication configuration.
- Firebase service account credentials may also be required for Firebase Admin SDK operations. Configure these according to the existing Firebase service implementation.

**Gemini Configuration:**

- `GEMINI_API_KEY` is used to authenticate requests to the Google Gemini API.

**Database Configuration:**

- `DATABASE_URL` specifies the PostgreSQL connection string used by the backend.

Make sure the variable names match those referenced in the application code.

### Important Security Notes

- Never commit `.env` files to GitHub.
- Never upload Firebase service account JSON files.
- Never expose database passwords or private API credentials.
- Use environment variables for sensitive configuration.
- Rotate any credentials that may have been accidentally exposed.

## ▶️ Running the Application

After configuring the environment variables and initializing the database, start the FastAPI development server:

```bash
uvicorn main:app --reload
```

The backend will run at:

```text
http://127.0.0.1:8000
```

To access the automatically generated API documentation:

**Swagger UI:**

http://127.0.0.1:8000/docs

**ReDoc:**

http://127.0.0.1:8000/redoc

## 🔌 API Modules

The backend is organized into the following functional modules:

| Module | Description |
|---|---|
| Authentication | User registration, login and authentication |
| Billing | Subscription and billing-related operations |
| Admin | Administrative operations |
| Institute | Institute-related management |
| AI | AI-powered search and processing |
| Usage | Usage tracking and related operations |

### API Testing

The API endpoints can be explored and tested using:

- Swagger UI
- Postman

Swagger UI provides an interactive interface to send requests, provide request parameters, and inspect API responses.

## 🏗️ Application Architecture

The application follows a modular architecture that separates API handling, business logic, data validation, and database operations.

| Layer | Responsibility |
|---|---|
| Routers | Define API endpoints and handle HTTP requests |
| Schemas | Validate request data and structure responses |
| Services | Implement application and business logic |
| Models | Represent database entities |
| Database | Manage PostgreSQL connectivity |
| Config | Manage application and external API configuration |

This structure makes the backend easier to maintain, test, and extend.

## 🔐 Authentication and Security

The backend integrates Firebase Authentication for user identity verification.

Security-related functionality includes:

- Firebase ID token verification.
- Authentication and authorization.
- Request validation using Pydantic.
- Secure environment variable configuration.
- Protected API operations.

## 🧪 Development and Testing

For local development:

1. Clone the repository.
2. Create and activate a virtual environment.
3. Install the dependencies.
4. Configure the `.env` file.
5. Start PostgreSQL using Docker or a local installation.
6. Initialize the required database tables and SQL functions.
7. Start the FastAPI server.
8. Test the API endpoints using Swagger UI or Postman.

## 📌 Important Notes

- The PostgreSQL database is not included in the GitHub repository.
- Each developer must configure their own PostgreSQL database.
- Required SQL schema definitions and database functions must be initialized separately.
- Firebase and Gemini credentials must be configured locally.
- The `.env` file and other private credentials must never be committed to the repository.

---

**MedhaAI Backend**

Built using Python, FastAPI, PostgreSQL, Firebase and Google Gemini.
