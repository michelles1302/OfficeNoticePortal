from flask_wtf import FlaskForm
from flask_wtf.file import FileField, FileAllowed
from wtforms import StringField, TextAreaField, SelectField, SubmitField, DateTimeLocalField, MultipleFileField
from wtforms.validators import DataRequired, Length, Optional

class NoticeForm(FlaskForm):
    """Form used by admins to create and edit corporate notices."""
    title = StringField('Notice Title', validators=[
        DataRequired(message="Title is required."),
        Length(min=3, max=200, message="Title must be between 3 and 200 characters.")
    ])
    
    content = TextAreaField('Notice Content', validators=[
        DataRequired(message="Notice content cannot be empty.")
    ])
    
    category_id = SelectField('Category', coerce=int, validators=[
        DataRequired(message="Please select a notice category.")
    ])
    
    target_dept_id = SelectField('Target Department', coerce=int, validators=[
        Optional()
    ])
    
    priority = SelectField('Priority Level', choices=[
        ('Low', 'Low'),
        ('Medium', 'Medium'),
        ('High', 'High')
    ], default='Medium', validators=[DataRequired()])
    
    status = SelectField('Publication Status', choices=[
        ('Draft', 'Draft'),
        ('Published', 'Published'),
        ('Archived', 'Archived')
    ], default='Draft', validators=[DataRequired()])
    
    expiry_date = DateTimeLocalField('Expiration Date (Optional)', format='%Y-%m-%dT%H:%M', validators=[Optional()])
    
    attachments = MultipleFileField('Attach Files (Optional)', validators=[
        FileAllowed(['pdf', 'doc', 'docx', 'png', 'jpg', 'jpeg', 'zip', 'txt'], 'Documents and images only!')
    ])
    
    submit = SubmitField('Save Notice')


class NoticeFilterForm(FlaskForm):
    """Form used for filtering and searching notice feeds."""
    search = StringField('Search Keywords', validators=[Optional()])
    category_id = SelectField('Category', coerce=int, choices=[(0, 'All Categories')], validators=[Optional()])
    priority = SelectField('Priority', choices=[('', 'All Priorities'), ('High', 'High'), ('Medium', 'Medium'), ('Low', 'Low')], validators=[Optional()])
    department_id = SelectField('Department', coerce=int, choices=[(0, 'All Departments')], validators=[Optional()])
    status = SelectField('Status', choices=[('', 'All Statuses'), ('Published', 'Published'), ('Draft', 'Draft'), ('Archived', 'Archived')], validators=[Optional()])
    read_status = SelectField('Read Status', choices=[('all', 'All Notices'), ('unread', 'Unread Only'), ('read', 'Read Only')], validators=[Optional()])
    submit = SubmitField('Filter')
