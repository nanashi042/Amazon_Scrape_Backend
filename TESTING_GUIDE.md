# Testing Guide & Curl Examples

## Setup for Testing

### 1. Start Django Server
```bash
uv run python manage.py migrate
uv run python manage.py runserver
```

Server will run at: `http://127.0.0.1:8000/`

### 2. Create Test Data (Optional)
```bash
uv run python manage.py shell
```

```python
from Scraping_Event.models import AmazonProduct, PriceTracker

# Create a test product manually
product = AmazonProduct.objects.create(
    asin='B0TESTPROD01',
    url='https://www.amazon.com/dp/B0TESTPROD01',
    title='Test Product',
    current_price=29.99,
    rating=4.5,
    number_of_reviews=100
)
print(f"Created product: {product.id}")
```

---

## API Testing with curl

### 1. Scrape a Product

#### Real Amazon Product (May take a few seconds)
```bash
curl -X POST http://127.0.0.1:8000/api/products/scrape/ \
  -H "Content-Type: application/json" \
  -d '{
    "url": "https://www.amazon.com/s?k=USB-C+cable"
  }' | python -m json.tool
```

#### Test with Invalid URL (Should Fail)
```bash
curl -X POST http://127.0.0.1:8000/api/products/scrape/ \
  -H "Content-Type: application/json" \
  -d '{
    "url": "https://www.google.com"
  }'
```

Expected Error:
```json
{
  "error": "Please provide a valid Amazon product URL."
}
```

---

### 2. Get List of Products

```bash
curl -X GET http://127.0.0.1:8000/api/products/ \
  -H "Content-Type: application/json" | python -m json.tool
```

#### Filter by Search
```bash
curl -X GET "http://127.0.0.1:8000/api/products/?search=cable" \
  -H "Content-Type: application/json" | python -m json.tool
```

#### Filter by ASIN
```bash
curl -X GET "http://127.0.0.1:8000/api/products/?asin=B0TESTPROD01" \
  -H "Content-Type: application/json" | python -m json.tool
```

---

### 3. Get Single Product

```bash
# Replace 1 with actual product ID
curl -X GET http://127.0.0.1:8000/api/products/1/ \
  -H "Content-Type: application/json" | python -m json.tool
```

---

### 4. Create Price Tracker

```bash
curl -X POST http://127.0.0.1:8000/api/trackers/ \
  -H "Content-Type: application/json" \
  -d '{
    "product_id": 1,
    "user_email": "test@example.com",
    "target_price": 20.00
  }' | python -m json.tool
```

#### Expected Response (201 Created)
```json
{
  "id": 1,
  "product": {
    "id": 1,
    "url": "https://...",
    "asin": "B0...",
    "title": "Product Name",
    ...
  },
  "user_email": "test@example.com",
  "target_price": "20.00",
  "status": "active",
  "email_sent": false,
  "created_at": "2024-12-01T10:35:00Z",
  "triggered_at": null
}
```

#### Try Duplicate Tracker (Should Fail)
```bash
curl -X POST http://127.0.0.1:8000/api/trackers/ \
  -H "Content-Type: application/json" \
  -d '{
    "product_id": 1,
    "user_email": "test@example.com",
    "target_price": 20.00
  }'
```

Expected Error:
```json
{
  "error": "A tracker with this product and email already exists."
}
```

---

### 5. Get All Trackers

```bash
curl -X GET http://127.0.0.1:8000/api/trackers/ \
  -H "Content-Type: application/json" | python -m json.tool
```

#### Filter by User Email
```bash
curl -X GET "http://127.0.0.1:8000/api/trackers/?user_email=test@example.com" \
  -H "Content-Type: application/json" | python -m json.tool
```

#### Filter by Status
```bash
curl -X GET "http://127.0.0.1:8000/api/trackers/?status=active" \
  -H "Content-Type: application/json" | python -m json.tool
```

