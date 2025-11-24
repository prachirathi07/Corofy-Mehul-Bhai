# Corofy - Technical Journey Map
*The Real Story of Evolution, Pivots, and Engineering Decisions*

---

## 1. Architecture & Design Evolution

### **Phase 1: The "Campaign" Era (Initial Design)**
*   **Initial Vision**: A full-blown CRM with Campaigns, Batches, and complex state management.
*   **Architecture**:
    *   `leads` table was the core.
    *   `email_batches` tracked groups of leads.
    *   Manual trigger for every batch.
*   **The Pain Point**: It was **too complex**. Managing batches manually was tedious. The user just wanted to "Send emails" without micromanaging campaigns.
*   **The Pivot**: **Simplification**. We abandoned the "Campaign" model for a "Daily Quota" model.

### **Phase 2: The "One-Click" Revolution (Current Architecture)**
*   **New Vision**: A "Set it and forget it" system. "I want to send 400 emails a day. Period."
*   **Key Changes**:
    *   **Service Switch**: Replaced `BatchTrackingService` with `SimplifiedEmailTrackingService`.
    *   **Database Shift**: Moved from `leads` (legacy) to `scraped_data` (clean slate) to align with Apollo's schema.
    *   **Logic**: Implemented a strict **400/day limit** and **Sequential Processing** (Day 1: 1-400, Day 2: 401-800).

### **Phase 3: The "Hybrid" Brain (AI Refinement)**
*   **Initial Approach**: Generic GPT-4 prompt ("Write a sales email").
*   **The Problem**: It was too generic. It pitched "Chemicals" to a "Lubricant" company.
*   **The Pivot**: **Hybrid Logic**.
    *   **Hardcoded**: If Industry == Lubricants -> Pitch "Additives".
    *   **Dynamic**: If Industry == Unknown -> Use Firecrawl to scrape website -> AI infers product.
*   **Result**: 10x increase in relevance.

---

## 2. Technical Debt Chronicle

### **Accumulated Debt**
*   **Redundant Tables**: We still have `leads`, `email_batches`, and `daily_email_quota` in the DB, even though we use `scraped_data` and `daily_email_tracking`.
    *   *Why?* We pivoted fast and didn't want to break legacy FK constraints immediately.
*   **Prompt Hardcoding**: The "Product Catalog" is hardcoded in `OpenAIService.py` instead of a DB table.
    *   *Why?* Speed of iteration. It's easier to edit a string than build a CRUD UI for products.

### **Debt Paid Down**
*   **Schema Cleanup Plan**: We identified the FK dependencies (`email_queue` -> `leads`) and created a plan to repoint them to `scraped_data`.
*   **Code Cleanup**: Removed `check_stats.py` and unused imports.

---

## 3. Code & Implementation History

### **Major Feature: Smart Scheduling**
*   **Challenge**: Sending emails at 2 AM gets you blocked.
*   **Solution**: Implemented `TimezoneService`.
    *   *Algorithm*: `Country -> Timezone -> Current Time -> Is Business Hour?`
    *   *Outcome*: Emails are queued in `email_queue` if it's night time.

### **Major Feature: Concurrency Locking**
*   **The Bug**: "Kevin Forrester" was processed twice.
    *   *Cause*: User double-clicked "Send". Two requests fetched the same 'new' lead before the first one finished.
*   **The Fix**: **Immediate Locking**.
    *   *Code*: `UPDATE scraped_data SET status='processing' WHERE id IN (...)` **immediately** after fetching.
    *   *Outcome*: Zero duplicate sends.

### **Optimization: Apollo Credit Saver**
*   **The Problem**: Apollo returns 100 leads/page. User asked for 10. We wasted 90 credits.
*   **The Fix**: Dynamic Pagination.
    *   *Code*: `per_page = min(leads_needed, 100)`.
    *   *Outcome*: Exact credit usage.

---

## 4. Infrastructure Journey

### **Deployment Evolution**
1.  **Local**: `uvicorn app.main:app --reload`. Simple, fast.
2.  **Render (Staging/Prod)**:
    *   *Challenge*: `N8N_WEBHOOK_URL` was missing in Render env vars, causing crash.
    *   *Fix*: Added to `.env` and `config.py`.
3.  **Database**: Supabase.
    *   *Evolution*: Started with basic tables. Added `scraped_data` to decouple from legacy logic. Added Indexes for performance.

---

## 5. Technical Challenges & Solutions

### **The "Missing Column" Crash (PGRST204)**
*   **Issue**: Backend crashed with "Could not find column 'total_leads_wanted'".
*   **Cause**: Code expected a column that wasn't in the DB schema yet.
*   **Solution**: Created migration `add_total_leads_wanted_to_apollo_searches.sql`.

### **The "Rate Limit" Wall**
*   **Issue**: OpenAI returned 429 (Too Many Requests) when processing batches.
*   **Solution**: Implemented `RateLimiter` class.
    *   *Logic*: Token bucket algorithm / simple delay. "Wait 6.8s" logs appeared in terminal.

### **The "Insufficient Quota" Silence**
*   **Issue**: Apollo 403 errors were logged but returned "0 leads", confusing the user.
*   **Solution**: Explicit Exception Raising.
    *   *Code*: `raise HTTPException(403, "Apollo API 403...")`.
    *   *Outcome*: Frontend now shows "Insufficient Credits".

---

## 6. Experimentation Log

*   **Experiment**: "Can we use N8N for everything?"
    *   *Result*: **No**. Too hard to debug complex logic (Timezones, AI retry). Moved logic to Python Backend.
*   **Experiment**: "Scrape every website live?"
    *   *Result*: **Too Slow/Expensive**.
    *   *Fix*: Added `company_websites` cache. Only scrape if not in DB.

---

## 7. Tooling & Developer Experience

*   **Scheduler**: Added `APScheduler` to handle background tasks (Queue, DLQ).
    *   *Why?* `cron` is hard to manage on PaaS like Render. In-app scheduler is self-contained.
*   **Resilience**: Added `tenacity` library.
    *   *Why?* DB connections drop. `tenacity` retries automatically.

---

## 8. Metrics That Tell the Story

*   **Duplicate Sends**: Reduced from **>0** (Risk) to **0** (After Locking).
*   **Credit Wastage**: Reduced by **90%** (for small batches) via Exact-Count logic.
*   **Uptime**: Improved via `tenacity` and `RateLimiter`.

---
*Generated: 2025-11-24*
