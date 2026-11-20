# MedhaAI Backend

Backend services and REST APIs for **MedhaAI**, built using FastAPI and PostgreSQL. The backend handles authentication, user management, billing, AI-powered functionality, institute management, and usage tracking.

## 🚀 Technologies Used

- **Python** – Backend programming language
- **FastAPI** – REST API framework
- **PostgreSQL** – Relational database
- **SQLAlchemy** – Database ORM
- **Docker** – Database containerization
- **Firebase Authentication** – User authentication and token verification
- **Gemini API** – AI-powered functionality
- **Uvicorn** – ASGI server
- **Pydantic** – Request validation and data schemas

## 📁 Project Structure

```text
MedhaAI-Backend/
│
├── app/
│   ├── config/
│   │   └── ai.py
│   ├── database/
│   │   └── connection.py
│   ├── models/
│   │   └── user.py
│   ├── routers/
│   │   ├── auth.py
│   │   ├── billing.py
│   │   ├── admin.py
│   │   ├── institute.py
│   │   ├── ai.py
│   │   └── usage.py
│   ├── schemas/
│   │   ├── auth.py
│   │   ├── billing.py
│   │   ├── admin.py
│   │   ├── institute.py
│   │   └── ai.py
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

### 1. Clone the Repository

```bash
git clone <YOUR_GITHUB_REPOSITORY_URL>
cd MedhaAI-Backend
```

### 2. Create a Virtual Environment

```bash
python -m venv venv
```

Activate it on Windows:

```powershell
venv\Scripts\Activate.ps1
```

### 3. Install Dependencies

```bash
pip install -r requirements.txt
```

### 4. Configure Environment Variables

Create a `.env` file in the project root.

Configure the following environment variables:

```env
# PostgreSQL Database
DATABASE_URL=your_postgresql_connection_string

# Firebase Configuration
FIREBASE_WEB_API_KEY=your_firebase_web_api_key

# Google Gemini AI
GEMINI_API_KEY=your_gemini_api_key
```

Replace the placeholder values with your actual configuration.

### 5. Start PostgreSQL

Ensure PostgreSQL is running and the configured database is accessible.

If using Docker, you can start PostgreSQL with:

```bash
docker run --name postgres-db ^
  -e POSTGRES_USER=postgres ^
  -e POSTGRES_PASSWORD=your_password ^
  -e POSTGRES_DB=college_db ^
  -p 5432:5432 ^
  -d postgres:17
```

Update the database connection configuration to match your environment.

### 6. Run the FastAPI Server

```bash
uvicorn main:app --reload
```

The backend will be available at:

```text
http://127.0.0.1:8000
```

## 📚 API Documentation

FastAPI automatically generates interactive API documentation.

| Documentation | URL |
|---|---|
| Swagger UI | http://127.0.0.1:8000/docs |
| ReDoc | http://127.0.0.1:8000/redoc |
| Root endpoint | http://127.0.0.1:8000/ |

Use Swagger UI to explore and test available API endpoints.

## 🔌 API Modules

| Module | Responsibility |
|---|---|
| Authentication | User registration, login and authentication |
| Billing | Subscription and billing-related operations |
| Admin | Administrative operations |
| Institute | Institute-related management |
| AI | AI-powered search and processing |
| Usage | Usage tracking and related operations |

## 🏗️ Application Architecture

The backend follows a modular architecture:

- **Routers:** Define API endpoints and handle incoming HTTP requests.
- **Schemas:** Validate incoming requests and structure API responses using Pydantic.
- **Services:** Contain business logic and application operations.
- **Models:** Represent database entities.
- **Database:** Manage database connectivity and operations.
- **Config:** Manage application configuration and external API settings.

## 🔐 Security

- Environment variables are used for sensitive configuration.
- Firebase authentication is used for identity verification.
- Request validation is handled through Pydantic.
- Authentication and authorization are handled through the relevant backend modules.

## 🧪 Testing

API endpoints can be tested using:

- Swagger UI
- Postman

Start the backend and use the interactive API documentation to send requests and inspect responses.

## 👨‍💻 Development

The project uses a modular architecture to make it easier to maintain, test, and extend individual backend modules.

Contributions and improvements should follow the existing router, schema, and service organization.

---

**MedhaAI Backend**

Built with Python, FastAPI and PostgreSQL.
