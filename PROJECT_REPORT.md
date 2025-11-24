# Corofy - AI Cold Outreach System Report

## 1. Project Overview
**Corofy** is an intelligent, automated cold email outreach system designed to scrape leads, generate highly personalized emails using AI, and send them within strict daily limits and business hours. It replaces manual outreach with a "One-Click" daily workflow.

---

## 2. System Architecture
*   **Backend**: Python (FastAPI) - Handles all business logic, API integrations, and background tasks.
*   **Frontend**: Next.js (React) - Provides a dashboard for managing leads, viewing stats, and triggering actions.
*   **Database**: Supabase (PostgreSQL) - Stores leads, email history, queues, and configuration.
*   **AI Engine**: OpenAI (GPT-4o-mini) - Generates personalized email content.
*   **Scraping Engine**: Apollo API (Leads) + Firecrawl (Website Content).
*   **Scheduler**: APScheduler (Async) - Manages background jobs (Queue, DLQ, Cleanup).

---

## 3. Key Features & Logic

### A. Lead Acquisition (Smart Scraping)
*   **Source**: Integrates with **Apollo API**.
*   **Cost Optimization**: The system calculates the exact number of API pages needed to fetch the *exact* number of leads requested (e.g., 10 leads), preventing wasted credits.
*   **Error Handling**: Explicitly catches and reports "Insufficient Credits" (403) errors to the user.

### B. "One-Click" Daily Sending
*   **Logic**: The system enforces a strict **400 emails/day** limit to protect domain reputation.
*   **Workflow**:
    1.  User clicks "Send Emails".
    2.  System checks `daily_email_tracking`.
    3.  If quota remains, it fetches the next batch of **unprocessed** leads.
    4.  **Concurrency Locking**: Immediately marks leads as `processing` to prevent duplicate sends if the button is clicked twice.

### C. Hybrid AI Personalization
*   **Logic**: Uses a hybrid approach for product selection to ensure accuracy.
    *   **Core Industries** (Lubricant, Oil & Gas, Agrochemical): The AI is forced to pick from a **hardcoded list** of Corofy's actual products.
    *   **Other Industries**: The AI dynamically infers the best chemical solution based on the prospect's website content.
*   **Context**: The prompt includes the prospect's **Website Content** (scraped via Firecrawl) and Corofy's **Global Supplier Profile**.
*   **Output**: Generates a Subject Line and Body, and classifies the company's industry.

### D. Smart Scheduling (Timezone Aware)
*   **Logic**: Emails are **never** sent outside business hours (9:00 AM - 7:00 PM lead's local time).
*   **Process**:
    *   **In Hours**: Sent immediately via Gmail/SMTP.
    *   **Out of Hours**: Added to `email_queue` with a scheduled time of 9:00 AM next business day.
*   **Automation**: A background scheduler checks the queue every **2 hours** and sends eligible emails.

### E. Resilience & Reliability
*   **Dead Letter Queue (DLQ)**: Failed emails are moved to `failed_emails` and retried automatically (up to 3 times) every hour.
*   **Rate Limiting**: Centralized limiter prevents hitting OpenAI/Firecrawl API limits (429 errors).
*   **Database Resilience**: Uses `tenacity` to retry database connections if they drop.

---

## 4. Database Schema (Key Tables)

| Table Name | Purpose |
| :--- | :--- |
| **`scraped_data`** | **The Master Table**. Stores all lead info (Name, Email, Company), status (`new`, `processing`, `email_sent`), and the generated email content. |
| **`daily_email_tracking`** | Tracks daily usage (Date, Count) to enforce the 400/day limit. |
| **`email_queue`** | Stores emails waiting for business hours. |
| **`failed_emails`** | Stores failed attempts for retry (DLQ). |
| **`company_websites`** | Caches scraped website content to save Firecrawl credits. |
| **`apollo_searches`** | Logs search history and criteria. |

*(Note: Old tables like `leads` and `email_batches` are slated for removal).*

---

## 5. Current Status

### ✅ Completed & Working
*   **Scraping**: Apollo integration is optimized and working.
*   **Personalization**: AI prompt is refined, hybrid logic is active.
*   **Sending**: Daily limit (400) and Concurrency Locking are active.
*   **Scheduling**: Timezone checks and Queue processing (2-hour interval) are active.
*   **Frontend**: Displays leads (up to 2000), stats, and error messages.

### ⏳ Pending / Maintenance
*   **Database Cleanup**: We need to drop unused tables (`leads`, `email_batches`) and repoint foreign keys to `scraped_data`.
*   **Production Deployment**: The system is ready for final deployment to Render.

---

## 6. How to Run
1.  **Start Backend**: `uvicorn app.main:app --reload`
2.  **Start Frontend**: `npm run dev`
3.  **Trigger**: Go to Dashboard -> Click "Send Emails".

---

## 7. Risk Mitigation Strategies
We have implemented multiple layers of protection to safeguard your budget, reputation, and data.

### A. Financial Risk (Cost Control)
*   **Exact-Count Scraping**: The system calculates the exact pagination needed to fetch *only* the requested number of leads (e.g., 10). This prevents Apollo from returning (and charging for) 100 leads when you only wanted 10.
*   **Website Caching**: Before scraping a website, we check `company_websites`. If we have scraped `example.com` before, we use the cached copy. This saves Firecrawl credits.
*   **Concurrency Locking**: By immediately marking leads as `processing` when a batch starts, we prevent "Double Spending". Even if you click "Send" 5 times, the system will only process the leads once, saving 5x the AI and Scraping costs.

### B. Reputation Risk (Email Deliverability)
*   **Strict Daily Limits**: The system enforces a hard cap of **400 emails/day**. This is the "Safe Zone" for warming up domains and avoiding Spam folders.
*   **Business Hours Enforcement**: Sending emails at 2 AM is a strong signal for Spam filters. Our system **queues** these emails and releases them at 9 AM local time, mimicking human behavior.
*   **Content Variation**: By using AI to personalize every single email based on the prospect's website, no two emails are identical. This bypasses "Template Matching" spam filters.

### C. Operational Risk (System Stability)
*   **Rate Limiting**: A centralized `RateLimiter` ensures we never exceed the API limits of OpenAI or Firecrawl. If we hit a limit, the system waits automatically instead of crashing.
*   **Dead Letter Queue (DLQ)**: If an email fails to send (e.g., API timeout), it is NOT lost. It is moved to `failed_emails` and the Scheduler retries it automatically up to 3 times.
*   **Database Resilience**: All database connections use `tenacity` to automatically reconnect if the connection drops, ensuring the server stays up 24/7.
