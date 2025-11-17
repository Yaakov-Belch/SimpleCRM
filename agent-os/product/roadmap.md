# Product Roadmap

## MVP: Core CRM Functionality

1. [x] User Authentication & Account Management — Implement simple session-based authentication with registration, login, logout, and basic user profile management. `S`

2. [ ] Contact Management System — Build full CRUD operations for contacts including name, email, phone, company, notes, and custom fields with a searchable contact list view. `M`

3. [ ] Pipeline Stage Management — Create a 4-stage pipeline (Lead, Qualified, Proposal, Client) with the ability to assign contacts to stages and view stage-wise contact distribution. `S`

4. [ ] Activity Timeline & Notes — Implement activity logging system where users can record calls, meetings, emails, and general notes with timestamps, creating a chronological timeline per contact. `M`

5. [ ] Follow-Up Reminder System — Build automated reminder creation based on last interaction date with configurable reminder rules, dashboard display of overdue follow-ups, and notification system. `M`

6. [ ] Revenue Tracking — Add revenue fields to contacts (deal value, actual revenue, close date) with calculation of total pipeline value and revenue by stage or time period. `S`

7. [ ] Dashboard & Analytics — Create main dashboard showing key metrics (pipeline value by stage, overdue follow-ups count, recent conversions, revenue summary) with simple charts. `M`

8. [ ] Email Template Management — Build template creation, editing, and storage system with variable substitution (contact name, company, etc.) and quick-send functionality from contact view. `S`

## Phase 2: AI Integration & Enhanced UX

9. [ ] LLM Integration with Caching — Integrate OpenAI or Anthropic API with SQLite-based response caching (no expiry) to enable AI features without repeated costs during demos/testing. `M`

10. [ ] AI Interaction Parser — Build AI-powered feature to extract key information (action items, sentiment, next steps) from user-entered meeting notes or email content and auto-populate relevant contact fields. `L`

11. [ ] AI Proposal Generator — Implement proposal generation based on contact history, deal value, and previous successful proposals, with editable output before saving. `L`

12. [ ] Drag-and-Drop Pipeline View — Create Kanban-style board interface where users can drag contacts between pipeline stages with visual pipeline management. `M`

13. [ ] Advanced Search & Filtering — Add multi-field search, saved filters, and sorting options across contacts with filter by stage, date range, revenue, last contact date, etc. `S`

14. [ ] Bulk Actions — Implement ability to select multiple contacts and perform batch operations (stage change, tag assignment, export, delete). `S`

## Phase 3: Integrations & Advanced Features

15. [ ] Gmail/Outlook Email Integration — Build email sync to automatically import contact interactions, parse sender information to match/create contacts, and display email timeline in activity feed. `XL`

16. [ ] Google Calendar/Outlook Calendar Sync — Implement calendar integration to automatically log meetings with contacts and create follow-up reminders based on meeting dates. `L`

17. [ ] Payment Integration — Add Stripe or PayPal integration to track actual payments against revenue projections and update contact revenue automatically on payment receipt. `L`

18. [ ] Export & Reporting — Build custom report builder with date range selection, export to CSV/PDF, and revenue reporting by source, stage, or time period. `M`

19. [ ] Mobile-Responsive Design — Optimize UI for mobile devices with touch-friendly pipeline management and quick contact lookup/notes on mobile. `M`

20. [ ] Zapier/Webhook Integration — Create webhook endpoints and Zapier integration to connect with form submissions, social media leads, and accounting software. `L`

> Notes
> - Features ordered by dependencies and progressive value delivery
> - MVP (items 1-8) focuses on core CRM without AI to establish foundation quickly
> - Phase 2 (items 9-14) adds AI differentiation and UX polish on proven foundation
> - Phase 3 (items 15-20) introduces external integrations that were explicitly deferred from MVP
> - Each item represents complete end-to-end functionality (backend API + frontend UI + testing)
> - AI features (items 9-11) are grouped together to build caching infrastructure once and reuse
> - Integration features (items 15-17) require significant architectural planning per vision document
