from app.extensions import db

class Role(db.Model):
    """
    Model representing user security roles (e.g., Admin, Manager, Employee).
    Determines access privileges across routes and actions.
    """
    __tablename__ = 'roles'

    # Centralized role name constants
    SUPER_ADMIN = 'Super Admin'
    DEPARTMENT_ADMIN = 'Department Admin'
    EMPLOYEE = 'Employee'

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(50), unique=True, nullable=False, index=True)
    description = db.Column(db.String(255), nullable=True)

    # Relationships
    users = db.relationship('User', back_populates='role', lazy='select')

    def __init__(self, name, description=None):
        self.name = name
        self.description = description

    def __repr__(self):
        return f"<Role {self.name}>"
