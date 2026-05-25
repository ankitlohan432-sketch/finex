# 🚀 Finex - Deployment Guide

## Docker Deployment (Recommended)

### Prerequisites
- Docker installed
- Docker Compose installed
- Port 8000 (backend) and 3000 (frontend) available

### Quick Start

```bash
# 1. Clone/extract the project
cd Finex_FINAL

# 2. Create environment file
cp .env.example .env

# 3. Build and run with Docker Compose
docker-compose up -d

# 4. Check if services are running
docker-compose ps

# 5. Access the application
# Frontend: http://localhost:3000
# Backend: http://localhost:8000
# API Docs: http://localhost:8000/docs
```

### Database

The application uses SQLite by default (auto-creates finex.db)

For production, update `backend/config.py` to use PostgreSQL:

```python
DATABASE_URL = "postgresql://user:password@db:5432/finex"
```

### Environment Variables

```
VITE_API_URL=http://localhost:8000
DATABASE_URL=sqlite:///./finex.db
SECRET_KEY=your-secret-key-change-this
MAIL_USERNAME=your-email@gmail.com
MAIL_PASSWORD=your-app-password
MARKET_API_KEY=4b49de0121444553852e9e591654f2c8
```

### Stop Services

```bash
docker-compose down

# Remove volumes (deletes data)
docker-compose down -v
```

---

## Local Development

### Backend

```bash
cd backend
pip install -r requirements.txt
uvicorn main:app --reload --port 8000
```

### Frontend

```bash
cd frontend
npm install
npm run dev
```

---

## Features Implemented

✅ **Authentication**
- Secure login/registration
- Token-based authentication
- Password hashing

✅ **Dashboard**
- Real-time portfolio overview
- Market data
- Top gainers/losers

✅ **Stock Market**
- Real-time prices (via TwelveData API)
- Buy/sell stocks
- Portfolio management
- Charts & analytics

✅ **Loans**
- Apply for personal loans
- Loan approval system
- Payment tracking
- APR calculation

✅ **Transactions**
- Buy/sell history
- Fraud detection
- Transaction status

✅ **Cards**
- Add payment cards
- Card management
- Fraud flagging

✅ **Chatbot**
- AI stock recommendations
- Loan inquiries
- Site navigation
- Fraud protection info

✅ **Admin**
- User management
- Platform statistics
- Fraud monitoring

---

## Database Schema

All user data is stored in SQLite/PostgreSQL:

- **users** - User accounts
- **stock_holdings** - Portfolio holdings
- **transactions** - Buy/sell history
- **loans** - Loan applications
- **loan_payments** - Payment records
- **payment_cards** - Card information
- **fraud_alerts** - Fraud detections
- **market_cache** - Stock prices
- **audit_logs** - Activity logs

---

## API Documentation

Once running, visit: `http://localhost:8000/docs`

Key endpoints:
- `POST /auth/register` - Register
- `POST /auth/login` - Login
- `GET /users/me` - Current user
- `GET /stocks/market-overview` - Market data
- `POST /transactions/buy` - Buy stocks
- `POST /loans/apply` - Apply for loan
- `POST /chatbot/ask` - Chat

---

## Troubleshooting

**Port already in use:**
```bash
# Change port in docker-compose.yml
ports:
  - "8001:8000"  # Changed from 8000 to 8001
```

**Database errors:**
```bash
# Reset database
rm finex.db
docker-compose restart backend
```

**Token issues:**
```bash
# Clear browser localStorage
# Open DevTools → Application → Local Storage → Clear
```

**API not responding:**
```bash
# Check logs
docker-compose logs backend

# Restart services
docker-compose restart
```

---

## Production Checklist

- [ ] Change SECRET_KEY to random string
- [ ] Set DEBUG=False in config.py
- [ ] Use PostgreSQL instead of SQLite
- [ ] Enable HTTPS/SSL
- [ ] Set up proper logging
- [ ] Configure CORS for your domain
- [ ] Set up database backups
- [ ] Monitor API rate limits
- [ ] Enable fraud monitoring
- [ ] Set up email notifications
- [ ] Configure backup database

---

## Support

For issues or questions, refer to the README.md file.

