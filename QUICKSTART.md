# 🚀 Quick Start Guide - Amazon Price Tracker

## ⚡ 5-Minute Setup

### 1. Start the Server
```bash
cd /home/nanashi/Documents/Projects/Amazon_backend
python manage.py runserver
```

**Server running at**: `http://127.0.0.1:8000/`

### 2. Open in Browser
Visit: **http://127.0.0.1:8000/**

You'll see the homepage with:
- Amazon Price Tracker logo
- "Track Amazon Prices in Real-Time" headline
- URL input form to paste Amazon links
- Features section explaining how it works

## 📱 User Journey

### Step 1: Paste Amazon Link
1. Go to Amazon (amazon.in, amazon.com, etc.)
2. Find any product
3. Copy the product URL
4. Paste it in the input field on homepage
5. Click **"Get Details"** button

Example URL:
```
https://www.amazon.in/Apple-iPhone-15-128GB-Black/dp/B0CHX1X1YG
```

### Step 2: View Product Details
After clicking "Get Details", you'll see:
- ✅ Product image
- ✅ Product title
- ✅ **Price in INR (₹)** or other currency
- ✅ Rating (1-5 stars)
- ✅ Number of customer reviews
- ✅ Original price (if on discount)
- ✅ Discount percentage (if applicable)
- ✅ Availability status
- ✅ ASIN (product code)
- ✅ Direct link to Amazon

### Step 3: Set Price Alert
1. Click **"Track Price"** button
2. Modal form appears with:
   - **Email field**: Enter your email
   - **Target Price field**: Enter price you want (must be less than current)
   - Currency symbol shows automatically (₹ for INR, $ for USD, etc.)
3. Click **"Create Alert"**
4. Success message appears: "Price alert created successfully!"

### Step 4: Get Email Alert
When price drops to your target price:
- 📧 You receive email notification
- 📧 Email contains product details and new price
- 📧 You can click link to view product on Amazon

## 🎯 Features Explained

| Feature | What It Does |
|---------|-------------|
| **Multi-Currency Support** | Automatically detects INR (₹), USD ($), GBP (£), EUR (€) |
| **Smart Scraping** | Extracts product details even with Amazon's anti-bot measures |
| **Rating Display** | Shows star ratings and review counts |
| **Responsive Design** | Works perfectly on phone, tablet, laptop |
| **Email Alerts** | Automatic notifications when prices drop |
| **No Login Required** | Just paste URL and email, no account needed |

## 📊 Example Scenarios

### Scenario 1: iPhone Price Drop
```
Current Price: ₹79,999
Your Target: ₹75,000
Status: Waiting for price to drop

→ When price reaches ₹75,000 or less:
  📧 Email alert sent to you!
```

### Scenario 2: Laptop Discount
```
Original Price: ₹1,00,000
Current Price: ₹85,000 (15% discount)
Your Target: ₹75,000
Status: Waiting

→ When price drops further:
  📧 Notification received!
```

## 🔍 Testing the Application

### Test 1: Scrape a Product
1. Paste any Amazon India product URL
2. See product details load
3. Verify price shows in ₹ (rupees)

### Test 2: Create Price Alert
1. From product page, click "Track Price"
2. Enter email: `test@example.com`
3. Enter target price: Less than current price
4. Click "Create Alert"
5. Success message appears

### Test 3: Check Console Emails (Development)
Emails are logged to console in development mode:
```
Terminal shows:
[Console email output]
From: noreply@amazonpricetracker.com
To: test@example.com
Subject: Price Drop Alert!
```

## 🛠️ Admin Panel

Access Django admin at: **http://127.0.0.1:8000/admin/**

### Default Credentials (if created)
```
Username: admin
Password: (you set during setup)
```

### Admin Features
- View all products
- View all price trackers
- Edit product prices manually
- Delete products/trackers
- Filter by status/email/currency

## 📱 Mobile Testing

The application works perfectly on mobile:
1. Open `http://127.0.0.1:8000/` on phone browser
2. Layout adapts automatically
3. All features work on mobile

## ❓ Common Questions

### Q: Does it work with all Amazon regions?
**A**: Yes! It supports:
- amazon.in (India)
- amazon.com (USA)
- amazon.co.uk (UK)
- amazon.de (Germany)
- amazon.fr (France)
- And more!

### Q: How often does it check prices?
**A**: 
- **Development**: Manual checks via API
- **Production**: Can be set to check every hour/day using Celery

### Q: Can I track multiple prices?
**A**: Yes! Each product can have multiple trackers with different target prices and emails.

### Q: Is my email secure?
**A**: 
- Emails stored in database only
- Never shared with third parties
- Can delete tracker anytime to stop notifications

### Q: Why doesn't it show the price sometimes?
**A**: Amazon blocks aggressive web scrapers. If price isn't shown:
1. Wait a few minutes
2. Try a different product
3. Use VPN if needed
4. Contact support if issue persists

## 🔗 Useful Links

| Link | Purpose |
|------|---------|
| `http://127.0.0.1:8000/` | Main website |
| `http://127.0.0.1:8000/admin/` | Admin panel |
| `http://127.0.0.1:8000/api/products/` | API - List products |
| `http://127.0.0.1:8000/api/trackers/` | API - List trackers |

## 🚨 Troubleshooting

### Server won't start
```bash
# Kill any existing process
pkill -f "runserver"

# Try again
python manage.py runserver
```

### Price not showing (404 error on scrape)
1. Try a different Amazon product
2. Make sure URL contains `/dp/` or `/gp/product/`
3. Wait a minute and try again

### Email not sending (development)
Emails are logged to terminal console:
1. Check terminal running Django server
2. Look for "Console email output"
3. If not there, check form submission succeeded

### Static files (CSS) not loading
```bash
python manage.py collectstatic --noinput
```

## 📝 Next Steps

1. ✅ Test scraping with 2-3 products
2. ✅ Create price alerts
3. ✅ Check that prices display correctly
4. ✅ For production: Configure SMTP email
5. ✅ For production: Switch to PostgreSQL database

## 🎉 You're All Set!

Your Amazon Price Tracker is ready to use. Enjoy tracking prices and getting alerts!

---

**Need Help?**
- Check `FULLSTACK_README.md` for detailed documentation
- Check `API_USAGE_FRONTEND.md` for API details
- Review Django logs for error messages
