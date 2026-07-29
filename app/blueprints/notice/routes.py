import os
from datetime import datetime, timezone
from werkzeug.utils import secure_filename
from flask import render_template, redirect, url_for, flash, request, jsonify, send_from_directory, current_app, abort
from flask_login import login_required, current_user
from sqlalchemy import or_, and_
from app.extensions import db
from app.models.notice import Notice
from app.models.notice_category import NoticeCategory
from app.models.department import Department
from app.models.user import User
from app.models.attachment import Attachment
from app.models.read_status import ReadStatus
from app.models.role import Role
from app.services.audit_service import AuditService
from app.utils.decorators import active_user_required, role_required
from app.blueprints.notice import notice_bp
from app.blueprints.notice.forms import NoticeForm, NoticeFilterForm

def is_admin_or_author(notice):
    """Helper to verify if current user is Super Admin, Dept Admin, or author of notice."""
    if not current_user.is_authenticated:
        return False
    if current_user.role and current_user.role.name in [Role.SUPER_ADMIN, Role.DEPARTMENT_ADMIN]:
        return True
    return notice.author_id == current_user.id


@notice_bp.route('/')
@login_required
@active_user_required
def index():
    """Renders all notices list view with search, filter, and tab navigation."""
    is_admin = current_user.role and current_user.role.name in [Role.SUPER_ADMIN, Role.DEPARTMENT_ADMIN]
    
    query = db.session.query(Notice)
    if not is_admin:
        now_utc = datetime.now(timezone.utc)
        query = query.filter(
            Notice.status == 'Published',
            or_(Notice.expiry_date.is_(None), Notice.expiry_date >= now_utc),
            or_(Notice.target_dept_id.is_(None), Notice.target_dept_id == current_user.department_id)
        )

    # Filters
    search_query = request.args.get('search', '').strip()
    status_filter = request.args.get('status', '').strip()
    category_id = request.args.get('category_id', type=int)
    priority = request.args.get('priority', '').strip()

    if search_query:
        query = query.filter(or_(Notice.title.ilike(f"%{search_query}%"), Notice.content.ilike(f"%{search_query}%")))
    if status_filter and is_admin:
        query = query.filter(Notice.status == status_filter)
    if category_id:
        query = query.filter(Notice.category_id == category_id)
    if priority:
        query = query.filter(Notice.priority == priority)

    page = request.args.get('page', 1, type=int)
    pagination = query.order_by(Notice.created_at.desc()).paginate(page=page, per_page=10, error_out=False)
    notices = pagination.items

    categories = NoticeCategory.query.order_by(NoticeCategory.name.asc()).all()

    return render_template(
        'notice/index.html',
        notices=notices,
        pagination=pagination,
        categories=categories,
        search_query=search_query,
        status_filter=status_filter,
        category_id=category_id,
        priority=priority,
        is_admin=is_admin
    )


@notice_bp.route('/<int:notice_id>')
@login_required
@active_user_required
def detail(notice_id):
    """
    Renders notice detail view. Automatically records ReadStatus for logged-in employees
    viewing published notices, and computes read receipt analytics for admins.
    """
    notice = Notice.query.get_or_404(notice_id)
    is_admin = is_admin_or_author(notice)

    # Authorization Check for non-published notices
    if notice.status != 'Published' and not is_admin:
        abort(403)

    # Auto-Acknowledge / Mark as Read for employee
    user_has_read = ReadStatus.query.filter_by(user_id=current_user.id, notice_id=notice.id).first()
    if not user_has_read and notice.status == 'Published':
        read_entry = ReadStatus(user_id=current_user.id, notice_id=notice.id)
        db.session.add(read_entry)
        db.session.commit()
        AuditService.log_event('NOTICE_READ', user_id=current_user.id, target_id=notice.id, target_type='Notice')
        user_has_read = read_entry

    # Compute Read Statistics for Admins
    read_stats = None
    if is_admin:
        total_read_count = ReadStatus.query.filter_by(notice_id=notice.id).count()
        # Compute target user count
        if notice.target_dept_id:
            target_user_count = User.query.filter_by(department_id=notice.target_dept_id, is_active=True).count()
        else:
            target_user_count = User.query.filter_by(is_active=True).count()

        read_percentage = round((total_read_count / target_user_count * 100), 1) if target_user_count > 0 else 0
        read_logs = ReadStatus.query.filter_by(notice_id=notice.id).order_by(ReadStatus.read_at.desc()).all()

        read_stats = {
            'total_read': total_read_count,
            'target_total': target_user_count,
            'percentage': read_percentage,
            'read_logs': read_logs
        }

    return render_template(
        'notice/detail.html',
        notice=notice,
        is_admin=is_admin,
        user_has_read=user_has_read,
        read_stats=read_stats
    )


