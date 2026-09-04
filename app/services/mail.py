from fastapi_mail import MessageSchema, MessageType, NameEmail, FastMail
from pydantic import EmailStr
from urllib.parse import urlunparse

from app.config import settings


class MailService:
    __mail_client: FastMail

    def __init__(self, mail: FastMail):
        self.__mail_client = mail

    async def send_onetime_code(
        self, subject: str, email: EmailStr, onetime_code: str
    ) -> None:
        template_params = {
            "email": email,
            "reset_url": urlunparse(
                (
                    "http",
                    f"{settings.FRONT_HOST}:{settings.FRONT_PORT}",
                    "/auth/change_password",
                    "",
                    f"onetime_code={onetime_code}",
                    "",
                )
            ),
        }

        message = MessageSchema(
            subject=subject,
            recipients=[NameEmail("", email)],
            template_body=template_params,
            subtype=MessageType.html,
        )

        await self.__mail_client.send_message(
            message, template_name="onetime_code.html"
        )
