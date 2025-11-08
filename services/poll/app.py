"""
Poll Service - Handles poll creation and management
"""
from flask import Flask, request, jsonify
from flask_cors import CORS
import os
import sys
from datetime import datetime

# Add parent directory to path for shared imports
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '../..')))

from shared.database import db, init_db
from shared.auth_utils import token_required
from shared.validators import sanitize_input

app = Flask(__name__)
CORS(app)

# Configuration
app.config['SQLALCHEMY_DATABASE_URI'] = os.getenv('DATABASE_URL', 'sqlite:///poll.db')
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.config['SECRET_KEY'] = os.getenv('JWT_SECRET_KEY', 'your-secret-key-change-in-production')

# Initialize database
init_db(app)


class Poll(db.Model):
    """Poll model"""
    __tablename__ = 'polls'
    
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(200), nullable=False)
    description = db.Column(db.Text)
    creator_id = db.Column(db.Integer, nullable=False)
    creator_username = db.Column(db.String(20), nullable=False)
    created_at = db.Column(db.DateTime, default=db.func.now())
    expires_at = db.Column(db.DateTime)
    is_active = db.Column(db.Boolean, default=True)
    allow_multiple_votes = db.Column(db.Boolean, default=False)
    is_anonymous = db.Column(db.Boolean, default=False)
    
    options = db.relationship('PollOption', backref='poll', lazy=True, cascade='all, delete-orphan')


class PollOption(db.Model):
    """Poll option model"""
    __tablename__ = 'poll_options'
    
    id = db.Column(db.Integer, primary_key=True)
    poll_id = db.Column(db.Integer, db.ForeignKey('polls.id'), nullable=False)
    text = db.Column(db.String(200), nullable=False)
    order = db.Column(db.Integer, default=0)


@app.route('/health', methods=['GET'])
def health():
    """Health check endpoint"""
    return jsonify({'status': 'healthy', 'service': 'poll'}), 200


@app.route('/polls', methods=['POST'])
@token_required
def create_poll():
    """Create a new poll"""
    data = request.get_json()
    
    if not data:
        return jsonify({'error': 'No data provided'}), 400
    
    # Validate inputs
    title = sanitize_input(data.get('title', ''), 200)
    description = sanitize_input(data.get('description', ''), 1000)
    options = data.get('options', [])
    
    if not title:
        return jsonify({'error': 'Poll title is required'}), 400
    
    if not options or len(options) < 2:
        return jsonify({'error': 'At least 2 options are required'}), 400
    
    if len(options) > 10:
        return jsonify({'error': 'Maximum 10 options allowed'}), 400
    
    # Create poll
    poll = Poll(
        title=title,
        description=description,
        creator_id=request.user_id,
        creator_username=request.username,
        allow_multiple_votes=data.get('allow_multiple_votes', False),
        is_anonymous=data.get('is_anonymous', False)
    )
    
    # Add expires_at if provided
    if 'expires_at' in data:
        try:
            poll.expires_at = datetime.fromisoformat(data['expires_at'])
        except ValueError:
            return jsonify({'error': 'Invalid date format for expires_at'}), 400
    
    # Add options
    for idx, option_text in enumerate(options):
        option_text = sanitize_input(option_text, 200)
        if option_text:
            option = PollOption(text=option_text, order=idx)
            poll.options.append(option)
    
    try:
        db.session.add(poll)
        db.session.commit()
        
        return jsonify({
            'message': 'Poll created successfully',
            'poll': {
                'id': poll.id,
                'title': poll.title,
                'description': poll.description,
                'creator': poll.creator_username,
                'created_at': poll.created_at.isoformat(),
                'expires_at': poll.expires_at.isoformat() if poll.expires_at else None,
                'is_active': poll.is_active,
                'allow_multiple_votes': poll.allow_multiple_votes,
                'is_anonymous': poll.is_anonymous,
                'options': [{'id': opt.id, 'text': opt.text} for opt in poll.options]
            }
        }), 201
    except Exception as e:
        db.session.rollback()
        app.logger.error(f"Failed to create poll: {str(e)}")
        return jsonify({'error': 'Failed to create poll'}), 500


@app.route('/polls', methods=['GET'])
def get_polls():
    """Get all active polls"""
    page = request.args.get('page', 1, type=int)
    per_page = request.args.get('per_page', 10, type=int)
    
    # Limit per_page
    per_page = min(per_page, 50)
    
    polls = Poll.query.filter_by(is_active=True).order_by(Poll.created_at.desc()).paginate(
        page=page, per_page=per_page, error_out=False
    )
    
    return jsonify({
        'polls': [{
            'id': poll.id,
            'title': poll.title,
            'description': poll.description,
            'creator': poll.creator_username,
            'created_at': poll.created_at.isoformat(),
            'expires_at': poll.expires_at.isoformat() if poll.expires_at else None,
            'is_anonymous': poll.is_anonymous,
            'allow_multiple_votes': poll.allow_multiple_votes,
            'options': [{'id': opt.id, 'text': opt.text} for opt in poll.options]
        } for poll in polls.items],
        'total': polls.total,
        'page': polls.page,
        'pages': polls.pages
    }), 200


@app.route('/polls/<int:poll_id>', methods=['GET'])
def get_poll(poll_id):
    """Get a specific poll"""
    poll = Poll.query.get(poll_id)
    
    if not poll:
        return jsonify({'error': 'Poll not found'}), 404
    
    return jsonify({
        'id': poll.id,
        'title': poll.title,
        'description': poll.description,
        'creator': poll.creator_username,
        'created_at': poll.created_at.isoformat(),
        'expires_at': poll.expires_at.isoformat() if poll.expires_at else None,
        'is_active': poll.is_active,
        'is_anonymous': poll.is_anonymous,
        'allow_multiple_votes': poll.allow_multiple_votes,
        'options': [{'id': opt.id, 'text': opt.text} for opt in poll.options]
    }), 200


@app.route('/polls/<int:poll_id>', methods=['DELETE'])
@token_required
def delete_poll(poll_id):
    """Delete a poll (only by creator)"""
    poll = Poll.query.get(poll_id)
    
    if not poll:
        return jsonify({'error': 'Poll not found'}), 404
    
    if poll.creator_id != request.user_id:
        return jsonify({'error': 'Unauthorized. Only poll creator can delete'}), 403
    
    try:
        db.session.delete(poll)
        db.session.commit()
        return jsonify({'message': 'Poll deleted successfully'}), 200
    except Exception as e:
        db.session.rollback()
        app.logger.error(f"Failed to delete poll: {str(e)}")
        return jsonify({'error': 'Failed to delete poll'}), 500


@app.route('/polls/<int:poll_id>/close', methods=['POST'])
@token_required
def close_poll(poll_id):
    """Close a poll (only by creator)"""
    poll = Poll.query.get(poll_id)
    
    if not poll:
        return jsonify({'error': 'Poll not found'}), 404
    
    if poll.creator_id != request.user_id:
        return jsonify({'error': 'Unauthorized. Only poll creator can close'}), 403
    
    poll.is_active = False
    
    try:
        db.session.commit()
        return jsonify({'message': 'Poll closed successfully'}), 200
    except Exception as e:
        db.session.rollback()
        app.logger.error(f"Failed to close poll: {str(e)}")
        return jsonify({'error': 'Failed to close poll'}), 500


if __name__ == '__main__':
    import os
    debug_mode = os.getenv('FLASK_DEBUG', 'False').lower() == 'true'
    app.run(host='0.0.0.0', port=5000, debug=debug_mode)
