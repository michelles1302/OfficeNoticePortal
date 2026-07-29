from functools import wraps
from flask import abort, redirect, url_for, flash
from flask_login import current_user, logout_user

def role_required(*roles):
    """
    Decorator that restricts access to users possessing specific roles.
    Aborts with a 403 Forbidden status if the authenticated user lacks the role.
    """
    def decorator(f):
        @wraps(f)
        def decorated_function(*args, **kwargs):
            if not current_user.is_authenticated:
                return redirect(url_for('auth.login'))
            
            # Check if the user's role matches any of the permitted roles
            user_role = current_user.role.name if current_user.role else None
            if user_role not in roles:
                abort(403)
                
            return f(*args, **kwargs)
        return decorated_function
    return decorator

def active_user_required(f):
    """
    Decorator that checks if the logged-in user is active.
    If the account is deactivated, it logs the user out and redirects to login.
    """
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if not current_user.is_authenticated:
            return redirect(url_for('auth.login'))
            
        if not current_user.is_active:
            logout_user()
            flash("Your account is inactive. Please contact your administrator.", "danger")
            return redirect(url_for('auth.login'))
            
        return f(*args, **kwargs)
    return decorated_function
