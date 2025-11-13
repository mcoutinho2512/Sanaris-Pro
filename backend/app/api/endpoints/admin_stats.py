from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from sqlalchemy import func
from datetime import datetime, timedelta
from app.core.database import get_db
from app.models.user import User
from app.models.organization import Organization
from app.core.security import get_current_user

router = APIRouter()

@router.get("/dashboard")
def get_super_admin_dashboard(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    if current_user.role != 'super_admin':
        raise HTTPException(status_code=403, detail="Acesso negado. Apenas Super Admin.")
    
    # 1. Organizações
    total_organizations = db.query(Organization).count()
    active_organizations = db.query(Organization).filter(Organization.is_active == True).count()
    
    # 2. Usuários por role (APENAS ATIVOS)
    users_by_role = db.query(
        User.role,
        func.count(User.id).label('count')
    ).filter(
        User.is_active == True
    ).group_by(User.role).all()
    
    role_stats = {
        'super_admin': 0,
        'admin': 0,
        'user': 0
    }
    
    for role, count in users_by_role:
        role_stats[role] = count
    
    total_users = sum(role_stats.values())
    
    # 3. Usuários logados nas últimas 24h
    twenty_four_hours_ago = (datetime.utcnow() - timedelta(hours=24)).isoformat()
    recently_active = db.query(User).filter(
        User.last_login >= twenty_four_hours_ago,
        User.is_active == True
    ).count()
    
    # 4. Ativos/Inativos
    active_users = db.query(User).filter(User.is_active == True).count()
    inactive_users = db.query(User).filter(User.is_active == False).count()
    
    # 5. Top 5 organizações (APENAS USUÁRIOS ATIVOS)
    top_orgs = db.query(
        Organization.name,
        func.count(User.id).label('user_count')
    ).join(
        User, User.organization_id == Organization.id
    ).filter(
        User.is_active == True
    ).group_by(
        Organization.id, Organization.name
    ).order_by(
        func.count(User.id).desc()
    ).limit(5).all()
    
    top_organizations = [
        {"name": org[0], "users": org[1]}
        for org in top_orgs
    ]
    
    # 6. Crescimento
    six_months_ago = (datetime.utcnow() - timedelta(days=180)).isoformat()
    new_orgs_last_6_months = db.query(Organization).filter(
        Organization.created_at >= six_months_ago
    ).count()
    
    return {
        "organizations": {
            "total": total_organizations,
            "active": active_organizations,
            "inactive": total_organizations - active_organizations,
            "new_last_6_months": new_orgs_last_6_months
        },
        "users": {
            "total": total_users,
            "active": active_users,
            "inactive": inactive_users,
            "recently_active_24h": recently_active,
            "by_role": {
                "super_admins": role_stats['super_admin'],
                "admins": role_stats['admin'],
                "users": role_stats['user']
            }
        },
        "top_organizations": top_organizations
    }
