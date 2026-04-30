from sqlalchemy.orm import Session
from fastapi import HTTPException, status, Response, Depends
from ..models import orders as model
from ..models import order_details as order_detail_model
from ..models import sandwiches as sandwich_model
from sqlalchemy.exc import SQLAlchemyError
from sqlalchemy import func
from datetime import datetime
import uuid

ROLE_ALLOWED_STATUSES = {
    "cook": {"preparing", "ready_for_pickup"},
    "staff": {"pending", "out_for_delivery", "completed", "cancelled"},
}

VALID_STATUS_TRANSITIONS = {
    "pending": {"preparing", "cancelled"},
    "preparing": {"ready_for_pickup", "cancelled"},
    "ready_for_pickup": {"out_for_delivery", "completed", "cancelled"},
    "out_for_delivery": {"completed", "cancelled"},
    "completed": set(),
    "cancelled": set(),
}


def create(db: Session, request):
    # Validation: delivery orders must have an address
    if request.order_type == 'delivery' and not request.customer_address:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Customer address is required for delivery orders"
        )
    tracking_number = f"ORD-{datetime.now().strftime('%Y%m%d%H%M%S')}-{uuid.uuid4().hex[:6].upper()}"
    new_item = model.Order(
        customer_name=request.customer_name,
        customer_phone=request.customer_phone,
        customer_address=request.customer_address,
        description=request.description,
        order_type=request.order_type,
        tracking_number=tracking_number,
        order_status="pending",
        status_updated_at=datetime.now(),
    )

    try:
        db.add(new_item)
        db.commit()
        db.refresh(new_item)
    except SQLAlchemyError as e:
        error = str(e.__dict__['orig'])
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=error)

    return new_item


def read_all(db: Session):
    try:
        result = db.query(model.Order).all()
    except SQLAlchemyError as e:
        error = str(e.__dict__['orig'])
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=error)
    return result


def read_history(db: Session):
    try:
        result = (
            db.query(
                model.Order.id.label("id"),
                model.Order.tracking_number.label("tracking_number"),
                model.Order.order_status.label("status"),
                model.Order.order_type.label("order_type"),
                func.coalesce(
                    func.sum(
                        sandwich_model.Sandwich.price * order_detail_model.OrderDetail.amount
                    ),
                    0,
                ).label("total_price"),
                model.Order.order_date.label("order_date"),
            )
            .outerjoin(
                order_detail_model.OrderDetail,
                order_detail_model.OrderDetail.order_id == model.Order.id,
            )
            .outerjoin(
                sandwich_model.Sandwich,
                sandwich_model.Sandwich.id == order_detail_model.OrderDetail.sandwich_id,
            )
            .group_by(
                model.Order.id,
                model.Order.tracking_number,
                model.Order.order_status,
                model.Order.order_type,
                model.Order.order_date,
            )
            .order_by(model.Order.order_date.desc(), model.Order.id.desc())
            .all()
        )
    except SQLAlchemyError as e:
        error = str(e.__dict__['orig'])
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=error)
    return result


def read_one(db: Session, item_id):
    try:
        item = db.query(model.Order).filter(model.Order.id == item_id).first()
        if not item:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Id not found!")
    except SQLAlchemyError as e:
        error = str(e.__dict__['orig'])
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=error)
    return item


def update(db: Session, item_id, request):
    try:
        item = db.query(model.Order).filter(model.Order.id == item_id)
        if not item.first():
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Id not found!")
        update_data = request.dict(exclude_unset=True)
        if update_data.get('order_type') == 'delivery':
            existing = item.first()
            new_address = update_data.get('customer_address', existing.customer_address)
            if not new_address:
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail="Customer address is required for delivery orders"
                )
        if "order_status" in update_data:
            update_data["status_updated_at"] = datetime.now()
        item.update(update_data, synchronize_session=False)
        db.commit()
    except SQLAlchemyError as e:
        error = str(e.__dict__['orig'])
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=error)
    return item.first()


def delete(db: Session, item_id):
    try:
        item = db.query(model.Order).filter(model.Order.id == item_id)
        if not item.first():
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Id not found!")
        item.delete(synchronize_session=False)
        db.commit()
    except SQLAlchemyError as e:
        error = str(e.__dict__['orig'])
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=error)
    return Response(status_code=status.HTTP_204_NO_CONTENT)


def read_by_tracking_number(db: Session, tracking_number: str):
    try:
        item = db.query(model.Order).filter(model.Order.tracking_number == tracking_number).first()
        if not item:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Tracking number not found!",
            )
    except SQLAlchemyError as e:
        error = str(e.__dict__['orig'])
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=error)
    return item


def update_status_by_role(db: Session, item_id: int, request):
    try:
        item = db.query(model.Order).filter(model.Order.id == item_id)
        existing = item.first()
        if not existing:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Id not found!")

        role = request.actor_role
        next_status = request.order_status
        current_status = existing.order_status

        if next_status not in ROLE_ALLOWED_STATUSES.get(role, set()):
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"{role} is not allowed to set status to '{next_status}'",
            )

        allowed_next_statuses = VALID_STATUS_TRANSITIONS.get(current_status, set())
        if next_status not in allowed_next_statuses:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"Invalid status transition: '{current_status}' -> '{next_status}'",
            )

        item.update(
            {"order_status": next_status, "status_updated_at": datetime.now()},
            synchronize_session=False,
        )
        db.commit()
    except SQLAlchemyError as e:
        error = str(e.__dict__['orig'])
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=error)

    return item.first()
