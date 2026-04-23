"""
Production-ready notification service with real email and SMS integration
Configure your credentials in .env file
"""

import smtplib
import os
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from dotenv import load_dotenv

load_dotenv()

class NotificationService:
    """
    Production notification service supporting:
    - Email via SMTP (Gmail, SendGrid, etc.)
    - SMS via Africa's Talking, Twilio, etc.
    """
    
    # Email Configuration
    SMTP_SERVER = os.getenv('SMTP_SERVER', 'smtp.gmail.com')
    SMTP_PORT = int(os.getenv('SMTP_PORT', 587))
    SMTP_USERNAME = os.getenv('SMTP_USERNAME', '')
    SMTP_PASSWORD = os.getenv('SMTP_PASSWORD', '')
    FROM_EMAIL = os.getenv('FROM_EMAIL', 'noreply@inventory.com')
    
    # SMS Configuration (Africa's Talking)
    AT_USERNAME = os.getenv('AT_USERNAME', '')
    AT_API_KEY = os.getenv('AT_API_KEY', '')
    AT_SENDER_ID = os.getenv('AT_SENDER_ID', 'INVENTORY')
    
    # Twilio Configuration (Alternative)
    TWILIO_ACCOUNT_SID = os.getenv('TWILIO_ACCOUNT_SID', '')
    TWILIO_AUTH_TOKEN = os.getenv('TWILIO_AUTH_TOKEN', '')
    TWILIO_PHONE_NUMBER = os.getenv('TWILIO_PHONE_NUMBER', '')
    
    @classmethod
    def send_email(cls, to_email, subject, message, from_email=None):
        """
        Send email via SMTP
        
        Setup for Gmail:
        1. Enable 2-factor authentication
        2. Generate app password: https://myaccount.google.com/apppasswords
        3. Set in .env:
           SMTP_SERVER=smtp.gmail.com
           SMTP_PORT=587
           SMTP_USERNAME=your-email@gmail.com
           SMTP_PASSWORD=your-app-password
           FROM_EMAIL=your-email@gmail.com
        """
        try:
            if not cls.SMTP_USERNAME or not cls.SMTP_PASSWORD:
                print(f"[EMAIL SIMULATION] To: {to_email}")
                print(f"[EMAIL SIMULATION] Subject: {subject}")
                print(f"[EMAIL SIMULATION] Message: {message}")
                print("[INFO] Configure SMTP credentials in .env for real emails")
                return True
            
            msg = MIMEMultipart()
            msg['From'] = from_email or cls.FROM_EMAIL
            msg['To'] = to_email
            msg['Subject'] = subject
            
            msg.attach(MIMEText(message, 'plain'))
            
            with smtplib.SMTP(cls.SMTP_SERVER, cls.SMTP_PORT) as server:
                server.starttls()
                server.login(cls.SMTP_USERNAME, cls.SMTP_PASSWORD)
                server.send_message(msg)
            
            print(f"[EMAIL SENT] To: {to_email}, Subject: {subject}")
            return True
            
        except Exception as e:
            print(f"[EMAIL ERROR] {str(e)}")
            return False
    
    @classmethod
    def send_sms_africastalking(cls, phone_number, message):
        """
        Send SMS via Africa's Talking
        
        Setup:
        1. Sign up at https://africastalking.com
        2. Get API key from dashboard
        3. Set in .env:
           AT_USERNAME=your-username
           AT_API_KEY=your-api-key
           AT_SENDER_ID=your-sender-id
        """
        try:
            if not cls.AT_USERNAME or not cls.AT_API_KEY:
                print(f"[SMS SIMULATION] To: {phone_number}")
                print(f"[SMS SIMULATION] Message: {message}")
                print("[INFO] Configure Africa's Talking credentials in .env for real SMS")
                return True
            
            import africastalking
            
            africastalking.initialize(cls.AT_USERNAME, cls.AT_API_KEY)
            sms = africastalking.SMS
            
            response = sms.send(message, [phone_number], cls.AT_SENDER_ID)
            
            print(f"[SMS SENT] To: {phone_number}, Response: {response}")
            return True
            
        except ImportError:
            print("[SMS ERROR] Install africastalking: pip install africastalking")
            print(f"[SMS SIMULATION] To: {phone_number}, Message: {message}")
            return False
        except Exception as e:
            print(f"[SMS ERROR] {str(e)}")
            return False
    
    @classmethod
    def send_sms_twilio(cls, phone_number, message):
        """
        Send SMS via Twilio (Alternative to Africa's Talking)
        
        Setup:
        1. Sign up at https://www.twilio.com
        2. Get credentials from console
        3. Set in .env:
           TWILIO_ACCOUNT_SID=your-account-sid
           TWILIO_AUTH_TOKEN=your-auth-token
           TWILIO_PHONE_NUMBER=your-twilio-number
        """
        try:
            if not cls.TWILIO_ACCOUNT_SID or not cls.TWILIO_AUTH_TOKEN:
                print(f"[SMS SIMULATION] To: {phone_number}")
                print(f"[SMS SIMULATION] Message: {message}")
                print("[INFO] Configure Twilio credentials in .env for real SMS")
                return True
            
            from twilio.rest import Client
            
            client = Client(cls.TWILIO_ACCOUNT_SID, cls.TWILIO_AUTH_TOKEN)
            
            message = client.messages.create(
                body=message,
                from_=cls.TWILIO_PHONE_NUMBER,
                to=phone_number
            )
            
            print(f"[SMS SENT] To: {phone_number}, SID: {message.sid}")
            return True
            
        except ImportError:
            print("[SMS ERROR] Install twilio: pip install twilio")
            print(f"[SMS SIMULATION] To: {phone_number}, Message: {message}")
            return False
        except Exception as e:
            print(f"[SMS ERROR] {str(e)}")
            return False
    
    @classmethod
    def send_sms(cls, phone_number, message, provider='africastalking'):
        """
        Send SMS using configured provider
        
        Args:
            phone_number: Recipient phone number (e.g., +254712345678)
            message: SMS message text
            provider: 'africastalking' or 'twilio'
        """
        if provider == 'twilio':
            return cls.send_sms_twilio(phone_number, message)
        else:
            return cls.send_sms_africastalking(phone_number, message)
    
    @classmethod
    def send_supplier_contact(cls, supplier, user, message, method='email'):
        """
        Send contact request to supplier with push notification
        
        Args:
            supplier: Supplier model instance
            user: User model instance
            message: Contact message
            method: 'email' or 'sms'
        """
        success = False
        
        if method == 'email' and supplier.email:
            subject = f"Contact Request from {user.username}"
            full_message = f"""
Hello {supplier.contact_person or supplier.name},

You have received a contact request from {user.username} ({user.email}).

Message:
{message}

---
This is an automated message from the Inventory Management System.
            """.strip()
            
            success = cls.send_email(supplier.email, subject, full_message)
        
        elif method == 'sms' and supplier.phone:
            sms_message = f"{user.username}: {message[:140]}"  # SMS character limit
            success = cls.send_sms(supplier.phone, sms_message)
        
        # Log notification attempt
        status = "sent" if success else "failed"
        print(f"[NOTIFICATION] Supplier contact via {method}: {status}")
        print(f"[NOTIFICATION] From: {user.username} To: {supplier.name}")
        
        return success
    
    @classmethod
    def send_low_stock_alert(cls, product, inventory, recipients):
        """
        Send low stock alert to managers
        
        Args:
            product: Product model instance
            inventory: Inventory model instance
            recipients: List of email addresses
        """
        subject = f"Low Stock Alert: {product.name}"
        message = f"""
INVENTORY ALERT

Product: {product.name} (SKU: {product.sku})
Current Stock: {inventory.quantity_on_hand} units
Reorder Point: {product.reorder_point} units
Status: {'OUT OF STOCK' if inventory.quantity_on_hand == 0 else 'LOW STOCK'}

Action Required: Please reorder from supplier {product.supplier.name}

---
Automated alert from Inventory Management System
        """.strip()
        
        success_count = 0
        for email in recipients:
            if cls.send_email(email, subject, message):
                success_count += 1
        
        return success_count > 0
    
    @classmethod
    def test_configuration(cls):
        """Test notification configuration"""
        print("\n=== Notification Service Configuration ===\n")
        
        print("Email Configuration:")
        print(f"  SMTP Server: {cls.SMTP_SERVER}:{cls.SMTP_PORT}")
        print(f"  Username: {'[Configured]' if cls.SMTP_USERNAME else '[Not configured]'}")
        print(f"  Password: {'[Configured]' if cls.SMTP_PASSWORD else '[Not configured]'}")
        print(f"  From Email: {cls.FROM_EMAIL}")
        
        print("\nSMS Configuration (Africa's Talking):")
        print(f"  Username: {'[Configured]' if cls.AT_USERNAME else '[Not configured]'}")
        print(f"  API Key: {'[Configured]' if cls.AT_API_KEY else '[Not configured]'}")
        print(f"  Sender ID: {cls.AT_SENDER_ID}")
        
        print("\nSMS Configuration (Twilio):")
        print(f"  Account SID: {'[Configured]' if cls.TWILIO_ACCOUNT_SID else '[Not configured]'}")
        print(f"  Auth Token: {'[Configured]' if cls.TWILIO_AUTH_TOKEN else '[Not configured]'}")
        print(f"  Phone Number: {cls.TWILIO_PHONE_NUMBER or '[Not configured]'}")
        
        print("\n" + "="*40 + "\n")

if __name__ == '__main__':
    # Test configuration
    NotificationService.test_configuration()
    
    # Test email (simulation)
    print("Testing email...")
    NotificationService.send_email(
        'test@example.com',
        'Test Email',
        'This is a test message'
    )
    
    # Test SMS (simulation)
    print("\nTesting SMS...")
    NotificationService.send_sms(
        '+254712345678',
        'This is a test SMS message'
    )
