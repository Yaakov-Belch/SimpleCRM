# SimpleCRM Technical Stack

## Technology Selection Philosophy

This is a **portfolio/learning project** prioritizing simplicity over enterprise-grade performance and reliability. All technology choices favor rapid development, clear code structure, and ease of demonstration over scalability or high availability.

## Core Stack

### Backend Framework & Runtime
- **Application Framework:** FastAPI (Python web framework)
  - Chosen for: Modern async support, automatic API documentation, type hints, excellent performance
  - Alternative considered: Django (too heavyweight), Flask (less modern)
- **Language/Runtime:** Python 3.11+
- **Package Manager:** pip with requirements.txt
- **ASGI Server:** Uvicorn for running FastAPI applications

### Frontend Stack
- **JavaScript Framework:** Vue.js 3 (Composition API)
  - Chosen for: Lightweight, excellent reactivity, gentle learning curve, powerful composables
  - Using Composition API for better TypeScript support and code organization
- **CSS Framework:** Tailwind CSS
  - Chosen for: Rapid UI development, utility-first approach, small bundle size
- **UI Components:** Custom components (no heavy component library)
  - Keep it simple and focused on learning
- **Build Tool:** Vite
  - Chosen for: Fast HMR, modern build system, excellent Vue.js integration

### Database & Persistence
- **Database:** SQLite (all persistence including application data and caching)
  - Chosen for: Zero configuration, single-file deployment, perfect for demo/portfolio
  - No need for separate database server, ideal for single-server deployment
- **ORM/Query Builder:** SQLAlchemy
  - Chosen for: Python standard, type-safe, works excellently with FastAPI
  - Provides abstraction if we ever need to migrate to PostgreSQL/MySQL later
- **Caching Strategy:** Simple SQLite table for LLM API response caching
  - No cache invalidation or expiry logic
  - Prevents repeated API costs during demos and testing
  - Cache key: hash of prompt/request, Cache value: API response JSON
  - No caching on anything else.

## Development Tools

### Testing & Quality Assurance
- **Backend Testing:** pytest
  - Unit tests for business logic
  - Integration tests for API endpoints
- **Frontend Testing:** Vitest
  - Component testing
  - Unit tests for composables and utilities
- **Code Formatting:**
  - Python: Black (auto-formatter)
  - JavaScript: Prettier
- **Code Linting:**
  - Python: Ruff (fast linter replacing Flake8, isort, etc.)
  - JavaScript: ESLint

### Development Environment
- **Version Control:** Git
- **API Documentation:** FastAPI auto-generated Swagger/OpenAPI docs
- **Environment Variables:** python-dotenv for local development
- **No Docker required:** Keep deployment simple with local Python/Node environments

## Third-Party Services & APIs

### AI/LLM Integration
- **Provider:** OpenAI API or Anthropic Claude API (configurable)
- **Use Cases:**
  - Parsing meeting notes and email content to extract key information
  - Generating proposal drafts based on contact history
  - Summarizing client interaction timelines
- **Cost Control:** SQLite-based caching with no expiry
  - Cache all LLM requests/responses
  - Avoid redundant API calls during development, demos, and repeated testing
  - Simple cache key generation (hash of prompt + parameters)

### Authentication
- **Method:** Simple session-based authentication (built-in, no third-party)
- **No OAuth providers in MVP:** Keep it simple with email/password
- **Session Storage:** Server-side sessions in SQLite or in-memory
- **Password Hashing:** bcrypt or argon2

### Email & External Integrations
- **MVP:** None - all data entry is manual
- **Future Phase 2/3:**
  - Gmail/Outlook API for email sync
  - Google Calendar/Outlook Calendar API
  - Stripe or PayPal for payment tracking
  - Zapier webhooks
- **Architecture Note:** Code structured to support future integrations without implementing them now

## Deployment & Infrastructure

### Hosting & Deployment
- **Environment:** Local deployment only (no cloud hosting in MVP)
- **CI/CD:** None (manual deployment)
- **Web Server:** Uvicorn directly (no Nginx/Apache in front)
- **Process Management:** Simple systemd service or manual launch for demo
- **No containers:** No Docker/Kubernetes complexity

### Monitoring & Logging
- **Application Logging:** Python built-in logging module (console output)
- **No APM/Monitoring:** Console logs only for debugging
- **No Error Tracking:** No Sentry or similar services

### Scalability Approach
- **Target:** Single server handles as many users as it can
- **No SLA requirements:** This is a demo/portfolio project
- **No load balancing, no clustering, no CDN**
- **Accept limitations:** If one server isn't enough, that's okay for this project phase

## Project Structure

### Backend Directory Layout
```
backend/
├── app/
│   ├── main.py              # FastAPI application entry point
│   ├── models/              # SQLAlchemy models
│   ├── routers/             # API route handlers
│   ├── services/            # Business logic layer
│   ├── schemas/             # Pydantic models for validation
│   ├── database.py          # Database connection & session
│   └── config.py            # Configuration management
├── tests/                   # pytest test files
├── requirements.txt         # Python dependencies
└── .env                     # Environment variables (not committed)
```

### Frontend Directory Layout
```
frontend/
├── src/
│   ├── main.js              # Vue app entry point
│   ├── App.vue              # Root component
│   ├── components/          # Reusable Vue components
│   ├── views/               # Page-level components
│   ├── composables/         # Composition API composables
│   ├── services/            # API client services
│   ├── router/              # Vue Router configuration
│   └── assets/              # Static assets, styles
├── tests/                   # Vitest test files
├── package.json             # Node dependencies
├── vite.config.js           # Vite configuration
└── tailwind.config.js       # Tailwind CSS configuration
```

## Design Principles

### Simplicity First
- No microservices architecture
- No complex infrastructure or cloud services
- No container orchestration
- Single server deployment
- Minimal external dependencies

### Future-Proof Structure
- Code organized to allow future integrations (Gmail, Calendar, etc.)
- Clean separation of concerns (routers, services, models)
- Integration points identified but not implemented
- Database schema designed with future sync fields (but unused in MVP)

### Cost-Effective Development
- All tools are free and open-source
- LLM caching prevents repeated API costs
- SQLite eliminates database hosting costs
- Local deployment eliminates cloud hosting costs during development

### Learning-Focused
- Modern best practices (FastAPI, Vue 3 Composition API)
- Type safety where practical (Pydantic, SQLAlchemy)
- Clear code organization following framework conventions
- Automated testing to demonstrate TDD practices
