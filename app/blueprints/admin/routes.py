from datetime import datetime, timezone
from flask import render_template, request, redirect, url_for, flash
from flask_login import login_required, current_user
from sqlalchemy import func, event
from app.extensions import db
from app.models.notice import Notice
from app.models.user import User
from app.models.department import Department
from app.models.notice_category import NoticeCategory
from app.models.read_status import ReadStatus
from app.models.audit_log import AuditLog
from app.models.role import Role
from app.utils.decorators import active_user_required, role_required
from app.blueprints.admin import admin_bp

# Auto-increment fallback handler for SQLite compatibility with BigInteger primary key
@event.listens_for(AuditLog, 'before_insert')
def auto_assign_audit_log_id(mapper, connection, target):
    if target.id is None:
        max_id = connection.execute(db.select(func.max(AuditLog.id))).scalar()
        target.id = (max_id or 0) + 1


@admin_bp.route('/')
@admin_bp.route('/dashboard')
@login_required
@active_user_required
@role_required(Role.SUPER_ADMIN, Role.DEPARTMENT_ADMIN)
def dashboard():
    """
    Renders the central Administrative Dashboard displaying key corporate metrics,
    system statistics, and recent notice management lists.
    """
    is_super_admin = current_user.role and current_user.role.name == Role.SUPER_ADMIN
    user_dept_id = current_user.department_id

    # Filter base query according to role scope
    notice_base_query = db.session.query(Notice)
    if not is_super_admin and user_dept_id:
        notice_base_query = notice_base_query.filter(
            (Notice.target_dept_id == user_dept_id) | (Notice.author_id == current_user.id)
        )

    # Compute Statistics
    total_notices = notice_base_query.count()
    published_notices = notice_base_query.filter(Notice.status == 'Published').count()
    draft_notices = notice_base_query.filter(Notice.status == 'Draft').count()
    archived_notices = notice_base_query.filter(Notice.status == 'Archived').count()

    total_users = User.query.count()
    total_departments = Department.query.count()
    total_categories = NoticeCategory.query.count()
    total_reads = ReadStatus.query.count()

    # Search and Filter Parameters
    search_query = request.args.get('search', '').strip()
    status_filter = request.args.get('status', '').strip()
    priority_filter = request.args.get('priority', '').strip()
    category_filter = request.args.get('category_id', type=int)
    department_filter = request.args.get('department_id', type=int)

    # Build Recent Notices Query with filters
    recent_query = notice_base_query

    if search_query:
        recent_query = recent_query.filter(
            Notice.title.ilike(f"%{search_query}%") | Notice.content.ilike(f"%{search_query}%")
        )
    if status_filter:
        recent_query = recent_query.filter(Notice.status == status_filter)
    if priority_filter:
        recent_query = recent_query.filter(Notice.priority == priority_filter)
    if category_filter:
        recent_query = recent_query.filter(Notice.category_id == category_filter)
    if department_filter:
        recent_query = recent_query.filter(Notice.target_dept_id == department_filter)

    # Pagination
    page = request.args.get('page', 1, type=int)
    per_page = 10
    pagination = recent_query.order_by(Notice.created_at.desc()).paginate(page=page, per_page=per_page, error_out=False)
    recent_notices = pagination.items

    # Choices for Filters
    categories = NoticeCategory.query.order_by(NoticeCategory.name.asc()).all()
    departments = Department.query.order_by(Department.name.asc()).all()

    stats = {
        'total_notices': total_notices,
        'published_notices': published_notices,
        'draft_notices': draft_notices,
        'archived_notices': archived_notices,
        'total_users': total_users,
        'total_departments': total_departments,
        'total_categories': total_categories,
        'total_reads': total_reads
    }

    return render_template(
        'admin/dashboard.html',
        stats=stats,
        notices=recent_notices,
        pagination=pagination,
        categories=categories,
        departments=departments,
        search_query=search_query,
        status_filter=status_filter,
        priority_filter=priority_filter,
        category_filter=category_filter,
        department_filter=department_filter,
        is_super_admin=is_super_admin,
        now=datetime.now(timezone.utc)
    )
