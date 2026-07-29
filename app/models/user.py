from datetime import datetime, timezone
from flask_login import UserMixin
from app.extensions import db, bcrypt

class User(db.Model, UserMixin):
    """
    Model representing system users/employees.
    Integrates with Flask-Login and handles password hashing via Bcrypt.
    """
    __tablename__ = 'users'

    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(80), unique=True, nullable=False, index=True)
    email = db.Column(db.String(120), unique=True, nullable=False, index=True)
    password_hash = db.Column(db.String(255), nullable=False)
    role_id = db.Column(db.Integer, db.ForeignKey('roles.id', ondelete='RESTRICT'), nullable=False)
    department_id = db.Column(db.Integer, db.ForeignKey('departments.id', ondelete='SET NULL'), nullable=True)
    is_active = db.Column(db.Boolean, default=True, nullable=False)
    created_at = db.Column(db.DateTime(timezone=True), default=lambda: datetime.now(timezone.utc), nullable=False)

    # Relationships
    role = db.relationship('Role', back_populates='users')
    department = db.relationship('Department', back_populates='users')
    notices = db.relationship('Notice', back_populates='author', lazy='select')
    read_statuses = db.relationship('ReadStatus', back_populates='user', cascade='all, delete-orphan', lazy='select')
    audit_logs = db.relationship('AuditLog', back_populates='user', lazy='select')

    def __init__(self, username, email, password, role_id, department_id=None, is_active=True):
        self.username = username
        self.email = email.lower()
        self.role_id = role_id
        self.department_id = department_id
        self.is_active = is_active
        self.set_password(password)

    def set_password(self, password):
        """Hashes the password and sets password_hash."""
        self.password_hash = bcrypt.generate_password_hash(password).decode('utf-8')

    def check_password(self, password):
        """Verifies password against stored password_hash."""
        return bcrypt.check_password_hash(self.password_hash, password)

    def __repr__(self):
        return f"<User {self.username} ({self.email})>"
