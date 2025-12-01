# API Documentation - Amazon Price Tracker

## Overview
This API allows users to:
1. **Scrape Amazon product details** from a product URL
2. **Set up price trackers** to get email alerts when prices drop

---

## Installation & Setup

### 1. Install Dependencies
```bash
uv sync
```

### 2. Apply Migrations
```bash
uv run python manage.py migrate
```

### 3. Run Development Server
```bash
uv run python manage.py runserver
```

Server will be available at `http://127.0.0.1:8000/`

---

## API Endpoints

### 1. Scrape Product (GET & POST)

**Endpoint:** `POST /api/products/scrape/`

**Purpose:** Scrape Amazon product details from a URL

**Request:**
```json
{
    "url": "https://www.amazon.com/dp/B0XXXXXXXXXX"
}
```

**Response (201 - New Product):**
```json
{
    "id": 1,
    "url": "https://www.amazon.com/dp/B0XXXXXXXXXX",
    "asin": "B0XXXXXXXXXX",
    "title": "Product Title",
    "current_price": 29.99,
    "original_price": 39.99,
    "currency": "USD",
    "rating": 4.5,
    "number_of_reviews": 1250,
    "image_url": "https://...",
    "description": "Product description...",
    "availability": "In Stock",
    "created_at": "2024-12-01T10:30:00Z",
    "updated_at": "2024-12-01T10:30:00Z"
}
```

**Response (200 - Existing Product, Updated):**
Same structure as above, but with status 200

**Error Response (400):**
```json
{
    "error": "Invalid Amazon product URL. Could not extract ASIN."
}
```

---

### 2. Create Price Tracker (POST)

**Endpoint:** `POST /api/trackers/`

**Purpose:** Create a price tracking alert for a product

**Request:**
```json
{
    "product_id": 1,
    "user_email": "user@example.com",
    "target_price": 25.50
}
```

**Response (201):**
```json
{
    "id": 1,
    "product": {
        "id": 1,
        "url": "https://www.amazon.com/dp/B0XXXXXXXXXX",
        "asin": "B0XXXXXXXXXX",
        "title": "Product Title",
        "current_price": 29.99,
        "original_price": 39.99,
        "currency": "USD",
        "rating": 4.5,
        "number_of_reviews": 1250,
        "image_url": "https://...",
        "description": "...",
        "availability": "In Stock",
        "created_at": "2024-12-01T10:30:00Z",
        "updated_at": "2024-12-01T10:30:00Z"
    },
    "user_email": "user@example.com",
    "target_price": 25.50,
    "status": "active",
    "email_sent": false,
    "created_at": "2024-12-01T10:35:00Z",
    "triggered_at": null
}
```

**Error Response (400):**
```json
{
    "error": "A tracker with this product and email already exists."
}
```

---

### 3. List All Products (GET)

**Endpoint:** `GET /api/products/`

**Response:**
```json
[
    {
        "id": 1,
        "url": "https://www.amazon.com/dp/B0XXXXXXXXXX",
        "asin": "B0XXXXXXXXXX",
        "title": "Product Title",
        "current_price": 29.99,
        ...
    }
]
```

**Query Parameters:**
- `search` - Search by title or ASIN
- `asin` - Filter by ASIN
- `currency` - Filter by currency

Example: `GET /api/products/?search=laptop`

---

### 4. List All Price Trackers (GET)

**Endpoint:** `GET /api/trackers/`

**Response:**
```json
[
    {
        "id": 1,
        "product": {...},
        "user_email": "user@example.com",
        "target_price": 25.50,
        "status": "active",
        "email_sent": false,
        "created_at": "2024-12-01T10:35:00Z",
        "triggered_at": null
    }
]
```

**Query Parameters:**
- `product_id` - Filter by product
- `user_email` - Filter by email
- `status` - Filter by status (active, inactive, triggered)

Example: `GET /api/trackers/?user_email=user@example.com&status=active`

---

### 5. Check All Prices & Send Alerts (POST)

**Endpoint:** `POST /api/trackers/check-prices/`

**Purpose:** Manually trigger price check for all active trackers

**Response:**
```json
{
    "total_checked": 5,
    "emails_sent": 2,
    "results": [
        {
            "tracker_id": 1,
            "product": "Product Title",
            "email": "user@example.com",
            "message": "Email sent successfully",
            "status": "success"
        }
    ]
}
```

---

### 6. Get Single Product (GET)

**Endpoint:** `GET /api/products/{id}/`

**Response:** Single product object

---

### 7. Get Single Tracker (GET)

