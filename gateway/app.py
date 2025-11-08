"""
API Gateway - Routes requests to appropriate microservices
"""
from flask import Flask, request, jsonify, Response
from flask_cors import CORS
import requests
import os
from functools import wraps

app = Flask(__name__)
CORS(app)

# Service URLs
AUTH_SERVICE_URL = os.getenv('AUTH_SERVICE_URL', 'http://localhost:5001')
POLL_SERVICE_URL = os.getenv('POLL_SERVICE_URL', 'http://localhost:5002')
VOTE_SERVICE_URL = os.getenv('VOTE_SERVICE_URL', 'http://localhost:5003')
RESULTS_SERVICE_URL = os.getenv('RESULTS_SERVICE_URL', 'http://localhost:5004')

# Rate limiting configuration
from collections import defaultdict
from datetime import datetime, timedelta
import threading

request_counts = defaultdict(list)
rate_limit_lock = threading.Lock()


def rate_limit(max_requests=100, window_seconds=60):
    """Simple rate limiting decorator"""
    def decorator(f):
        @wraps(f)
        def wrapped(*args, **kwargs):
            client_ip = request.remote_addr
            current_time = datetime.utcnow()
            
            with rate_limit_lock:
                # Clean old requests
                request_counts[client_ip] = [
                    req_time for req_time in request_counts[client_ip]
                    if current_time - req_time < timedelta(seconds=window_seconds)
                ]
                
                # Check rate limit
                if len(request_counts[client_ip]) >= max_requests:
                    return jsonify({
                        'error': 'Rate limit exceeded',
                        'retry_after': window_seconds
                    }), 429
                
                # Add current request
                request_counts[client_ip].append(current_time)
            
            return f(*args, **kwargs)
        return wrapped
    return decorator


def forward_request(service_url, path, method='GET', json_data=None, headers=None):
    """Forward request to a microservice"""
    url = f"{service_url}{path}"
    
    try:
        if method == 'GET':
            response = requests.get(url, headers=headers, timeout=10)
        elif method == 'POST':
            response = requests.post(url, json=json_data, headers=headers, timeout=10)
        elif method == 'DELETE':
            response = requests.delete(url, headers=headers, timeout=10)
        elif method == 'PUT':
            response = requests.put(url, json=json_data, headers=headers, timeout=10)
        else:
            return jsonify({'error': 'Unsupported method'}), 400
        
        return Response(
            response.content,
            status=response.status_code,
            content_type=response.headers.get('content-type', 'application/json')
        )
    except requests.exceptions.Timeout:
        return jsonify({'error': 'Service timeout'}), 504
    except requests.exceptions.ConnectionError:
        return jsonify({'error': 'Service unavailable'}), 503
    except Exception as e:
        return jsonify({'error': 'Internal gateway error', 'details': str(e)}), 500


@app.route('/', methods=['GET'])
def home():
    """Gateway home endpoint"""
    return jsonify({
        'service': 'Sec-Vote API Gateway',
        'version': '1.0.0',
        'endpoints': {
            'auth': '/api/auth/*',
            'polls': '/api/polls/*',
            'vote': '/api/vote/*',
            'results': '/api/results/*'
        }
    }), 200


@app.route('/health', methods=['GET'])
def health():
    """Health check endpoint"""
    services_health = {}
    
    # Check each service
    for service_name, service_url in [
        ('auth', AUTH_SERVICE_URL),
        ('poll', POLL_SERVICE_URL),
        ('vote', VOTE_SERVICE_URL),
        ('results', RESULTS_SERVICE_URL)
    ]:
        try:
            response = requests.get(f"{service_url}/health", timeout=2)
            services_health[service_name] = 'healthy' if response.status_code == 200 else 'unhealthy'
        except:
            services_health[service_name] = 'unreachable'
    
    overall_healthy = all(status == 'healthy' for status in services_health.values())
    
    return jsonify({
        'status': 'healthy' if overall_healthy else 'degraded',
        'services': services_health
    }), 200 if overall_healthy else 503


# Authentication Routes
@app.route('/api/auth/register', methods=['POST'])
@rate_limit(max_requests=5, window_seconds=60)
def register():
    """Register a new user"""
    return forward_request(AUTH_SERVICE_URL, '/register', 'POST', request.get_json())


@app.route('/api/auth/login', methods=['POST'])
@rate_limit(max_requests=10, window_seconds=60)
def login():
    """Login user"""
    return forward_request(AUTH_SERVICE_URL, '/login', 'POST', request.get_json())


