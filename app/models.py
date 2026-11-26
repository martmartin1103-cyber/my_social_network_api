import enum
from sqlalchemy import Column, Integer, String, Boolean, Enum, ForeignKey
from app.database import Base
from sqlalchemy import Column, Integer, String, Boolean, Enum, ForeignKey, DateTime

class User(Base):
    __tablename__ = "users"

    id = Column(Integer, primary_key=True, index=True)
    username = Column(String, unique=True, index=True, nullable=False)
    email = Column(String, unique=True, index=True, nullable=False)
    password_hash = Column(String, nullable=False)
    full_name = Column(String, nullable=True)
    bio = Column(String, nullable=True)


class GroupType(str, enum.Enum):
    public = "public"
    private = "private"
    secret = "secret"


class GroupRole(str, enum.Enum):
    admin = "admin"
    member = "member"


class Group(Base):
    __tablename__ = "groups"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, index=True, nullable=False)
    description = Column(String, nullable=True)
    icon_url = Column(String, nullable=True)
    cover_photo_url = Column(String, nullable=True)
    group_type = Column(Enum(GroupType), default=GroupType.public, nullable=False)
    allow_member_posts = Column(Boolean, default=True, nullable=False)
    allow_member_events = Column(Boolean, default=True, nullable=False)


class GroupMember(Base):
    __tablename__ = "group_members"

    group_id = Column(Integer, ForeignKey("groups.id", ondelete="CASCADE"), primary_key=True)
    user_id = Column(Integer, ForeignKey("users.id", ondelete="CASCADE"), primary_key=True)
    role = Column(Enum(GroupRole), default=GroupRole.member, nullable=False)

class EventVisibility(str, enum.Enum):
    public = "public"
    private = "private"


class EventRole(str, enum.Enum):
    organizer = "organizer"
    participant = "participant"


class InvitationStatus(str, enum.Enum):
    pending = "pending"
    accepted = "accepted"
    declined = "declined"


class Event(Base):
    __tablename__ = "events"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, index=True, nullable=False)
    description = Column(String, nullable=True)
    start_date = Column(DateTime, nullable=False)
    end_date = Column(DateTime, nullable=False)
    location = Column(String, nullable=False)
    cover_photo_url = Column(String, nullable=True)
    visibility = Column(Enum(EventVisibility), default=EventVisibility.public, nullable=False)
    group_id = Column(Integer, ForeignKey("groups.id", ondelete="SET NULL"), nullable=True)


class EventParticipant(Base):
    __tablename__ = "event_participants"

    event_id = Column(Integer, ForeignKey("events.id", ondelete="CASCADE"), primary_key=True)
    user_id = Column(Integer, ForeignKey("users.id", ondelete="CASCADE"), primary_key=True)
    role = Column(Enum(EventRole), default=EventRole.participant, nullable=False)
    status = Column(Enum(InvitationStatus), default=InvitationStatus.pending, nullable=False)