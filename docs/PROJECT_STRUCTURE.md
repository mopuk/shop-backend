# Project Structure

## Directory Overview

```
shop-backend/
├── README.md                 # Project overview and quick start guide
├── Dockerfile               # Docker configuration for containerization
├── docker-compose.yml       # Multi-container Docker setup
├── requirements.txt         # Python dependencies
├── alembic.ini             # Alembic database migration configuration
├── Makefile                # Common commands and tasks
├── package.json            # Node.js/npm metadata (if applicable)
│
├── app/                    # Main application directory
│   ├── __init__.py
│   ├── app.py              # FastAPI application entry point
│   ├── config.py           # Configuration management (env variables)
│   ├── database.py         # Database connection and session setup
│   ├── enums.py            # Enum definitions (Role, TargetGroup, etc.)
│   ├── security.py         # Password hashing and security utilities
│   │
│   ├── models/             # SQLAlchemy ORM models
│   │   ├── __init__.py
│   │   ├── user.py         # User model with authentication fields
│   │   ├── product.py      # Product and ProductVariant models
│   │   ├── cart.py         # Cart and CartItem models
│   │   └── order.py        # Order and OrderItem models
│   │
│   ├── routes/             # API endpoint handlers
│   │   ├── __init__.py
│   │   ├── auth.py         # Authentication endpoints (login, register, refresh)
│   │   ├── products.py     # Product CRUD endpoints
│   │   ├── cart.py         # Shopping cart endpoints
│   │   ├── orders.py       # Order management endpoints
│   │   └── payment.py      # Payment processing endpoints
│   │
│   ├── schemas/            # Pydantic request/response schemas
│   │   ├── __init__.py
│   │   ├── user.py         # User request/response models
│   │   ├── product.py      # Product request/response models
│   │   ├── cart.py         # Cart request/response models
│   │   └── order.py        # Order request/response models
│   │
│   ├── seeds/              # Database seeding utilities
│   │   ├── __init__.py
│   │   ├── seed.py         # Main seed orchestrator
│   │   ├── products_seed.py    # Product data seeding
│   │   ├── variants_seed.py    # Product variant seeding
│   │   ├── reference_seeds.py  # Category, brand, color, material seeding
│   │   ├── products.json       # Product seed data
│   │   ├── variants.json       # Variant seed data
│   │   └── references.json     # Reference data (categories, brands, etc.)
│   │
│   └── utils/              # Utility functions
│       ├── __init__.py
│       └── json_loader.py  # JSON file loading utilities
│
├── migrations/             # Alembic database migrations
│   ├── env.py             # Alembic environment configuration
│   ├── script.py.mako     # Alembic migration template
│   └── versions/          # Individual migration files
│       ├── 14ea606e7244_.py
│       ├── 3b6b2c1c1708_.py
│       ├── 3ea6dc74609c_baseline_reset_migration_history.py
│       ├── 7da593b1eb38_add_thumbnail_to_product_variant.py
│       ├── 9e78fb346339_initial.py
│       ├── bf844adc160c_initial_migration.py
│       └── c90fcc571617_added_cart_related_models_and_user_model.py
│
└── docs/                   # Documentation
    ├── PROJECT_STRUCTURE.md    # This file
    ├── MODELS.md               # Database models explanation
    ├── SETUP.md                # Detailed setup instructions
    └── API_ENDPOINTS.md        # API endpoint reference
```

## Key Directories Explained

### `/app`

The main application code following a modular structure:

- **models/**: SQLAlchemy ORM definitions mapping Python classes to database tables
- **routes/**: FastAPI route handlers - where HTTP requests are processed
- **schemas/**: Pydantic models for request/response validation
- **seeds/**: Data initialization scripts for populating the database with initial data
- **utils/**: Helper functions and utilities

### `/migrations`

Alembic database migration system for version control of the database schema:

- Each `.py` file in `versions/` represents a specific schema change
- Enables reproducible database schema evolution across environments
- Track database changes with version history and rollback capability

### `/docs`

Project documentation:

- `PROJECT_STRUCTURE.md` - This file (folder layout)
- `MODELS.md` - Detailed explanation of database models and relationships
- `SETUP.md` - Environment setup and configuration guide
- `API_ENDPOINTS.md` - Complete API endpoint reference (if applicable)

## Architecture Pattern

This project follows a **layered architecture**:

1. **Routes Layer** (`/routes`) - HTTP request handling
2. **Schema Layer** (`/schemas`) - Request/response validation
3. **Models Layer** (`/models`) - Database representation
4. **Database Layer** (`database.py`) - Connection management

This separation ensures:

- Clean separation of concerns
- Easy testing
- Reusability of models across different endpoints
- Clear data validation boundaries

## Dependencies Structure

- **FastAPI** - Web framework
- **SQLAlchemy** - ORM for database operations
- **Pydantic** - Request/response validation
- **Alembic** - Database migration tool
- **psycopg2** - PostgreSQL adapter
- **asyncpg** - Async PostgreSQL driver
- **PyJWT** - JWT token handling
- **argon2** - Password hashing (via pwdlib)
- **python-dotenv** - Environment variable management

## Database Schema Overview

Key relationships:

```
User (1) ─── (1) Cart
     │
     └─── (M) Orders

Product (1) ─── (M) ProductVariants
     │
     ├─── (M) OrderItems
     └─── (N) Categories
     └─── (N) Brands

ProductVariant (M) ─── (M) CartItems
     │
     └─── (M) OrderItems
```

Each variant can be purchased by adding to cart or directly ordering. Variants handle color, material, and price variations of base products.
