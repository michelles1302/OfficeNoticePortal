from app.extensions import db

class NoticeCategory(db.Model):
    """
    Model representing notice classifications (e.g., Policy, General Memo, Meeting, Holiday).
    """
    __tablename__ = 'notice_categories'

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(50), unique=True, nullable=False, index=True)
    description = db.Column(db.String(255), nullable=True)

    # Relationships
    notices = db.relationship('Notice', back_populates='category', lazy='select')

    def __init__(self, name, description=None):
        self.name = name
        self.description = description

    def __repr__(self):
        return f"<NoticeCategory {self.name}>"
