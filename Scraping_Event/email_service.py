from django.core.mail import send_mail
from django.conf import settings


def send_price_alert_email(user_email, product):
    """
    Send email notification when price drops to target
    """
    subject = f"Price Alert: {product.title}"
    
    message = f"""
    Good news! The price of the product you're tracking has dropped!

    Product: {product.title}
    Current Price: ${product.current_price}
    ASIN: {product.asin}
    Rating: {product.rating}/5 ({product.number_of_reviews} reviews)
    
    Link: {product.url}

    Check it out before the price goes back up!

    Best regards,
    Amazon Price Tracker
    """

    html_message = f"""
    <html>
        <body style="font-family: Arial, sans-serif;">
            <h2>Price Alert: {product.title}</h2>
            <p>Good news! The price of the product you're tracking has dropped!</p>
            
            <div style="border: 1px solid #ddd; padding: 15px; border-radius: 5px;">
                <p><strong>Product:</strong> {product.title}</p>
                <p><strong>Current Price:</strong> ${product.current_price}</p>
                <p><strong>ASIN:</strong> {product.asin}</p>
                <p><strong>Rating:</strong> {product.rating}/5 ({product.number_of_reviews} reviews)</p>
            </div>
            
            <p><a href="{product.url}" style="background-color: #FF9900; color: white; padding: 10px 20px; text-decoration: none; border-radius: 5px;">View Product</a></p>
            
            <p>Check it out before the price goes back up!</p>
            <hr>
            <p style="color: #666; font-size: 12px;">Amazon Price Tracker</p>
        </body>
    </html>
    """

    try:
        send_mail(
            subject,
            message,
            settings.DEFAULT_FROM_EMAIL,
            [user_email],
            html_message=html_message,
            fail_silently=False,
        )
        return True
    except Exception as e:
        print(f"Error sending email to {user_email}: {str(e)}")
        return False
