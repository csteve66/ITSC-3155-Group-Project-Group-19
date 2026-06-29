# SandwichShopAPI

A FastAPI backend for a sandwich shop ordering system. The API supports ordering, order tracking, staff and kitchen views, sandwich and recipe management, resources/inventory, promotions, payments, reviews, and sales analytics.

## Features

- Create, update, track, and manage takeout or delivery orders
- Staff dashboard and kitchen order views
- Sandwich, recipe, and resource management
- Promotion and payment endpoints
- Customer review submission and lookup
- Analytics for revenue, order volume, top sandwiches, and order type breakdowns
- Interactive API documentation through FastAPI Swagger UI

## Tech Stack

- Python
- FastAPI
- Uvicorn
- SQLAlchemy
- MySQL with PyMySQL
- Pytest

## Project Structure

```text
api/
  controllers/      Business logic and database operations
  dependencies/     Database and application configuration
  models/           SQLAlchemy models and table setup
  routers/          FastAPI route definitions
  schemas/          Pydantic request and response schemas
  tests/            Pytest test suite
  main.py           Application entry point
STAFF_TRAINING.md   Staff quick reference guide
requirements.txt    Python dependencies
```

## Getting Started

### Prerequisites

- Python 3.10 or newer
- MySQL Server
- Git

### Installation

1. Clone the repository:

```powershell
git clone <repository-url>
cd SandwichFastAPI
```

1. Create and activate a virtual environment:

```powershell
python -m venv .venv
.\.venv\Scripts\activate
```

1. Install dependencies:

```powershell
pip install -r requirements.txt
```

## Database Setup

The application is configured to connect to a local MySQL database using the settings in `api/dependencies/config.py`:

```text
host: localhost
port: 3306
database: sandwich_maker_api
user: root
password: rootroot
```

Create the database before starting the API:

```sql
CREATE DATABASE sandwich_maker_api;
```

When the app starts, it creates the required tables through SQLAlchemy if they do not already exist.

If your local MySQL username or password is different, update `api/dependencies/config.py` before running the server.

## Running the Application

Start the development server:

```powershell
uvicorn api.main:app --reload
```

The API will run at:

```text
http://127.0.0.1:8000
```

Open the interactive API documentation:

- Swagger UI: [http://127.0.0.1:8000/docs](http://127.0.0.1:8000/docs)
- API summary endpoint: [http://127.0.0.1:8000/docs/api-summary](http://127.0.0.1:8000/docs/api-summary)

## Main API Areas


| Area          | Base Endpoint   | Description                              |
| ------------- | --------------- | ---------------------------------------- |
| Orders        | `/orders`       | Create, update, track, and manage orders |
| Order Details | `/orderdetails` | Manage items within an order             |
| Sandwiches    | `/sandwiches`   | View and manage sandwich menu items      |
| Recipes       | `/recipes`      | Manage sandwich recipes                  |
| Resources     | `/resources`    | Manage inventory resources               |
| Promotions    | `/promotions`   | Manage discounts and promotions          |
| Payments      | `/payments`     | Create and confirm payments              |
| Reviews       | `/reviews`      | Create and view customer reviews         |
| Analytics     | `/analytics`    | View sales and order analytics           |


## Example Requests

Create a delivery order:

```json
{
  "customer_name": "John Doe",
  "customer_phone": "555-1234",
  "customer_address": "123 Main St",
  "order_type": "delivery",
  "description": "Ring doorbell"
}
```

View analytics summary:

```text
GET /analytics/summary
```

Track an order:

```text
GET /orders/track/{tracking_number}
```

## Running Tests

Run the test suite with:

```powershell
pytest
```

The tests use SQLite fixtures for isolated test data.

## Staff Guide

See `STAFF_TRAINING.md` for a quick reference covering order types, common endpoints, and staff workflow examples.