**Endpoint:** `GET /api/trackers/{id}/`

**Response:** Single tracker object

---

### 8. Update Tracker (PATCH)

**Endpoint:** `PATCH /api/trackers/{id}/`

**Request:**
```json
{
    "target_price": 20.00,
    "status": "inactive"
}
```

**Response:** Updated tracker object

---

### 9. Delete Tracker (DELETE)

**Endpoint:** `DELETE /api/trackers/{id}/`

**Response:** 204 No Content

---

## Management Commands

### Check Prices Periodically
```bash
uv run python manage.py check_prices
```

This command:
- Fetches all active trackers with unsent emails
- Scrapes latest prices for each product
- Sends email alerts if price drops to target
- Updates tracker status to 'triggered'

**To run automatically every hour**, use Celery Beat or a cron job:
```bash
# Cron job example (runs every hour)
0 * * * * cd /path/to/project && uv run python manage.py check_prices
```

---

## Email Configuration

### Development (Console Backend)
Emails are printed to console by default. Check your Django logs.

### Production (Gmail SMTP)

Update `main_api/settings.py`:
```python
EMAIL_BACKEND = 'django.core.mail.backends.smtp.EmailBackend'
EMAIL_HOST = 'smtp.gmail.com'
EMAIL_PORT = 587
EMAIL_USE_TLS = True
EMAIL_HOST_USER = 'your-email@gmail.com'
EMAIL_HOST_PASSWORD = 'your-app-password'  # Use Gmail App Password
DEFAULT_FROM_EMAIL = 'your-email@gmail.com'
```

Get Gmail App Password:
1. Enable 2-Step Verification on your Google account
2. Go to https://myaccount.google.com/apppasswords
3. Select "Mail" and "Windows Computer"
4. Copy the 16-character password

---

## Example Workflow

### Step 1: Scrape a Product
```bash
curl -X POST http://127.0.0.1:8000/api/products/scrape/ \
  -H "Content-Type: application/json" \
  -d '{"url": "https://www.amazon.com/dp/B0XXXXXXXXXX"}'
```

### Step 2: Create a Price Tracker
```bash
curl -X POST http://127.0.0.1:8000/api/trackers/ \
  -H "Content-Type: application/json" \
  -d '{
    "product_id": 1,
    "user_email": "user@example.com",
    "target_price": 25.50
  }'
```

### Step 3: Check Prices (Manual or Automated)
```bash
curl -X POST http://127.0.0.1:8000/api/trackers/check-prices/
```

When price drops to $25.50 or below, an email is sent to the user!

---

## Database Models

### AmazonProduct
- `asin` - Amazon Standard Identification Number (unique)
- `url` - Amazon product URL (unique)
- `title` - Product title
- `current_price` - Current price on Amazon
- `original_price` - Original/list price (optional)
- `currency` - Currency (default: USD)
- `rating` - Product rating (0-5)
- `number_of_reviews` - Number of customer reviews
- `image_url` - Product image URL
- `description` - Product description
- `availability` - Stock status
- `created_at` - When product was first added
- `updated_at` - When product was last updated

### PriceTracker
- `product` - Foreign key to AmazonProduct
- `user_email` - Email to send alerts to
- `target_price` - Price at which to trigger alert
- `status` - One of: active, inactive, triggered
- `email_sent` - Whether alert email was sent
- `created_at` - When tracker was created
- `triggered_at` - When alert was triggered

---

## Notes

1. **Product updates**: Scraping the same product URL updates the existing product with latest prices
2. **Unique trackers**: Each user can have only one tracker per product per target price
3. **Email fallback**: If email sending fails, the tracker remains active and can be retried
4. **Async processing**: For production, use Celery to run `check_prices` in background tasks

---

## Troubleshooting

### Import Errors
Make sure dependencies are installed:
```bash
uv sync
```

### Database Errors
Reset migrations:
```bash
uv run python manage.py migrate Scraping_Event zero
uv run python manage.py migrate
```

### Scraping Failures
- The scraper may fail if Amazon changes their HTML structure
- Amazon may block requests - use a rotating proxy service if needed
- Ensure valid Amazon product URL format

### Email Not Sending
- Check email configuration in settings.py
- For Gmail, ensure App Password is used (not regular password)
- Check Django logs for errors

---

## Next Steps

1. Implement async task queue with Celery for automatic price checking
2. Add product image storage with S3 or local storage
3. Add user authentication and authorization
4. Create frontend dashboard for tracking prices
5. Implement webhook notifications (Slack, Discord)
6. Add product comparison features
7. Implement discount percentage calculation
