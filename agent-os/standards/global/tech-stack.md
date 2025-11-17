## Tech stack

This is our technical stack for the SimpleCRM project. We prioritize **simplicity over performance and reliability** - this is a portfolio/demo project.

### Framework & Runtime
- **Application Framework:** FastAPI (Python web framework)
- **Language/Runtime:** Python 3.11+
- **Package Manager:** pip with requirements.txt

### Frontend
- **JavaScript Framework:** Vue.js 3 (Composition API)
- **CSS Framework:** Tailwind CSS
- **UI Components:** Custom components (keep it simple)
- **Build Tool:** Vite

### Database & Storage
- **Database:** SQLite (all persistence)
- **ORM/Query Builder:** SQLAlchemy
- **Caching:** Simple SQLite cache for LLM API calls only (no cache invalidation/expiry)

### Testing & Quality
- **Test Framework:** pytest (Python), Vitest (Vue.js)
- **Linting/Formatting:**
  - Python: Black (formatter), Ruff (linter)
  - JavaScript: ESLint, Prettier

### Deployment & Infrastructure
- **Hosting:** None (local deployment only)
- **CI/CD:** None (manual deployment)
- **Server:** Uvicorn (ASGI server for FastAPI)

### Third-Party Services
- **Authentication:** Simple session-based auth (built-in, no third-party)
- **Email:** None in MVP (future enhancement)
- **Monitoring:** None (console logging only)
- **LLM Integration:** OpenAI API or Anthropic Claude API (with simple caching)

### Design Principles
- **Simplicity First:** No complex infrastructure, no microservices, no cloud services
- **Single Server:** Everything runs on one server/machine
- **No SLA Requirements:** This is a demo/portfolio project
- **Manual Input:** No external integrations in MVP (Gmail, Calendar, etc.) - all data entry is manual
- **Future-Proof Structure:** Code should be structured to allow future integrations, but they are not implemented