#### Filter by Product
```bash
curl -X GET "http://127.0.0.1:8000/api/trackers/?product_id=1" \
  -H "Content-Type: application/json" | python -m json.tool
```

---

### 6. Get Single Tracker

```bash
curl -X GET http://127.0.0.1:8000/api/trackers/1/ \
  -H "Content-Type: application/json" | python -m json.tool
```

---

### 7. Update Tracker

#### Change Target Price
```bash
curl -X PATCH http://127.0.0.1:8000/api/trackers/1/ \
  -H "Content-Type: application/json" \
  -d '{
    "target_price": 15.00
  }' | python -m json.tool
```

#### Deactivate Tracker
```bash
curl -X PATCH http://127.0.0.1:8000/api/trackers/1/ \
  -H "Content-Type: application/json" \
  -d '{
    "status": "inactive"
  }' | python -m json.tool
```

---

### 8. Delete Tracker

```bash
curl -X DELETE http://127.0.0.1:8000/api/trackers/1/ \
  -H "Content-Type: application/json"
```

Expected: 204 No Content (no response body)

---

### 9. Check Prices & Send Alerts

```bash
curl -X POST http://127.0.0.1:8000/api/trackers/check-prices/ \
  -H "Content-Type: application/json" | python -m json.tool
```

#### Expected Response
```json
{
  "total_checked": 3,
  "emails_sent": 1,
  "results": [
    {
      "tracker_id": 1,
      "product": "Product Title",
      "email": "test@example.com",
      "message": "Email sent successfully",
      "status": "success"
    }
  ]
}
```

---

## Testing Workflow (Complete Example)

### Script to Test Everything
```bash
#!/bin/bash
# Save as test_api.sh
# Run: chmod +x test_api.sh && ./test_api.sh

API="http://127.0.0.1:8000/api"

echo "1. Scraping product..."
PRODUCT=$(curl -s -X POST "$API/products/scrape/" \
  -H "Content-Type: application/json" \
  -d '{"url": "https://www.amazon.com/s?k=USB"}')

PRODUCT_ID=$(echo "$PRODUCT" | grep -o '"id":[0-9]*' | head -1 | grep -o '[0-9]*')
echo "   Product ID: $PRODUCT_ID"
echo ""

echo "2. Creating tracker..."
TRACKER=$(curl -s -X POST "$API/trackers/" \
  -H "Content-Type: application/json" \
  -d "{
    \"product_id\": $PRODUCT_ID,
    \"user_email\": \"test@example.com\",
    \"target_price\": 10.00
  }")

TRACKER_ID=$(echo "$TRACKER" | grep -o '"id":[0-9]*' | head -1 | grep -o '[0-9]*')
echo "   Tracker ID: $TRACKER_ID"
echo ""

echo "3. Listing products..."
curl -s -X GET "$API/products/" \
  -H "Content-Type: application/json" | python -m json.tool | head -20
echo ""

echo "4. Listing trackers..."
curl -s -X GET "$API/trackers/" \
  -H "Content-Type: application/json" | python -m json.tool | head -20
echo ""

echo "5. Checking prices..."
curl -s -X POST "$API/trackers/check-prices/" \
  -H "Content-Type: application/json" | python -m json.tool
echo ""

echo "✓ Test complete!"
```

---

## Django Admin Testing

### 1. Create Superuser
```bash
uv run python manage.py createsuperuser
```

### 2. Visit Admin Panel
- URL: `http://127.0.0.1:8000/admin/`
- Login with credentials created above
- View/manage products and trackers

---

## Email Testing

### Development (Console Backend)
Emails print to console. Look for:
```
[email output]
Subject: Price Alert: Product Title
From: noreply@amazonpricetracker.com
To: test@example.com
...
```

### Testing Email Sending Directly (Python)
```python
# In Django shell
from django.core.mail import send_mail

send_mail(
    'Test Email',
    'This is a test message',
    'noreply@amazonpricetracker.com',
    ['test@example.com'],
    fail_silently=False,
)
```

