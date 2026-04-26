from . import orders, order_details, sandwiches, payments, reviews, docs


def load_routes(app):
    app.include_router(orders.router)
    app.include_router(order_details.router)
    app.include_router(sandwiches.router)
    app.include_router(payments.router)
    app.include_router(reviews.router)
    app.include_router(docs.router)