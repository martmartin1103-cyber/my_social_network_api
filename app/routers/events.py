from typing import List, Optional
from fastapi import APIRouter, BackgroundTasks, Depends, HTTPException, Query, status
from sqlalchemy import or_
from sqlalchemy.orm import Session

from app.database import SessionLocal, get_db
from app.models import (
    Event,
    EventParticipant,
    EventRole,
    EventVisibility,
    Group,
    GroupMember,
    GroupRole,
    InvitationStatus,
    User,
)
from app.schemas import (
    EventCreate,
    EventParticipantAdd,
    EventParticipantResponse,
    EventResponse,
    EventUpdate,
)

router = APIRouter(
    prefix="/api/v1",
    tags=["Events"]
)


# TÂCHE ASYNCHRONE (US-09) : Inviter tous les membres d'un groupe en arrière-plan
def invite_all_group_members_task(group_id: int, event_id: int, creator_id: int):
    db = SessionLocal()
    try:
        members = db.query(GroupMember).filter(GroupMember.group_id == group_id).all()
        for member in members:
            if member.user_id == creator_id:
                continue  # Le créateur est déjà inscrit comme organisateur
            existing = db.query(EventParticipant).filter(
                EventParticipant.event_id == event_id,
                EventParticipant.user_id == member.user_id
            ).first()
            if not existing:
                db.add(EventParticipant(
                    event_id=event_id,
                    user_id=member.user_id,
                    role=EventRole.participant,
                    status=InvitationStatus.pending
                ))
        db.commit()
    finally:
        db.close()


# 1. CRÉER UN ÉVÉNEMENT INDÉPENDANT
@router.post("/events", response_model=EventResponse, status_code=status.HTTP_201_CREATED)
def create_event(event: EventCreate, db: Session = Depends(get_db)):
    if event.end_date <= event.start_date:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="La date de fin doit être postérieure à la date de début."
        )
    if not db.query(User).filter(User.id == event.creator_id).first():
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Créateur introuvable.")

    db_event = Event(
        name=event.name,
        description=event.description,
        start_date=event.start_date,
        end_date=event.end_date,
        location=event.location,
        cover_photo_url=event.cover_photo_url,
        visibility=event.visibility,
    )
    db.add(db_event)
    db.commit()
    db.refresh(db_event)

    db.add(EventParticipant(
        event_id=db_event.id,
        user_id=event.creator_id,
        role=EventRole.organizer,
        status=InvitationStatus.accepted
    ))
    db.commit()
    return db_event


# 2. CRÉER UN ÉVÉNEMENT DANS UN GROUPE + INVITATION AUTO DES MEMBRES (US-09)
@router.post("/groups/{group_id}/events", response_model=EventResponse, status_code=status.HTTP_201_CREATED)
def create_group_event(
    group_id: int,
    event: EventCreate,
    background_tasks: BackgroundTasks,
    db: Session = Depends(get_db)
):
    if event.end_date <= event.start_date:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="La date de fin doit être postérieure à la date de début."
        )

    group = db.query(Group).filter(Group.id == group_id).first()
    if not group:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Groupe introuvable.")

    membership = db.query(GroupMember).filter(
        GroupMember.group_id == group_id,
        GroupMember.user_id == event.creator_id
    ).first()
    if not membership:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Vous devez être membre du groupe pour y créer un événement."
        )
    if not group.allow_member_events and membership.role != GroupRole.admin:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Seuls les administrateurs peuvent créer un événement dans ce groupe."
        )

    db_event = Event(
        name=event.name,
        description=event.description,
        start_date=event.start_date,
        end_date=event.end_date,
        location=event.location,
        cover_photo_url=event.cover_photo_url,
        visibility=event.visibility,
        group_id=group_id,
    )
    db.add(db_event)
    db.commit()
    db.refresh(db_event)

    # Le créateur est organisateur
    db.add(EventParticipant(
        event_id=db_event.id,
        user_id=event.creator_id,
        role=EventRole.organizer,
        status=InvitationStatus.accepted
    ))
    db.commit()

    # Asynchrone : invite tous les autres membres du groupe en arrière-plan
    background_tasks.add_task(invite_all_group_members_task, group_id, db_event.id, event.creator_id)

    return db_event


