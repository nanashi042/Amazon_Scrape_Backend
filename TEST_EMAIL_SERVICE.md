# Email Service Verification Guide

## Current Configuration

**Email Backend:** Console Backend (Development)
- Emails are printed to console/terminal
- Perfect for testing without SMTP setup
- Can be switched to SMTP for production

**Default From Email:** `noreply@amazonpricetracker.com`

## How to Test Email Service

### Step 1: Verify Current Setup

```bash
# The email backend is configured in settings.py:
# EMAIL_BACKEND = 'django.core.mail.backends.console.EmailBackend'
# DEFAULT_FROM_EMAIL = 'noreply@amazonpricetracker.com'
```

### Step 2: Test Scenario - Price Alert with Current Price as Target

#### Before Fix:
- ❌ Form rejected: "Target price must be less than current price"
- Email service untested

#### After Fix:
- ✅ Form accepts: target_price = current_price
- ✅ Trigger logic checks: `if current_price <= target_price`
- ✅ Email sent immediately when price check runs

### Step 3: Manual Testing Steps

1. **Scrape a product** (e.g., current price = ₹500)
   
2. **Create price tracker** with:
   - Target Price: ₹500 (equal to current price)
   - Email: test@example.com
   
3. **Check Prices** (via API or management command):
   ```bash
   # Option A: Via management command
   python manage.py check_prices
   
   # Option B: Via API
   POST /api/trackers/check-prices/
   ```

4. **Watch the Console Output** - you should see:
   ```
   ------------------ Email Output ------------------
   Content-Type: text/plain; charset="utf-8"
   MIME-Version: 1.0
   Content-Transfer-Encoding: 7bit
   Subject: Price Alert: [Product Title]
   From: noreply@amazonpricetracker.com
   To: test@example.com
   Date: [timestamp]
   
   [Email body text]
   
   ------------------- HTML version --------------------
   [HTML email content]
   ```

## Email Service Logic Flow

```
┌─────────────────────────────────────────────────────────┐
│ 1. User creates tracker with target_price               │
├─────────────────────────────────────────────────────────┤
│ 2. Validation checks:                                   │
│    - target_price > 0                                   │
│    - target_price <= current_price  ✅ (NOW ALLOWS =)  │
├─────────────────────────────────────────────────────────┤
│ 3. Tracker created in database with status='active'     │
├─────────────────────────────────────────────────────────┤
│ 4. Price check runs (via command or API)                │
├─────────────────────────────────────────────────────────┤
│ 5. Trigger condition: current_price <= target_price     │
│    ✅ TRUE: Email sent, status='triggered'              │
│    ❌ FALSE: No email, tracker stays active             │
├─────────────────────────────────────────────────────────┤
│ 6. Email content:                                       │
│    - Subject: "Price Alert: [Product Title]"            │
│    - Format: Plain text + HTML                          │
│    - Backend: Console (prints to terminal)              │
│    - Settings: Can switch to SMTP for production        │
└─────────────────────────────────────────────────────────┘
```

## Validation Changes Made

### Before:
```python
if target_price_decimal >= product.current_price:
    return error: "Target price must be less than current price"
```

### After:
```python
if target_price_decimal > product.current_price:
    return error: "Target price must be less than or equal to current price"
```

**Impact:**
- Now allows: `target_price = current_price` ✅
- Still rejects: `target_price > current_price` ❌

## Email Service Features

### Plain Text Email:
- Product title
- Current price (with currency symbol)
- ASIN
- Rating and reviews
- Product URL

### HTML Email:
- Styled with Amazon brand colors (Orange #FF9900)
- Card layout with product information
- Clickable "View Product" button
- Professional formatting

### Error Handling:
- If email fails, exception caught and logged
- Tracker still marked as triggered (won't retry)
- Error message printed to console

## Testing with API

```bash
# 1. Create a product (or use existing one with ID=1)
curl -X POST http://localhost:8000/api/products/scrape/ \
  -H "Content-Type: application/json" \
  -d '{"url": "https://www.amazon.com/..."}'

# 2. Create tracker with current price as target
curl -X POST http://localhost:8000/api/trackers/ \
  -H "Content-Type: application/json" \
  -d '{
    "product_id": 1,
    "user_email": "test@example.com",
    "target_price": "500.00"
  }'

# 3. Check prices (emails will print to console)
curl -X POST http://localhost:8000/api/trackers/check-prices/
```

## Production Setup

To use real email (Gmail, SendGrid, etc.):

```python
# settings.py
EMAIL_BACKEND = 'django.core.mail.backends.smtp.EmailBackend'
EMAIL_HOST = 'smtp.gmail.com'
EMAIL_PORT = 587
EMAIL_USE_TLS = True
EMAIL_HOST_USER = 'your-email@gmail.com'
EMAIL_HOST_PASSWORD = 'your-app-password'
DEFAULT_FROM_EMAIL = 'your-email@gmail.com'
```

## Summary

✅ **Email service is fully functional**
- Console backend works perfectly for development
- Validation now allows target_price = current_price
- Email triggers immediately when price check runs
- Both plain text and HTML versions sent
- Error handling in place
- Easy to switch to SMTP for production
