import uuid

from sqlalchemy import (
    UUID,
    text,
    func,
    String,
    Text,
    TIMESTAMP,
    Date,
    ForeignKey,
)
from sqlalchemy.orm import Mapped, mapped_column, relationship

from typing import Optional
from datetime import datetime, date

from app.db.conexion import Base


class Role(Base):
    __tablename__ = "role"

    id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        primary_key=True,
        default=uuid.uuid4,
        server_default=text("gen_random_uuid()"),
    )
    name: Mapped[str] = mapped_column(String(255))
    code: Mapped[str] = mapped_column(String(255), unique=True)
    description: Mapped[Optional[str]] = mapped_column(Text, default=None)
    users: Mapped[list[User]] = relationship(back_populates="role")
    created_at: Mapped[datetime] = mapped_column(
        TIMESTAMP,
        default=func.now(),
        server_default=func.now(),
    )
    updated_at: Mapped[datetime] = mapped_column(
        TIMESTAMP,
        default=func.now(),
        server_default=func.now(),
        onupdate=func.now(),
        server_onupdate=func.now(),
    )


class User(Base):
    __tablename__ = "user"

    id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        primary_key=True,
        default=uuid.uuid4,
        server_default=text("gen_random_uuid()"),
    )
    photo: Mapped[Optional[str]] = mapped_column(Text)
    last_name: Mapped[str] = mapped_column(String(255))
    first_name: Mapped[str] = mapped_column(String(255))
    second_name: Mapped[Optional[str]] = mapped_column(
        String(255), default=None
    )
    birthday: Mapped[date] = mapped_column(Date)
    email: Mapped[str] = mapped_column(String(255), unique=True)
    password: Mapped[str] = mapped_column(Text)
    role_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), ForeignKey("role.id")
    )
    role: Mapped[Role] = relationship(back_populates="users")
    created_at: Mapped[datetime] = mapped_column(
        TIMESTAMP,
        default=func.now(),
        server_default=func.now(),
    )
    updated_at: Mapped[datetime] = mapped_column(
        TIMESTAMP,
        default=func.now(),
        server_default=func.now(),
        onupdate=func.now(),
        server_onupdate=func.now(),
    )
