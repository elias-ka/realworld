from sqlalchemy import CheckConstraint, DateTime, ForeignKey, Uuid, func
from sqlalchemy.orm import mapped_column

from realworld.database.core import Base


class Follow(Base):
    __tablename__ = "follow"
    __table_args__ = (
        CheckConstraint(
            "followed_user_id != following_user_id",
            name="ck_user_cannot_follow_self",
        ),
    )
    # Having the following_user_id and followed_user_id as primary keys is fine
    # because it's a one-to-one relationship.
    following_user_id = mapped_column(
        Uuid,
        ForeignKey("user.id", ondelete="CASCADE", name="fk_following_user_id"),
        nullable=False,
        primary_key=True,
    )
    followed_user_id = mapped_column(
        Uuid,
        ForeignKey("user.id", ondelete="CASCADE", name="fk_followed_user_id"),
        nullable=False,
        primary_key=True,
    )
    created_at = mapped_column(DateTime(timezone=True), nullable=False, server_default=func.now())
    # updated_at isn't needed but it's here for consistency
    updated_at = mapped_column(DateTime(timezone=True), nullable=True, onupdate=func.now())
