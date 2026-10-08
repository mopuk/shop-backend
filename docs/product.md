# Product Overwiew

## Core idea

Online e-commerce shoe shop

## Main actors

### Guest

Can:

1. Browse catalog
2. Add product to cart
3. Register / Login

### Authorized customer

Can:

1. Browse catalog
2. Add product to cart
3. Checkout (Place an order)
4. Pay
5. Cancel order
6. Browse history of orders
7. Logout

### Admin

Can:

1. Browse catalog
2. Add, remove, edit products
3. Add, remove, edit users (customer accounts)
4. Browse history of orders

### Main concepts

1. ProductVariant
2. Product
3. Customer
4. Cart
5. Order
6. Payment

### Core flow

#### For Guest

1. Browse catalog
2. Add product to cart
3. Go to cart
4. Checkout
5. **If user is not authorized** - Register / Login
6. Create an order
7. Create a payment
8. Pay
9. (Possible cancelation of an order)
10. Success/failure/cancelled order status page
