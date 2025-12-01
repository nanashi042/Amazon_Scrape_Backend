#!/bin/bash
# Complete workflow example for Amazon Price Tracker API

API_URL="http://127.0.0.1:8000/api"

echo "=== Amazon Price Tracker - Complete Workflow Example ==="
echo ""

# Step 1: Scrape a Product
echo "STEP 1: Scraping Amazon Product..."
echo "==========================================="
PRODUCT_RESPONSE=$(curl -s -X POST "$API_URL/products/scrape/" \
  -H "Content-Type: application/json" \
  -d '{
    "url": "https://www.amazon.com/s?k=laptop"
  }')

echo "Response:"
echo "$PRODUCT_RESPONSE" | python -m json.tool 2>/dev/null || echo "$PRODUCT_RESPONSE"
echo ""

# Extract product ID from response
PRODUCT_ID=$(echo "$PRODUCT_RESPONSE" | python -c "import sys, json; data=json.load(sys.stdin); print(data.get('id', ''))" 2>/dev/null)

if [ -z "$PRODUCT_ID" ]; then
  echo "❌ Failed to scrape product. Check URL and try again."
  exit 1
fi

echo "✓ Product ID: $PRODUCT_ID"
echo ""

# Step 2: Create Price Tracker
echo "STEP 2: Creating Price Tracker..."
echo "==========================================="
TRACKER_RESPONSE=$(curl -s -X POST "$API_URL/trackers/" \
  -H "Content-Type: application/json" \
  -d "{
    \"product_id\": $PRODUCT_ID,
    \"user_email\": \"user@example.com\",
    \"target_price\": 25.50
  }")

echo "Response:"
echo "$TRACKER_RESPONSE" | python -m json.tool 2>/dev/null || echo "$TRACKER_RESPONSE"
echo ""

TRACKER_ID=$(echo "$TRACKER_RESPONSE" | python -c "import sys, json; data=json.load(sys.stdin); print(data.get('id', ''))" 2>/dev/null)
echo "✓ Tracker ID: $TRACKER_ID"
echo ""

# Step 3: List Products
echo "STEP 3: Listing All Products..."
echo "==========================================="
curl -s -X GET "$API_URL/products/" \
  -H "Content-Type: application/json" | python -m json.tool 2>/dev/null || echo "No products found"
echo ""

# Step 4: List Trackers
echo "STEP 4: Listing All Trackers..."
echo "==========================================="
curl -s -X GET "$API_URL/trackers/" \
  -H "Content-Type: application/json" | python -m json.tool 2>/dev/null || echo "No trackers found"
echo ""

# Step 5: Check Prices and Send Alerts
echo "STEP 5: Checking Prices and Sending Alerts..."
echo "==========================================="
CHECK_RESPONSE=$(curl -s -X POST "$API_URL/trackers/check-prices/" \
  -H "Content-Type: application/json")

echo "Response:"
echo "$CHECK_RESPONSE" | python -m json.tool 2>/dev/null || echo "$CHECK_RESPONSE"
echo ""

echo "=== Workflow Complete ==="
echo ""
echo "Next Steps:"
echo "1. Check your email (or console output in development) for price alerts"
echo "2. View products: GET $API_URL/products/"
echo "3. View trackers: GET $API_URL/trackers/"
echo "4. Update tracker: PATCH $API_URL/trackers/$TRACKER_ID/"
echo "5. Delete tracker: DELETE $API_URL/trackers/$TRACKER_ID/"