---

## Debugging Tips

### Check Database Content
```bash
# Django shell
uv run python manage.py shell

# Import models
from Scraping_Event.models import AmazonProduct, PriceTracker

# View all products
for product in AmazonProduct.objects.all():
    print(f"{product.id}: {product.title} - ${product.current_price}")

# View all trackers
for tracker in PriceTracker.objects.all():
    print(f"{tracker.id}: {tracker.product.title} - Target: ${tracker.target_price}")

# Exit
exit()
```

### Check Logs
```bash
# View Django server output for errors
# (appears in terminal where you ran runserver)
```

### Test Scraping Function Directly
```python
# In Django shell
from Scraping_Event.scraper import scrape_amazon_product

result = scrape_amazon_product('https://www.amazon.com/dp/B0...')
print(result)
```

---

## Common Issues & Solutions

### Issue: "Import could not be resolved"
**Solution:** Install dependencies
```bash
uv sync
```

### Issue: "Table does not exist"
**Solution:** Run migrations
```bash
uv run python manage.py migrate
```

### Issue: Scraping returns error
**Possible causes:**
- Invalid Amazon URL
- Amazon blocked the request (try with user-agent)
- Amazon changed HTML structure
- Network timeout

**Solution:** Check Amazon URL format:
- Valid: `https://www.amazon.com/dp/B0XXXXXXXXXX`
- Invalid: `https://www.amazon.com/` or `https://amazon.com`

### Issue: Email not sending
**Development:** Check Django server terminal for email output
**Production:** Check email configuration in settings.py

### Issue: Tracker not triggering alert
**Check:**
1. Is tracker status "active"? (`GET /api/trackers/`)
2. What is current price vs target price?
3. Run price check: `POST /api/trackers/check-prices/`

---

## Performance Testing

### Load Test with Multiple Requests
```bash
# Install Apache Bench
brew install httpd  # macOS
sudo apt-get install apache2-utils  # Ubuntu

# Test endpoint
ab -n 100 -c 10 http://127.0.0.1:8000/api/products/
```

### Monitor Database Queries
```python
# In Django shell, enable query logging
from django.db import connection
from django.test.utils import CaptureQueriesContext

with CaptureQueriesContext(connection) as ctx:
    # Run your code here
    pass

print(f"Queries executed: {len(ctx)}")
for query in ctx:
    print(query['sql'])
```

---

## Testing Checklist

- [ ] Can scrape Amazon product URL
- [ ] Can list all products
- [ ] Can get single product
- [ ] Can create price tracker
- [ ] Can list all trackers
- [ ] Can get single tracker
- [ ] Can update tracker
- [ ] Can delete tracker
- [ ] Can check prices and send alerts
- [ ] Admin panel accessible
- [ ] Email sending works (check console)
- [ ] Database has correct data
- [ ] Duplicate trackers are rejected
- [ ] Invalid URLs are rejected

---

## Quick Test All Endpoints

```bash
# Step 1: Scrape
curl -X POST http://127.0.0.1:8000/api/products/scrape/ \
  -H "Content-Type: application/json" \
  -d '{"url": "https://www.amazon.com/s?k=laptop"}' -s | python -m json.tool

# Step 2: Create tracker (use product ID from step 1)
curl -X POST http://127.0.0.1:8000/api/trackers/ \
  -H "Content-Type: application/json" \
  -d '{"product_id": 1, "user_email": "test@example.com", "target_price": 500}' -s | python -m json.tool

# Step 3: List products
curl http://127.0.0.1:8000/api/products/ -s | python -m json.tool

# Step 4: List trackers
curl http://127.0.0.1:8000/api/trackers/ -s | python -m json.tool

# Step 5: Check prices
curl -X POST http://127.0.0.1:8000/api/trackers/check-prices/ -s | python -m json.tool
```

Done! All endpoints tested. ✓