# 3. LISTER / RECHERCHER LES ÉVÉNEMENTS PUBLICS
@router.get("/events", response_model=List[EventResponse])
def search_events(
    q: Optional[str] = Query(None, description="Filtrer par nom, lieu ou description"),
    db: Session = Depends(get_db)
):
    query = db.query(Event).filter(Event.visibility == EventVisibility.public)
    if q:
        pattern = f"%{q}%"
        query = query.filter(
            or_(
                Event.name.ilike(pattern),
                Event.location.ilike(pattern),
                Event.description.ilike(pattern)
            )
        )
    return query.all()


# 4. LISTER LES ÉVÉNEMENTS D'UN GROUPE
@router.get("/groups/{group_id}/events", response_model=List[EventResponse])
def list_group_events(group_id: int, db: Session = Depends(get_db)):
    if not db.query(Group).filter(Group.id == group_id).first():
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Groupe introuvable.")
    return db.query(Event).filter(Event.group_id == group_id).all()


# 5. DÉTAIL D'UN ÉVÉNEMENT
@router.get("/events/{event_id}", response_model=EventResponse)
def get_event(event_id: int, db: Session = Depends(get_db)):
    event = db.query(Event).filter(Event.id == event_id).first()
    if not event:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Événement introuvable.")
    return event


# 6. MODIFIER UN ÉVÉNEMENT
@router.put("/events/{event_id}", response_model=EventResponse)
def update_event(event_id: int, event_update: EventUpdate, db: Session = Depends(get_db)):
    db_event = db.query(Event).filter(Event.id == event_id).first()
    if not db_event:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Événement introuvable.")

    update_data = event_update.model_dump(exclude_unset=True)
    new_start = update_data.get("start_date", db_event.start_date)
    new_end = update_data.get("end_date", db_event.end_date)
    if new_end <= new_start:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="La date de fin doit être postérieure à la date de début."
        )

    for field, value in update_data.items():
        setattr(db_event, field, value)

    db.commit()
    db.refresh(db_event)
    return db_event


# 7. SUPPRIMER UN ÉVÉNEMENT
@router.delete("/events/{event_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_event(event_id: int, db: Session = Depends(get_db)):
    db_event = db.query(Event).filter(Event.id == event_id).first()
    if not db_event:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Événement introuvable.")

    db.query(EventParticipant).filter(EventParticipant.event_id == event_id).delete()
    db.delete(db_event)
    db.commit()
    return None


# 8. LISTER LES PARTICIPANTS / INVITÉS D'UN ÉVÉNEMENT
@router.get("/events/{event_id}/participants", response_model=List[EventParticipantResponse])
def list_event_participants(event_id: int, db: Session = Depends(get_db)):
    if not db.query(Event).filter(Event.id == event_id).first():
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Événement introuvable.")
    return db.query(EventParticipant).filter(EventParticipant.event_id == event_id).all()


# 9. INVITER / AJOUTER UN PARTICIPANT MANUELLEMENT
@router.post("/events/{event_id}/participants", response_model=EventParticipantResponse, status_code=status.HTTP_201_CREATED)
def add_event_participant(event_id: int, participant: EventParticipantAdd, db: Session = Depends(get_db)):
    if not db.query(Event).filter(Event.id == event_id).first():
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Événement introuvable.")
    if not db.query(User).filter(User.id == participant.user_id).first():
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Utilisateur introuvable.")

    existing = db.query(EventParticipant).filter(
        EventParticipant.event_id == event_id,
        EventParticipant.user_id == participant.user_id
    ).first()
    if existing:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="Cet utilisateur est déjà invité ou participant à l'événement."
        )

    db_participant = EventParticipant(
        event_id=event_id,
        user_id=participant.user_id,
        role=participant.role,
        status=participant.status
    )
    db.add(db_participant)
    db.commit()
    db.refresh(db_participant)
    return db_participant