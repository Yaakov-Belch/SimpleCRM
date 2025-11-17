# SimpleCRM - Learning Exercise

## Project Overview

I want to create a portfolio project with Claude Code and with agent-os -- an AI coding platform. In our current conversation, I want to develop an example project specification: What to build.

This specification should have a full product perspective -- from the user persona, user problems, user stories -- to technical architecture, roadmap, features to implementation.

I want to ground my project on a concrete job description, but apply specific changes to the technologies:
**I use Python on the backend and Vue.js on the frontend.**

---

## Original Job Description

### Summary
The client is building an innovative Customer Relationship Management (CRM) platform designed to help client-facing teams attract, convert, and retain clients efficiently. Their technology aims to automate key processes so teams can generate more revenue without increasing workload.

They are looking for a highly skilled developer to join their team and help with the development of this platform.

### General Information
The project involves developing a robust, scalable, and user-friendly CRM platform using modern Python frameworks and Vue.js front-end technologies. They need a senior developer capable of taking ownership of the platform architecture, providing technical guidance to the development team, and ensuring smooth integrations with vendors and in-house systems.

### Task and Deliverables

- Design, develop, and maintain high-quality Python applications.
- Collaborate with product, engineering teams, and vendors to evaluate software solutions and solve integration challenges.
- Create and maintain comprehensive documentation, including UML, architectural, and data flow diagrams.
- Analyze and optimize application performance and scalability, implementing improvements where needed.
- Work with DevOps engineers to ensure smooth production deployments and maintain post-production reliability.
- Evaluate and integrate vendor software, ensuring seamless interoperability with internal systems.

### Required Experience

- Python development experience (Django, FastAPI, Flask).
- Front-end experience with Vue.js.
- Experience working with database technologies such as PostgreSQL, MySQL, or SQLite.
- Production experience with Docker, containerization, and Linux server administration.
- Familiarity with open-source infrastructure and deployment tools.
- Experience writing documentation and creating UML, architectural, and data flow diagrams.
- Experience building integrations with vendors and internal APIs.
- Knowledge of performance optimization, scalability, and enterprise system architecture.

### Nice to Have

- Proficiency with Nuxt.js or other Vue.js meta-frameworks.
- Experience with open-source tools: Redis, Celery, RabbitMQ, Nginx, ElasticSearch.
- Experience with Linux system administration and shell scripting.
- Experience optimizing applications for performance at scale.
- Background in Banking, Financial Services, or FinTech.
- Proven experience with cross-functional team collaboration.
- Hands-on experience with production deployments and troubleshooting.

### Engagement Highlights

- Work closely with cross-functional teams including product, engineering, and vendors.
- Direct impact on product performance, scalability, and client success.
- Exposure to modern cloud infrastructure and enterprise-level systems.

---

## One-Sentence Product Focus

**We're building a simple CRM specifically for freelancers and solo consultants that automatically tracks client interactions across email and calendar to help them follow up consistently without manual data entry.**

---

## Detailed Product Definition

### User & Market Understanding

#### Target Users

- **Primary:** Freelancers, independent consultants, solo practitioners (lawyers, accountants, coaches, designers)
- **Secondary:** Small service businesses with 1-5 employees
- **Company size:** Solopreneurs to 5-person teams
- **Industries:** Professional services, creative agencies, consulting
- **Technical level:** Semi-technical (comfortable with web apps but not developers)

#### User Problems & Pain Points

- Losing track of potential clients who inquired via email or social media
- Forgetting to follow up with prospects after initial conversations
- Manually copying contact details from emails into spreadsheets
- No visibility into which marketing efforts actually generate revenue
- Spending 2-3 hours weekly on administrative CRM tasks instead of billable work

### Product Features & Functionality

#### Core CRM Features

- Contact management with automatic email/calendar sync
- Simple pipeline tracking (Lead → Qualified → Proposal → Client)
- Automated follow-up reminders based on last interaction
- Basic email templates for common scenarios
- Revenue tracking tied to contacts
- Simple dashboard showing pipeline value and overdue follow-ups

#### "Innovative" Differentiators

- Zero manual data entry - everything syncs automatically from Gmail/Outlook and Google Calendar
- AI-powered interaction parsing to identify potential clients in email threads
- One-click proposal generation from contact history
- ~~Mobile-first design for on-the-go consultants~~ (Removed - see Simplifications)

#### Integration Requirements

- ~~Gmail/Outlook email integration~~ (Future enhancement)
- ~~Google Calendar/Outlook Calendar sync~~ (Future enhancement)
- ~~Stripe/PayPal for payment tracking~~ (Future enhancement)
- ~~Basic Zapier integrations for forms and social media~~ (Future enhancement)
- ~~Simple export to accounting software (QuickBooks)~~ (Future enhancement)

### Technical Architecture

#### Scale & Performance

- ~~Target: 10,000 active users within 2 years~~ (Not applicable - see Simplifications)
- ~~Data volume: ~500 contacts per user, 50 deals per month per user~~ (Not applicable)
- ~~Single region deployment initially (US)~~ (Not applicable)
- ~~99.5% uptime requirement~~ (Not applicable - demo project)

#### Data & Security

- ~~Contact information, email metadata (not content), calendar events, revenue data~~ (Simplified - see below)
- ~~GDPR compliance for EU users~~ (Not in scope)
- ~~SOC 2 Type II certification goal~~ (Not in scope)
- ~~Data encryption at rest and in transit~~ (Not in scope)

### Business Model & Success Metrics

#### Revenue Model

- $29/month subscription per user
- 14-day free trial with Gmail sync
- Success measured by: reduced time spent on admin tasks, increased follow-up consistency, higher conversion rates from prospect to client

#### Go-to-Market

- Self-serve signup with automated onboarding
- Content marketing targeting freelancer communities
- 15-minute onboarding with Gmail/calendar connection

---

## Sales Pitch Summary

**Customer - Problem - Solution:**

Freelancers and solo consultants are losing potential clients and revenue because they can't keep track of all their prospect interactions across email, social media, and networking events - leading to missed follow-ups and forgotten opportunities. Our CRM automatically captures every client touchpoint from their existing Gmail and calendar, creates a simple pipeline view, and reminds them exactly when to follow up, so they can focus on delivering great work instead of managing spreadsheets while ensuring no potential client falls through the cracks.

---

## Simplifications for MVP

### Removed Requirements

1. **Mobile-first design for on-the-go consultants** - Not in scope for initial version
2. **Data & Security** - No added complexity allowed for that. This is just an exercise and we don't have time for these features.
3. **Scale and Performance** - No complexity. We serve as many users as one server can handle, no more. NO SLA requirement. This is a demo.
4. **Integrations with outside vendors** - We start with simple non-integrated solution that allows manual input for all required data. This solution should be structured so that future integration will be feasible. But that is not in scope for the first version of the project.

### In-Scope Features

**AI integration with LLMs:** This is in-scope. Make sure to cache all LLM API requests with a very simple cache (no cache expiry) -- so that repeating a demo or repeated testing of the platform does not incur repeated LLM costs (and delays).

### Feature Prioritization

Order features from MVP to advanced -- so that we can get to a viable product soon with options to grow.
