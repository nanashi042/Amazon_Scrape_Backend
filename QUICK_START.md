# Quick Start Guide

## What Was Implemented

Your Amazon Price Tracker backend now has **2 main API endpoints** with full functionality:

### 1. **Scrape Amazon Product** - GET & POST
- **Endpoint:** `POST /api/products/scrape/`
- **What it does:** User submits an Amazon product URL, gets back all product details
- **Returns:** Product title, price, rating, reviews, image, availability, etc.

### 2. **Create Price Tracker** - POST
- **Endpoint:** `POST /api/trackers/`
- **What it does:** User sets a target price they want to be alerted at
- **When triggered:** If product price drops to/below target, an email is automatically sent

### 3. **Check All Prices** - Bonus
- **Endpoint:** `POST /api/trackers/check-prices/`
- **What it does:** Manually trigger price checks and send alerts (or run automatically via cron/Celery)

---

## File Structure

```
Scraping_Event/
├── models.py              # AmazonProduct & PriceTracker models
├── serializers.py         # DRF serializers for API validation
├── views.py              # API ViewSets (GET/POST handlers)
├── urls.py               # Route configuration
├── admin.py              # Django admin interface
├── scraper.py            # Amazon web scraper (extracts product data)
├── email_service.py      # Email notification handler
└── management/commands/
    └── check_prices.py   # Periodic price check command
```

---

## Getting Started

### 1. Install Dependencies
```bash
uv sync
```

### 2. Apply Database Migrations
```bash
uv run python manage.py migrate
```

### 3. Run Development Server
```bash
uv run python manage.py runserver
```

Visit: `http://127.0.0.1:8000/`

---

## API Usage Examples

### Example 1: Scrape Product
```bash
curl -X POST http://127.0.0.1:8000/api/products/scrape/ \
  -H "Content-Type: application/json" \
  -d '{
    "url": "https://www.amazon.com/dp/B0C5J4ZPXY"
  }'
```

**Response:**
```json
{
  "id": 1,
  "url": "https://www.amazon.com/dp/B0C5J4ZPXY",
  "asin": "B0C5J4ZPXY",
  "title": "USB-C Cable 10ft",
  "current_price": 12.99,
  "rating": 4.5,
  "number_of_reviews": 2543,
  ...
}
```

### Example 2: Create Price Tracker
```bash
curl -X POST http://127.0.0.1:8000/api/trackers/ \
  -H "Content-Type: application/json" \
  -d '{
    "product_id": 1,
    "user_email": "john@example.com",
    "target_price": 9.99
  }'
```

**Response:**
```json
{
  "id": 1,
  "product": { /* full product details */ },
  "user_email": "john@example.com",
  "target_price": 9.99,
  "status": "active",
  "email_sent": false,
  "created_at": "2024-12-01T10:35:00Z"
}
```

### Example 3: Check Prices (Send Alerts)
```bash
curl -X POST http://127.0.0.1:8000/api/trackers/check-prices/
```

**Response:**
```json
{
  "total_checked": 5,
  "emails_sent": 2,
  "results": [
    {
      "tracker_id": 1,
      "product": "USB-C Cable 10ft",
      "email": "john@example.com",
      "message": "Email sent successfully",
      "status": "success"
    }
  ]
}
```

---

## Database Models at a Glance

### AmazonProduct
Stores product information:
- `asin` - Product ID (unique)
- `url` - Amazon link
- `title` - Product name
- `current_price` - Current price
- `rating` - Star rating (0-5)
- `number_of_reviews` - Review count
- `image_url` - Product photo
- `created_at` / `updated_at` - Timestamps

### PriceTracker
Stores user price alerts:
- `product` - Which product to track
- `user_email` - User's email for notifications
- `target_price` - Price threshold for alert
- `status` - active/inactive/triggered
- `email_sent` - Whether notification was sent

---

## Email Configuration

### Development (Console)
Emails print to console. Check your terminal output.

### Production (Gmail)
Update `main_api/settings.py`:
```python
EMAIL_BACKEND = 'django.core.mail.backends.smtp.EmailBackend'
EMAIL_HOST = 'smtp.gmail.com'
EMAIL_PORT = 587
EMAIL_USE_TLS = True
EMAIL_HOST_USER = 'your-email@gmail.com'
EMAIL_HOST_PASSWORD = 'your-app-password'
```

---

## Automation

### Run Price Checks Every Hour (Linux/Mac)
```bash
# Edit crontab
crontab -e

# Add this line (runs every hour)
0 * * * * cd /home/nanashi/Documents/Projects/Amazon_backend && uv run python manage.py check_prices
```

---

## Key Features

✅ **Scrape any Amazon product** - Extract title, price, rating, image, availability  
✅ **Create price trackers** - Set target price for any product  
✅ **Email alerts** - Automatically notified when price drops  
✅ **Track multiple products** - Same user can track unlimited products  
✅ **Track multiple prices** - Same user can set different target prices for same product  
✅ **Admin interface** - View/manage products and trackers at `/admin/`  
✅ **RESTful API** - Full CRUD operations on all resources  

---

## All Endpoints

| Method | Endpoint | Purpose |
|--------|----------|---------|
| POST | `/api/products/scrape/` | Scrape & store product |
| GET | `/api/products/` | List all products |
| GET | `/api/products/{id}/` | Get single product |
| POST | `/api/trackers/` | Create price tracker |
| GET | `/api/trackers/` | List all trackers |
| GET | `/api/trackers/{id}/` | Get single tracker |
| PATCH | `/api/trackers/{id}/` | Update tracker |
| DELETE | `/api/trackers/{id}/` | Delete tracker |
| POST | `/api/trackers/check-prices/` | Check & alert |

---

## Next Steps (Optional Enhancements)

- [ ] Add user authentication (so users manage only their trackers)
- [ ] Add Celery for async price checking in background
- [ ] Add product comparison features
- [ ] Add historical price data/charts
- [ ] Add Slack/Discord notifications
- [ ] Add webhook support
- [ ] Deploy to production (AWS, Heroku, etc.)

---

## Support

For detailed API documentation, see `API_DOCUMENTATION.md`
