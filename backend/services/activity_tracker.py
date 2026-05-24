"""
FINEX - User Activity Tracker
Tracks: Registrations, Logins, Activity
Exports to CSV for admin dashboard
"""

import csv
from datetime import datetime
from pathlib import Path
import logging
from typing import List, Dict

logger = logging.getLogger(__name__)

# Data directory
DATA_DIR = Path("data/user_activity")
DATA_DIR.mkdir(parents=True, exist_ok=True)

REGISTRATIONS_FILE = DATA_DIR / "registrations.csv"
LOGINS_FILE = DATA_DIR / "logins.csv"
ACTIVITY_FILE = DATA_DIR / "activity.csv"


class ActivityTracker:
    """Track user activities and export to CSV"""

    @staticmethod
    def log_registration(user_id: str, email: str, username: str, phone: str = None):
        """Log user registration"""
        try:
            timestamp = datetime.now()
            data = {
                'user_id': user_id,
                'email': email,
                'username': username,
                'phone': phone or 'N/A',
                'registration_date': timestamp.strftime('%Y-%m-%d'),
                'registration_time': timestamp.strftime('%H:%M:%S'),
                'timestamp': timestamp.isoformat()
            }
            file_exists = REGISTRATIONS_FILE.exists()
            with open(REGISTRATIONS_FILE, 'a', newline='') as f:
                writer = csv.DictWriter(f, fieldnames=data.keys())
                if not file_exists:
                    writer.writeheader()
                writer.writerow(data)
            logger.info(f"✅ Registered: {email}")
            return True
        except Exception as e:
            logger.error(f"❌ Registration log failed: {e}")
            return False

    @staticmethod
    def log_login(user_id: str, email: str, ip_address: str = None, device: str = None):
        """Log user login"""
        try:
            timestamp = datetime.now()
            data = {
                'user_id': user_id,
                'email': email,
                'login_date': timestamp.strftime('%Y-%m-%d'),
                'login_time': timestamp.strftime('%H:%M:%S'),
                'ip_address': ip_address or 'Unknown',
                'device': device or 'Unknown',
                'timestamp': timestamp.isoformat()
            }
            file_exists = LOGINS_FILE.exists()
            with open(LOGINS_FILE, 'a', newline='') as f:
                writer = csv.DictWriter(f, fieldnames=data.keys())
                if not file_exists:
                    writer.writeheader()
                writer.writerow(data)
            logger.info(f"✅ Login: {email}")
            return True
        except Exception as e:
            logger.error(f"❌ Login log failed: {e}")
            return False

    @staticmethod
    def log_activity(user_id: str, email: str, action: str, details: str = None):
        """Log user activity (page visit, transaction, etc)"""
        try:
            timestamp = datetime.now()
            data = {
                'user_id': user_id,
                'email': email,
                'action': action,
                'details': details or 'N/A',
                'date': timestamp.strftime('%Y-%m-%d'),
                'time': timestamp.strftime('%H:%M:%S'),
                'timestamp': timestamp.isoformat()
            }
            file_exists = ACTIVITY_FILE.exists()
            with open(ACTIVITY_FILE, 'a', newline='') as f:
                writer = csv.DictWriter(f, fieldnames=data.keys())
                if not file_exists:
                    writer.writeheader()
                writer.writerow(data)
            logger.info(f"✅ Activity logged: {email} - {action}")
            return True
        except Exception as e:
            logger.error(f"❌ Activity log failed: {e}")
            return False

    @staticmethod
    def get_registrations() -> List[Dict]:
        """Get all registrations"""
        try:
            if not REGISTRATIONS_FILE.exists():
                return []
            with open(REGISTRATIONS_FILE, 'r') as f:
                reader = csv.DictReader(f)
                return list(reader)
        except Exception as e:
            logger.error(f"❌ Failed to read registrations: {e}")
            return []

    @staticmethod
    def get_logins() -> List[Dict]:
        """Get all logins"""
        try:
            if not LOGINS_FILE.exists():
                return []
            with open(LOGINS_FILE, 'r') as f:
                reader = csv.DictReader(f)
                return list(reader)
        except Exception as e:
            logger.error(f"❌ Failed to read logins: {e}")
            return []

    @staticmethod
    def get_activity() -> List[Dict]:
        """Get all activities"""
        try:
            if not ACTIVITY_FILE.exists():
                return []
            with open(ACTIVITY_FILE, 'r') as f:
                reader = csv.DictReader(f)
                return list(reader)
        except Exception as e:
            logger.error(f"❌ Failed to read activity: {e}")
            return []

    @staticmethod
    def get_user_stats() -> Dict:
        """Get user statistics"""
        registrations = ActivityTracker.get_registrations()
        logins = ActivityTracker.get_logins()
        activity = ActivityTracker.get_activity()

        unique_emails = set([r.get('email') for r in registrations])

        login_counts = {}
        for login in logins:
            email = login.get('email')
            login_counts[email] = login_counts.get(email, 0) + 1

        return {
            'total_registrations': len(registrations),
            'total_unique_users': len(unique_emails),
            'total_logins': len(logins),
            'total_activities': len(activity),
            'avg_logins_per_user': len(logins) / len(unique_emails) if unique_emails else 0,
            'login_counts': login_counts
        }

    @staticmethod
    def delete_user_data(email: str) -> bool:
        """Delete all data for a user"""
        try:
            registrations = ActivityTracker.get_registrations()
            logins = ActivityTracker.get_logins()
            activities = ActivityTracker.get_activity()

            registrations = [r for r in registrations if r.get('email') != email]
            logins = [l for l in logins if l.get('email') != email]
            activities = [a for a in activities if a.get('email') != email]

            if registrations:
                with open(REGISTRATIONS_FILE, 'w', newline='') as f:
                    writer = csv.DictWriter(f, fieldnames=registrations[0].keys())
                    writer.writeheader()
                    writer.writerows(registrations)
            else:
                REGISTRATIONS_FILE.unlink(missing_ok=True)

            if logins:
                with open(LOGINS_FILE, 'w', newline='') as f:
                    writer = csv.DictWriter(f, fieldnames=logins[0].keys())
                    writer.writeheader()
                    writer.writerows(logins)
            else:
                LOGINS_FILE.unlink(missing_ok=True)

            if activities:
                with open(ACTIVITY_FILE, 'w', newline='') as f:
                    writer = csv.DictWriter(f, fieldnames=activities[0].keys())
                    writer.writeheader()
                    writer.writerows(activities)
            else:
                ACTIVITY_FILE.unlink(missing_ok=True)

            logger.info(f"✅ Deleted all data for: {email}")
            return True
        except Exception as e:
            logger.error(f"❌ Failed to delete user data: {e}")
            return False


# Global tracker instance
activity_tracker = ActivityTracker()
