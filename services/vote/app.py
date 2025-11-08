"""
Vote Service - Handles vote casting and validation
"""
from flask import Flask, request, jsonify
from flask_cors import CORS
import os
import sys
import redis
from datetime import datetime

# Add parent directory to path for shared imports
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '../..')))

from shared.database import db, init_db
from shared.auth_utils import token_required

app = Flask(__name__)
CORS(app)

# Configuration
app.config['SQLALCHEMY_DATABASE_URI'] = os.getenv('DATABASE_URL', 'sqlite:///vote.db')
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.config['SECRET_KEY'] = os.getenv('JWT_SECRET_KEY', 'your-secret-key-change-in-production')

# Redis configuration for vote tracking
REDIS_URL = os.getenv('REDIS_URL', 'redis://localhost:6379/2')
try:
    redis_client = redis.from_url(REDIS_URL, decode_responses=True)
except:
    redis_client = None

# Initialize database
init_db(app)


class Vote(db.Model):
    """Vote model"""
    __tablename__ = 'votes'
    
    id = db.Column(db.Integer, primary_key=True)
    poll_id = db.Column(db.Integer, nullable=False)
    option_id = db.Column(db.Integer, nullable=False)
    user_id = db.Column(db.Integer, nullable=True)  # Null for anonymous votes
    username = db.Column(db.String(20), nullable=True)
    voted_at = db.Column(db.DateTime, default=db.func.now())
    ip_address = db.Column(db.String(45))  # For tracking (IPv4/IPv6)
    
    __table_args__ = (
        db.Index('idx_poll_user', 'poll_id', 'user_id'),
    )


@app.route('/health', methods=['GET'])
def health():
    """Health check endpoint"""
    return jsonify({'status': 'healthy', 'service': 'vote'}), 200


def check_poll_active(poll_id):
    """Check if poll is active (would normally call Poll service)"""
    # In a real implementation, this would make an HTTP request to the Poll service
    # For now, we'll assume the poll exists and is active
    return True


def has_user_voted(poll_id, user_id):
    """Check if user has already voted on this poll"""
    # Check Redis cache first
    if redis_client:
        cache_key = f"vote:{poll_id}:{user_id}"
        if redis_client.exists(cache_key):
            return True
    
    # Check database
    vote = Vote.query.filter_by(poll_id=poll_id, user_id=user_id).first()
    
    if vote:
        # Cache the result
        if redis_client:
            redis_client.setex(f"vote:{poll_id}:{user_id}", 3600, "1")
        return True
    
    return False


@app.route('/vote', methods=['POST'])
@token_required
def cast_vote():
    """Cast a vote on a poll"""
    data = request.get_json()
    
    if not data:
        return jsonify({'error': 'No data provided'}), 400
    
    poll_id = data.get('poll_id')
    option_id = data.get('option_id')
    
    if not poll_id or not option_id:
        return jsonify({'error': 'poll_id and option_id are required'}), 400
    
    # Check if poll is active
    # In production, verify with Poll service
    
    # Check if user has already voted
    if has_user_voted(poll_id, request.user_id):
        return jsonify({'error': 'You have already voted on this poll'}), 409
    
    # Create vote
    vote = Vote(
        poll_id=poll_id,
        option_id=option_id,
        user_id=request.user_id,
        username=request.username,
        ip_address=request.remote_addr
    )
    
    try:
        db.session.add(vote)
        db.session.commit()
        
        # Cache the vote
        if redis_client:
            redis_client.setex(f"vote:{poll_id}:{request.user_id}", 3600, "1")
            # Increment vote count in cache
            redis_client.incr(f"poll_votes:{poll_id}:{option_id}")
        
        return jsonify({
            'message': 'Vote cast successfully',
            'vote': {
                'poll_id': vote.poll_id,
                'option_id': vote.option_id,
                'voted_at': vote.voted_at.isoformat()
            }
        }), 201
    except Exception as e:
        db.session.rollback()
        app.logger.error(f"Failed to cast vote: {str(e)}")
        return jsonify({'error': 'Failed to cast vote'}), 500


@app.route('/vote/anonymous', methods=['POST'])
def cast_anonymous_vote():
    """Cast an anonymous vote on a poll"""
    data = request.get_json()
    
    if not data:
        return jsonify({'error': 'No data provided'}), 400
    
    poll_id = data.get('poll_id')
    option_id = data.get('option_id')
    
    if not poll_id or not option_id:
        return jsonify({'error': 'poll_id and option_id are required'}), 400
    
    # For anonymous votes, use IP-based rate limiting
    ip_address = request.remote_addr
    
    # Check if IP has voted recently (simple rate limiting)
    if redis_client:
        ip_vote_key = f"vote_ip:{poll_id}:{ip_address}"
        if redis_client.exists(ip_vote_key):
            return jsonify({'error': 'You have already voted on this poll'}), 429
    
    # Create anonymous vote
    vote = Vote(
        poll_id=poll_id,
        option_id=option_id,
        user_id=None,
        username=None,
        ip_address=ip_address
    )
    
    try:
        db.session.add(vote)
        db.session.commit()
        
        # Cache IP vote (expires in 1 hour)
        if redis_client:
            redis_client.setex(ip_vote_key, 3600, "1")
            redis_client.incr(f"poll_votes:{poll_id}:{option_id}")
        
        return jsonify({
            'message': 'Anonymous vote cast successfully',
            'vote': {
                'poll_id': vote.poll_id,
                'option_id': vote.option_id,
                'voted_at': vote.voted_at.isoformat()
            }
        }), 201
    except Exception as e:
        db.session.rollback()
        app.logger.error(f"Failed to cast anonymous vote: {str(e)}")
        return jsonify({'error': 'Failed to cast vote'}), 500


@app.route('/vote/check/<int:poll_id>', methods=['GET'])
@token_required
def check_vote_status(poll_id):
    """Check if user has voted on a specific poll"""
    has_voted = has_user_voted(poll_id, request.user_id)
    
    vote = None
    if has_voted:
        vote = Vote.query.filter_by(poll_id=poll_id, user_id=request.user_id).first()
    
    return jsonify({
        'has_voted': has_voted,
        'vote': {
            'option_id': vote.option_id,
            'voted_at': vote.voted_at.isoformat()
        } if vote else None
    }), 200


@app.route('/vote/user', methods=['GET'])
@token_required
def get_user_votes():
    """Get all votes cast by the authenticated user"""
    page = request.args.get('page', 1, type=int)
    per_page = request.args.get('per_page', 10, type=int)
    
    per_page = min(per_page, 50)
    
    votes = Vote.query.filter_by(user_id=request.user_id).order_by(Vote.voted_at.desc()).paginate(
        page=page, per_page=per_page, error_out=False
    )
    
    return jsonify({
        'votes': [{
            'poll_id': vote.poll_id,
            'option_id': vote.option_id,
            'voted_at': vote.voted_at.isoformat()
        } for vote in votes.items],
        'total': votes.total,
        'page': votes.page,
        'pages': votes.pages
    }), 200


if __name__ == '__main__':
    import os
    debug_mode = os.getenv('FLASK_DEBUG', 'False').lower() == 'true'
    app.run(host='0.0.0.0', port=5000, debug=debug_mode)
