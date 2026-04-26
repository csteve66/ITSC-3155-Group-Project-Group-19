from sqlalchemy.orm import Session
from fastapi import HTTPException, status
from sqlalchemy.exc import SQLAlchemyError

from ..models import orders as order_model
from ..models import payments as pay_model

ALLOWED_TYPES = frozenset({"card", "cash", "digital_wallet"})


def create(db: Session, request):
    order = db.query(order_model.Order).filter(order_model.Order.id == request.order_id).first()
    if not order:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Order not found")

    if request.payment_type not in ALLOWED_TYPES:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"payment_type must be one of: {', '.join(sorted(ALLOWED_TYPES))}",
        )

    if request.payment_type in ("card", "digital_wallet"):
        if not request.card_expiration_date:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="card_expiration_date is required for card and digital_wallet payments",
            )

    if request.payment_type == "cash":
        status_val = "succeeded"
    else:
        status_val = "pending"

    new_item = pay_model.Payment(
        order_id=request.order_id,
        card_csv=request.card_csv,
        card_brand=request.card_brand,
        card_expiration_date=request.card_expiration_date,
        payment_type=request.payment_type,
        transaction_status=status_val,
    )

    try:
        db.add(new_item)
        db.commit()
        db.refresh(new_item)
    except SQLAlchemyError as e:
        error = str(e.__dict__["orig"])
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=error)

    return new_item


def read_for_order(db: Session, order_id: int):
    try:
        order = db.query(order_model.Order).filter(order_model.Order.id == order_id).first()
        if not order:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Order not found")
        return (
            db.query(pay_model.Payment)
            .filter(pay_model.Payment.order_id == order_id)
            .order_by(pay_model.Payment.id.asc())
            .all()
        )
    except HTTPException:
        raise
    except SQLAlchemyError as e:
        error = str(e.__dict__["orig"])
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=error)


def read_one(db: Session, payment_id: int):
    try:
        item = db.query(pay_model.Payment).filter(pay_model.Payment.id == payment_id).first()
        if not item:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Payment not found")
        return item
    except HTTPException:
        raise
    except SQLAlchemyError as e:
        error = str(e.__dict__["orig"])
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=error)


def confirm(db: Session, payment_id: int, simulate_failure: bool):
    try:
        item = db.query(pay_model.Payment).filter(pay_model.Payment.id == payment_id).first()
        if not item:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Payment not found")

        if item.transaction_status == "succeeded":
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Payment already succeeded; create a new payment to try again.",
            )
        if item.transaction_status == "failed":
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Payment already failed; create a new payment to retry.",
            )

        if item.payment_type == "cash":
            item.transaction_status = "succeeded"
        else:
            item.transaction_status = "failed" if simulate_failure else "succeeded"

        db.commit()
        db.refresh(item)
        return item
    except HTTPException:
        raise
    except SQLAlchemyError as e:
        error = str(e.__dict__["orig"])
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=error)
