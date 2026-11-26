from typing import List, Optional
from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy import or_
from sqlalchemy.orm import Session

from app.database import get_db
from app.models import Group, GroupMember, GroupRole, GroupType, User
from app.schemas import (
    GroupCreate,
    GroupMemberAdd,
    GroupMemberResponse,
    GroupResponse,
    GroupUpdate,
)

router = APIRouter(
    prefix="/api/v1/groups",
    tags=["Groups"]
)

# 1. CRÉER UN GROUPE (+ ajout auto du créateur en admin)
@router.post("", response_model=GroupResponse, status_code=status.HTTP_201_CREATED)
def create_group(group: GroupCreate, db: Session = Depends(get_db)):
    creator = db.query(User).filter(User.id == group.creator_id).first()
    if not creator:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Utilisateur créateur introuvable."
        )

    db_group = Group(
        name=group.name,
        description=group.description,
        icon_url=group.icon_url,
        cover_photo_url=group.cover_photo_url,
        group_type=group.group_type,
        allow_member_posts=group.allow_member_posts,
        allow_member_events=group.allow_member_events,
    )
    db.add(db_group)
    db.commit()
    db.refresh(db_group)

    # Règle métier : le créateur devient automatiquement administrateur
    admin_membership = GroupMember(
        group_id=db_group.id,
        user_id=creator.id,
        role=GroupRole.admin,
    )
    db.add(admin_membership)
    db.commit()

    return db_group


# 2. RECHERCHER / LISTER LES GROUPES (hors groupes secrets)
@router.get("", response_model=List[GroupResponse])
def search_groups(
    q: Optional[str] = Query(None, description="Filtrer par nom ou description"),
    db: Session = Depends(get_db)
):
    query = db.query(Group).filter(Group.group_type != GroupType.secret)
    if q:
        pattern = f"%{q}%"
        query = query.filter(
            or_(Group.name.ilike(pattern), Group.description.ilike(pattern))
        )
    return query.all()


# 3. DÉTAIL D'UN GROUPE
@router.get("/{group_id}", response_model=GroupResponse)
def get_group(group_id: int, db: Session = Depends(get_db)):
    group = db.query(Group).filter(Group.id == group_id).first()
    if not group:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Groupe introuvable.")
    return group


# 4. MODIFIER UN GROUPE
@router.put("/{group_id}", response_model=GroupResponse)
def update_group(group_id: int, group_update: GroupUpdate, db: Session = Depends(get_db)):
    db_group = db.query(Group).filter(Group.id == group_id).first()
    if not db_group:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Groupe introuvable.")

    for field, value in group_update.model_dump(exclude_unset=True).items():
        setattr(db_group, field, value)

    db.commit()
    db.refresh(db_group)
    return db_group


# 5. SUPPRIMER UN GROUPE
@router.delete("/{group_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_group(group_id: int, db: Session = Depends(get_db)):
    db_group = db.query(Group).filter(Group.id == group_id).first()
    if not db_group:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Groupe introuvable.")

    db.query(GroupMember).filter(GroupMember.group_id == group_id).delete()
    db.delete(db_group)
    db.commit()
    return None


# 6. LISTER LES MEMBRES D'UN GROUPE
@router.get("/{group_id}/members", response_model=List[GroupMemberResponse])
def list_group_members(group_id: int, db: Session = Depends(get_db)):
    if not db.query(Group).filter(Group.id == group_id).first():
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Groupe introuvable.")
    return db.query(GroupMember).filter(GroupMember.group_id == group_id).all()


# 7. AJOUTER UN MEMBRE OU ADMIN
@router.post("/{group_id}/members", response_model=GroupMemberResponse, status_code=status.HTTP_201_CREATED)
def add_group_member(group_id: int, member: GroupMemberAdd, db: Session = Depends(get_db)):
    if not db.query(Group).filter(Group.id == group_id).first():
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Groupe introuvable.")
    if not db.query(User).filter(User.id == member.user_id).first():
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Utilisateur introuvable.")

    existing = db.query(GroupMember).filter(
        GroupMember.group_id == group_id,
        GroupMember.user_id == member.user_id
    ).first()
    if existing:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="Cet utilisateur est déjà membre du groupe."
        )

    db_member = GroupMember(group_id=group_id, user_id=member.user_id, role=member.role)
    db.add(db_member)
    db.commit()
    db.refresh(db_member)
    return db_member


# 8. RETIRER UN MEMBRE (en protégeant le dernier admin)
@router.delete("/{group_id}/members/{user_id}", status_code=status.HTTP_204_NO_CONTENT)
def remove_group_member(group_id: int, user_id: int, db: Session = Depends(get_db)):
    membership = db.query(GroupMember).filter(
        GroupMember.group_id == group_id,
        GroupMember.user_id == user_id
    ).first()
    if not membership:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Membre introuvable dans ce groupe.")

    if membership.role == GroupRole.admin:
        admin_count = db.query(GroupMember).filter(
            GroupMember.group_id == group_id,
            GroupMember.role == GroupRole.admin
        ).count()
        if admin_count <= 1:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Impossible de retirer le dernier administrateur du groupe."
            )

    db.delete(membership)
    db.commit()
    return None