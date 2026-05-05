# Ecommerce API

A full-featured ecommerce REST API built with FastAPI and MySQL, featuring JWT authentication, Paystack payment integration, and a machine learning powered recommendation system.

## Features

- User authentication with JWT
- Role based access control (admin and customer)
- Product and category management
- Order management and processing
- Paystack payment integration with webhook verification
- Email notifications with Resend
- ML based product recommendation system using KNN
- Scheduled background tasks with TaskIQ and RabbitMQ
- Rate limiting and CORS protection

## Tech Stack

- **Framework** — FastAPI
- **Database** — MySQL with SQLAlchemy ORM
- **Authentication** — JWT with python-jose
- **Payments** — Paystack
- **Email** — Resend
- **ML** — Scikit-learn, Pandas, NumPy
- **Background Tasks** — TaskIQ with RabbitMQ broker and Redis backend
- **Password Hashing** — Passlib with bcrypt

## Project Structure

ecommerce/ # Main ecommerce API
recommendation/ # ML recommendation microservice

### Prerequisites

- Python 3.10+
- MySQL
- Redis
- RabbitMQ
