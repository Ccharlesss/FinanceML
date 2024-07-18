
import logging
import os
from pathlib import Path
from typing import List
# Library used to handle background tasks:
from fastapi import BackgroundTasks
# ConnectionConfig: Used for email server configuration
# FastMail: Used for handling sending emails
# MessageSchema: Defines the structure of email messages
# MessageType: Specifies the type of email content
from fastapi_mail import ConnectionConfig, FastMail, MessageSchema, MessageType
from jinja2 import FileSystemLoader
from pydantic import BaseModel, EmailStr
# Imports from Configuration:
from src.Configuration.settings import get_settings


# Get settings instance from src/Configuration/settings.py:
settings = get_settings()

# Define the structure for the input data: Email field is a lost of valid email addresses:
# class EmailSchema(BaseModel):
#     email: List[EmailStr]



conf = ConnectionConfig(
    MAIL_USERNAME=os.environ.get("MAIL_USERNAME", ""),
    MAIL_PASSWORD=os.environ.get("MAIL_PASSWORD", ""),
    MAIL_PORT=os.environ.get("MAIL_PORT", 587),
    MAIL_SERVER=os.environ.get("MAIL_SERVER", "smtp"),
    # MAIL_STARTTLS=os.environ.get("MAIL_STARTTLS", True),#was false
    # MAIL_SSL_TLS=os.environ.get("MAIL_SSL_TLS", True), #was false
    MAIL_STARTTLS=os.environ.get("MAIL_STARTTLS", "true").lower() in ("true", "yes", "1"),  # Adjusted to handle boolean from string
    MAIL_SSL_TLS=os.environ.get("MAIL_SSL_TLS", "false").lower() in ("true", "yes", "1"),  # Adjusted to handle boolean from string
    MAIL_DEBUG=True,
    MAIL_FROM=os.environ.get("MAIL_FROM", 'noreply@test.com'),
    MAIL_FROM_NAME=os.environ.get("MAIL_FROM_NAME", settings.APP_NAME),
    TEMPLATE_FOLDER=Path(__file__).parent.parent / "Template",
    USE_CREDENTIALS=os.environ.get("USE_CREDENTIALS", "true").lower() in ("true", "yes", "1"),  # Adjusted to handle boolean from string
    # USE_CREDENTIALS=os.environ.get("USE_CREDENTIALS", True)
)



# # Initializes a FastMail instance and will handle sending emails based on the settings stored in conf:
fm = FastMail(conf)



async def send_email(recipients: list, subject: str, context: dict, template_name: str,
                     background_tasks: BackgroundTasks):
    # Define the structure of the email message (subject, recipients, body, and context)
    message = MessageSchema(
        subject=subject,
        recipients=recipients,
        template_body=context,
        subtype=MessageType.html
    )
    try:
        # Add a task to send an email using fm.send_message method
        background_tasks.add_task(fm.send_message, message, template_name=template_name)
        logging.info(f"Email queued to be sent to: {recipients}")
    except Exception as e:
        logging.error(f"Failed to send email to {recipients}: {e}")





# Initializes the email server by pulling configuration values from settings insttance:
# conf = ConnectionConfig(
#     MAIL_USERNAME=settings.MAIL_USERNAME,
#     MAIL_PASSWORD=settings.MAIL_PASSWORD,
#     MAIL_FROM=settings.MAIL_FROM,
#     MAIL_PORT=settings.MAIL_PORT,
#     MAIL_SERVER=settings.MAIL_SERVER,
#     MAIL_FROM_NAME=settings.MAIL_FROM_NAME,
#     # keep this commented
#     #MAIL_STARTTLS=settings.MAIL_STARTTLS,
#     #MAIL_SSL=settings.MAIL_SSL_TLS,  # Corrected to MAIL_SSL_TLS based on your actual setting
#     USE_CREDENTIALS=settings.MAIL_USE_CREDENTIALS,
#     VALIDATE_CERTS=settings.MAIL_VALIDATE_CERTS
# )


# async def send_email_async(subject: str, email_to: str, body: dict):
#     message = MessageSchema(
#         subject=subject,
#         recipients=[email_to],
#         body=body,
#         subtype='html',
#     )
    
#     fm = FastMail(conf)
#     await fm.send_message(message, template_name='account-verification.html')

# def send_email_background(background_tasks: BackgroundTasks, subject: str, email_to: str, body: dict):
#     message = MessageSchema(
#         subject=subject,
#         recipients=[email_to],
#         body=body,
#         subtype='html',
#     )
#     fm = FastMail(conf)
#     background_tasks.add_task(
#        fm.send_message, message, template_name='email.html')




# Function to send email asynchronously with background tasks
# recipients: List of email addresses to send email to
# subject: subject of the email
# Context: Dictionary containing email content (HTML body)
# template_name:  Name of the email template
# background_tasks: Parameter to add tasks that should run in the background
# async def send_email(recipients: list, subject: str, context: dict, template_name: str,
#                      background_tasks: BackgroundTasks):
#     # MessageSchema: Defines the structure of the email message (subject, recipient, body and context)
#     message = MessageSchema(
#         subject=subject,
#         recipients=recipients,
#         template_body=context,
#         # Specifies that the email content is in HTML format
#         subtype=MessageType.html
#     )
#     # Adds a task to send an email using fm.send_message method:
#     background_tasks.add_task(fm.send_message, message, template_name=template_name)