@notice_bp.route('/create', methods=['GET', 'POST'])
@login_required
@active_user_required
@role_required(Role.SUPER_ADMIN, Role.DEPARTMENT_ADMIN)
def create():
    """Handles notice creation with file attachments and audit logging."""
    form = NoticeForm()

    # Dynamic Choice Population
    form.category_id.choices = [(c.id, c.name) for c in NoticeCategory.query.order_by(NoticeCategory.name.asc()).all()]
    depts = [(0, 'All Departments (Company-wide)')] + [(d.id, f"{d.name} ({d.code})") for d in Department.query.order_by(Department.name.asc()).all()]
    form.target_dept_id.choices = depts

    if form.validate_on_submit():
        target_dept = form.target_dept_id.data if form.target_dept_id.data != 0 else None
        
        notice = Notice(
            title=form.title.data,
            content=form.content.data,
            author_id=current_user.id,
            category_id=form.category_id.data,
            target_dept_id=target_dept,
            priority=form.priority.data,
            status=form.status.data,
            expiry_date=form.expiry_date.data
        )
        db.session.add(notice)
        db.session.flush()  # Generate notice.id for attachments

        # Handle File Attachments Upload
        uploaded_files = request.files.getlist('attachments')
        upload_folder = os.path.join(current_app.root_path, 'static', 'uploads', 'attachments')
        os.makedirs(upload_folder, exist_ok=True)

        for file in uploaded_files:
            if file and file.filename:
                orig_filename = secure_filename(file.filename)
                if orig_filename:
                    unique_filename = f"{notice.id}_{int(datetime.now().timestamp())}_{orig_filename}"
                    save_path = os.path.join(upload_folder, unique_filename)
                    file.save(save_path)
                    file_size = os.path.getsize(save_path)

                    attachment = Attachment(
                        notice_id=notice.id,
                        s3_key=unique_filename,
                        filename=orig_filename,
                        file_size=file_size
                    )
                    db.session.add(attachment)

        db.session.commit()
        AuditService.log_event('NOTICE_CREATED', user_id=current_user.id, target_id=notice.id, target_type='Notice')
        flash(f'Notice "{notice.title}" has been created successfully.', 'success')
        return redirect(url_for('notice.detail', notice_id=notice.id))

    return render_template('notice/create.html', form=form)


@notice_bp.route('/<int:notice_id>/edit', methods=['GET', 'POST'])
@login_required
@active_user_required
def edit(notice_id):
    """Handles editing an existing notice."""
    notice = Notice.query.get_or_404(notice_id)
    if not is_admin_or_author(notice):
        abort(403)

    form = NoticeForm()
    form.category_id.choices = [(c.id, c.name) for c in NoticeCategory.query.order_by(NoticeCategory.name.asc()).all()]
    depts = [(0, 'All Departments (Company-wide)')] + [(d.id, f"{d.name} ({d.code})") for d in Department.query.order_by(Department.name.asc()).all()]
    form.target_dept_id.choices = depts

    if form.validate_on_submit():
        notice.title = form.title.data
        notice.content = form.content.data
        notice.category_id = form.category_id.data
        notice.target_dept_id = form.target_dept_id.data if form.target_dept_id.data != 0 else None
        notice.priority = form.priority.data
        notice.status = form.status.data
        notice.expiry_date = form.expiry_date.data

        # Handle New Attachments Upload
        uploaded_files = request.files.getlist('attachments')
        upload_folder = os.path.join(current_app.root_path, 'static', 'uploads', 'attachments')
        os.makedirs(upload_folder, exist_ok=True)

        for file in uploaded_files:
            if file and file.filename:
                orig_filename = secure_filename(file.filename)
                if orig_filename:
                    unique_filename = f"{notice.id}_{int(datetime.now().timestamp())}_{orig_filename}"
                    save_path = os.path.join(upload_folder, unique_filename)
                    file.save(save_path)
                    file_size = os.path.getsize(save_path)

                    attachment = Attachment(
                        notice_id=notice.id,
                        s3_key=unique_filename,
                        filename=orig_filename,
                        file_size=file_size
                    )
                    db.session.add(attachment)

        db.session.commit()
        AuditService.log_event('NOTICE_UPDATED', user_id=current_user.id, target_id=notice.id, target_type='Notice')
        flash('Notice updated successfully.', 'success')
        return redirect(url_for('notice.detail', notice_id=notice.id))

    elif request.method == 'GET':
        form.title.data = notice.title
        form.content.data = notice.content
        form.category_id.data = notice.category_id
        form.target_dept_id.data = notice.target_dept_id if notice.target_dept_id else 0
        form.priority.data = notice.priority
        form.status.data = notice.status
        form.expiry_date.data = notice.expiry_date

    return render_template('notice/edit.html', form=form, notice=notice)


