# SimpleCRM

A clean, minimal CRM (Customer Relationship Management) application built with modern web technologies. This project demonstrates best practices for full-stack web development with secure authentication and user management.

## Features

- User Authentication & Account Management
  - Secure user registration with auto-login
  - Session-based authentication (7-day sessions)
  - User profile management
  - Password security with bcrypt (12+ rounds)
  - Email uniqueness enforcement (case-insensitive)
  - Multiple concurrent sessions support

- Security Features
  - Cryptographically secure session tokens
  - HTTP-only secure cookies for session management
  - Timing-safe password verification
  - No plain text passwords stored or logged
  - Generic error messages to prevent email enumeration

- Admin Tools
  - Command-line user deletion tool
  - Database management utilities

## Technology Stack

### Backend
- **Framework:** FastAPI (Python 3.11+)
- **Database:** SQLite with SQLAlchemy ORM
- **Authentication:** Session-based with bcrypt password hashing
- **Validation:** Pydantic schemas
- **Server:** Uvicorn ASGI server

### Frontend
- **Framework:** Vue.js 3 (Composition API)
- **Routing:** Vue Router 4
- **Styling:** Tailwind CSS 3
- **Build Tool:** Vite
- **HTTP Client:** Native Fetch API

### Development Tools
- **Testing:** Pytest (backend), Vitest (frontend)
- **Formatting:** Black (Python), Prettier (JavaScript)
- **Linting:** Ruff (Python), ESLint (JavaScript)

## Prerequisites

- Python 3.11 or higher
- Node.js 18 or higher
- npm or yarn package manager
- Git

## Installation & Setup

### 1. Clone the Repository

```bash
git clone https://github.com/yourusername/SimpleCRM.git
cd SimpleCRM
```

### 2. Backend Setup

```bash
# Navigate to backend directory
cd backend

# Create and activate virtual environment
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt

# Create .env file from example
cp .env.example .env

# (Optional) Edit .env file to customize settings
# nano .env
```

### 3. Frontend Setup

```bash
# Navigate to frontend directory (from project root)
cd frontend

# Install dependencies
npm install
```

### 4. Database Initialization

The database will be created automatically on first run. No manual setup required.

The SQLite database file will be created at: `backend/simplecrm.db`

## Running the Application

You'll need two terminal windows/tabs - one for backend and one for frontend.

### Terminal 1: Start Backend Server

```bash
cd backend
source venv/bin/activate  # On Windows: venv\Scripts\activate
uvicorn app.main:app --reload --port 8000
```

Backend will be available at: http://localhost:8000
- API endpoints: http://localhost:8000/api
- API documentation: http://localhost:8000/docs (Swagger UI)
- Alternative docs: http://localhost:8000/redoc (ReDoc)

### Terminal 2: Start Frontend Development Server

```bash
cd frontend
npm run dev
```

Frontend will be available at: http://localhost:5173 (or next available port)

## Running Tests

### Backend Tests

```bash
cd backend
source venv/bin/activate
pytest -v

# Run specific test file
pytest tests/test_auth_routes.py -v

# Run with coverage
pytest --cov=app --cov-report=html
```

### Frontend Tests

```bash
cd frontend
npm run test

# Run in watch mode
npm run test:watch

# Run with coverage
npm run test:coverage
```

## API Documentation

Once the backend server is running, comprehensive API documentation is available at:

- **Swagger UI:** http://localhost:8000/docs
- **ReDoc:** http://localhost:8000/redoc

### API Endpoints Overview

**Authentication (Public)**
- `POST /api/auth/register` - Register new user account
- `POST /api/auth/login` - Login with email and password
- `POST /api/auth/logout` - Logout (requires authentication)

**User Profile (Protected)**
- `GET /api/users/me` - Get current user profile
- `PUT /api/users/me` - Update current user profile

**Health Check**
- `GET /health` - Check server health

For detailed endpoint documentation with request/response examples, see the Swagger UI.

## Project Structure

```
SimpleCRM/
├── backend/                 # FastAPI backend
│   ├── app/
│   │   ├── models/         # SQLAlchemy database models
│   │   ├── routers/        # API route handlers
│   │   ├── schemas/        # Pydantic request/response schemas
│   │   ├── services/       # Business logic services
│   │   ├── config.py       # Application configuration
│   │   ├── database.py     # Database connection setup
│   │   ├── dependencies.py # FastAPI dependency injection
│   │   └── main.py         # Application entry point
│   ├── docs/               # Documentation
│   ├── scripts/            # Admin command-line tools
│   ├── tests/              # Pytest test suite
│   ├── requirements.txt    # Python dependencies
│   └── .env.example        # Environment variables template
├── frontend/               # Vue.js frontend
│   ├── src/
│   │   ├── components/     # Reusable Vue components
│   │   ├── views/          # Page components
│   │   ├── composables/    # Vue composables (shared logic)
│   │   ├── services/       # API service utilities
│   │   ├── router/         # Vue Router configuration
│   │   ├── assets/         # Static assets (CSS, images)
│   │   ├── App.vue         # Root component
│   │   └── main.js         # Application entry point
│   ├── tests/              # Vitest test suite
│   ├── package.json        # Node.js dependencies
│   └── vite.config.js      # Vite build configuration
└── README.md               # This file
```

