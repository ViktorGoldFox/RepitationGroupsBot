from typing import List

from sqlalchemy import Column, ForeignKey, Integer, String
from sqlalchemy.orm import (
    DeclarativeBase,
    Mapped,
    declared_attr,
    mapped_column,
    relationship,
    relationships,
)


class Base(DeclarativeBase):
    __abstract__ = True

    @declared_attr.directive
    def __tablename__(cls) -> str:
        return cls.__name__.lower()


class GroupUser(Base):
    __tablename__ = "group_users"

    group_id: Mapped[int] = mapped_column(
        ForeignKey("groups.id"),
        primary_key=True,
    )

    user_id: Mapped[int] = mapped_column(
        ForeignKey("users.id"),
        primary_key=True,
    )

    group: Mapped["Groups"] = relationship(back_populates="members")

    user: Mapped["Users"] = relationship(back_populates="groups")


class Users(Base):
    t_user_id: Mapped[int] = mapped_column(unique=True, primary_key=True)
    t_user_name: Mapped[str]

    groups: Mapped[List["GroupUser"]] = relationship(
        back_populates="user", cascase="all, delete-orphan"
    )


class Groups(Base):
    t_chat_id: Mapped[int] = mapped_column(unique=True, primary_key=True)

    users: Mapped[List["GroupUser"]] = relationship(
        back_populates="group", cascade="all, delete-orphan"
    )


class Admins(Base):
    t_user_id: Mapped[int] = mapped_column(unique=True, primary_key=True)
