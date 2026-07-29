from flask import render_template, redirect, url_for, flash, request, session
from flask_login import login_user, logout_user, login_required, current_user
from urllib.parse import urlsplit
from app.extensions import db
from app.models.user import User
from app.services.audit_service import AuditService
from app.utils.decorators import active_user_required
from app.blueprints.auth import auth_bp
from app.blueprints.auth.forms import LoginForm, ProfileForm, ChangePasswordForm

@auth_bp.route('/login', methods=['GET', 'POST'])
def login():
    """Handles user authentication requests."""
    if current_user.is_authenticated:
        return redirect(url_for('employee.home'))
        
    form = LoginForm()
    if form.validate_on_submit():
        user = User.query.filter_by(email=form.email.data.lower()).first()
        
        if user and user.check_password(form.password.data):
            if not user.is_active:
                AuditService.log_event('LOGIN_FAILED_INACTIVE', user_id=user.id)
                flash('Your account is inactive. Please contact your administrator.', 'danger')
                return render_template('auth/login.html', form=form)
                
            login_user(user, remember=form.remember_me.data)
            session.permanent = True

            AuditService.log_event('LOGIN_SUCCESS', user_id=user.id)
            flash(f'Welcome back, {user.username}!', 'success')
            
            next_page = request.args.get('next')
            # Protect against open redirect attacks
            if not next_page or urlsplit(next_page).netloc != '':
                next_page = url_for('employee.home')
            return redirect(next_page)
        else:
            # Record failed attempt; log username/email if exists to trace target user
            target_user_id = user.id if user else None
            AuditService.log_event('LOGIN_FAILED', user_id=target_user_id)
            flash('Invalid email or password.', 'danger')
            
    return render_template('auth/login.html', form=form)

@auth_bp.route('/logout')
@login_required
def logout():
    """Handles user logout actions."""
    uid = current_user.id
    logout_user()
    AuditService.log_event('LOGOUT', user_id=uid)
    flash('You have been logged out.', 'info')
    return redirect(url_for('auth.login'))

@auth_bp.route('/profile', methods=['GET', 'POST'])
@login_required
@active_user_required
def profile():
    """Renders profile form and handles username/email updates."""
    form = ProfileForm(original_username=current_user.username, original_email=current_user.email)
    if form.validate_on_submit():
        current_user.username = form.username.data
        current_user.email = form.email.data.lower()
        db.session.commit()
        AuditService.log_event('PROFILE_UPDATED', user_id=current_user.id)
        flash('Your profile has been updated.', 'success')
        return redirect(url_for('auth.profile'))
    elif request.method == 'GET':
        form.username.data = current_user.username
        form.email.data = current_user.email
    return render_template('auth/profile.html', form=form)

@auth_bp.route('/change-password', methods=['GET', 'POST'])
@login_required
@active_user_required
def change_password():
    """Renders change password form and commits new hash value."""
    form = ChangePasswordForm()
    if form.validate_on_submit():
        if current_user.check_password(form.current_password.data):
            current_user.set_password(form.new_password.data)
            db.session.commit()
            AuditService.log_event('PASSWORD_CHANGED', user_id=current_user.id)
            flash('Your password has been changed successfully.', 'success')
            return redirect(url_for('auth.profile'))
        else:
            flash('Invalid current password.', 'danger')
    return render_template('auth/change_password.html', form=form)