@notice_bp.route('/<int:notice_id>/delete', methods=['POST'])
@login_required
@active_user_required
def delete(notice_id):
    """Handles notice deletion."""
    notice = Notice.query.get_or_404(notice_id)
    if not is_admin_or_author(notice):
        abort(403)

    title = notice.title
    db.session.delete(notice)
    db.session.commit()

    AuditService.log_event('NOTICE_DELETED', user_id=current_user.id, target_id=notice_id, target_type='Notice')
    flash(f'Notice "{title}" has been deleted.', 'info')
    
    if current_user.role and current_user.role.name in [Role.SUPER_ADMIN, Role.DEPARTMENT_ADMIN]:
        return redirect(url_for('admin.dashboard'))
    return redirect(url_for('employee.home'))


@notice_bp.route('/<int:notice_id>/toggle-status', methods=['POST'])
@login_required
@active_user_required
def toggle_status(notice_id):
    """Toggles notice publication status between Draft and Published."""
    notice = Notice.query.get_or_404(notice_id)
    if not is_admin_or_author(notice):
        abort(403)

    if notice.status == 'Published':
        notice.status = 'Draft'
    else:
        notice.status = 'Published'

    db.session.commit()
    AuditService.log_event('NOTICE_STATUS_TOGGLED', user_id=current_user.id, target_id=notice.id, target_type='Notice')
    flash(f'Notice status changed to {notice.status}.', 'success')
    return redirect(request.referrer or url_for('admin.dashboard'))


@notice_bp.route('/<int:notice_id>/acknowledge', methods=['POST'])
@login_required
@active_user_required
def acknowledge(notice_id):
    """Records read acknowledgement for an employee."""
    notice = Notice.query.get_or_404(notice_id)
    existing = ReadStatus.query.filter_by(user_id=current_user.id, notice_id=notice.id).first()

    if not existing:
        read_entry = ReadStatus(user_id=current_user.id, notice_id=notice.id)
        db.session.add(read_entry)
        db.session.commit()
        AuditService.log_event('NOTICE_READ', user_id=current_user.id, target_id=notice.id, target_type='Notice')

    if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
        return jsonify({'success': True, 'message': 'Notice acknowledged as read.'})

    flash('Notice marked as read.', 'success')
    return redirect(url_for('employee.home'))


@notice_bp.route('/attachment/<int:attachment_id>/download')
@login_required
@active_user_required
def download_attachment(attachment_id):
    """Serves uploaded file attachments for download."""
    attachment = Attachment.query.get_or_404(attachment_id)
    upload_folder = os.path.join(current_app.root_path, 'static', 'uploads', 'attachments')
    return send_from_directory(
        upload_folder,
        attachment.s3_key,
        as_attachment=True,
        download_name=attachment.filename
    )


@notice_bp.route('/attachment/<int:attachment_id>/delete', methods=['POST'])
@login_required
@active_user_required
def delete_attachment(attachment_id):
    """Deletes an attachment file."""
    attachment = Attachment.query.get_or_404(attachment_id)
    notice = attachment.notice
    if not is_admin_or_author(notice):
        abort(403)

    upload_folder = os.path.join(current_app.root_path, 'static', 'uploads', 'attachments')
    file_path = os.path.join(upload_folder, attachment.s3_key)
    if os.path.exists(file_path):
        os.remove(file_path)

    db.session.delete(attachment)
    db.session.commit()

    flash(f'Attachment "{attachment.filename}" removed.', 'info')
    return redirect(url_for('notice.edit', notice_id=notice.id))
