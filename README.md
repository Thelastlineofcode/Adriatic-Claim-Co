# Adriatic Claim Co

Claims management system for tracking property claims with owner intake forms and workflow management.

## Tech Stack

- **Frontend**: React 18 with React Hook Form
- **Backend**: Flask (Python 3.11) with SQLAlchemy
- **Database**: PostgreSQL (production) / SQLite (development)
- **Testing**: Jest + React Testing Library (frontend), unittest (backend)

## Features

- ✅ Owner claim intake form with validation
- ✅ Email and phone validation
- ✅ Loading states and error handling
- ✅ Accessibility (ARIA attributes)
- ✅ RESTful API for owners and claims
- ✅ Comprehensive test coverage
- ✅ Production-ready deployment configuration

## Local Development

### Backend Setup

```bash
cd backend
python3 -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
pip install -r requirements.txt
python app.py
```

Backend runs at `http://localhost:5000`

### Frontend Setup

```bash
cd frontend
npm install --legacy-peer-deps
npm start
```

Frontend runs at `http://localhost:3000`

### Run Tests

**Backend tests:**

```bash
cd backend
python -m pytest test_*.py
```

**Frontend tests:**

```bash
cd frontend
npm test
```

## Deployment

See [DEPLOY.md](DEPLOY.md) for detailed deployment instructions for:

- Render.com (easiest, recommended)
- Google Cloud Run (most powerful free tier)
- Railway.app (simplest dashboard)

### Quick Deploy to Render

1. Fork/clone this repository
2. Sign up at [render.com](https://render.com)
3. Create new **Web Service** → Connect GitHub → Select this repo
4. Configure:
   - **Root Directory**: `backend`
   - **Build Command**: `pip install -r requirements.txt`
   - **Start Command**: `gunicorn app:app`
   - Add environment variable: `FLASK_ENV=production`
5. Create **Static Site** for frontend:
   - **Root Directory**: `frontend`
   - **Build Command**: `npm install --legacy-peer-deps && npm run build`
   - **Publish Directory**: `build`

## Project Structure

```
Adriatic-Claim-Co/
├── backend/
│   ├── app.py              # Flask application
│   ├── db.py               # Database instance
│   ├── requirements.txt    # Python dependencies
│   ├── Dockerfile          # Backend container
│   ├── api/
│   │   ├── claims.py       # Claims API endpoints
│   │   └── owners.py       # Owners API endpoints
│   ├── models/
│   │   └── models.py       # Database models
│   └── tests/
│       ├── test_app.py
│       ├── test_claims_api.py
│       └── test_owners_api.py
├── frontend/
│   ├── package.json
│   ├── Dockerfile          # Frontend container
│   ├── nginx.conf          # Production web server config
│   ├── src/
│   │   ├── App.js
│   │   └── components/
│   │       └── forms/
│   │           ├── OwnerClaimIntakeForm.jsx
│   │           └── OwnerClaimIntakeForm.test.jsx
│   └── public/
├── render.yaml             # Render.com deployment config
├── Dockerfile              # Root-level Docker config
└── DEPLOY.md               # Deployment guide
```

## API Endpoints

### Owners

- `POST /api/owners` - Create new owner
- `GET /api/owners` - List all owners
- `GET /api/owners/<id>` - Get owner by ID
- `PUT /api/owners/<id>` - Update owner
- `DELETE /api/owners/<id>` - Delete owner

### Claims

- `POST /api/claims` - Create new claim
- `GET /api/claims` - List all claims
- `GET /api/claims/<id>` - Get claim by ID
- `PUT /api/claims/<id>` - Update claim
- `DELETE /api/claims/<id>` - Delete claim

### Health

- `GET /health` - Health check endpoint

## Environment Variables

**Backend (.env)**:

```bash
DATABASE_URL=postgresql://user:password@host:5432/database
FLASK_ENV=production
SECRET_KEY=your_secret_key_here
PORT=5000
```

**Frontend (.env.production)**:

```bash
REACT_APP_API_URL=https://your-backend-url.onrender.com
```

## Contributing

1. Fork the repository
2. Create a feature branch (`git checkout -b feature/amazing-feature`)
3. Commit your changes (`git commit -m 'Add amazing feature'`)
4. Push to the branch (`git push origin feature/amazing-feature`)
5. Open a Pull Request

## License

This project is private and proprietary.

## Support

For deployment issues, see [DEPLOY.md](DEPLOY.md) or check platform documentation:

- [Render Docs](https://render.com/docs)
- [Google Cloud Run Docs](https://cloud.google.com/run/docs)
- [Railway Docs](https://docs.railway.app)
