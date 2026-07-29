from flask import request
from flask_login import current_user
from app.extensions import db
from app.models.audit_log import AuditLog

class AuditService:
    """
    Service responsible for recording security, compliance, and transaction logs.
    Captures request context parameters automatically.
    """
    @staticmethod
    def log_event(action, user_id=None, target_id=None, target_type=None):
        """
        Creates and commits an AuditLog entry.
        Captures calling IP address from Flask request headers/remote_addr.
        """
        # Auto-resolve user_id from current context if not provided
        if user_id is None and current_user and current_user.is_authenticated:
            user_id = current_user.id

        # Safely capture client IP address (supporting proxy forwarding headers)
        ip_address = None
        try:
            if request:
                if request.headers.getlist("X-Forwarded-For"):
                    ip_address = request.headers.getlist("X-Forwarded-For")[0].split(',')[0].strip()
                else:
                    ip_address = request.remote_addr
        except RuntimeError:
            # Request context might not be available (e.g. CLI or background task execution)
            pass

        log_entry = AuditLog(
            action=action,
            user_id=user_id,
            target_id=target_id,
            target_type=target_type,
            ip_address=ip_address
        )

        try:
            db.session.add(log_entry)
            db.session.commit()
        except Exception as e:
            db.session.rollback()
            # Re-raise to ensure calling logic can handle db transaction errors
            raise e
