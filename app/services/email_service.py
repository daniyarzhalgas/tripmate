import aiosmtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from typing import Literal, Optional
import logging
from pathlib import Path

from app.core.config import config

logger = logging.getLogger(__name__)

# Type for supported languages
Language = Literal["kk", "ru", "en"]

# Email templates directory
TEMPLATES_DIR = Path(__file__).parent.parent / "templates" / "email"


class EmailService:
    """Service for sending multilingual emails asynchronously."""

    def __init__(self):
        self.smtp_host = config.MAIL_SERVER
        self.smtp_port = config.MAIL_PORT
        self.username = config.MAIL_USERNAME
        self.password = config.MAIL_PASSWORD
        self.from_email = config.MAIL_FROM or config.MAIL_USERNAME
        self.app_name = config.APPLICATION_NAME

    def _load_template(self, template_name: str, language: Language) -> str:
        
        template_file = TEMPLATES_DIR / f"{template_name}_{language}.html"
        try:
            with open(template_file, "r", encoding="utf-8") as f:
                return f.read()
        except FileNotFoundError:
            logger.error(f"Template not found: {template_file}")
            # Fallback to English if template not found
            if language != "en":
                return self._load_template(template_name, "en")
            raise

    def _get_plain_text_content(
        self, template_type: str, language: Language, **kwargs
    ) -> str:
        translations = {
            "verification": {
                "kk": {
                    "welcome": "{app_name}-ке қош келдіңіз!",
                    "thanks": "Тіркелгеніңіз үшін рахмет. Төмендегі кодты пайдаланып электрондық поштаңызды растаңыз:",
                    "expires": "Бұл код 60 минуттан кейін жарамсыз болады.",
                    "ignore": "Егер сіз {app_name} жүйесінде тіркелмеген болсаңыз, бұл хатты елемеңіз.",
                },
                "ru": {
                    "welcome": "Добро пожаловать в {app_name}!",
                    "thanks": "Спасибо за регистрацию. Пожалуйста, подтвердите свой адрес электронной почты, используя код ниже:",
                    "expires": "Этот код истекает через 60 минут.",
                    "ignore": "Если вы не создавали учетную запись в {app_name}, просто проигнорируйте это письмо.",
                },
                "en": {
                    "welcome": "Welcome to {app_name}!",
                    "thanks": "Thank you for registering. Please verify your email address using this code:",
                    "expires": "This code will expire in 60 minutes.",
                    "ignore": "If you didn't create an account with {app_name}, please ignore this email.",
                },
            },
            "password_reset": {
                "kk": {
                    "title": "Құпия сөзді қалпына келтіру сұрауы",
                    "body": "Біз құпия сөзді қалпына келтіру сұрауын алдық.",
                    "link": "Құпия сөзді қалпына келтіру үшін осы сілтемені басыңыз:",
                    "expires": "Бұл сілтеме 1 сағаттан кейін жарамсыз болады.",
                    "ignore": "Егер сіз құпия сөзді қалпына келтіруді сұрамаған болсаңыз, бұл хатты елемеңіз.",
                },
                "ru": {
                    "title": "Запрос на сброс пароля",
                    "body": "Мы получили запрос на сброс вашего пароля.",
                    "link": "Нажмите на эту ссылку, чтобы сбросить пароль:",
                    "expires": "Эта ссылка истекает через 1 час.",
                    "ignore": "Если вы не запрашивали сброс пароля, просто проигнорируйте это письмо.",
                },
                "en": {
                    "title": "Password Reset Request",
                    "body": "We received a request to reset your password.",
                    "link": "Click this link to reset your password:",
                    "expires": "This link will expire in 1 hour.",
                    "ignore": "If you didn't request a password reset, please ignore this email.",
                },
            },
            "welcome": {
                "kk": {
                    "title": "🎉 {app_name}-ке қош келдіңіз!",
                    "verified": "Электрондық поштаңыз сәтті расталды!",
                    "enjoy": "Енді сіз {app_name} қосымшасының барлық мүмкіндіктерін пайдалана аласыз.",
                    "support": "Егер сұрақтарыңыз болса, біздің қолдау тобына хабарласыңыз.",
                    "travels": "Саяхаттарыңыз сәтті болсын!",
                },
                "ru": {
                    "title": "🎉 Добро пожаловать в {app_name}!",
                    "verified": "Ваш email был успешно подтвержден!",
                    "enjoy": "Теперь вы можете пользоваться всеми функциями {app_name}.",
                    "support": "Если у вас есть вопросы, обращайтесь в нашу службу поддержки.",
                    "travels": "Счастливых путешествий!",
                },
                "en": {
                    "title": "🎉 Welcome to {app_name}!",
                    "verified": "Your email has been verified successfully!",
                    "enjoy": "You can now enjoy all the features of {app_name}.",
                    "support": "If you have any questions, feel free to reach out to our support team.",
                    "travels": "Happy travels!",
                },
            },
        }

        texts = translations.get(template_type, {}).get(
            language, translations[template_type]["en"]
        )

        if template_type == "verification":
            return f"""
{texts['welcome'].format(app_name=kwargs['app_name'])}

{texts['thanks'].format(app_name=kwargs['app_name'])}

{kwargs['verification_code']}

{texts['expires']}

{texts['ignore'].format(app_name=kwargs['app_name'])}
"""
        elif template_type == "password_reset":
            return f"""
{texts['title']}

{texts['body']}

{texts['link']}
{kwargs['reset_url']}

{texts['expires']}

{texts['ignore']}
"""
        elif template_type == "welcome":
            greeting = (
                f" {kwargs.get('user_name', '')}" if kwargs.get("user_name") else ""
            )
            return f"""
{texts['title'].format(app_name=kwargs['app_name'])}

{texts['verified']}

{texts['enjoy'].format(app_name=kwargs['app_name'])}

{texts['support']}

{texts['travels']}
"""

        return ""

    async def send_email(
        self,
        to_email: str,
        subject: str,
        html_content: str,
        plain_content: Optional[str] = None,
    ) -> bool:
        try:
            message = MIMEMultipart("alternative")
            message["From"] = self.from_email
            message["To"] = to_email
            message["Subject"] = subject

            # Add plain text version if provided
            if plain_content:
                part1 = MIMEText(plain_content, "plain")
                message.attach(part1)

            # Add HTML version
            part2 = MIMEText(html_content, "html")
            message.attach(part2)

            # Send email
            await aiosmtplib.send(
                message,
                hostname=self.smtp_host,
                port=self.smtp_port,
                username=self.username,
                password=self.password,
                start_tls=True,
            )

            logger.info(f"Email sent successfully to {to_email}")
            return True

        except Exception as e:
            logger.error(f"Failed to send email to {to_email}: {str(e)}")
            return False

    async def send_verification_email(
        self,
        to_email: str,
        verification_code: str,
        user_id: int,
        language: Language = "kk",
    ) -> bool:
        # Always use English subject
        subject = f"{self.app_name} - Verify Your Email"

        # Create minimal multilingual content - Order: KZ, EN, RU
        template_kk = self._load_template("verification", "kk")
        template_en = self._load_template("verification", "en")
        template_ru = self._load_template("verification", "ru")

        html_content = f"""
        <!DOCTYPE html>
        <html>
        <head>
            <meta charset="UTF-8">
        </head>
        <body style="font-family: Arial, sans-serif; max-width: 600px; margin: 0 auto; padding: 20px;">
            <div style="text-align: center; margin-bottom: 30px;">
                <h1 style="color: #333;">{self.app_name}</h1>
            </div>
            {template_kk.format(app_name=self.app_name, verification_code=verification_code)}
            <hr style="margin: 20px 0; border: none; border-top: 1px solid #ddd;">
            {template_en.format(app_name=self.app_name, verification_code=verification_code)}
            <hr style="margin: 20px 0; border: none; border-top: 1px solid #ddd;">
            {template_ru.format(app_name=self.app_name, verification_code=verification_code)}
        </body>
        </html>
        """

        # Create multilingual plain text content - Order: KZ, EN, RU
        plain_kk = self._get_plain_text_content(
            "verification",
            "kk",
            app_name=self.app_name,
            verification_code=verification_code,
        )
        plain_en = self._get_plain_text_content(
            "verification",
            "en",
            app_name=self.app_name,
            verification_code=verification_code,
        )
        plain_ru = self._get_plain_text_content(
            "verification",
            "ru",
            app_name=self.app_name,
            verification_code=verification_code,
        )

        plain_content = (
            f"{plain_kk}\n\n{'='*50}\n\n{plain_en}\n\n{'='*50}\n\n{plain_ru}"
        )

        print(f"Sending verification email to {to_email} with code {verification_code}")
        return True
        # return await self.send_email(to_email, subject, html_content, plain_content)

    async def send_password_reset_email(
        self, to_email: str, reset_token: str, language: Language = "kk"
    ) -> bool:
        # Always use English subject
        subject = f"{self.app_name} - Password Reset"

        reset_url = f"{config.FRONTEND_URL_RESET}/reset-password?token={reset_token}"

        # Create minimal multilingual content - Order: KZ, EN, RU
        template_kk = self._load_template("password_reset", "kk")
        template_en = self._load_template("password_reset", "en")
        template_ru = self._load_template("password_reset", "ru")

        html_content = f"""
        <!DOCTYPE html>
        <html>
        <head>
            <meta charset="UTF-8">
        </head>
        <body style="font-family: Arial, sans-serif; max-width: 600px; margin: 0 auto; padding: 20px;">
            <div style="text-align: center; margin-bottom: 30px;">
                <h1 style="color: #333;">{self.app_name}</h1>
            </div>
            {template_kk.format(app_name=self.app_name, reset_url=reset_url)}
            <hr style="margin: 20px 0; border: none; border-top: 1px solid #ddd;">
            {template_en.format(app_name=self.app_name, reset_url=reset_url)}
            <hr style="margin: 20px 0; border: none; border-top: 1px solid #ddd;">
            {template_ru.format(app_name=self.app_name, reset_url=reset_url)}
        </body>
        </html>
        """

        # Create multilingual plain text content - Order: KZ, EN, RU
        plain_kk = self._get_plain_text_content(
            "password_reset", "kk", app_name=self.app_name, reset_url=reset_url
        )
        plain_en = self._get_plain_text_content(
            "password_reset", "en", app_name=self.app_name, reset_url=reset_url
        )
        plain_ru = self._get_plain_text_content(
            "password_reset", "ru", app_name=self.app_name, reset_url=reset_url
        )

        plain_content = (
            f"{plain_kk}\n\n{'='*50}\n\n{plain_en}\n\n{'='*50}\n\n{plain_ru}"
        )

        print(f"Sending password reset email to {to_email}")
        print(f"Reset URL: {reset_url}")
        return True
        # return await self.send_email(to_email, subject, html_content, plain_content)

    async def send_welcome_email(
        self, to_email: str, user_name: str = "", language: Language = "kk"
    ) -> bool:
        subject = f"Welcome to {self.app_name}!"

        greeting = f" {user_name}" if user_name else ""

        # Create minimal multilingual content - Order: KZ, EN, RU
        template_kk = self._load_template("welcome", "kk")
        template_en = self._load_template("welcome", "en")
        template_ru = self._load_template("welcome", "ru")

        html_content = f"""
        <!DOCTYPE html>
        <html>
        <head>
            <meta charset="UTF-8">
        </head>
        <body style="font-family: Arial, sans-serif; max-width: 600px; margin: 0 auto; padding: 20px;">
            <div style="text-align: center; margin-bottom: 30px;">
                <h1 style="color: #333;">{self.app_name}</h1>
            </div>
            {template_kk.format(app_name=self.app_name, greeting=greeting)}
            <hr style="margin: 20px 0; border: none; border-top: 1px solid #ddd;">
            {template_en.format(app_name=self.app_name, greeting=greeting)}
            <hr style="margin: 20px 0; border: none; border-top: 1px solid #ddd;">
            {template_ru.format(app_name=self.app_name, greeting=greeting)}
        </body>
        </html>
        """

        # Create multilingual plain text content - Order: KZ, EN, RU
        plain_kk = self._get_plain_text_content(
            "welcome", "kk", app_name=self.app_name, user_name=user_name
        )
        plain_en = self._get_plain_text_content(
            "welcome", "en", app_name=self.app_name, user_name=user_name
        )
        plain_ru = self._get_plain_text_content(
            "welcome", "ru", app_name=self.app_name, user_name=user_name
        )

        plain_content = (
            f"{plain_kk}\n\n{'='*50}\n\n{plain_en}\n\n{'='*50}\n\n{plain_ru}"
        )

        print(f"Sending welcome email to {to_email}")
        return True
        # return await self.send_email(to_email, subject, html_content, plain_content)


# Singleton instance
email_service = EmailService()
