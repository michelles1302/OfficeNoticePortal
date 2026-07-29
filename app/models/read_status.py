from datetime import datetime, timezone
from app.extensions import db

class ReadStatus(db.Model):
    """
    Model representing employee acknowledgement (read verification) of a notice.
    """
    __tablename__ = 'read_statuses'
    __table_args__ = (
        db.UniqueConstraint('user_id', 'notice_id', name='uq_user_notice_read'),
    )

    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id', ondelete='CASCADE'), nullable=False)
    notice_id = db.Column(db.Integer, db.ForeignKey('notices.id', ondelete='CASCADE'), nullable=False)
    read_at = db.Column(db.DateTime(timezone=True), default=lambda: datetime.now(timezone.utc), nullable=False)

    # Relationships
    user = db.relationship('User', back_populates='read_statuses')
    notice = db.relationship('Notice', back_populates='read_statuses')

    def __init__(self, user_id, notice_id):
        self.user_id = user_id
        self.notice_id = notice_id

    def __repr__(self):
        return f"<ReadStatus User {self.user_id} - Notice {self.notice_id} (Read: {self.read_at})>"
