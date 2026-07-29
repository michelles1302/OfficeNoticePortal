from datetime import datetime, timezone
from app.extensions import db

class Attachment(db.Model):
    """
    Model representing file attachments uploaded to AWS S3.
    """
    __tablename__ = 'attachments'

    id = db.Column(db.Integer, primary_key=True)
    notice_id = db.Column(db.Integer, db.ForeignKey('notices.id', ondelete='CASCADE'), nullable=False)
    s3_key = db.Column(db.String(255), unique=True, nullable=False, index=True)
    filename = db.Column(db.String(255), nullable=False)
    file_size = db.Column(db.Integer, nullable=False)  # in bytes
    uploaded_at = db.Column(db.DateTime(timezone=True), default=lambda: datetime.now(timezone.utc), nullable=False)

    # Relationships
    notice = db.relationship('Notice', back_populates='attachments')

    def __init__(self, notice_id, s3_key, filename, file_size):
        self.notice_id = notice_id
        self.s3_key = s3_key
        self.filename = filename
        self.file_size = file_size

    def __repr__(self):
        return f"<Attachment {self.id}: {self.filename} (Notice {self.notice_id})>"
