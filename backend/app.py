import os
from datetime import datetime, timedelta, timezone
from functools import wraps

import jwt
from flask import Flask, request, jsonify, g
from flask_cors import CORS
from sqlalchemy import or_
from werkzeug.security import generate_password_hash, check_password_hash

from models import db, Notice, User

app = Flask(__name__)
CORS(app)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///notice_board.db'
app.config['SECRET_KEY'] = os.environ.get('SECRET_KEY', 'dev-secret-change-later')
db.init_app(app)


# ---------- Login protection ----------
def login_required(admin_only=False):
    def decorator(f):
        @wraps(f)
        def wrapper(*args, **kwargs):
            auth_header = request.headers.get('Authorization', '')
            if not auth_header.startswith('Bearer '):
                return jsonify({"error": "Login required"}), 401

            token = auth_header.split(' ', 1)[1]
            try:
                payload = jwt.decode(token, app.config['SECRET_KEY'], algorithms=['HS256'])
            except jwt.ExpiredSignatureError:
                return jsonify({"error": "Session expired, please log in again"}), 401
            except jwt.InvalidTokenError:
                return jsonify({"error": "Invalid token"}), 401

            if admin_only and payload.get('role') != 'admin':
                return jsonify({"error": "Admin access required"}), 403

            g.user = payload
            return f(*args, **kwargs)
        return wrapper
    return decorator


@app.route('/')
def home():
    return {"message": "Notice Board API is running!"}


# ---------- Auth ----------
@app.route('/register', methods=['POST'])
def register():
    data = request.get_json() or {}
    name = (data.get('name') or '').strip()
    email = (data.get('email') or '').strip().lower()
    password = data.get('password') or ''

    if not name or not email or not password:
        return jsonify({"error": "Name, email and password are required"}), 400
    if len(password) < 6:
        return jsonify({"error": "Password must be at least 6 characters"}), 400
    if User.query.filter_by(email=email).first():
        return jsonify({"error": "Email already registered"}), 400

    # Public registration always creates a student
    new_user = User(
        name=name,
        email=email,
        password_hash=generate_password_hash(password),
        role='student'
    )
    db.session.add(new_user)
    db.session.commit()
    return jsonify({"message": "Registered successfully"}), 201


@app.route('/login', methods=['POST'])
def login():
    data = request.get_json() or {}
    email = (data.get('email') or '').strip().lower()
    password = data.get('password') or ''

    user = User.query.filter_by(email=email).first()
    if not user or not check_password_hash(user.password_hash, password):
        return jsonify({"error": "Invalid email or password"}), 401

    token = jwt.encode(
        {
            "user_id": user.id,
            "role": user.role,
            "exp": datetime.now(timezone.utc) + timedelta(hours=8)
        },
        app.config['SECRET_KEY'],
        algorithm='HS256'
    )

    return jsonify({
        "message": "Login successful",
        "token": token,
        "user": {"id": user.id, "name": user.name, "email": user.email, "role": user.role}
    })


# ---------- Notices ----------
@app.route('/notices', methods=['GET'])
@login_required()
def get_notices():
    category = request.args.get('category')

    query = Notice.query.filter(
        or_(Notice.expiry_date.is_(None), Notice.expiry_date > datetime.now())
    )
    if category:
        query = query.filter_by(category=category)

    notices = query.order_by(Notice.created_at.desc()).all()

    result = []
    for notice in notices:
        result.append({
            "id": notice.id,
            "title": notice.title,
            "description": notice.description,
            "category": notice.category,
            "posted_by": notice.posted_by,
            "created_at": notice.created_at,
            "expiry_date": notice.expiry_date.strftime('%Y-%m-%d') if notice.expiry_date else None
        })
    return jsonify(result)


@app.route('/notices', methods=['POST'])
@login_required(admin_only=True)
def create_notice():
    data = request.get_json() or {}

    if not data.get('title') or not data.get('description') or not data.get('category'):
        return jsonify({"error": "Title, description and category are required"}), 400

    expiry = None
    if data.get('expiry_date'):
        try:
            expiry = datetime.strptime(data['expiry_date'], '%Y-%m-%d').replace(hour=23, minute=59, second=59)
        except ValueError:
            return jsonify({"error": "expiry_date must be YYYY-MM-DD"}), 400

    new_notice = Notice(
        title=data['title'],
        description=data['description'],
        category=data['category'],
        posted_by=g.user['user_id'],
        expiry_date=expiry
    )
    db.session.add(new_notice)
    db.session.commit()
    return jsonify({"message": "Notice created successfully", "id": new_notice.id}), 201


@app.route('/notices/<int:notice_id>', methods=['PUT'])
@login_required(admin_only=True)
def update_notice(notice_id):
    notice = db.session.get(Notice, notice_id)
    if not notice:
        return jsonify({"error": "Notice not found"}), 404

    data = request.get_json() or {}
    notice.title = data.get('title', notice.title)
    notice.description = data.get('description', notice.description)
    notice.category = data.get('category', notice.category)
    db.session.commit()
    return jsonify({"message": "Notice updated successfully"})


@app.route('/notices/<int:notice_id>', methods=['DELETE'])
@login_required(admin_only=True)
def delete_notice(notice_id):
    notice = db.session.get(Notice, notice_id)
    if not notice:
        return jsonify({"error": "Notice not found"}), 404

    db.session.delete(notice)
    db.session.commit()
    return jsonify({"message": "Notice deleted successfully"})


if __name__ == '__main__':
    with app.app_context():
        db.create_all()
    app.run(debug=True)
    