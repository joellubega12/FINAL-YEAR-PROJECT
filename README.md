<<<<<<< HEAD
# E-Voting System

A secure and user-friendly electronic voting platform built with Django. This system allows voters to register, authenticate, and cast votes in elections while providing administrators with tools to manage elections, candidates, and results.

## Features

- **User Registration & Authentication**: Secure user registration with email OTP verification
- **Admin Dashboard**: Complete administrative control over elections, candidates, and voters
- **Voting System**: Secure ballot casting with position-based voting
- **Real-time Results**: Live election results and statistics
- **Mobile Responsive**: Optimized for mobile devices and phones
- **Email Integration**: OTP-based email verification system

## Tech Stack

- **Backend**: Django 3.1.7
- **Database**: PostgreSQL (production) / SQLite (development)
- **Frontend**: HTML, CSS, Bootstrap, JavaScript
- **Deployment**: Heroku-ready configuration

## Local Development Setup

1. **Clone the repository**
   ```bash
   git clone https://github.com/joellubega12/FINAL-YEAR-PROJECT.git
   cd FINAL-YEAR-PROJECT
   ```

2. **Create virtual environment**
   ```bash
   python -m venv venv
   source venv/bin/activate  # On Windows: venv\Scripts\activate
   ```

3. **Install dependencies**
   ```bash
   pip install -r requirements.txt
   ```

4. **Run migrations**
   ```bash
   python manage.py migrate
   ```

5. **Create superuser**
   ```bash
   python manage.py createsuperuser
   ```

6. **Run development server**
   ```bash
   python manage.py runserver
   ```

7. **Access the application**
   - Main site: http://localhost:8000
   - Admin panel: http://localhost:8000/admin

## Deployment to Heroku

### Prerequisites
- Heroku CLI installed
- Heroku account
- Git repository

### Deployment Steps

1. **Create Heroku App**
   ```bash
   heroku create your-app-name
   ```

2. **Set Environment Variables**
   ```bash
   heroku config:set SECRET_KEY=your-secret-key-here
   heroku config:set DEBUG=False
   heroku config:set ALLOWED_HOSTS=your-app-name.herokuapp.com
   heroku config:set DATABASE_URL=your-postgresql-database-url
   ```

3. **Deploy to Heroku**
   ```bash
   git push heroku main
   ```

4. **Run Migrations on Heroku**
   ```bash
   heroku run python manage.py migrate
   ```

5. **Create Superuser on Heroku**
   ```bash
   heroku run python manage.py createsuperuser
   ```

6. **Open Your App**
   ```bash
   heroku open
   ```

## Environment Variables

Create a `.env` file in the root directory with:

```
DEBUG=False
SECRET_KEY=your-secret-key-here
ALLOWED_HOSTS=your-app-name.herokuapp.com,localhost,127.0.0.1
DATABASE_URL=postgresql://user:password@host:port/database
```

## Project Structure

```
e_voting/
├── account/          # User authentication and registration
├── voting/           # Main voting application
├── administrator/    # Admin dashboard and management
├── media/            # User uploaded files
├── static/           # Static files (CSS, JS, images)
├── templates/        # HTML templates
└── db.sqlite3        # Local database (not in production)
```

## Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Test thoroughly
5. Submit a pull request

## License

This project is for educational purposes as part of a final year project.

## Support

For questions or issues, please open an issue on GitHub.
