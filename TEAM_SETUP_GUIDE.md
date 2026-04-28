# Nexora Pulse - Team Setup Guide

Welcome to the team! Follow these steps to get your local environment running after cloning the repository for the first time.

## 1. Clone the Repository
First, clone the project to your local machine:
```bash
git clone <repository-url>
cd NexoraPulse
```

## 2. Backend Setup
Our backend runs on Python/FastAPI. You need to set up a virtual environment and configure the database.

```bash
cd backend

# Create a virtual environment
python -m venv venv

# Activate the virtual environment
# On Windows:
venv\Scripts\activate
# On Mac/Linux:
source venv/bin/activate

# Install all required dependencies
pip install -r requirements.txt
```

### Environment Variables (Backend)
1. Copy `.env.example` and create a new `.env` file in the `backend` folder.
2. Fill in the required secrets (ask the team for credentials if you are missing any API keys or database URLs).

### Initialize Database
Set up the local database by running:
```bash
python init_db.py
```

### Start the Backend Server
```bash
# Run this inside the backend folder
python -m uvicorn app.main:app --reload
```
*(Note: Ensure your `venv` is activated before starting the server.)*

## 3. Frontend Setup
Our frontend is built with React and Vite.

```bash
# From the project root, navigate to the frontend
cd frontend

# Install node modules
npm install
```

### Environment Variables (Frontend)
1. Ask the team for the frontend environment variables and place them in a `.env` file inside the `frontend` folder.
2. Example configuration usually includes `VITE_API_URL=http://localhost:8000`.

### Start the Frontend Server
```bash
npm run dev
```

## 4. You're Good to Go!
With both the frontend and backend servers running, you can access the local app in your browser (usually at `http://localhost:5173`). Happy coding!
