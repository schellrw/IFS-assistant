# IFS Assistant

A powerful application for Internal Family Systems (IFS) therapy self-exploration and journaling. This tool helps users identify, track, and work with their internal parts according to the IFS model.

## Features

- **User Authentication**: Secure login and registration system
- **Parts Management**: Create, update, and track your internal parts
- **Relationship Mapping**: Define and visualize relationships between your parts
- **Journaling**: Record your insights and experiences with timestamp tracking
- **System Overview**: Get a holistic view of your internal system

## Technology Stack

### Backend
- **Python 3.9+**
- **Flask**: Web framework
- **SQLAlchemy**: ORM for database interactions
- **Flask-JWT-Extended**: Authentication with JWT tokens
- **Marshmallow**: Schema validation and serialization
- **PostgreSQL**: Database (configurable)

### Frontend
- **React**: Frontend framework
- **Redux**: State management
- **Axios**: API client
- **D3.js**: Visualization for part relationships
- **Material-UI**: UI component library

## Installation

### Prerequisites
- Python 3.9 or higher
- Node.js 14 or higher
- PostgreSQL (or SQLite for development)

### Backend Setup

1. Clone the repository:
```bash
git clone https://github.com/yourusername/ifs-assistant.git
cd ifs-assistant
```

2. Set up a virtual environment:
```bash
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
```

3. Install dependencies:
```bash
pip install -r requirements.txt
```

4. Configure environment variables in a `.env` file:
```
FLASK_APP=backend/app
FLASK_ENV=development
DATABASE_URL=postgresql://username:password@localhost/ifs_assistant
JWT_SECRET_KEY=your_secure_jwt_key
```

5. Initialize the database:
```bash
flask db upgrade
```

6. Run the backend server:
```bash
flask run
```

### Frontend Setup

1. Navigate to the frontend directory:
```bash
cd frontend
```

2. Install dependencies:
```bash
npm install
```

3. Start the development server:
```bash
npm start
```

4. The app should now be running at http://localhost:3000

## API Documentation

### Authentication

- `POST /api/auth/register`: Register a new user
- `POST /api/auth/login`: Login and get JWT token
- `POST /api/auth/refresh`: Refresh JWT token

### System Management

- `GET /api/system`: Get user's IFS system
- `PUT /api/system`: Update system details
- `GET /api/system/overview`: Get comprehensive system overview
- `POST /api/system/reset`: Reset system (delete all parts except Self)

### Parts Management

- `GET /api/parts`: Get all parts
- `POST /api/parts`: Create a new part
- `GET /api/parts/<part_id>`: Get a specific part
- `PUT /api/parts/<part_id>`: Update a part
- `DELETE /api/parts/<part_id>`: Delete a part

### Relationships Management

- `GET /api/relationships`: Get all relationships
- `POST /api/relationships`: Create a new relationship
- `GET /api/relationships/<relationship_id>`: Get a specific relationship
- `PUT /api/relationships/<relationship_id>`: Update a relationship
- `DELETE /api/relationships/<relationship_id>`: Delete a relationship

### Journaling

- `GET /api/journals`: Get all journal entries
- `POST /api/journals`: Create a new journal entry
- `GET /api/journals/<journal_id>`: Get a specific journal entry
- `PUT /api/journals/<journal_id>`: Update a journal entry
- `DELETE /api/journals/<journal_id>`: Delete a journal entry

## Development

### Project Structure

```
ifs-assistant/
├── backend/
│   ├── app/
│   │   ├── api/
│   │   │   ├── auth.py
│   │   │   ├── parts.py
│   │   │   ├── relationships.py
│   │   │   ├── journals.py
│   │   │   └── systems.py
│   │   ├── config/
│   │   ├── models/
│   │   ├── __init__.py
│   ├── migrations/
│   └── tests/
├── frontend/
│   ├── public/
│   ├── src/
│   │   ├── components/
│   │   ├── pages/
│   │   ├── services/
│   │   ├── store/
│   │   └── App.js
├── .env
├── .gitignore
└── README.md
```

### Running Tests

```bash
# Backend tests
cd backend
pytest

# Frontend tests
cd frontend
npm test
```

## Deployment

### Docker Deployment

1. Build the Docker images:
```bash
docker-compose build
```

2. Run the containers:
```bash
docker-compose up -d
```

### Manual Deployment

For production deployment, consider:
- Using Gunicorn as WSGI server
- Setting up Nginx as reverse proxy
- Using a production-grade database like PostgreSQL
- Enabling HTTPS with Let's Encrypt

## Contributing

Contributions are welcome! Please feel free to submit a Pull Request.

## License

This project is licensed under the MIT License - see the LICENSE file for details.

## Acknowledgements

- Internal Family Systems therapy developed by Richard C. Schwartz
- All contributors and the open-source community
