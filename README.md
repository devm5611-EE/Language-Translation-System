# LinguaFlow - AI Translation Application

**AI-powered translation service supporting 100+ languages with real-time translation, language detection, and translation history.**

[![Python](https://img.shields.io/badge/Python-3.8+-blue.svg)](https://www.python.org/)
[![Flask](https://img.shields.io/badge/Flask-3.0.3-green.svg)](https://flask.palletsprojects.com/)
[![License](https://img.shields.io/badge/License-MIT-yellow.svg)](LICENSE)

---

## 📋 Table of Contents

- [Features](#-features)
- [Quick Start](#-quick-start)
- [Installation](#-installation)
- [Configuration](#-configuration)
- [Usage](#-usage)
- [API Reference](#-api-reference)
- [Development](#-development)
- [Deployment](#-deployment)
- [Troubleshooting](#-troubleshooting)
- [Contributing](#-contributing)
- [License](#-license)

---

## ✨ Features

### Core Features
- 🌍 **40+ Languages** - Translate between any language pair
- 🤖 **AI Models** - 2 Groq models (Llama 3.3 70B, Llama 3.1 8B)
- 🔍 **Auto-Detection** - Automatic source language detection
- 📚 **Translation History** - Save and search past translations
- 🎤 **Speech-to-Text** - Voice input for translations
- 🔊 **Text-to-Speech** - Listen to translations
- 📊 **Confidence Scoring** - Translation quality indicators

### Advanced Features
- 🔐 **User Authentication** - JWT-based secure authentication
- 👨‍💼 **Admin Dashboard** - Analytics and user management
- ⚡ **Rate Limiting** - 200/day, 50/hour per user
- 💾 **Caching** - Redis-based translation caching
- 📱 **Responsive Design** - Works on desktop and mobile
- 🌙 **Dark Mode** - Light and dark themes
- 🔒 **Security** - CORS, HTTPS, input validation, audit logging

---

## 🚀 Quick Start

### Prerequisites
- Python 3.8 or higher
- MongoDB Atlas account (free tier available)
- Redis Cloud account (free tier available)
- Groq API key (free tier available)

### 30-Second Setup

```bash
# 1. Clone and navigate
git clone <repository-url>
cd Language-Translation-System/linguaflow

# 2. Install dependencies
pip install -r requirements.txt

# 3. Configure environment
cp .env.example .env
# Edit .env with your credentials

# 4. Run
python app.py
```

Open browser: `http://localhost:5000`

---

## 📦 Installation

### Step 1: Clone Repository
```bash
git clone <repository-url>
cd Language-Translation-System
```

### Step 2: Create Virtual Environment
```bash
# Windows
python -m venv venv
venv\Scripts\activate

# macOS/Linux
python3 -m venv venv
source venv/bin/activate
```

### Step 3: Install Dependencies
```bash
cd linguaflow
pip install -r requirements.txt
```

### Step 4: Configure Environment
```bash
cp .env.example .env
```

Edit `.env` file with your credentials:
```bash
# Flask Configuration
FLASK_SECRET_KEY=<generate-with-command-below>
FLASK_DEBUG=True

# JWT Configuration
JWT_SECRET=<generate-with-command-below>
JWT_EXPIRY_HOURS=24

# MongoDB Configuration
MONGODB_URI=mongodb+srv://username:password@cluster.mongodb.net/linguaflow

# Groq API Configuration
GROQ_API_KEY=gsk_your_groq_api_key_here

# Redis Configuration
REDIS_URL=redis://default:password@host:port

# CORS Configuration
ALLOWED_ORIGINS=http://localhost:5000,http://127.0.0.1:5000
```

**Generate secrets:**
```bash
python -c "import secrets; print(secrets.token_urlsafe(32))"
```

### Step 5: Run Application
```bash
python app.py
```

Application starts at: `http://localhost:5000`

---

## ⚙️ Configuration

### Environment Variables

| Variable | Required | Description | Example |
|----------|----------|-------------|---------|
| `FLASK_SECRET_KEY` | Yes | Flask secret key | `<32-char-random>` |
| `JWT_SECRET` | Yes | JWT signing key | `<32-char-random>` |
| `MONGODB_URI` | Yes | MongoDB connection string | `mongodb+srv://...` |
| `GROQ_API_KEY` | Yes | Groq API key | `gsk_...` |
| `REDIS_URL` | Yes | Redis connection string | `redis://...` |
| `FLASK_DEBUG` | No | Debug mode (default: False) | `True` or `False` |
| `JWT_EXPIRY_HOURS` | No | JWT expiry (default: 24) | `24` |
| `ALLOWED_ORIGINS` | No | CORS origins | `http://localhost:5000` |

### Getting API Keys

#### MongoDB Atlas (Free)
1. Go to [mongodb.com/cloud/atlas](https://www.mongodb.com/cloud/atlas)
2. Create free account
3. Create cluster
4. Get connection string

#### Redis Cloud (Free)
1. Go to [redis.com/try-free](https://redis.com/try-free/)
2. Create free account
3. Create database
4. Get connection string

#### Groq API (Free)
1. Go to [console.groq.com](https://console.groq.com/)
2. Create account
3. Generate API key

### Current AI Models

```python
# Default Model (Recommended)
llama-3.3-70b-versatile  # Best quality, 2-3s response

# Fast Model
llama-3.1-8b-instant     # Good quality, 1-2s response
```

---

## 💻 Usage

### Web Interface

1. **Register/Login**
   - Click "Get started" or "Log in"
   - Create account or sign in

2. **Translate Text**
   - Enter text in source box
   - Select target language
   - Choose AI model (optional)
   - Click "Translate"

3. **Use Microphone**
   - Click microphone icon (🎤)
   - Allow browser permission
   - Speak clearly
   - Text appears automatically

4. **View History**
   - Click "History" in navigation
   - Search and filter translations
   - Reuse previous translations

5. **Admin Dashboard** (Admin only)
   - View platform statistics
   - Manage users
   - Monitor usage

### API Usage

#### Register User
```bash
curl -X POST http://localhost:5000/api/auth/register \
  -H "Content-Type: application/json" \
  -d '{
    "name": "John Doe",
    "email": "john@example.com",
    "password": "SecurePass123"
  }'
```

#### Login
```bash
curl -X POST http://localhost:5000/api/auth/login \
  -H "Content-Type: application/json" \
  -d '{
    "email": "john@example.com",
    "password": "SecurePass123"
  }'
```

#### Translate Text
```bash
curl -X POST http://localhost:5000/api/translate \
  -H "Authorization: Bearer YOUR_JWT_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "text": "Hello, how are you?",
    "target_lang": "es",
    "model": "llama-3.3-70b-versatile"
  }'
```

#### Get Translation History
```bash
curl -X GET http://localhost:5000/api/history \
  -H "Authorization: Bearer YOUR_JWT_TOKEN"
```

---

## 📡 API Reference

### Authentication Endpoints

#### POST `/api/auth/register`
Register new user.

**Request:**
```json
{
  "name": "John Doe",
  "email": "john@example.com",
  "password": "SecurePass123"
}
```

**Response (201):**
```json
{
  "message": "User registered successfully",
  "user_id": "507f1f77bcf86cd799439011",
  "token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9..."
}
```

#### POST `/api/auth/login`
Login user.

**Request:**
```json
{
  "email": "john@example.com",
  "password": "SecurePass123"
}
```

**Response (200):**
```json
{
  "message": "Login successful",
  "user_id": "507f1f77bcf86cd799439011",
  "token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...",
  "user": {
    "name": "John Doe",
    "email": "john@example.com",
    "is_admin": false
  }
}
```

#### POST `/api/auth/logout`
Logout user (requires authentication).

**Response (200):**
```json
{
  "message": "Logout successful"
}
```

### Translation Endpoints

#### GET `/api/translate/languages`
Get list of supported languages.

**Response (200):**
```json
{
  "languages": [
    {"code": "en", "name": "English"},
    {"code": "es", "name": "Spanish"},
    {"code": "fr", "name": "French"}
  ],
  "total": 100
}
```

#### POST `/api/translate`
Translate text (requires authentication).

**Request:**
```json
{
  "text": "Hello, how are you?",
  "target_lang": "es",
  "source_lang": "auto",
  "model": "llama-3.3-70b-versatile"
}
```

**Response (200):**
```json
{
  "translation": "Hola, ¿cómo estás?",
  "source_lang": "en",
  "target_lang": "es",
  "confidence": 0.98,
  "model_used": "llama-3.3-70b-versatile",
  "response_time_ms": 2450,
  "cache_hit": false
}
```

#### POST `/api/translate/detect`
Detect language (requires authentication).

**Request:**
```json
{
  "text": "Bonjour, comment allez-vous?"
}
```

**Response (200):**
```json
{
  "detected_language": "fr",
  "language_name": "French",
  "confidence": 0.99
}
```

### History Endpoints

#### GET `/api/history`
Get translation history (requires authentication).

**Query Parameters:**
- `page` (optional): Page number (default: 1)
- `limit` (optional): Items per page (default: 20)
- `search` (optional): Search text
- `source_lang` (optional): Filter by source language
- `target_lang` (optional): Filter by target language

**Response (200):**
```json
{
  "translations": [
    {
      "id": "507f1f77bcf86cd799439011",
      "source_text": "Hello",
      "translation": "Hola",
      "source_lang": "en",
      "target_lang": "es",
      "confidence": 0.98,
      "created_at": "2026-05-07T10:30:00Z"
    }
  ],
  "total": 150,
  "page": 1,
  "pages": 8
}
```

#### DELETE `/api/history/:id`
Delete specific translation (requires authentication).

#### DELETE `/api/history`
Clear all history (requires authentication).

#### GET `/api/history/stats`
Get user statistics (requires authentication).

### Profile Endpoints

#### GET `/api/profile`
Get user profile (requires authentication).

#### PUT `/api/profile`
Update profile (requires authentication).

#### DELETE `/api/profile`
Delete account (requires authentication).

### Admin Endpoints

#### GET `/api/admin/stats`
Get platform statistics (requires admin).

#### GET `/api/admin/users`
Get all users (requires admin).

#### PUT `/api/admin/users/:id`
Update user (requires admin).

### Health Check

#### GET `/health`
Check application health.

**Response (200):**
```json
{
  "status": "ok",
  "version": "1.0.0",
  "dependencies": {
    "mongodb": "ok",
    "redis": "ok",
    "groq_api": "configured"
  }
}
```

---

## 🛠️ Development

### Project Structure
```
linguaflow/
├── app.py                 # Flask application
├── config.py              # Configuration
├── requirements.txt       # Dependencies
├── .env                   # Environment variables
│
├── routes/                # API endpoints
│   ├── auth_routes.py
│   ├── translate_routes.py
│   ├── history_routes.py
│   ├── profile_routes.py
│   └── admin_routes.py
│
├── services/              # Business logic
│   ├── auth_service.py
│   ├── translation_service.py
│   ├── detect_service.py
│   └── analytics_service.py
│
├── models/                # Data models
│   ├── user_model.py
│   ├── translation_model.py
│   └── analytics_model.py
│
├── database/              # Database layer
│   └── mongodb.py
│
├── middleware/            # Request processing
│   └── validation.py
│
├── utils/                 # Utilities
│   ├── jwt_handler.py
│   ├── password_hash.py
│   ├── validators.py
│   └── audit_logger.py
│
├── static/                # Frontend assets
│   ├── css/
│   │   └── style.css
│   └── js/
│       ├── main.js
│       ├── auth.js
│       ├── translate.js
│       ├── history.js
│       ├── profile.js
│       └── admin.js
│
├── templates/
│   └── index.html         # Single-page app
│
└── logs/
    ├── app.log
    └── audit.log
```

### Running Tests
```bash
# Test all models
python test_translation.py

# Check health
curl http://localhost:5000/health

# Run with debug
FLASK_DEBUG=True python app.py
```

### Adding New Features

1. **Create route** in `routes/`
2. **Add service logic** in `services/`
3. **Update model** in `models/` (if needed)
4. **Register blueprint** in `app.py`
5. **Add frontend** in `static/js/`

### Code Style
- Follow PEP 8 for Python
- Use meaningful variable names
- Add docstrings to functions
- Comment complex logic

---

## 🚀 Deployment

### Docker Deployment

```bash
# Build image
docker build -t linguaflow .

# Run container
docker run -p 5000:5000 \
  -e FLASK_SECRET_KEY=your_key \
  -e JWT_SECRET=your_secret \
  -e MONGODB_URI=your_uri \
  -e GROQ_API_KEY=your_key \
  -e REDIS_URL=your_url \
  linguaflow
```

### Production Deployment

#### Using Gunicorn
```bash
# Install gunicorn
pip install gunicorn

# Run with 4 workers
gunicorn -w 4 -b 0.0.0.0:5000 app:app
```

#### Environment Setup
```bash
# Production settings
FLASK_DEBUG=False
FLASK_SECRET_KEY=<strong-random-key>
JWT_SECRET=<strong-random-key>
MONGODB_URI=<production-uri>
GROQ_API_KEY=<your-key>
REDIS_URL=<production-url>
ALLOWED_ORIGINS=https://yourdomain.com
```

#### Security Checklist
- [ ] Use HTTPS
- [ ] Set strong secrets
- [ ] Configure firewall
- [ ] Enable rate limiting
- [ ] Set up monitoring
- [ ] Configure backups
- [ ] Review logs regularly

---

## 🔧 Troubleshooting

### Common Issues

#### Issue: Application won't start
**Solution:**
```bash
# Check environment variables
python -c "from config import Config; print('Config OK')"

# Check dependencies
pip list | grep -E "flask|pymongo|groq|redis"

# Check logs
tail -f linguaflow/logs/app.log
```

#### Issue: Translation fails
**Solution:**
- Verify Groq API key is valid
- Check internet connection
- Verify model name is correct
- Check logs for errors

#### Issue: Database connection error
**Solution:**
- Verify MongoDB URI is correct
- Check IP whitelist in MongoDB Atlas
- Test connection:
```bash
python -c "from database.mongodb import get_db; get_db().admin.command('ping')"
```

#### Issue: Redis connection error
**Solution:**
- Verify Redis URL is correct
- Application will fallback to in-memory storage
- Check Redis status:
```bash
redis-cli -u $REDIS_URL ping
```

#### Issue: Microphone not working
**Solution:**
- Use Chrome, Edge, or Safari (Firefox has limited support)
- Ensure HTTPS or localhost
- Allow microphone permission in browser
- Check microphone in system settings

### Browser Support

| Browser | Desktop | Mobile | Speech Recognition |
|---------|---------|--------|-------------------|
| Chrome | ✅ Yes | ✅ Yes | ✅ Full support |
| Edge | ✅ Yes | ✅ Yes | ✅ Full support |
| Safari | ✅ Yes | ✅ Yes | ✅ Full support |
| Firefox | ✅ Yes | ⚠️ Limited | ⚠️ Limited support |

### Getting Help

1. **Check logs:**
   ```bash
   tail -f linguaflow/logs/app.log
   tail -f linguaflow/logs/audit.log
   ```

2. **Check health:**
   ```bash
   curl http://localhost:5000/health
   ```

3. **Test models:**
   ```bash
   python test_translation.py
   ```

4. **Check browser console** (F12) for frontend errors

---

## 📊 Performance

### Response Times
- **Translation:** 1-3 seconds (depending on model)
- **Cached Translation:** <100ms
- **API Response:** <500ms
- **Database Query:** <100ms

### Optimization
- ✅ Redis caching (1-hour TTL)
- ✅ Database connection pooling (10-50 connections)
- ✅ Database indexes (9 indexes)
- ✅ Rate limiting (prevents abuse)
- ✅ Response compression

### Scalability
- Horizontal scaling ready
- Stateless API design
- Load balancer compatible
- Database connection pooling

---

## 🔒 Security

### Features
- ✅ JWT authentication with token blacklist
- ✅ Password hashing with bcrypt
- ✅ CORS protection
- ✅ Rate limiting (200/day, 50/hour)
- ✅ Input validation and sanitization
- ✅ Security headers (CSP, HSTS, X-Frame-Options)
- ✅ HTTPS enforcement (production)
- ✅ Audit logging
- ✅ NoSQL injection prevention

### Best Practices
- Never commit `.env` file
- Use strong secrets (32+ characters)
- Rotate secrets regularly
- Enable HTTPS in production
- Monitor logs for suspicious activity
- Keep dependencies updated

---

## 🤝 Contributing

### How to Contribute
1. Fork the repository
2. Create feature branch (`git checkout -b feature/name`)
3. Make changes
4. Test thoroughly
5. Commit changes (`git commit -m 'Add feature'`)
6. Push to branch (`git push origin feature/name`)
7. Create Pull Request

### Code Guidelines
- Follow PEP 8 style guide
- Add tests for new features
- Update documentation
- Keep commits atomic
- Write clear commit messages

---

## 📄 License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

---

## 🙏 Acknowledgments

- **Groq** - AI language models
- **MongoDB Atlas** - Database hosting
- **Redis Cloud** - Caching service
- **Flask** - Web framework
- **Contributors** - Thank you!

---

## 📞 Support

### Resources
- **Documentation:** This README
- **Issues:** GitHub Issues
- **Email:** support@linguaflow.com

### Status
- **Version:** 1.0.0
- **Status:** ✅ Production Ready
- **Last Updated:** May 7, 2026

---

## 🎯 Roadmap

### Planned Features
- [ ] Batch translation API
- [ ] Document translation (PDF, DOCX)
- [ ] Translation memory
- [ ] Glossary management
- [ ] GraphQL API
- [ ] Webhook support
- [ ] Mobile app
- [ ] Advanced analytics

---

**Made with ❤️ by the LinguaFlow Team**

**⭐ Star this repo if you find it useful!**
