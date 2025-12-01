# Architecture & Database Design

## Data Model Relationships

```
┌─────────────────────────────────────────────────────────────┐
│                    DATABASE SCHEMA                          │
└─────────────────────────────────────────────────────────────┘

AmazonProduct
├── id (Primary Key)
├── asin (Unique, Index) ────────────┐
├── url (Unique)                     │
├── title                            │
├── current_price                    │
├── original_price                   │
├── currency                         │
├── rating                           │
├── number_of_reviews                │
├── image_url                        │
├── description                      │
├── availability                     │
├── created_at                       │
└── updated_at                       │
                                     │
                                     │ 1 to Many
                                     │ Relationship
                                     │
                                     ▼
PriceTracker
├── id (Primary Key)
├── product_id (Foreign Key) ────────┘
├── user_email (Index)
├── target_price
├── status (active/inactive/triggered)
├── email_sent
├── created_at
└── triggered_at
```

---

## How Data Flows

### 1. Product Scraping Flow
```
┌─────────────────┐
│  User sends URL │
└────────┬────────┘
         │
         ▼
┌──────────────────┐
│ POST /scrape/    │
│ Validate URL     │
└────────┬─────────┘
         │
         ▼
┌──────────────────┐
│ Extract ASIN     │
│ from URL         │
└────────┬─────────┘
         │
         ▼
┌──────────────────┐
│ BeautifulSoup    │
│ Scrape HTML      │
└────────┬─────────┘
         │
         ▼
┌──────────────────┐
│ Parse data:      │
│ • Title          │
│ • Price          │
│ • Rating         │
│ • Reviews        │
│ • Image          │
└────────┬─────────┘
         │
         ▼
┌──────────────────┐
│ Save to DB or    │
│ Update existing  │
└────────┬─────────┘
         │
         ▼
┌──────────────────┐
│ Return product   │
│ JSON response    │
└──────────────────┘
```

### 2. Price Tracking Flow
```
┌──────────────────────┐
│ User creates tracker │
│ • product_id        │
│ • user_email        │
│ • target_price      │
└──────────┬───────────┘
           │
           ▼
┌──────────────────────┐
│ POST /trackers/      │
│ Validate inputs      │
└──────────┬───────────┘
           │
           ▼
┌──────────────────────┐
│ Create database      │
│ record (active)      │
└──────────┬───────────┘
           │
           ▼
┌──────────────────────┐
│ Return tracker info  │
│ (waiting for alert)  │
└──────────┬───────────┘
           │
           ▼ (Later - manual or automatic)
┌──────────────────────┐
│ check_prices cmd     │
│ (cron/Celery)       │
└──────────┬───────────┘
           │
           ▼
┌──────────────────────┐
│ Get all active       │
│ trackers             │
└──────────┬───────────┘
           │
           ▼
┌──────────────────────┐
│ For each tracker:    │
│ Rescrape product    │
│ Update price        │
└──────────┬───────────┘
           │
           ▼
        ┌──────────────────────┐
        │ Is price ≤ target?   │
        └──┬────────────────┬──┘
           │                │
        YES│                │NO
           │                │
           ▼                ▼
    ┌───────────────┐  ┌──────────────┐
    │ Send email    │  │ Do nothing   │
    │ Mark triggered│  │ Keep active  │
    │ Set email_sent│  │              │
    └───────────────┘  └──────────────┘
           │
           ▼
    ┌───────────────────┐
    │ User gets notified│
    │ Check Amazon!    │
    └───────────────────┘
```

---

## Key Database Constraints

### AmazonProduct
```sql
-- Unique ASIN (prevents duplicate products)
UNIQUE(asin)

-- Unique URL (prevents duplicate URLs)
UNIQUE(url)

-- Index on ASIN for fast lookups
INDEX(asin)
```

### PriceTracker
```sql
-- Composite unique constraint
-- User can't have same tracker twice for same product/price
UNIQUE(product_id, user_email, target_price)

-- Indexes for filtering
INDEX(user_email)  -- Fast lookup by user
INDEX(product_id)  -- Fast lookup by product
```

---

## API Response Examples

### Create Product (POST /api/products/scrape/)
```
Request:
{
  "url": "https://www.amazon.com/dp/B0XXXXXXXXXX"
}

Response (201 Created):
{
  "id": 1,
  "url": "https://www.amazon.com/dp/B0XXXXXXXXXX",
  "asin": "B0XXXXXXXXXX",
  "title": "Premium USB-C Cable",
  "current_price": "12.99",
  "original_price": "19.99",
  "currency": "USD",
  "rating": 4.5,
  "number_of_reviews": 2543,
  "image_url": "https://images-amazon.com/...",
  "description": "High-quality cable...",
  "availability": "In Stock",
  "created_at": "2024-12-01T10:30:00Z",
  "updated_at": "2024-12-01T10:30:00Z"
}
```

### Create Tracker (POST /api/trackers/)
```
Request:
{
  "product_id": 1,
  "user_email": "john@example.com",
  "target_price": "9.99"
}

Response (201 Created):
{
  "id": 1,
  "product": {
    "id": 1,
    "url": "https://www.amazon.com/dp/B0XXXXXXXXXX",
    "asin": "B0XXXXXXXXXX",
    "title": "Premium USB-C Cable",
    ... (full product object)
  },
  "user_email": "john@example.com",
  "target_price": "9.99",
  "status": "active",
  "email_sent": false,
  "created_at": "2024-12-01T10:35:00Z",
  "triggered_at": null
}
```

