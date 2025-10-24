# Ride Booking Platform

A Django-based platform that allows customers to book rides with riders, featuring real-time tracking and a comprehensive staff dashboard.

## Features

- Custom User Authentication System
- Role-based Access Control (Customer, Rider, Staff)
- Real-time Ride Tracking
- Automatic Distance Calculation
- In-platform Balance System
- Staff Dashboard
- AWS S3 Integration for Static Files

## Prerequisites

- Python 3.8+
- pip
- AWS Account (for S3 static file hosting)
- PostgreSQL (for production)

## Setup Instructions

1. Clone the repository:
```bash
git clone <repository-url>
cd <repository-name>
```

2. Create and activate a virtual environment:
```bash
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
```

3. Install required packages:
```bash
pip install -r requirements.txt
```

4. Create a .env file in the project root with the following variables:
```
DJANGO_SECRET_KEY=your_secret_key
AWS_ACCESS_KEY_ID=your_aws_access_key
AWS_SECRET_ACCESS_KEY=your_aws_secret_key
AWS_STORAGE_BUCKET_NAME=your_bucket_name
AWS_S3_REGION_NAME=your_region
```

5. Apply database migrations:
```bash
python manage.py migrate
```

6. Create a superuser (staff account):
```bash
python manage.py createsuperuser
```

7. Run the development server:
```bash
python manage.py runserver
```

## Creating Test Accounts

1. Access the admin interface at http://localhost:8000/admin/
2. Log in with your superuser credentials
3. Create test accounts for:
   - Customers (user_role: 'customer')
   - Riders (user_role: 'rider')

Or use the staff dashboard to create accounts at http://localhost:8000/dashboard/users/create/

## Deployment

This project is configured for deployment on various platforms:

### Heroku
1. Create a new Heroku app
2. Add PostgreSQL addon
3. Configure environment variables
4. Deploy using Git

### AWS
1. Configure S3 bucket for static files
2. Update AWS credentials in environment variables
3. Set `DEBUG=False` for production

## Project Structure

- `accounts/` - Custom user model and authentication
- `rides/` - Core ride booking functionality
- `dashboard/` - Staff management interface
- `static/` - CSS, JavaScript, and other static files
- `templates/` - HTML templates

## Contributing

1. Fork the repository
2. Create a feature branch
3. Commit your changes
4. Push to the branch
5. Create a Pull Request

## Environment Variables

Required environment variables:
- `DJANGO_SECRET_KEY`
- `AWS_ACCESS_KEY_ID`
- `AWS_SECRET_ACCESS_KEY`
- `AWS_STORAGE_BUCKET_NAME`
- `AWS_S3_REGION_NAME`

For production:
- `DATABASE_URL`
- `DEBUG`
- `ALLOWED_HOSTS`
