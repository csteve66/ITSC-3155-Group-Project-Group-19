from fastapi import APIRouter, Depends, Query
from sqlalchemy.orm import Session

from ..controllers import payments as controller
from ..schemas import payments as schema
from ..dependencies.database import get_db

router = APIRouter(
    tags=["Payments"],
    prefix="/payments",
)


@router.post("/", response_model=schema.Payment)
def create_payment(request: schema.PaymentCreate, db: Session = Depends(get_db)):
    return controller.create(db=db, request=request)


@router.get("/order/{order_id}", response_model=list[schema.Payment])
def list_for_order(order_id: int, db: Session = Depends(get_db)):
    return controller.read_for_order(db, order_id)


@router.get("/{payment_id}", response_model=schema.Payment)
def read_one(payment_id: int, db: Session = Depends(get_db)):
    return controller.read_one(db, payment_id)


@router.post("/{payment_id}/confirm", response_model=schema.Payment)
def confirm_payment(
    payment_id: int,
    simulate_failure: bool = Query(
        default=False,
        description="Mock processor: true forces a failed charge (card / digital_wallet only).",
    ),
    db: Session = Depends(get_db),
):
    return controller.confirm(db, payment_id, simulate_failure=simulate_failure)
