# API Reference Guide

## Table of Contents
- [Authentication API](#authentication-api)
- [Poll API](#poll-api)
- [Vote API](#vote-api)
- [Results API](#results-api)

## Authentication API

### POST /api/auth/register
Register a new user account.

**Request Body:**
```json
{
  "username": "string (3-20 alphanumeric characters)",
  "email": "string (valid email format)",
  "password": "string (min 8 chars, letters + numbers)"
}
```

**Success Response (201):**
```json
{
  "message": "User registered successfully",
  "user": {
    "id": 1,
    "username": "johndoe",
    "email": "john@example.com"
  },
  "token": "eyJ0eXAiOiJKV1QiLCJhbGc..."
}
```

**Error Responses:**
- 400: Invalid input (username, email, or password format)
- 409: Username or email already exists

### POST /api/auth/login
Authenticate a user and receive a JWT token.

**Request Body:**
```json
{
  "username": "string",
  "password": "string"
}
```

**Success Response (200):**
```json
{
  "message": "Login successful",
  "user": {
    "id": 1,
    "username": "johndoe",
    "email": "john@example.com"
  },
  "token": "eyJ0eXAiOiJKV1QiLCJhbGc..."
}
```

**Error Responses:**
- 400: Missing username or password
- 401: Invalid credentials
- 403: Account deactivated

## Poll API

### POST /api/polls
Create a new poll (requires authentication).

**Headers:**
```
Authorization: Bearer <token>
```

**Request Body:**
```json
{
  "title": "string (max 200 chars)",
  "description": "string (max 1000 chars, optional)",
  "options": ["string", "string", ...],  // 2-10 options
  "allow_multiple_votes": boolean (optional, default: false),
  "is_anonymous": boolean (optional, default: false),
  "expires_at": "ISO 8601 datetime (optional)"
}
```

**Success Response (201):**
```json
{
  "message": "Poll created successfully",
  "poll": {
    "id": 1,
    "title": "Favorite Programming Language?",
    "description": "Vote for your favorite",
    "creator": "johndoe",
    "created_at": "2025-11-08T10:30:00",
    "expires_at": null,
    "is_active": true,
    "allow_multiple_votes": false,
    "is_anonymous": false,
    "options": [
      {"id": 1, "text": "Python"},
      {"id": 2, "text": "JavaScript"}
    ]
  }
}
```

### GET /api/polls
Get all active polls with pagination.

**Query Parameters:**
- `page`: integer (default: 1)
- `per_page`: integer (default: 10, max: 50)

**Success Response (200):**
```json
{
  "polls": [
    {
      "id": 1,
      "title": "Poll Title",
      "description": "Poll description",
      "creator": "johndoe",
      "created_at": "2025-11-08T10:30:00",
      "expires_at": null,
      "is_anonymous": false,
      "allow_multiple_votes": false,
      "options": [...]
    }
  ],
  "total": 42,
  "page": 1,
  "pages": 5
}
```

### GET /api/polls/{poll_id}
Get details of a specific poll.

**Success Response (200):**
```json
{
  "id": 1,
  "title": "Poll Title",
  "description": "Poll description",
  "creator": "johndoe",
  "created_at": "2025-11-08T10:30:00",
  "expires_at": null,
  "is_active": true,
  "is_anonymous": false,
  "allow_multiple_votes": false,
  "options": [
    {"id": 1, "text": "Option 1"},
    {"id": 2, "text": "Option 2"}
  ]
}
```

**Error Response:**
- 404: Poll not found

### DELETE /api/polls/{poll_id}
Delete a poll (only by creator, requires authentication).

**Headers:**
```
Authorization: Bearer <token>
```

**Success Response (200):**
```json
{
  "message": "Poll deleted successfully"
}
```

**Error Responses:**
- 403: Unauthorized (not poll creator)
- 404: Poll not found

### POST /api/polls/{poll_id}/close
Close a poll (only by creator, requires authentication).

**Headers:**
```
Authorization: Bearer <token>
```

**Success Response (200):**
```json
{
  "message": "Poll closed successfully"
}
```

## Vote API

### POST /api/vote
Cast a vote on a poll (requires authentication).

**Headers:**
```
Authorization: Bearer <token>
```

**Request Body:**
```json
{
  "poll_id": 1,
  "option_id": 2
}
```

**Success Response (201):**
```json
{
  "message": "Vote cast successfully",
  "vote": {
    "poll_id": 1,
    "option_id": 2,
    "voted_at": "2025-11-08T10:35:00"
  }
}
```

**Error Responses:**
- 400: Missing poll_id or option_id
- 409: User has already voted on this poll

### POST /api/vote/anonymous
Cast an anonymous vote on a poll.

**Request Body:**
```json
{
  "poll_id": 1,
  "option_id": 2
}
```

**Success Response (201):**
```json
{
  "message": "Anonymous vote cast successfully",
  "vote": {
    "poll_id": 1,
    "option_id": 2,
    "voted_at": "2025-11-08T10:35:00"
  }
}
```

**Error Response:**
- 429: Rate limit exceeded (IP has already voted)

### GET /api/vote/check/{poll_id}
Check if authenticated user has voted on a poll.

**Headers:**
```
Authorization: Bearer <token>
```

**Success Response (200):**
```json
{
  "has_voted": true,
  "vote": {
    "option_id": 2,
    "voted_at": "2025-11-08T10:35:00"
  }
}
```

### GET /api/vote/user
Get authenticated user's voting history.

**Headers:**
```
Authorization: Bearer <token>
```

**Query Parameters:**
- `page`: integer (default: 1)
- `per_page`: integer (default: 10, max: 50)

**Success Response (200):**
```json
{
  "votes": [
    {
      "poll_id": 1,
      "option_id": 2,
      "voted_at": "2025-11-08T10:35:00"
    }
  ],
  "total": 5,
  "page": 1,
  "pages": 1
}
```

## Results API

### GET /api/results/{poll_id}
Get aggregated results for a poll.

**Success Response (200):**
```json
{
  "poll_id": 1,
  "total_votes": 42,
  "results": [
    {
      "option_id": 2,
      "votes": 18,
      "percentage": 42.86
    },
    {
      "option_id": 1,
      "votes": 15,
      "percentage": 35.71
    },
    {
      "option_id": 3,
      "votes": 9,
      "percentage": 21.43
    }
  ]
}
```

### GET /api/results/{poll_id}/detailed
Get detailed results including voter information (requires authentication, creator only).

**Headers:**
```
Authorization: Bearer <token>
```

**Success Response (200):**
```json
{
  "poll_id": 1,
  "total_votes": 42,
  "results": [
    {
      "option_id": 2,
      "votes": 18,
      "percentage": 42.86,
      "voters": [
        {
          "username": "johndoe",
          "voted_at": "2025-11-08T10:35:00"
        }
      ]
    }
  ]
}
```

### GET /api/results/{poll_id}/export
Export poll results as CSV (requires authentication, creator only).

**Headers:**
```
Authorization: Bearer <token>
```

**Success Response (200):**
Returns CSV file with headers:
```
Option ID,Username,Voted At
2,johndoe,2025-11-08T10:35:00
1,janedoe,2025-11-08T10:36:00
```

### GET /api/results/stats
Get overall platform statistics.

**Success Response (200):**
```json
{
  "total_votes": 1234,
  "total_polls": 56,
  "total_voters": 89
}
```

### GET /api/results/trending
Get trending polls based on recent activity.

**Success Response (200):**
```json
{
  "trending_polls": [
    {
      "poll_id": 5,
      "recent_votes": 42
    },
    {
      "poll_id": 3,
      "recent_votes": 28
    }
  ]
}
```

## Rate Limiting

All endpoints have rate limiting enabled:

- **Registration**: 5 requests per 60 seconds per IP
- **Login**: 10 requests per 60 seconds per IP
- **Vote**: 20 requests per 60 seconds per IP
- **Anonymous Vote**: 10 requests per 60 seconds per IP
- **Other endpoints**: 100 requests per 60 seconds per IP

When rate limit is exceeded:

**Response (429):**
```json
{
  "error": "Rate limit exceeded",
  "retry_after": 60
}
```

## Error Codes

- **200**: Success
- **201**: Created
- **400**: Bad Request (invalid input)
- **401**: Unauthorized (invalid or missing token)
- **403**: Forbidden (insufficient permissions)
- **404**: Not Found
- **409**: Conflict (duplicate resource)
- **429**: Too Many Requests (rate limit)
- **500**: Internal Server Error
- **503**: Service Unavailable
- **504**: Gateway Timeout
