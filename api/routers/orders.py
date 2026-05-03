from fastapi import APIRouter, Depends, FastAPI, status, Response
from sqlalchemy.orm import Session
from ..controllers import orders as controller
from ..schemas import orders as schema
from ..dependencies.database import engine, get_db

router = APIRouter(
    tags=['Orders'],
    prefix="/orders"
)


@router.post("/", response_model=schema.Order)
def create(request: schema.OrderCreate, db: Session = Depends(get_db)):
    return controller.create(db=db, request=request)


@router.get("/", response_model=list[schema.Order])
def read_all(db: Session = Depends(get_db)):
    return controller.read_all(db)


@router.get("/history", response_model=list[schema.OrderHistoryRecord])
def read_history(db: Session = Depends(get_db)):
    return controller.read_history(db)


@router.get("/track/{tracking_number}", response_model=schema.Order)
def read_by_tracking_number(tracking_number: str, db: Session = Depends(get_db)):
    return controller.read_by_tracking_number(db, tracking_number=tracking_number)


@router.get("/staff", response_model=list[schema.Order])
def read_staff_dashboard(db: Session = Depends(get_db)):
    return controller.read_staff_dashboard(db)


@router.get("/kitchen", response_model=list[schema.KitchenOrder])
def read_kitchen_view(db: Session = Depends(get_db)):
    orders = controller.read_kitchen_view(db)
    result = []
    for order in orders:
        items = [
            schema.KitchenItem(
                sandwich_name=detail.sandwich.sandwich_name,
                quantity=detail.amount
            )
            for detail in order.order_details
            if detail.sandwich
        ]
        result.append(schema.KitchenOrder(
            id=order.id,
            tracking_number=order.tracking_number,
            order_status=order.order_status,
            order_type=order.order_type,
            order_date=order.order_date,
            items=items
        ))
    return result


@router.get("/{item_id}", response_model=schema.Order)
def read_one(item_id: int, db: Session = Depends(get_db)):
    return controller.read_one(db, item_id=item_id)


@router.put("/{item_id}", response_model=schema.Order)
def update(item_id: int, request: schema.OrderUpdate, db: Session = Depends(get_db)):
    return controller.update(db=db, request=request, item_id=item_id)


@router.patch("/{item_id}/status", response_model=schema.Order)
def update_status(item_id: int, request: schema.OrderStatusUpdate, db: Session = Depends(get_db)):
    return controller.update_status_by_role(db=db, request=request, item_id=item_id)


@router.delete("/{item_id}")
def delete(item_id: int, db: Session = Depends(get_db)):
    return controller.delete(db=db, item_id=item_id)
