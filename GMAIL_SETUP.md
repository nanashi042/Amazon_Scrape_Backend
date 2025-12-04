# Gmail SMTP Setup - Authentication Error Solution

## Problem
```
Username and Password not accepted
https://support.google.com/mail/?p=BadCredentials
```

## Solutions

### Option 1: Use Gmail App Password (Recommended)

If your Gmail account has 2-Factor Authentication enabled:

1. Go to [Google Account Security](https://myaccount.google.com/security)
2. Enable 2-Step Verification (if not already enabled)
3. Generate App Password:
   - Go to [App passwords](https://myaccount.google.com/apppasswords)
   - Select "Mail" and "Windows Computer" (or your device)
   - Google will generate a 16-character password
4. Update `settings.py`:
   ```python
   EMAIL_HOST_PASSWORD = 'xxxx xxxx xxxx xxxx'  # 16-char app password
   ```

### Option 2: Enable Less Secure Apps

If your account doesn't have 2FA:

1. Go to [Less secure apps](https://myaccount.google.com/lesssecureapps)
2. Enable "Allow less secure apps"
3. Wait a few minutes for the change to take effect

### Option 3: Use Gmail App-Specific Password

1. Visit [Google Account](https://myaccount.google.com)
2. Security > 2-Step Verification > App passwords
3. Create a password specifically for this app
4. Use that 16-character password in settings.py

## Current Configuration

```python
# settings.py
EMAIL_BACKEND = 'django.core.mail.backends.smtp.EmailBackend'
EMAIL_HOST = 'smtp.gmail.com'
EMAIL_PORT = 587
EMAIL_USE_TLS = True
EMAIL_HOST_USER = 'nikhilkaito@gmail.com'
EMAIL_HOST_PASSWORD = '[PASTE APP PASSWORD HERE]'
DEFAULT_FROM_EMAIL = 'nikhilkaito@gmail.com'
```

## After Getting App Password

Replace the password in settings.py and test again:

```bash
python manage.py shell << 'EOF'
from Scraping_Event.email_service import send_price_alert_email
from Scraping_Event.models import AmazonProduct

product = AmazonProduct.objects.first()
success = send_price_alert_email("test@gmail.com", product)
print("Success!" if success else "Failed!")
EOF
```

## Security Notes

⚠️ **Important:**
- Never commit credentials to git
- Consider using environment variables for production:
  ```python
  import os
  EMAIL_HOST_PASSWORD = os.environ.get('EMAIL_PASSWORD')
  ```

## Testing the Connection

Once credentials are updated:

```bash
# Test SMTP connection
python manage.py shell << 'EOF'
from django.core.mail import get_connection
try:
    connection = get_connection()
    connection.open()
    print("✓ Connection successful!")
    connection.close()
except Exception as e:
    print(f"✗ Connection failed: {e}")
EOF
```

## Fallback: Use Console Backend

If SMTP setup doesn't work, revert to console backend for testing:

```python
EMAIL_BACKEND = 'django.core.mail.backends.console.EmailBackend'
```
