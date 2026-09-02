## Core Modules

### `app.py` - Application Entry Point

Initializes FastAPI and configures middleware:

```python
app = FastAPI()
app.add_middleware(CORSMiddleware, ...)  # Cross-Origin Resource Sharing
app.include_router(api_router)            # Add route handlers
```

### `config.py` - Configuration Management

Centralized configuration using environment variables:

```python
class Config:
    DATABASE_URL = os.getenv("DATABASE_URL")
    JWT_SECRET_KEY = os.getenv("JWT_SECRET_KEY")
    ALLOW_ORIGINS = os.getenv("ALLOW_ORIGINS").split(",")
```

### `database.py` - Database Connection

Manages SQLAlchemy setup:

```python
engine = create_engine(DATABASE_URL)
SessionLocal = sessionmaker(bind=engine)
Base = declarative_base()
```

**Purpose**: Connection pooling, session management, ORM setup

### `security.py` - Authentication & Password Management

Password hashing and security utilities:

```python
def get_password_hash(password: str) -> str
def verify_password(password: str, hash: str) -> bool
def check_requirements_for_password(password: str) -> bool
```

---

## Routes Layer (`/routes`)

Each file handles a specific domain:

### `auth.py` - Authentication Routes

```python
POST /auth/register       # Create new user account
POST /auth/login          # Get JWT access token
POST /auth/refresh        # Get new token using refresh token
POST /auth/logout         # Invalidate token
```

**Key function**: Token generation and validation

### `products.py` - Product Management

```python
GET /products             # List all products (with filters)
GET /products/{id}        # Get product details
POST /products            # Create product (admin only)
PUT /products/{id}        # Update product (admin only)
DELETE /products/{id}     # Delete product (admin only)
```

### `cart.py` - Shopping Cart Operations

```python
GET /cart                 # Get user's cart with items
POST /cart/items          # Add item to cart
PUT /cart/items/{id}      # Update item quantity
DELETE /cart/items/{id}   # Remove item from cart
```

### `orders.py` - Order Management

```python
GET /orders               # List user's orders
GET /orders/{id}          # Get order details
POST /orders              # Create order from cart
PUT /orders/{id}          # Update order status (admin)
DELETE /orders/{id}       # Cancel order
```

**Order creation flow**:

1. Validate cart items exist and have stock
2. Calculate total price
3. Create Order with OrderItems (snapshot of cart)
4. Clear cart after successful order
5. Reduce product variant stock

### `payment.py` - Payment Processing

```python
POST /payments            # Process payment for order
GET /payments/{id}        # Get payment status
```

**Note**: Payment gateway integration would go here

---

## Schemas Layer (`/schemas`)

Pydantic models for validation and documentation:

**Request Schema** (incoming data):

```python
class ProductCreate(BaseModel):
    name: str
    description: Optional[str]
    price: Decimal
    category_id: int
```

**Response Schema** (outgoing data):

```python
class ProductResponse(BaseModel):
    id: int
    name: str
    price: Decimal
    created_at: datetime

    class Config:
        from_attributes = True  # Works with ORM models
```

---

## Models Layer (`/models`)

**Key features**:

- Type hints for IDE autocomplete
- Relationships between models
- Database constraints (unique, foreign keys)
- Automatic timestamp fields

---

## Enums (`enums.py`)

PostgreSQL native enums for type safety:

```python
class Role(str, Enum):
    customer = "customer"
    admin = "admin"

class OrderStatus(str, Enum):
    pending = "pending"
    confirmed = "confirmed"
    shipped = "shipped"
    delivered = "delivered"
```

---

## Seeding (`/seeds`)

Database initialization with sample data:

```python
python -m app.seeds.seed
```

Populates:

- **Categories**: Product classifications
- **Brands**: Manufacturers
- **Products**: Items in catalog
- **Variants**: Color/material combinations
- **Colors**: Available product colors
- **Materials**: Available materials

Data sources: JSON files in `/seeds/*.json`

---

## Common API Patterns

### Pagination (Example)

```python
GET /products?skip=0&limit=10
GET /orders?page=1&page_size=20
```

### Filtering (Example)

```python
GET /products?category_id=1&is_featured=true
GET /products?gender=male&min_price=10&max_price=50
```

### Authentication

All protected endpoints require JWT:

```python
Authorization: Bearer eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...
```

---

## Error Handling

Standard HTTP status codes:

- `200 OK` - Successful GET/PUT
- `201 Created` - Successful POST
- `204 No Content` - Successful DELETE
- `400 Bad Request` - Invalid input
- `401 Unauthorized` - Missing/invalid JWT
- `403 Forbidden` - Insufficient permissions
- `404 Not Found` - Resource doesn't exist
- `500 Internal Server Error` - Server error

All errors return JSON:

```json
{
  "detail": "Product not found"
}
```

---

## Database Migrations

Alembic version controls database schema:

```bash
# Create migration
alembic revision --autogenerate -m "add thumbnail field"

# Apply migrations
alembic upgrade head

# Check status
alembic current
```

Each migration file is timestamped and reversible.

---

## Testing Endpoints

Use Swagger UI at http://localhost:8000/docs:

1. Click endpoint
2. Click "Try it out"
3. Fill in parameters
4. Click "Execute"
5. See response

Or use curl:

```bash
# Get products
curl http://localhost:8000/products

# Create product (requires admin JWT)
curl -X POST http://localhost:8000/products \
  -H "Authorization: Bearer YOUR_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{"name":"Shirt","price":29.99}'
```
