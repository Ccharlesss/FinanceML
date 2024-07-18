from fastapi import BackgroundTasks
from src.Configuration.settings import get_settings
from src.Models.UserModel import User
from src.Configuration.email import send_email
from src.Context.EmailContext import  USER_VERIFY_ACCOUNT
from src.Configuration.security import hash_password
# from src.Configuration.email import render_email_template




settings = get_settings()


# Purpose: Send an account verification email:
async def send_account_verification_email(user: User, background_tasks: BackgroundTasks):
    # 1) Generate a context string for account verification: context string uses User's password
    string_context = user.get_context_string(context=USER_VERIFY_ACCOUNT)
    # 2) Hashes the context string to create a token:
    # 2) token that will be sent to the user via email for verification.
    token = hash_password(string_context)
    # 3) Construct the account activation URL using the token and user's email:
    # 3) The token is included in the verification email sent to the user. 
    # activate_url = f"{settings.FRONTEND_HOST}/auth/account-verify?token={token}&email={user.email}"
    activate_url = f"{settings.FRONTEND_HOST}/account-verify?token={token}&email={user.email}"
    # 4) Data that will be sent in the verification email: app_name, username and activation link:
    data = {
        'app_name': settings.APP_NAME,
        "name": user.username,
        'activate_url': activate_url
    }
    # 5) Set the subject of the email:
    subject = f"Account Verification - {settings.APP_NAME}"
    # 6) Send the verification email to the newly created user:
    await send_email(
        recipients=[user.email],
        subject=subject,
        template_name="email/account-verification.html",
        context=data,
        background_tasks=background_tasks
    )






# Purpose: Send an account activation confirmation email when user clicks on verification link:
async def send_account_activation_confirmation_email(user: User, background_tasks: BackgroundTasks):
    # 1) set app name, username and frontend host:
    data = {
        'app_name': settings.APP_NAME,
        "name": user.username,
        'login_url': f'{settings.FRONTEND_HOST}'
    }
    # 2) Set the subject of the email:
    subject = f"Welcome - {settings.APP_NAME}"
    # 3) Send the mail to the newly created user that is now active:
    await send_email(
        recipients=[user.email],
        subject=subject,
        template_name="/email/account-verification-confirmation.html",
        context=data,
        background_tasks=background_tasks
    )
    

