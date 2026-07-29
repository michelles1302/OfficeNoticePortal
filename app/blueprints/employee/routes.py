from datetime import datetime, timezone
from flask import render_template, request, redirect, url_for, flash
from flask_login import login_required, current_user
from sqlalchemy import or_, and_
from app.extensions import db
from app.models.notice import Notice
from app.models.notice_category import NoticeCategory
from app.models.read_status import ReadStatus
from app.utils.decorators import active_user_required
from app.blueprints.employee import employee_bp

@employee_bp.route('/')
@login_required
@active_user_required
def home():
    """
    Renders the primary Employee Notice Feed dashboard displaying company-wide
    and department-targeted announcements, acknowledgement badges, and filtering.
    """
    user_dept_id = current_user.department_id
    now_utc = datetime.now(timezone.utc)

    # 1. Base Query: Only Published and Non-Expired notices targeted to user's dept or ALL depts
    base_query = db.session.query(Notice).filter(
        Notice.status == 'Published',
        or_(Notice.expiry_date.is_(None), Notice.expiry_date >= now_utc),
        or_(Notice.target_dept_id.is_(None), Notice.target_dept_id == user_dept_id)
    )

    # 2. Extract Read Statuses for current user
    user_read_records = db.session.query(ReadStatus.notice_id).filter(
        ReadStatus.user_id == current_user.id
    ).all()
    read_notice_ids = {r[0] for r in user_read_records}

    # 3. Calculate Personalized Dashboard Metrics
    all_targeted_notices = base_query.all()
    total_targeted = len(all_targeted_notices)
    unread_count = sum(1 for n in all_targeted_notices if n.id not in read_notice_ids)
    high_priority_unread = sum(1 for n in all_targeted_notices if n.id not in read_notice_ids and n.priority == 'High')

    # 4. Filters
    search_query = request.args.get('search', '').strip()
    category_id = request.args.get('category_id', type=int)
    priority = request.args.get('priority', '').strip()
    read_filter = request.args.get('read_status', 'all').strip()

    filtered_query = base_query

    if search_query:
        filtered_query = filtered_query.filter(
            or_(
                Notice.title.ilike(f"%{search_query}%"),
                Notice.content.ilike(f"%{search_query}%")
            )
        )

    if category_id:
        filtered_query = filtered_query.filter(Notice.category_id == category_id)

    if priority:
        filtered_query = filtered_query.filter(Notice.priority == priority)

    if read_filter == 'unread':
        if read_notice_ids:
            filtered_query = filtered_query.filter(~Notice.id.in_(read_notice_ids))
    elif read_filter == 'read':
        if read_notice_ids:
            filtered_query = filtered_query.filter(Notice.id.in_(read_notice_ids))
        else:
            filtered_query = filtered_query.filter(Notice.id == -1)  # No read notices

    # 5. Pagination
    page = request.args.get('page', 1, type=int)
    per_page = 9
    pagination = filtered_query.order_by(Notice.created_at.desc()).paginate(page=page, per_page=per_page, error_out=False)
    notices = pagination.items

    categories = NoticeCategory.query.order_by(NoticeCategory.name.asc()).all()

    stats = {
        'total_targeted': total_targeted,
        'unread_count': unread_count,
        'high_priority_unread': high_priority_unread
    }

    return render_template(
        'employee/dashboard.html',
        notices=notices,
        pagination=pagination,
        stats=stats,
        categories=categories,
        read_notice_ids=read_notice_ids,
        search_query=search_query,
        category_id=category_id,
        priority=priority,
        read_filter=read_filter
    )
