from fastapi import APIRouter
from fastapi.responses import JSONResponse

router = APIRouter(
    tags=['Documentation'],
    prefix="/docs"
)


@router.get("/api-summary")
def get_api_summary():
    return JSONResponse(content={
        "version": "1.0.0",
        "last_updated": "2026-04-26",
        "base_url": "http://localhost:8000",
        "endpoints": {
            "Orders": {
                "POST /orders/": "Create order (takeout or delivery)",
                "GET /orders/": "List all orders",
                "GET /orders/{id}": "Get order by ID",
                "PUT /orders/{id}": "Update order",
                "DELETE /orders/{id}": "Delete order"
            },
            "Reviews": {
                "POST /reviews/": "Submit a review (one per order)",
                "GET /reviews/": "List all reviews",
                "GET /reviews/order/{order_id}": "Get review by order",
                "GET /reviews/customer/{customer_id}": "Get reviews by customer",
                "PUT /reviews/{id}": "Update review",
                "DELETE /reviews/{id}": "Delete review"
            },
            "Sandwiches": {
                "GET /sandwiches/": "List all sandwiches",
                "GET /sandwiches/category/{category}": "Filter by category"
            },
            "Payments": {
                "POST /payments/": "Create payment",
                "POST /payments/{id}/confirm": "Confirm payment"
            }
        },
        "order_types": {
            "takeout": "Customer picks up - no address needed",
            "delivery": "Delivery to customer - address required"
        },
        "review_rules": {
            "score": "1 to 5 stars",
            "one_per_order": "Each order can have only one review"
        }
    })