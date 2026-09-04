# Igris Tech Official Backend

Minimal, clean, maintainable REST API backend for **Igris Tech** built with **Python 3**, **FastAPI**, **SQLAlchemy**, and **PostgreSQL**.

---

## 📁 Project Structure

```text
igris-backend/
│
├── main.py              # Thin FastAPI application entrypoint & middleware
├── database.py          # SQLAlchemy database engine and session dependencies
├── models.py            # 4 Core ORM models: Project, EcosystemProduct, Review, ContactSubmission
├── schemas.py           # Pydantic v2 validation & public/admin response schemas
├── auth.py              # Protected admin password verification dependency
│
├── routes/
│   ├── projects.py      # /api/v1/projects (Case-studies content & publishing)
│   ├── ecosystem.py     # /api/v1/ecosystem (Ecosystem tools & products)
│   ├── reviews.py       # /api/v1/reviews (Public testimonials & admin moderation)
│   └── contact.py       # /api/v1/contact (Client inquiry intake & admin management)
│
├── requirements.txt     # Python dependencies
├── .env                 # Local environment variables
├── .env.example         # Environment variables template
└── README.md            # Backend blueprint documentation
```

---

## 🚀 Getting Started

### 1. Prerequisites
- Python 3.10+
- `pip` or `uv` / `virtualenv`

### 2. Setup Virtual Environment

```bash
# Create virtual environment
python3 -m venv venv

# Activate virtual environment
# On Linux/macOS:
source venv/bin/activate
# On Windows:
# venv\Scripts\activate
```

### 3. Install Dependencies

```bash
pip install -r requirements.txt
```

### 4. Configure Environment Variables

Copy `.env.example` to `.env` and set your admin password and database connection:

```bash
cp .env.example .env
```

Configuration parameters:
- `DATABASE_URL`: Database connection string (`sqlite:///./igris.db` for local dev or `postgresql://user:password@localhost:5432/igris_db` for production)
- `ADMIN_API_PASSWORD`: Secret password used to authorize admin mutations
- `CORS_ORIGINS`: Comma-separated list of allowed frontend origins (e.g. `http://localhost:3000,https://igristech.com`)

### 5. Run the Server

```bash
uvicorn main:app --reload --host 0.0.0.0 --port 8000
```

The API will be available at:
- **API Root**: `http://127.0.0.1:8000`
- **Interactive Swagger Docs**: `http://127.0.0.1:8000/docs`
- **Redoc Documentation**: `http://127.0.0.1:8000/redoc`

---

## 📡 API Endpoints Overview (/api/v1/)

### 📂 Projects (`/api/v1/projects`)
| Method | Endpoint | Description | Access |
|---|---|---|---|
| `GET` | `/api/v1/projects` | List all published case-study projects | Public |
| `GET` | `/api/v1/projects/{slug}` | Get single published project by slug | Public |
| `POST` | `/api/v1/projects` | Create a project (defaults to DRAFT) | Admin |
| `PATCH` | `/api/v1/projects/{id}` | Update project or change status to PUBLISHED | Admin |
| `DELETE` | `/api/v1/projects/{id}` | Delete a project | Admin |

### 🌐 Ecosystem (`/api/v1/ecosystem`)
| Method | Endpoint | Description | Access |
|---|---|---|---|
| `GET` | `/api/v1/ecosystem` | List all active ecosystem products & tools | Public |
| `GET` | `/api/v1/ecosystem/{slug}` | Get single active ecosystem product by slug | Public |
| `POST` | `/api/v1/ecosystem` | Add new ecosystem product | Admin |
| `PATCH` | `/api/v1/ecosystem/{id}` | Update ecosystem product | Admin |
| `DELETE` | `/api/v1/ecosystem/{id}` | Delete ecosystem product | Admin |

### ⭐ Reviews (`/api/v1/reviews`)
| Method | Endpoint | Description | Access |
|---|---|---|---|
| `GET` | `/api/v1/reviews` | List all approved client testimonials | Public |
| `POST` | `/api/v1/reviews` | Submit a review (created in PENDING status) | Public |
| `GET` | `/api/v1/reviews/admin` | List all reviews across all moderation statuses | Admin |
| `PATCH` | `/api/v1/reviews/{id}` | Moderate review (approve/reject/edit) | Admin |
| `DELETE` | `/api/v1/reviews/{id}` | Delete review | Admin |

### 📬 Contact (`/api/v1/contact`)
| Method | Endpoint | Description | Access |
|---|---|---|---|
| `POST` | `/api/v1/contact` | Submit contact / project inquiry form | Public |
| `GET` | `/api/v1/contact` | List all received inquiries | Admin |
| `GET` | `/api/v1/contact/{id}` | Get specific inquiry details | Admin |
| `PATCH` | `/api/v1/contact/{id}` | Update inquiry status (`NEW`, `CONTACTED`, `IN_PROGRESS`, etc.) | Admin |
| `DELETE` | `/api/v1/contact/{id}` | Delete inquiry | Admin |

---

## 🔒 Admin Authentication

Protected admin operations require the configured `ADMIN_API_PASSWORD`.

You can authenticate in either of two ways:

1. **Bearer Token Header**:
   ```http
   Authorization: Bearer <ADMIN_API_PASSWORD>
   ```

2. **Custom Header**:
   ```http
   X-Admin-Password: <ADMIN_API_PASSWORD>
   ```

In Swagger UI (`/docs`), click the **Authorize** button at the top right and enter your `ADMIN_API_PASSWORD` to execute protected endpoints directly.
# IGRIS-TECH-OFFICIAL-BACKEND-FOR-REAL
