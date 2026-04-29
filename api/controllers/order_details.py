from sqlalchemy.orm import Session
from fastapi import HTTPException, status, Response, Depends
from ..models import order_details as model
from sqlalchemy.exc import SQLAlchemyError
from sqlalchemy import text


def create(db: Session, request):
    try:
        order_exists = db.execute(
            text("SELECT 1 FROM orders WHERE id = :order_id LIMIT 1"),
            {"order_id": request.order_id},
        ).first()
        if not order_exists:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Order not found")

        sandwich_exists = db.execute(
            text("SELECT 1 FROM sandwiches WHERE id = :sandwich_id LIMIT 1"),
            {"sandwich_id": request.sandwich_id},
        ).first()
        if not sandwich_exists:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Sandwich not found")

        new_item = model.OrderDetail(
            order_id=request.order_id,
            sandwich_id=request.sandwich_id,
            amount=request.amount
        )

        db.add(new_item)
        db.commit()
        db.refresh(new_item)
    except SQLAlchemyError as e:
        error = str(e.__dict__['orig'])
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=error)

    return new_item


def read_all(db: Session):
    try:
        result = db.query(model.OrderDetail).all()
    except SQLAlchemyError as e:
        error = str(e.__dict__['orig'])
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=error)
    return result


def read_one(db: Session, item_id):
    try:
        item = db.query(model.OrderDetail).filter(model.OrderDetail.id == item_id).first()
        if not item:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Id not found!")
    except SQLAlchemyError as e:
        error = str(e.__dict__['orig'])
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=error)
    return item


def update(db: Session, item_id, request):
    try:
        item = db.query(model.OrderDetail).filter(model.OrderDetail.id == item_id)
        existing_item = item.first()
        if not existing_item:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Id not found!")

        update_data = request.dict(exclude_unset=True)

        if "order_id" in update_data:
            order_exists = db.execute(
                text("SELECT 1 FROM orders WHERE id = :order_id LIMIT 1"),
                {"order_id": update_data["order_id"]},
            ).first()
            if not order_exists:
                raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Order not found")

        if "sandwich_id" in update_data:
            sandwich_exists = db.execute(
                text("SELECT 1 FROM sandwiches WHERE id = :sandwich_id LIMIT 1"),
                {"sandwich_id": update_data["sandwich_id"]},
            ).first()
            if not sandwich_exists:
                raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Sandwich not found")

        item.update(update_data, synchronize_session=False)
        db.commit()
    except SQLAlchemyError as e:
        error = str(e.__dict__['orig'])
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=error)
    return item.first()


def delete(db: Session, item_id):
    try:
        item = db.query(model.OrderDetail).filter(model.OrderDetail.id == item_id)
        if not item.first():
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Id not found!")
        item.delete(synchronize_session=False)
        db.commit()
    except SQLAlchemyError as e:
        error = str(e.__dict__['orig'])
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=error)
    return Response(status_code=status.HTTP_204_NO_CONTENT)
