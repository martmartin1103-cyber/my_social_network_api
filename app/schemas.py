from typing import Optional
from pydantic import BaseModel, ConfigDict

class UserBase(BaseModel):
    username: str
    email: str
    full_name: Optional[str] = None
    bio: Optional[str] = None

class UserCreate(UserBase):
    password: str  # Requis uniquement à la création

class UserUpdate(BaseModel):
    username: Optional[str] = None
    email: Optional[str] = None
    full_name: Optional[str] = None
    bio: Optional[str] = None

class UserResponse(UserBase):
    id: int

    model_config = ConfigDict(from_attributes=True)

from app.models import GroupType, GroupRole

# --- SCHÉMAS GROUPES ---
class GroupBase(BaseModel):
    name: str
    description: Optional[str] = None
    icon_url: Optional[str] = None
    cover_photo_url: Optional[str] = None
    group_type: GroupType = GroupType.public
    allow_member_posts: bool = True
    allow_member_events: bool = True

class GroupCreate(GroupBase):
    creator_id: int  # L'utilisateur qui crée le groupe devient automatiquement admin

class GroupUpdate(BaseModel):
    name: Optional[str] = None
    description: Optional[str] = None
    icon_url: Optional[str] = None
    cover_photo_url: Optional[str] = None
    group_type: Optional[GroupType] = None
    allow_member_posts: Optional[bool] = None
    allow_member_events: Optional[bool] = None

class GroupResponse(GroupBase):
    id: int

    model_config = ConfigDict(from_attributes=True)

# --- SCHÉMAS MEMBRES ---
class GroupMemberAdd(BaseModel):
    user_id: int
    role: GroupRole = GroupRole.member

class GroupMemberResponse(BaseModel):
    group_id: int
    user_id: int
    role: GroupRole

    model_config = ConfigDict(from_attributes=True)

from datetime import datetime
from app.models import GroupType, GroupRole, EventVisibility, EventRole, InvitationStatus

# --- SCHÉMAS ÉVÉNEMENTS ---
class EventBase(BaseModel):
    name: str
    description: Optional[str] = None
    start_date: datetime
    end_date: datetime
    location: str
    cover_photo_url: Optional[str] = None
    visibility: EventVisibility = EventVisibility.public

class EventCreate(EventBase):
    creator_id: int  # Devient automatiquement organisateur (statut accepted)

class EventUpdate(BaseModel):
    name: Optional[str] = None
    description: Optional[str] = None
    start_date: Optional[datetime] = None
    end_date: Optional[datetime] = None
    location: Optional[str] = None
    cover_photo_url: Optional[str] = None
    visibility: Optional[EventVisibility] = None

class EventResponse(EventBase):
    id: int
    group_id: Optional[int] = None

    model_config = ConfigDict(from_attributes=True)

# --- SCHÉMAS PARTICIPANTS ---
class EventParticipantAdd(BaseModel):
    user_id: int
    role: EventRole = EventRole.participant
    status: InvitationStatus = InvitationStatus.pending

class EventParticipantResponse(BaseModel):
    event_id: int
    user_id: int
    role: EventRole
    status: InvitationStatus

    model_config = ConfigDict(from_attributes=True)