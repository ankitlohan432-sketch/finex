"""
FINEX - Admin Control Panel (SECRET)
Only accessible by: ankitlohan432@gmail.com / rohan
Manages user data, registrations, logins, activity
"""

from fastapi import APIRouter, Query, HTTPException
from fastapi.responses import FileResponse
from services.activity_tracker import activity_tracker
import logging
from pathlib import Path

logger = logging.getLogger(__name__)
router = APIRouter(tags=["Admin Control (SECRET)"])

# Admin credentials (hardcoded - only you know this)
ADMIN_EMAIL = "ankitlohan432@gmail.com"
ADMIN_USERNAME = "rohan"
ADMIN_PASSWORD = "finex_admin_secret_2024"


def verify_admin(email: str, username: str, password: str) -> bool:
    """Verify admin credentials"""
    return (
        email == ADMIN_EMAIL
        and username == ADMIN_USERNAME
        and password == ADMIN_PASSWORD
    )


# ── Dashboard ─────────────────────────────────────────────────────────────────

@router.get("/admin/dashboard")
async def admin_dashboard(
    email: str = Query(...),
    username: str = Query(...),
    password: str = Query(...)
):
    """Get admin dashboard data"""
    if not verify_admin(email, username, password):
        raise HTTPException(status_code=403, detail="Unauthorized")

    stats = activity_tracker.get_user_stats()

    return {
        "status": "authorized",
        "admin": ADMIN_EMAIL,
        "dashboard": {
            "total_registrations": stats['total_registrations'],
            "total_unique_users": stats['total_unique_users'],
            "total_logins": stats['total_logins'],
            "total_activities": stats['total_activities'],
            "avg_logins_per_user": round(stats['avg_logins_per_user'], 2)
        }
    }


# ── View Users ────────────────────────────────────────────────────────────────

@router.get("/admin/users/registrations")
async def get_registrations(
    email: str = Query(...),
    username: str = Query(...),
    password: str = Query(...)
):
    """Get all registrations"""
    if not verify_admin(email, username, password):
        raise HTTPException(status_code=403, detail="Unauthorized")

    registrations = activity_tracker.get_registrations()
    return {"total": len(registrations), "data": registrations}


@router.get("/admin/users/logins")
async def get_logins(
    email: str = Query(...),
    username: str = Query(...),
    password: str = Query(...),
    user_email: str = Query(None)
):
    """Get all logins (optionally filtered by user)"""
    if not verify_admin(email, username, password):
        raise HTTPException(status_code=403, detail="Unauthorized")

    logins = activity_tracker.get_logins()
    if user_email:
        logins = [l for l in logins if l.get('email') == user_email]

    return {"total": len(logins), "data": logins}


@router.get("/admin/users/activity")
async def get_activity(
    email: str = Query(...),
    username: str = Query(...),
    password: str = Query(...),
    user_email: str = Query(None),
    action: str = Query(None)
):
    """Get all user activities"""
    if not verify_admin(email, username, password):
        raise HTTPException(status_code=403, detail="Unauthorized")

    activities = activity_tracker.get_activity()
    if user_email:
        activities = [a for a in activities if a.get('email') == user_email]
    if action:
        activities = [a for a in activities if a.get('action') == action]

    return {"total": len(activities), "data": activities}


# ── Delete Users ──────────────────────────────────────────────────────────────

@router.delete("/admin/users/delete")
async def delete_user(
    email: str = Query(...),
    username: str = Query(...),
    password: str = Query(...),
    user_email: str = Query(...)
):
    """Delete all activity data for a user"""
    if not verify_admin(email, username, password):
        raise HTTPException(status_code=403, detail="Unauthorized")

    if user_email == ADMIN_EMAIL:
        raise HTTPException(status_code=400, detail="Cannot delete admin account")

    success = activity_tracker.delete_user_data(user_email)
    if not success:
        raise HTTPException(status_code=400, detail="Failed to delete user")

    return {
        "status": "success",
        "message": f"User {user_email} deleted",
        "deleted_user": user_email
    }


# ── Export CSV ────────────────────────────────────────────────────────────────

@router.get("/admin/export/registrations")
async def export_registrations(
    email: str = Query(...),
    username: str = Query(...),
    password: str = Query(...)
):
    """Export registrations as CSV"""
    if not verify_admin(email, username, password):
        raise HTTPException(status_code=403, detail="Unauthorized")

    file_path = Path("data/user_activity/registrations.csv")
    if not file_path.exists():
        raise HTTPException(status_code=404, detail="No data available")

    return FileResponse(file_path, filename="registrations.csv", media_type="text/csv")


@router.get("/admin/export/logins")
async def export_logins(
    email: str = Query(...),
    username: str = Query(...),
    password: str = Query(...)
):
    """Export logins as CSV"""
    if not verify_admin(email, username, password):
        raise HTTPException(status_code=403, detail="Unauthorized")

    file_path = Path("data/user_activity/logins.csv")
    if not file_path.exists():
        raise HTTPException(status_code=404, detail="No data available")

    return FileResponse(file_path, filename="logins.csv", media_type="text/csv")


@router.get("/admin/export/activity")
async def export_activity(
    email: str = Query(...),
    username: str = Query(...),
    password: str = Query(...)
):
    """Export activity as CSV"""
    if not verify_admin(email, username, password):
        raise HTTPException(status_code=403, detail="Unauthorized")

    file_path = Path("data/user_activity/activity.csv")
    if not file_path.exists():
        raise HTTPException(status_code=404, detail="No data available")

    return FileResponse(file_path, filename="activity.csv", media_type="text/csv")


# ── Stats ─────────────────────────────────────────────────────────────────────

@router.get("/admin/stats")
async def get_stats(
    email: str = Query(...),
    username: str = Query(...),
    password: str = Query(...)
):
    """Get comprehensive statistics"""
    if not verify_admin(email, username, password):
        raise HTTPException(status_code=403, detail="Unauthorized")

    stats = activity_tracker.get_user_stats()

    return {
        "status": "success",
        "stats": {
            "total_registrations": stats['total_registrations'],
            "total_unique_users": stats['total_unique_users'],
            "total_logins": stats['total_logins'],
            "total_activities": stats['total_activities'],
            "average_logins_per_user": round(stats['avg_logins_per_user'], 2),
            "login_frequency": stats['login_counts']
        }
    }
