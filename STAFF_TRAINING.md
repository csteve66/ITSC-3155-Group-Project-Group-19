# Staff Training Manual - Sandwich Shop API

## Quick Reference

### Order Types
| Type | Description | Address Required? |
|------|-------------|-------------------|
| takeout | Customer picks up | No |
| delivery | Driver delivers | Yes |

### Common API Endpoints

| Action | Method | Endpoint |
|--------|--------|----------|
| Place takeout order | POST | `/orders/` |
| Place delivery order | POST | `/orders/` (with address) |
| View all orders | GET | `/orders/` |
| Submit a review | POST | `/reviews/` |
| View reviews | GET | `/reviews/` |

### Example: Delivery Order
```json
POST /orders/
{
    "customer_name": "John Doe",
    "customer_phone": "555-1234",
    "customer_address": "123 Main St",
    "order_type": "delivery",
    "description": "Ring doorbell"
}