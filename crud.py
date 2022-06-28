from typing import List
from datetime import datetime, timedelta
from uuid import UUID

from sqlalchemy.orm import Session
from fastapi import HTTPException

import models, schemas

def get_children_recur(db: Session, itemId: UUID) -> List[models.Item]:
    children: List[models.Item] = db.query(models.Item).filter(models.Item.parentId == itemId).all()
    if not children:
        return None
    for child in children:
        child.children = get_children_recur(db, child.id)
    return children

def calc_category_price_rec(db: Session, itemId: UUID) -> int:
    children: List[models.Item] = db.query(models.Item).filter(models.Item.parentId == itemId).all()
    if not children:
        return db.query(models.Item).filter(models.Item.id == itemId).first().price
    sum = 0
    for child in children:
        sum += calc_category_price_rec(db, child.id)
    return sum // len(children)

def recalc_prices_bot_to_top(db: Session, itemId: UUID):
    db_item: models.Item = db.query(models.Item).filter(models.Item.id == itemId).first()
    if db_item.type != schemas.ShopUnitType.CATEGORY.value:
        raise TypeError(f"Item is not a {schemas.ShopUnitType.CATEGORY.value}")
    db_item.price = calc_category_price_rec(db, db_item.id)
    while(db_item.parentId is not None):
        db_item = db.query(models.Item).filter(models.Item.id == db_item.parentId).first()
        db_item.price = calc_category_price_rec(db, db_item.id)
    db.commit()

def get_item(db: Session, itemId: UUID) -> models.Item:
    db_item: models.Item = db.query(models.Item).filter(models.Item.id == itemId).first()
    if db_item is None:
        raise HTTPException(404, "Item not found")
    db_item.children = get_children_recur(db, itemId)
    return db_item

def get_item_history(db: Session, itemId: UUID, dateStart: datetime, dateEnd: datetime) -> list[models.ItemStatistic]:
    db_item_statistics: List[models.ItemStatistic]
    if dateStart is None and dateEnd is None:
        db_item_statistics = db.query(models.ItemStatistic).filter(models.ItemStatistic.id == itemId).all()
    elif dateStart is None:
        db_item_statistics = db.query(models.ItemStatistic).filter(
        models.ItemStatistic.id == itemId, models.ItemStatistic.date < dateEnd).all()
    elif dateEnd is None:
        db_item_statistics = db.query(models.ItemStatistic).filter(
        models.ItemStatistic.id == itemId, models.ItemStatistic.date >= dateStart).all()
    else:
        db_item_statistics = db.query(models.ItemStatistic).filter(
        models.ItemStatistic.id == itemId, models.ItemStatistic.date.between(dateStart, dateEnd - timedelta(seconds=1))).all()
    if not db_item_statistics:
        raise HTTPException(404, "Item not found")
    return db_item_statistics

def create_item(db: Session, item: schemas.ShopUnitImport, date: datetime):
    db_item = models.Item(id=item.id, name=item.name, type=item.type, parentId=item.parentId, price=item.price, date=date)
    db.add(db_item)
    db.commit()
    if db_item.type == schemas.ShopUnitType.OFFER.value and db_item.parentId is not None:
        recalc_prices_bot_to_top(db, db_item.parentId)
    elif db_item.type == schemas.ShopUnitType.CATEGORY.value:
        db_item.price = calc_category_price_rec(db, db_item.id)
    db.commit()

def update_item(db: Session, db_item: models.Item, item: schemas.ShopUnitImport, date: datetime):
    db_item: models.Item = db.query(models.Item).filter(models.Item.id == item.id).first()
    db_item.id = item.id
    db_item.name = item.name
    db_item.type = item.type
    oldParentId = db_item.parentId
    db_item.parentId = item.parentId
    db_item.price = item.price
    db_item.date = date
    db.commit()
    if db_item.type == schemas.ShopUnitType.OFFER.value and db_item.parentId is not None:
        recalc_prices_bot_to_top(db, db_item.parentId)
        if oldParentId != db_item.parentId and oldParentId is not None:
            recalc_prices_bot_to_top(db, oldParentId)
    elif db_item.type == schemas.ShopUnitType.CATEGORY.value:
        db_item.price = calc_category_price_rec(db, db_item.id)
    db.commit()
    

def create_or_update_items(db: Session, request: schemas.ShopUnitImportRequest):
    for item in request.items:
        db_item: models.Item = db.query(models.Item).filter(models.Item.id == item.id).first()
        if db_item is None:
            create_item(db, item, request.updateDate)
        else:
            update_item(db, db_item, item, request.updateDate)
        db_history_item = models.ItemStatistic(
            id=item.id, name=item.name, type=item.type, parentId=item.parentId, price=item.price, date=request.updateDate)
        db.add(db_history_item)
    db.commit()
        
def delete_item(db: Session, itemId: UUID):
    db_item: models.Item = db.query(models.Item).filter(models.Item.id == itemId).first()
    if db_item is None:
        raise HTTPException(404, "Item not found")
    for child in get_children_recur(db, itemId):
        child.parentId = db_item.parentId
    for entry in db.query(models.ItemStatistic).filter(models.ItemStatistic.id == itemId).all():
        db.delete(entry)
    db.delete(db_item)
    db.commit()


def get_sales(db: Session, date: datetime):
    db_items: List[models.Item] = db.query(models.Item).filter(
        models.Item.date.between(date - timedelta(days=1), date), models.Item.type == schemas.ShopUnitType.OFFER.value).all()
    return db_items
