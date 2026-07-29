from datetime import datetime, timezone
from app.extensions import db

class Notice(db.Model):
    """
    Model representing notices published by administrators/managers.
    Includes targeting, priority level, category, and expiration support.
    """
    __tablename__ = 'notices'
    __table_args__ = (
        db.CheckConstraint("priority IN ('Low', 'Medium', 'High')", name='check_notice_priority'),
        db.CheckConstraint("status IN ('Draft', 'Published', 'Archived')", name='check_notice_status'),
    )

    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(200), nullable=False)
    content = db.Column(db.Text, nullable=False)
    author_id = db.Column(db.Integer, db.ForeignKey('users.id', ondelete='RESTRICT'), nullable=False)
    target_dept_id = db.Column(db.Integer, db.ForeignKey('departments.id', ondelete='SET NULL'), nullable=True)
    category_id = db.Column(db.Integer, db.ForeignKey('notice_categories.id', ondelete='RESTRICT'), nullable=False)
    priority = db.Column(db.String(20), default='Medium', nullable=False)
    status = db.Column(db.String(20), default='Draft', nullable=False)
    expiry_date = db.Column(db.DateTime(timezone=True), nullable=True)
    created_at = db.Column(db.DateTime(timezone=True), default=lambda: datetime.now(timezone.utc), nullable=False)
    updated_at = db.Column(db.DateTime(timezone=True), default=lambda: datetime.now(timezone.utc), onupdate=lambda: datetime.now(timezone.utc), nullable=False)

    # Relationships
    author = db.relationship('User', back_populates='notices')
    target_department = db.relationship('Department', back_populates='notices')
    category = db.relationship('NoticeCategory', back_populates='notices')
    attachments = db.relationship('Attachment', back_populates='notice', cascade='all, delete-orphan', lazy='select')
    read_statuses = db.relationship('ReadStatus', back_populates='notice', cascade='all, delete-orphan', lazy='select')

    def __init__(self, title, content, author_id, category_id, target_dept_id=None, priority='Medium', status='Draft', expiry_date=None):
        self.title = title
        self.content = content
        self.author_id = author_id
        self.category_id = category_id
        self.target_dept_id = target_dept_id
        self.priority = priority
        self.status = status
        self.expiry_date = expiry_date

    def __repr__(self):
        return f"<Notice {self.id}: {self.title[:20]} ({self.status})>"
