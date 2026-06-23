from typing import List
from datetime import datetime

from sqlalchemy import Column, DateTime, ForeignKey, Integer, String, func
from sqlalchemy.orm import (
    DeclarativeBase,
    Mapped,
    declared_attr,
    mapped_column,
    relationship,
)


class Base(DeclarativeBase):
    __abstract__ = True

    @declared_attr.directive
    def __tablename__(cls) -> str:
        return cls.__name__.lower()


class GroupUser(Base):
    __tablename__ = "group_users"

    group_id: Mapped[int] = mapped_column(
        ForeignKey("groups.t_chat_id"),
        primary_key=True,
    )

    user_id: Mapped[int] = mapped_column(
        ForeignKey("users.t_user_id"),
        primary_key=True,
    )

    group: Mapped["Groups"] = relationship(back_populates="users")

    user: Mapped["Users"] = relationship(back_populates="groups")


class Users(Base):
    t_user_id: Mapped[int] = mapped_column(unique=True, primary_key=True)
    t_user_name: Mapped[str | None]
    t_user_fullname: Mapped[str]

    repitation: Mapped[float] = mapped_column(default=10.0)

    groups: Mapped[List["GroupUser"]] = relationship(
        back_populates="user", cascade="all, delete-orphan"
    )


class Groups(Base):
    t_chat_id: Mapped[int] = mapped_column(unique=True, primary_key=True)

    users: Mapped[List["GroupUser"]] = relationship(
        back_populates="group", cascade="all, delete-orphan"
    )


class Admins(Base):
    t_user_id: Mapped[int] = mapped_column(unique=True, primary_key=True)


class RepitationActions(Base):
    __tablename__ = "repitation_actions"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    t_chat_id: Mapped[int] = mapped_column(index=True)
    t_user_id: Mapped[int] = mapped_column(index=True)
    action: Mapped[str]
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), nullable=False, server_default=func.now(), index=True
    )
