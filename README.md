# LinguaFlow - AI Translation Application

**AI-powered translation service supporting 100+ languages with real-time translation, language detection, and translation history.**

---

## 🚀 Quick Start

### Prerequisites
- Python 3.8+
- MongoDB Atlas account
- Redis Cloud account
- Groq API key

### Installation

```bash
# 1. Clone repository
git clone <repository-url>
cd Language-Translation-System

# 2. Create virtual environment
cd linguaflow
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate

# 3. Install dependencies
pip install -r requirements.txt

# 4. Configure environment
cp .env.example .env
# Edit .env with your credentials

# 5. Run application
python app.py
```

Application will start at: `http://localhost:5000`

---

## 📚 Documentation

### Essential Guides
- **[QUICK_START.md](QUICK_START.md)** - 30-second setup guide
- **[QUICK_REFERENCE.md](QUICK_REFERENCE.md)** - Quick command reference
- **[CURRENT_STATUS.md](CURRENT_STATUS.md)** - Current system status

### Technical Documentation
- **[API_REFERENCE.md](API_REFERENCE.md)** - Complete API documentation
- **[DEVELOPER_GUIDE.md](DEVELOPER_GUIDE.md)** - Development guide
- **[TRANSLATION_GUIDE.md](TRANSLATION_GUIDE.md)** - Translation features guide

### Deployment & Operations
- **[DEPLOYMENT_CHECKLIST.md](DEPLOYMENT_CHECKLIST.md)** - Deployment guide
- **[FINAL_SUMMARY.md](FINAL_SUMMARY.md)** - Project completion summary

### Troubleshooting
- **[GROQ_MODELS_FINAL_UPDATE.md](GROQ_MODELS_FINAL_UPDATE.md)** - Model configuration
- **[MICROPHONE_TROUBLESHOOTING.md](MICROPHONE_TROUBLESHOOTING.md)** - Mic feature guide

---

## ✨ Features

### Core Features
- ✅ **100+ Languages** - Translate between any language pair
- ✅ **AI Models** - 2 Groq models (Llama 3.3 70B, Llama 3.1 8B)
- ✅ **Auto-Detection** - Automatic source language detection
- ✅ **Translation History** - Save and search past translations
- ✅ **Speech-to-Text** - Voice input for translations
- ✅ **Text-to-Speech** - Listen to translations

### Advanced Features
- ✅ **User Authentication** - JWT-based secure authentication
- ✅ **Admin Dashboard** - Analytics and user management
- ✅ **Rate Limiting** - 200/day, 50/hour per user
- ✅ **Caching** - Redis-based translation caching
- ✅ **Responsive Design** - Works on desktop and mobile
- ✅ **Dark Mode** - Light and dark themes

---

## 🔧 Configuration

### Environment Variables

Required variables in `.env`:

```bash
# Flask
FLASK_SECRET_KEY=<generate-with-secrets>
FLASK_DEBUG=False

# JWT
JWT_SECRET=<generate-with-secrets>
JWT_EXPIRY_HOURS=24

# MongoDB
MONGODB_URI=<your-mongodb-atlas-uri>

# Groq API
GROQ_API_KEY=<your-groq-api-key>

# Redis
REDIS_URL=<your-redis-cloud-url>

# CORS
ALLOWED_ORIGINS=http://localhost:5000,https://yourdomain.com
```

### Current Models

```python
# Default: Llama 3.3 70B (Best quality)
# Alternative: Llama 3.1 8B (Fast)
```

---

## 📊 API Endpoints

### Authentication
- `POST /api/auth/register` - Register user
- `POST /api/auth/login` - Login user
- `POST /api/auth/logout` - Logout user

### Translation
- `GET /api/translate/languages` - Get supported languages
- `POST /api/translate` - Translate text
- `POST /api/translate/detect` - Detect language

### History
- `GET /api/history` - Get translation history
- `DELETE /api/history/:id` - Delete translation
- `DELETE /api/history` - Clear all history
- `GET /api/history/stats` - Get user statistics

### Profile
- `GET /api/profile` - Get user profile
- `PUT /api/profile` - Update profile
- `DELETE /api/profile` - Delete account

### Admin
- `GET /api/admin/stats` - Get platform statistics
- `GET /api/admin/users` - Get all users
- `PUT /api/admin/users/:id` - Update user

### Health
- `GET /health` - Health check

---

## 🧪 Testing

### Test All Models
```bash
python test_translation.py
```

### Test API
```bash
curl -X POST http://localhost:5000/api/translate \
  -H "Authorization: Bearer TOKEN" \
  -H "Content-Type: application/json" \
  -d '{"text":"Hello","target_lang":"es"}'
```

### Check Health
```bash
curl http://localhost:5000/health
```

---

## 🚀 Deployment

### Docker
```bash
docker build -t linguaflow .
docker run -p 5000:5000 linguaflow
```

### Production
```bash
# Use Gunicorn
gunicorn -w 4 -b 0.0.0.0:5000 app:app
```

See [DEPLOYMENT_CHECKLIST.md](DEPLOYMENT_CHECKLIST.md) for complete guide.

---

## 🔒 Security

- ✅ JWT authentication
- ✅ Password hashing (bcrypt)
- ✅ CORS protection
- ✅ Rate limiting
- ✅ Input validation
- ✅ Security headers
- ✅ Audit logging

---

## 📈 Performance

- **Translation:** 1-3 seconds
- **Cached:** <100ms
- **API Response:** <500ms
- **Cache Hit Rate:** 40-60%

---

## 🌐 Browser Support

| Browser | Desktop | Mobile |
|---------|---------|--------|
| Chrome | ✅ Yes | ✅ Yes |
| Edge | ✅ Yes | ✅ Yes |
| Safari | ✅ Yes | ✅ Yes |
| Firefox | ⚠️ Limited | ❌ No |

---

## 📞 Support

### Getting Help
1. Check documentation files
2. Review error logs: `linguaflow/logs/app.log`
3. Check health: `curl http://localhost:5000/health`
4. Run tests: `python test_translation.py`

### Common Issues
- **Translation fails:** Check Groq API key
- **Database error:** Check MongoDB URI
- **Cache error:** Check Redis URL
- **Mic not working:** See [MICROPHONE_TROUBLESHOOTING.md](MICROPHONE_TROUBLESHOOTING.md)

---

## 📝 License

[Your License Here]

---

## 🙏 Credits

- **Groq API** - AI language models
- **MongoDB Atlas** - Database
- **Redis Cloud** - Caching
- **Flask** - Web framework

---

## ✨ Status

**✅ PRODUCTION READY**

- All features implemented
- All tests passing
- Security hardened
- Performance optimized
- Fully documented

---

**Last Updated:** May 7, 2026  
**Version:** 1.0.0
