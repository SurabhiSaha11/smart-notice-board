from flask import Flask, request, jsonify
from models import db, Notice, User
from datetime import datetime

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///notice_board.db'
db.init_app(app)

@app.route('/')
def home():
    return {"message": "Notice Board API is running!"}

# CREATE a notice
@app.route('/notices', methods=['POST'])
def create_notice():
    data = request.get_json()
    
    new_notice = Notice(
        title=data['title'],
        description=data['description'],
        category=data['category'],
        posted_by=data['posted_by']
    )
    
    db.session.add(new_notice)
    db.session.commit()
    
    return jsonify({"message": "Notice created successfully", "id": new_notice.id}), 201

# GET all notices (with optional category filter)
@app.route('/notices', methods=['GET'])
def get_notices():
    category = request.args.get('category')
    
    if category:
        notices = Notice.query.filter_by(category=category).order_by(Notice.created_at.desc()).all()
    else:
        notices = Notice.query.order_by(Notice.created_at.desc()).all()
    
    result = []
    for notice in notices:
        result.append({
            "id": notice.id,
            "title": notice.title,
            "description": notice.description,
            "category": notice.category,
            "posted_by": notice.posted_by,
            "created_at": notice.created_at
        })
    
    return jsonify(result)

# UPDATE a notice
@app.route('/notices/<int:notice_id>', methods=['PUT'])
def update_notice(notice_id):
    notice = Notice.query.get(notice_id)
    
    if not notice:
        return jsonify({"error": "Notice not found"}), 404
    
    data = request.get_json()
    
    notice.title = data.get('title', notice.title)
    notice.description = data.get('description', notice.description)
    notice.category = data.get('category', notice.category)
    
    db.session.commit()
    
    return jsonify({"message": "Notice updated successfully"})

# DELETE a notice
@app.route('/notices/<int:notice_id>', methods=['DELETE'])
def delete_notice(notice_id):
    notice = Notice.query.get(notice_id)
    
    if not notice:
        return jsonify({"error": "Notice not found"}), 404
    
    db.session.delete(notice)
    db.session.commit()
    
    return jsonify({"message": "Notice deleted successfully"})

# CREATE a user (simple registration)
@app.route('/users', methods=['POST'])
def create_user():
    data = request.get_json()
    
    existing_user = User.query.filter_by(email=data['email']).first()
    if existing_user:
        return jsonify({"error": "Email already registered"}), 400
    
    new_user = User(
        name=data['name'],
        email=data['email'],
        role=data['role']
    )
    
    db.session.add(new_user)
    db.session.commit()
    
    return jsonify({"message": "User created successfully", "id": new_user.id}), 201

# LOGIN (simple version - no password yet, just email lookup)
@app.route('/login', methods=['POST'])
def login():
    data = request.get_json()
    
    user = User.query.filter_by(email=data['email']).first()
    
    if not user:
        return jsonify({"error": "User not found"}), 404
    
    return jsonify({
        "message": "Login successful",
        "user": {
            "id": user.id,
            "name": user.name,
            "email": user.email,
            "role": user.role
        }
    })

if __name__ == '__main__':
    with app.app_context():
        db.create_all()
    app.run(debug=True)