## Admin Tools

### Delete User Script

Delete a user account and all associated data from the command line:

```bash
cd backend
source venv/bin/activate
python scripts/delete_user.py --email user@example.com
```

For more information, see `backend/scripts/README.md`

## Environment Variables

Create a `.env` file in the `backend` directory with the following variables:

```env
# Database
DATABASE_URL=sqlite:///./simplecrm.db

# Security
SECRET_KEY=your-secret-key-here-change-in-production

# Session Configuration
SESSION_DURATION_DAYS=7
```

See `backend/.env.example` for the template.

## Development Workflow

### Making Code Changes

1. Create a new branch for your feature/fix
2. Make changes in the appropriate directory (backend or frontend)
3. Write tests for new functionality
4. Run tests to ensure everything passes
5. Format and lint your code
6. Commit changes with clear messages
7. Push and create a pull request

### Code Formatting

**Backend (Python):**
```bash
cd backend
black app/ tests/
ruff check app/ tests/
```

**Frontend (JavaScript):**
```bash
cd frontend
npm run format
npm run lint
```

## Database

SimpleCRM uses SQLite for development with SQLAlchemy ORM.

### Database Schema

See `backend/docs/database-schema.md` for comprehensive database documentation including:
- Table structures
- Relationships
- Indexes
- Constraints
- Example queries
- Migration strategies

### Database Management

**Reset database (development only):**
```bash
cd backend
rm simplecrm.db
# Database will be recreated on next server start
```

**Backup database:**
```bash
cd backend
cp simplecrm.db simplecrm.db.backup
```

## Security Considerations

- Passwords are hashed with bcrypt using 12 salt rounds
- Session tokens use cryptographically secure random generation (32+ bytes)
- Email lookups are case-insensitive
- Authentication errors use generic messages to prevent email enumeration
- All user input is validated server-side with Pydantic schemas
- SQLAlchemy ORM prevents SQL injection vulnerabilities
- Frontend sanitizes all user input to prevent XSS attacks

## Troubleshooting

### Backend won't start

- Verify Python version: `python --version` (should be 3.11+)
- Ensure virtual environment is activated: `source venv/bin/activate`
- Check all dependencies are installed: `pip install -r requirements.txt`
- Verify port 8000 is not already in use: `lsof -i :8000`

### Frontend won't start

- Verify Node.js version: `node --version` (should be 18+)
- Delete node_modules and reinstall: `rm -rf node_modules && npm install`
- Clear Vite cache: `rm -rf node_modules/.vite`
- Verify port 5173 is not already in use: `lsof -i :5173`

### Tests failing

- Backend: Ensure virtual environment is activated and test database is clean
- Frontend: Clear test cache: `npm run test -- --clearCache`
- Check for port conflicts if running concurrent tests
- Verify all dependencies are up to date

### Database errors

- Ensure database file has write permissions
- Check disk space availability
- Verify database file is not corrupted (restore from backup)
- Check SQLite version compatibility

## Production Deployment

For production deployment, consider:

1. **Switch to PostgreSQL** - Better performance and concurrency than SQLite
2. **Use proper secrets** - Generate secure SECRET_KEY, don't use defaults
3. **Enable HTTPS** - Use SSL/TLS certificates for secure communication
4. **Configure CORS** - Restrict allowed origins to your domain
5. **Set up session cleanup** - Implement background task to delete expired sessions
6. **Enable logging** - Configure structured logging for monitoring
7. **Use production ASGI server** - Gunicorn with Uvicorn workers
8. **Implement rate limiting** - Prevent abuse and brute force attacks
9. **Add monitoring** - Application performance monitoring (APM)
10. **Set up backups** - Regular automated database backups

## Contributing

Contributions are welcome! Please follow these guidelines:

1. Fork the repository
2. Create a feature branch: `git checkout -b feature-name`
3. Write tests for new functionality
4. Ensure all tests pass
5. Format and lint your code
6. Commit with clear, descriptive messages
7. Push to your fork and submit a pull request

## License

This project is licensed under the MIT License - see the LICENSE file for details.

## Documentation

- [API Documentation](http://localhost:8000/docs) - Interactive API documentation (Swagger UI)
- [Database Schema](backend/docs/database-schema.md) - Complete database schema documentation
- [Admin Scripts](backend/scripts/README.md) - Command-line admin tools documentation

## Support

For issues, questions, or contributions, please open an issue on GitHub.

## Acknowledgments

Built with modern web technologies and best practices for secure authentication and user management.
