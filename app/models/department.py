from app.extensions import db

class Department(db.Model):
    """
    Model representing organizational departments (e.g., HR, IT, Finance).
    Used for target notice delivery and user segmentation.
    """
    __tablename__ = 'departments'

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), unique=True, nullable=False, index=True)
    code = db.Column(db.String(10), unique=True, nullable=False, index=True)

    # Relationships
    users = db.relationship('User', back_populates='department', lazy='select')
    notices = db.relationship('Notice', back_populates='target_department', lazy='select')

    def __init__(self, name, code):
        self.name = name
        self.code = code.upper()

    def __repr__(self):
        return f"<Department {self.code} - {self.name}>"
