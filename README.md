# Shop Backend

A FastAPI-based e-commerce backend API for managing products, users, shopping carts, and orders.

## Overview

This is a RESTful API backend for an online shop built with FastAPI and PostgreSQL. It provides complete e-commerce functionality including user authentication, product catalog management, shopping cart operations, and order processing.

## Tech Stack

- **Framework**: FastAPI 0.139.0
- **Database**: PostgreSQL with SQLAlchemy ORM
- **Authentication**: JWT (JSON Web Tokens)
- **Password Hashing**: Argon2
- **Database Migrations**: Alembic
- **Deployment**: Docker & Gunicorn
- **API Documentation**: Automatic OpenAPI/Swagger (built-in with FastAPI)

## Features

- User authentication and authorization with JWT tokens
- Shopping cart management
- Product catalog with variants (colors, materials, pricing)
- Order processing and tracking
- Payment processing integration
- Product categorization and branding
- CORS support for frontend integration
- Database migrations with Alembic

## Project Structure

See [docs/PROJECT_STRUCTURE.md](docs/PROJECT_STRUCTURE.md) for a detailed breakdown of the project organization.

## Quick Start

### Prerequisites

- Python 3.14+
- PostgreSQL 12+
- Docker & Docker Compose (optional)

### Setup

1. **Clone the repository** (if applicable)
2. **Install dependencies**:

   ```bash
   pip install -r requirements.txt
   ```

3. **Set up environment variables** (create `.env` file):

   ```
   DATABASE_URL=postgresql://user:password@localhost:5432/shop_db
   JWT_SECRET_KEY=your-secret-key-here
   JWT_ALGORITHM=HS256
   JWT_ACCESS_TOKEN_EXPIRE_MINUTES=600
   ALLOW_ORIGINS=http://localhost:3000,http://127.0.0.1:3000
   ```

4. **Run database migrations**:

   ```bash
   alembic upgrade head
   ```

5. **Seed the database** (optional):

   ```bash
   python -m app.seeds.seed
   ```

6. **Start the server**:
   ```bash
   fastapi run app/app.py --port 8000
   ```

The API will be available at `http://localhost:8000`

- API docs: `http://localhost:8000/docs` (Swagger UI)
- ReDoc: `http://localhost:8000/redoc`

### Using Docker

```bash
docker-compose up
```

This will start both PostgreSQL and the FastAPI server.

## API Endpoints

### Authentication

- `POST /auth/register` - Register a new user
- `POST /auth/login` - Login user
- `POST /auth/refresh` - Refresh JWT token

### Products

- `GET /products` - List all products
- `GET /products/{id}` - Get product details
- `POST /products` - Create product (admin)
- `PUT /products/{id}` - Update product (admin)
- `DELETE /products/{id}` - Delete product (admin)

### Shopping Cart

- `GET /cart` - Get current user's cart
- `POST /cart/items` - Add item to cart
- `PUT /cart/items/{item_id}` - Update cart item
- `DELETE /cart/items/{item_id}` - Remove item from cart

### Orders

- `GET /orders` - List user's orders
- `POST /orders` - Create new order
- `GET /orders/{id}` - Get order details
- `PUT /orders/{id}` - Update order

### Payments

- `POST /payments` - Process payment

## Database Schema

The project uses SQLAlchemy ORM with PostgreSQL. Key models include:

- **User**: Stores user account information and authentication details
- **Product**: Product catalog with pricing and metadata
- **ProductVariant**: Product variations (color, material, pricing)
- **Cart & CartItem**: Shopping cart management
- **Order & OrderItem**: Order history and details
- **Category & Brand**: Product classification

See [docs/MODELS.md](docs/MODELS.md) for detailed model documentation.

## Configuration

Configuration is managed through environment variables in `.env`. Key settings:

- `DATABASE_URL`: PostgreSQL connection string
- `JWT_SECRET_KEY`: Secret key for JWT token signing
- `JWT_ALGORITHM`: Algorithm for JWT (default: HS256)
- `JWT_ACCESS_TOKEN_EXPIRE_MINUTES`: Token expiration time (default: 600 minutes)
- `ALLOW_ORIGINS`: Comma-separated list of allowed origins for CORS
- `ALLOW_CREDENTIALS`: Enable credentials in CORS (default: true)
