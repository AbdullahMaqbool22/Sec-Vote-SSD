"""
Results Service - Handles vote aggregation and results display
"""
from flask import Flask, request, jsonify
from flask_cors import CORS
import os
import sys
import redis
from collections import defaultdict

# Add parent directory to path for shared imports
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '../..')))

from shared.database import db, init_db
from shared.auth_utils import token_required

app = Flask(__name__)
CORS(app)

# Configuration
app.config['SQLALCHEMY_DATABASE_URI'] = os.getenv('DATABASE_URL', 'sqlite:///results.db')
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.config['SECRET_KEY'] = os.getenv('JWT_SECRET_KEY', 'your-secret-key-change-in-production')

# Redis configuration for caching
REDIS_URL = os.getenv('REDIS_URL', 'redis://localhost:6379/3')
try:
    redis_client = redis.from_url(REDIS_URL, decode_responses=True)
except:
    redis_client = None

# Initialize database
init_db(app)


# Import Vote model from vote service (in production, would query via API)
class Vote(db.Model):
    """Vote model (replicated from vote service for results)"""
    __tablename__ = 'votes'
    
    id = db.Column(db.Integer, primary_key=True)
    poll_id = db.Column(db.Integer, nullable=False)
    option_id = db.Column(db.Integer, nullable=False)
    user_id = db.Column(db.Integer, nullable=True)
    username = db.Column(db.String(20), nullable=True)
    voted_at = db.Column(db.DateTime, default=db.func.now())
    ip_address = db.Column(db.String(45))


@app.route('/health', methods=['GET'])
def health():
    """Health check endpoint"""
    return jsonify({'status': 'healthy', 'service': 'results'}), 200


@app.route('/results/<int:poll_id>', methods=['GET'])
def get_poll_results(poll_id):
    """Get results for a specific poll"""
    # Check cache first
    cache_key = f"results:{poll_id}"
    
    if redis_client:
        cached_results = redis_client.get(cache_key)
        if cached_results:
            import json
            return jsonify(json.loads(cached_results)), 200
    
    # Query votes from database
    votes = Vote.query.filter_by(poll_id=poll_id).all()
    
    if not votes:
        return jsonify({
            'poll_id': poll_id,
            'total_votes': 0,
            'results': []
        }), 200
    
    # Aggregate results
    vote_counts = defaultdict(int)
    for vote in votes:
        vote_counts[vote.option_id] += 1
    
    total_votes = len(votes)
    
    # Calculate percentages
    results = []
    for option_id, count in vote_counts.items():
        percentage = (count / total_votes * 100) if total_votes > 0 else 0
        results.append({
            'option_id': option_id,
            'votes': count,
            'percentage': round(percentage, 2)
        })
    
    # Sort by vote count
    results.sort(key=lambda x: x['votes'], reverse=True)
    
    response = {
        'poll_id': poll_id,
        'total_votes': total_votes,
        'results': results
    }
    
    # Cache results for 30 seconds
    if redis_client:
        import json
        redis_client.setex(cache_key, 30, json.dumps(response))
    
    return jsonify(response), 200


@app.route('/results/<int:poll_id>/detailed', methods=['GET'])
@token_required
def get_detailed_results(poll_id):
    """Get detailed results including voter information (for poll creator)"""
    # In production, verify if user is poll creator
    
    votes = Vote.query.filter_by(poll_id=poll_id).all()
    
    if not votes:
        return jsonify({
            'poll_id': poll_id,
            'total_votes': 0,
            'votes': []
        }), 200
    
    # Aggregate by option
    vote_counts = defaultdict(int)
    vote_details = defaultdict(list)
    
    for vote in votes:
        vote_counts[vote.option_id] += 1
        vote_details[vote.option_id].append({
            'username': vote.username if vote.username else 'Anonymous',
            'voted_at': vote.voted_at.isoformat()
        })
    
    total_votes = len(votes)
    
    # Build detailed results
    results = []
    for option_id, count in vote_counts.items():
        percentage = (count / total_votes * 100) if total_votes > 0 else 0
        results.append({
            'option_id': option_id,
            'votes': count,
            'percentage': round(percentage, 2),
            'voters': vote_details[option_id]
        })
    
    results.sort(key=lambda x: x['votes'], reverse=True)
    
    return jsonify({
        'poll_id': poll_id,
        'total_votes': total_votes,
        'results': results
    }), 200


@app.route('/results/<int:poll_id>/export', methods=['GET'])
@token_required
def export_results(poll_id):
    """Export poll results in CSV format"""
    # In production, verify if user is poll creator
    
    votes = Vote.query.filter_by(poll_id=poll_id).all()
    
    if not votes:
        return jsonify({'error': 'No votes found for this poll'}), 404
    
    # Create CSV data
    csv_lines = ['Option ID,Username,Voted At']
    
    for vote in votes:
        username = vote.username if vote.username else 'Anonymous'
        csv_lines.append(f"{vote.option_id},{username},{vote.voted_at.isoformat()}")
    
    csv_content = '\n'.join(csv_lines)
    
    from flask import Response
    return Response(
        csv_content,
        mimetype='text/csv',
        headers={'Content-Disposition': f'attachment;filename=poll_{poll_id}_results.csv'}
    )


@app.route('/results/stats', methods=['GET'])
def get_overall_stats():
    """Get overall voting statistics"""
    total_votes = Vote.query.count()
    
    # Get unique polls
    unique_polls = db.session.query(Vote.poll_id).distinct().count()
    
    # Get unique voters
    unique_voters = db.session.query(Vote.user_id).filter(Vote.user_id.isnot(None)).distinct().count()
    
    return jsonify({
        'total_votes': total_votes,
        'total_polls': unique_polls,
        'total_voters': unique_voters
    }), 200


@app.route('/results/trending', methods=['GET'])
def get_trending_polls():
    """Get trending polls based on recent vote activity"""
    from datetime import datetime, timedelta
    
    # Get polls with votes in the last 24 hours
    recent_cutoff = datetime.utcnow() - timedelta(hours=24)
    
    # Query votes from last 24 hours
    recent_votes = Vote.query.filter(Vote.voted_at >= recent_cutoff).all()
    
    # Count votes per poll
    poll_vote_counts = defaultdict(int)
    for vote in recent_votes:
        poll_vote_counts[vote.poll_id] += 1
    
    # Sort by vote count
    trending = sorted(poll_vote_counts.items(), key=lambda x: x[1], reverse=True)[:10]
    
    return jsonify({
        'trending_polls': [
            {'poll_id': poll_id, 'recent_votes': count}
            for poll_id, count in trending
        ]
    }), 200


if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000, debug=True)
