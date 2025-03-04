
# Loan Management System REST API - Django

The Loan Management System is a Django-based REST API for managing loans with monthly compound interest, role-based authentication, automatic interest calculations, and repayment schedules. It supports early foreclosure with adjusted interest calculations.


## Tech Stack

**Backend:** Django, Django REST Framework (DRF)

**Authentication:** JWT (Simple JWT)

**OTP Email Service:**  Nodemailer (via SMTP)

**Database:** PostgreSQL

**API testing tool:** Postman

## Features

- Implement JWT authentication using Simple JWT.
- Support two user roles: **Admin** & **User**.
Users can:
- Add a new loan by specifying the amount, tenure, and interest rate.
- View their active and past loans.
- View loan details with monthly installments and interest breakdown.
- Foreclose a loan before tenure completion (adjusted interest calculations apply).
Admins can:
- View all loans in the system.
- View all user loan details.
- Delete loan records.



## Prerequisites

Before setting up the project, ensure that you have the following installed:

1. Python (version 3.8 or higher)
2. pip (Python package manager)
3. Virtualenv (recommended for environment isolation)
4. PostgreSQL (for database management)
## Steps to run the project

1. Clone the respository

```bash
  git clone https://link-to-project
```

2. Go to the project directory

```bash
  cd loan
```

3. Install dependencies

```bash
  npm install
```

4. Navigate to the email service directory

```bash
  cd email_service
```

5. Start the server

```bash
  node server.js
```

5. Run Migrations

```bash
  python manage.py makemigrations
  python manage.py migrate
```

6. Run the Development Server

```bash
  python manage.py runserver
```
## API Reference

####  user :

#### Authentication


| Method    | Endpoint     | Description                |
| :-------- | :-------     | :------------------------- |
| POST      | `POST /apimodels/register`    | Register a new user |
| POST      | `POST /apimodels/verify-otp/` | verify email account using otp |
| POST      | `POST /apimodels/login`       | User  Login |

#### loans


| Method    | Endpoint     | Description                       |
| :-------- | :-------     | :-------------------------------- |
| POST      | `POST /apimodels/loans`      | Add Loans|
| GET       | `POST /apimodels/loans`      | List all loans|
| GET       | `POST /apimodels/{loan_id}/` | List a loan|

####  Loan Foreclosure

| Method | Endpoint     | Description                       |
| :------| :-------     | :-------------------------------- |
| POST   | `POST /apimodels/{loan_id}/foreclose` | Foreclose a loan|

####  Accessing the Admin Panel :

1. Create a superuser
```bash
  python manage.py createsuperuser
```
2. Run the Django server:
```bash
  python manage.py runserver
```
3. Login to Admin Panel:

- Open http://127.0.0.1:8000/admin/ in your browser.
- Enter admin credentials to access the dashboard.

| operation    | Description                       |
| :--------    | :-------------------------------- |
| View Loans   | Admins can see all loans in the system |
| Delete Loans | Admins can delete loan records if necessary |
| View users   | Admins can view and edit user details. |

## Additional information
 1. To use a JWT token for authentication in Postman, follow these steps:

 - If your API has a login endpoint (/auth/login or similar), send a POST request with credentials (e.g., username & password).
 - he response should include an access token and possibly a refresh token.
  
2. Use the Token in Postman

- Open Postman.
- Go to the "Authorization" tab.
- Select "Bearer Token" from the dropdown.
- Paste the access_token you received in Step 1.
- Send the request.

3. Handle Expired Tokens (Refresh Token)

- If the access token expires, use the refresh token to get a new one
