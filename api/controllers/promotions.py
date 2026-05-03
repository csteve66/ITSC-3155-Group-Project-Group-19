from sqlalchemy.orm import Session
from fastapi import HTTPException, status, Response
from ..models import promotions as model
from ..schemas import promotions as schema
from sqlalchemy.exc import SQLAlchemyError
from datetime import datetime


def create(db: Session, request: schema.PromotionCreate):
    new_promo = model.Promotion(
        code=request.code.strip().upper(),
        discount_percentage=request.discount_percentage,
        expiration_date=request.expiration_date,
    )
    try:
        db.add(new_promo)
        db.commit()
        db.refresh(new_promo)
    except SQLAlchemyError as e:
        error = str(e.__dict__['orig'])
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=error)
    return new_promo


def read_all(db: Session):
    try:
        result = db.query(model.Promotion).all()
    except SQLAlchemyError as e:
        error = str(e.__dict__['orig'])
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=error)
    return result


def read_one(db: Session, item_id: int):
    try:
        item = db.query(model.Promotion).filter(model.Promotion.id == item_id).first()
        if not item:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Promotion not found!")
    except SQLAlchemyError as e:
        error = str(e.__dict__['orig'])
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=error)
    return item


def update(db: Session, item_id: int, request: schema.PromotionUpdate):
    try:
        item = db.query(model.Promotion).filter(model.Promotion.id == item_id)
        if not item.first():
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Promotion not found!")
        update_data = request.dict(exclude_unset=True)
        if 'code' in update_data:
            update_data['code'] = update_data['code'].strip().upper()
        item.update(update_data, synchronize_session=False)
        db.commit()
    except SQLAlchemyError as e:
        error = str(e.__dict__['orig'])
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=error)
    return item.first()


def delete(db: Session, item_id: int):
    try:
        item = db.query(model.Promotion).filter(model.Promotion.id == item_id)
        if not item.first():
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Promotion not found!")
        item.delete(synchronize_session=False)
        db.commit()
    except SQLAlchemyError as e:
        error = str(e.__dict__['orig'])
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=error)
    return Response(status_code=status.HTTP_204_NO_CONTENT)


def validate(db: Session, code: str) -> schema.PromotionValidateResponse:
    promo = (
        db.query(model.Promotion)
        .filter(model.Promotion.code == code.strip().upper())
        .first()
    )
    if not promo:
        return schema.PromotionValidateResponse(valid=False, message="Promo code not found.")

    if promo.expiration_date < datetime.now():
        return schema.PromotionValidateResponse(valid=False, message="Promo code has expired.")

    return schema.PromotionValidateResponse(
        valid=True,
        discount_percentage=promo.discount_percentage,
        message=f"Valid! {promo.discount_percentage}% discount applied.",
    )


def get_valid_promotion_by_code(db: Session, code: str) -> model.Promotion:
    promo = (
        db.query(model.Promotion)
        .filter(model.Promotion.code == code.strip().upper())
        .first()
    )
    if not promo:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Promo code not found.")
    if promo.expiration_date < datetime.now():
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Promo code has expired.")
    return promo