# Poll Routes
@app.route('/api/polls', methods=['GET', 'POST'])
@rate_limit()
def polls():
    """Get all polls or create a new poll"""
    headers = {'Authorization': request.headers.get('Authorization')}
    
    if request.method == 'GET':
        # Add query parameters
        query_params = f"?page={request.args.get('page', 1)}&per_page={request.args.get('per_page', 10)}"
        return forward_request(POLL_SERVICE_URL, f'/polls{query_params}', 'GET', headers=headers)
    else:
        return forward_request(POLL_SERVICE_URL, '/polls', 'POST', request.get_json(), headers)


@app.route('/api/polls/<int:poll_id>', methods=['GET', 'DELETE'])
@rate_limit()
def poll_detail(poll_id):
    """Get or delete a specific poll"""
    headers = {'Authorization': request.headers.get('Authorization')}
    
    if request.method == 'GET':
        return forward_request(POLL_SERVICE_URL, f'/polls/{poll_id}', 'GET', headers=headers)
    else:
        return forward_request(POLL_SERVICE_URL, f'/polls/{poll_id}', 'DELETE', headers=headers)


@app.route('/api/polls/<int:poll_id>/close', methods=['POST'])
@rate_limit()
def close_poll(poll_id):
    """Close a poll"""
    headers = {'Authorization': request.headers.get('Authorization')}
    return forward_request(POLL_SERVICE_URL, f'/polls/{poll_id}/close', 'POST', headers=headers)


# Vote Routes
@app.route('/api/vote', methods=['POST'])
@rate_limit(max_requests=20, window_seconds=60)
def vote():
    """Cast a vote"""
    headers = {'Authorization': request.headers.get('Authorization')}
    return forward_request(VOTE_SERVICE_URL, '/vote', 'POST', request.get_json(), headers)


@app.route('/api/vote/anonymous', methods=['POST'])
@rate_limit(max_requests=10, window_seconds=60)
def anonymous_vote():
    """Cast an anonymous vote"""
    return forward_request(VOTE_SERVICE_URL, '/vote/anonymous', 'POST', request.get_json())


@app.route('/api/vote/check/<int:poll_id>', methods=['GET'])
@rate_limit()
def check_vote(poll_id):
    """Check if user has voted on a poll"""
    headers = {'Authorization': request.headers.get('Authorization')}
    return forward_request(VOTE_SERVICE_URL, f'/vote/check/{poll_id}', 'GET', headers=headers)


@app.route('/api/vote/user', methods=['GET'])
@rate_limit()
def user_votes():
    """Get user's voting history"""
    headers = {'Authorization': request.headers.get('Authorization')}
    query_params = f"?page={request.args.get('page', 1)}&per_page={request.args.get('per_page', 10)}"
    return forward_request(VOTE_SERVICE_URL, f'/vote/user{query_params}', 'GET', headers=headers)


# Results Routes
@app.route('/api/results/<int:poll_id>', methods=['GET'])
@rate_limit()
def results(poll_id):
    """Get poll results"""
    return forward_request(RESULTS_SERVICE_URL, f'/results/{poll_id}', 'GET')


@app.route('/api/results/<int:poll_id>/detailed', methods=['GET'])
@rate_limit()
def detailed_results(poll_id):
    """Get detailed poll results"""
    headers = {'Authorization': request.headers.get('Authorization')}
    return forward_request(RESULTS_SERVICE_URL, f'/results/{poll_id}/detailed', 'GET', headers=headers)


@app.route('/api/results/<int:poll_id>/export', methods=['GET'])
@rate_limit()
def export_results(poll_id):
    """Export poll results"""
    headers = {'Authorization': request.headers.get('Authorization')}
    return forward_request(RESULTS_SERVICE_URL, f'/results/{poll_id}/export', 'GET', headers=headers)


@app.route('/api/results/stats', methods=['GET'])
@rate_limit()
def stats():
    """Get overall statistics"""
    return forward_request(RESULTS_SERVICE_URL, '/results/stats', 'GET')


@app.route('/api/results/trending', methods=['GET'])
@rate_limit()
def trending():
    """Get trending polls"""
    return forward_request(RESULTS_SERVICE_URL, '/results/trending', 'GET')


if __name__ == '__main__':
    app.run(host='0.0.0.0', port=8080, debug=True)