### List Trackers (GET /api/trackers/)
```
Response (200 OK):
[
  {
    "id": 1,
    "product": { ... },
    "user_email": "john@example.com",
    "target_price": "9.99",
    "status": "active",
    "email_sent": false,
    "created_at": "2024-12-01T10:35:00Z",
    "triggered_at": null
  },
  {
    "id": 2,
    "product": { ... },
    "user_email": "jane@example.com",
    "target_price": "15.00",
    "status": "triggered",
    "email_sent": true,
    "created_at": "2024-11-28T09:20:00Z",
    "triggered_at": "2024-12-01T08:15:00Z"
  }
]
```

### Check Prices (POST /api/trackers/check-prices/)
```
Response (200 OK):
{
  "total_checked": 3,
  "emails_sent": 1,
  "results": [
    {
      "tracker_id": 1,
      "product": "Premium USB-C Cable",
      "email": "john@example.com",
      "message": "Email sent successfully",
      "status": "success"
    }
  ]
}
```

---

## Status Field Values

```
┌─────────────────┬──────────────────────────────────────┐
│ Status          │ Meaning                              │
├─────────────────┼──────────────────────────────────────┤
│ active          │ Tracker is waiting for price drop    │
│                 │ Email not yet sent                   │
├─────────────────┼──────────────────────────────────────┤
│ inactive        │ User deactivated the tracker         │
│                 │ Won't send emails anymore            │
├─────────────────┼──────────────────────────────────────┤
│ triggered       │ Price dropped! Email was sent        │
│                 │ Tracker now inactive/complete        │
└─────────────────┴──────────────────────────────────────┘
```

---

## Scalability Considerations

### Current Setup
- SQLite database (good for development)
- Synchronous email sending
- Manual or cron-based price checking

### For Production, Consider:

1. **Database**
   ```
   SQLite → PostgreSQL or MySQL
   (Better concurrency, more reliable)
   ```

2. **Async Tasks**
   ```
   Cron jobs → Celery + Redis
   (Automatic, scalable price checking)
   ```

3. **Email**
   ```
   Console → SMTP (Gmail/SendGrid)
   (Real email delivery)
   ```

4. **Caching**
   ```
   Add Redis
   (Cache frequently scraped products)
   ```

5. **Rate Limiting**
   ```
   Add django-ratelimit
   (Prevent API abuse)
   ```

---

## Example: Complete Tracker Lifecycle

```
Time    Event                          Status    Email Sent
────────────────────────────────────────────────────────────
10:30   Product scraped                -         -
10:35   Tracker created for $9.99      active    false
        (current price: $12.99)

11:30   Price check runs               active    false
        (current price: $12.99)

14:30   Price check runs               active    false
        (current price: $10.50)

17:30   Price check runs               triggered true  ✓
        (current price: $9.49)
        → Email sent to user!
        → User checks Amazon
        → Buys product!

[Later]
        Tracker remains at status=triggered
        (Complete, won't send more emails)
```

---

## Error Handling

### Scraping Errors
```
Scenario: Invalid URL
Request: POST /api/products/scrape/ with invalid URL
Response: 400 Bad Request
{
  "error": "Please provide a valid Amazon product URL."
}
```

### Tracker Errors
```
Scenario: Product not found
Request: POST /api/trackers/ with non-existent product_id
Response: 400 Bad Request
{
  "error": "Product not found."
}

Scenario: Duplicate tracker
Request: POST /api/trackers/ with existing combination
Response: 400 Bad Request
{
  "error": "A tracker with this product and email already exists."
}
```

---

## Performance Optimization Tips

1. **Index heavily used fields**
   ```python
   - asin (Product lookup)
   - user_email (Filter by user)
   - product_id (Filter trackers)
   ```

2. **Cache product data**
   - Don't re-scrape if recently updated
   - Use Redis for quick lookups

3. **Batch price checks**
   - Check multiple products in parallel
   - Use Celery for concurrent tasks

4. **Limit scraping frequency**
   - Rate limit requests to Amazon
   - Respect robots.txt

5. **Archive old trackers**
   - Move triggered trackers to archive table
   - Keep active trackers table small

---

## Security Considerations

1. **Email validation**
   - Verify email addresses are valid
   - Prevent email spoofing

2. **Rate limiting**
   - Limit API requests per IP
   - Prevent scraping abuse

3. **Input validation**
   - Validate all URLs
   - Sanitize price inputs

4. **Authentication** (for production)
   - Require user login
   - Users can only access own trackers

5. **HTTPS only** (for production)
   - Encrypt data in transit
   - Prevent man-in-the-middle attacks

---

## Future Enhancements

```
Current:
User → Scrape Product → Create Tracker → Manual Check Prices → Email

With Authentication:
User Login → Scrape Product → Create Tracker → Auto Check (Celery) → Email

With Dashboard:
User Login → View Trackers → Edit Targets → View Charts → Email

With Notifications:
Email + Slack + Discord + Webhook + SMS Alerts
```
