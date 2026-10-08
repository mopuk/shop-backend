# Overview of ordering

To place an order user must be authorized.

## API route prefix - /api/v1/orders

### API routes:

1. `GET` / - get a list of all orders of a user
2. `POST` / - place an order
3. `GET` /{order_id} - get order by id
4. `DELETE` /{order_id} - remove order by id

Order consists of:

1. Id of the order
2. Id of user that places the order
3. Order number
4. Order status (Pending / Paid / Delivered / Cancelled)
5. Subtotal = item price \* quantity
6. Shipping total - shipping costs (not planned yet)
7. Total = subtotal + shipping
8. Grand total = total (without discounts yet)
9. Created at
10. Updated at
11. One to Many relationship with OrderItem, where items accessed via items property
12. Many to One relationship with User, where user is accessed via user property

OrderItem consist of

1. Id
2. Order id
3. Variant id
4. Product name - required to avoid fetching variant and its corresponding product from DB
5. Quantity
6. Price paid - so that already paid price doesn't change, when price of the actual variant does change
7. Many to One relationship with Order, where order accessed via order property
8. Many to One relationship with Variant, where variant is accessed via variant property
