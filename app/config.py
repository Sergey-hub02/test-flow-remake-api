from dynaconf import LazySettings
from pathlib import Path
from fastapi_mail import ConnectionConfig

settings = LazySettings(envvar_prefix=False, load_dotenv=True)

mail_settings = ConnectionConfig(
    MAIL_USERNAME=settings.MAIL_USERNAME,
    MAIL_PASSWORD=settings.MAIL_PASSWORD,
    MAIL_SERVER=settings.MAIL_SERVER,
    MAIL_PORT=settings.MAIL_PORT,
    MAIL_FROM=settings.MAIL_FROM,
    MAIL_SSL_TLS=False,
    MAIL_DEBUG=1,
    MAIL_STARTTLS=True,
    TEMPLATE_FOLDER=Path(__file__).parent.parent / "templates",
)
