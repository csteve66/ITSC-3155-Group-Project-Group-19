from fastapi import APIRouter, Depends, status, Response
from sqlalchemy.orm import Session
from ..controllers import reviews as controller
from ..schemas import reviews as schema
from ..dependencies.database import get_db

router = APIRouter(
    tags=['Reviews'],
    prefix="/reviews"
)


@router.post("/", response_model=schema.Review, status_code=status.HTTP_201_CREATED)
def create(request: schema.ReviewCreate, db: Session = Depends(get_db)):
    return controller.create(db=db, request=request)


@router.get("/", response_model=list[schema.Review])
def read_all(db: Session = Depends(get_db)):
    return controller.read_all(db)


@router.get("/order/{order_id}", response_model=schema.Review)
def read_by_order(order_id: int, db: Session = Depends(get_db)):
    return controller.read_by_order(db, order_id=order_id)


@router.get("/customer/{customer_id}", response_model=list[schema.Review])
def read_by_customer(customer_id: int, db: Session = Depends(get_db)):
    return controller.read_by_customer(db, customer_id=customer_id)


@router.get("/{item_id}", response_model=schema.Review)
def read_one(item_id: int, db: Session = Depends(get_db)):
    return controller.read_one(db, item_id=item_id)


@router.put("/{item_id}", response_model=schema.Review)
def update(item_id: int, request: schema.ReviewUpdate, db: Session = Depends(get_db)):
    return controller.update(db=db, request=request, item_id=item_id)


@router.delete("/{item_id}")
def delete(item_id: int, db: Session = Depends(get_db)):
    return controller.delete(db=db, item_id=item_id)