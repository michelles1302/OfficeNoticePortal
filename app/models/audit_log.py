from datetime import datetime, timezone
from app.extensions import db

class AuditLog(db.Model):
    """
    Model representing system operations for audit trails and security verification.
    Uses PostgreSQL BIGINT auto-incrementing key.
    """
    __tablename__ = 'audit_logs'

    id = db.Column(db.BigInteger, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id', ondelete='SET NULL'), nullable=True)
    action = db.Column(db.String(100), nullable=False)
    target_id = db.Column(db.Integer, nullable=True)
    target_type = db.Column(db.String(50), nullable=True)
    ip_address = db.Column(db.String(45), nullable=True)  # Supports both IPv4 and IPv6
    created_at = db.Column(db.DateTime(timezone=True), default=lambda: datetime.now(timezone.utc), nullable=False, index=True)

    # Relationships
    user = db.relationship('User', back_populates='audit_logs')

    def __init__(self, action, user_id=None, target_id=None, target_type=None, ip_address=None):
        self.action = action
        self.user_id = user_id
        self.target_id = target_id
        self.target_type = target_type
        self.ip_address = ip_address

    def __repr__(self):
        return f"<AuditLog {self.id}: {self.action} by User {self.user_id} at {self.created_at}>"
