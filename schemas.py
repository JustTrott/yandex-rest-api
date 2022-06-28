from __future__ import annotations

from datetime import datetime
from enum import Enum
from typing import List, Optional, Any
from uuid import UUID

from pydantic import BaseModel, Field, validator

from date_shenanigans import string_to_date, date_to_string

class ShopUnitType(Enum):
    OFFER = 'OFFER'
    CATEGORY = 'CATEGORY'


class ShopUnitBase(BaseModel):
    id: UUID = Field(
        ...,
        description='Уникальный идентфикатор',
        example='3fa85f64-5717-4562-b3fc-2c963f66a333',
    )
    name: str = Field(..., description='Имя элемента')
    parentId: Optional[UUID] = Field(
        None,
        description='UUID родительской категории',
        example='3fa85f64-5717-4562-b3fc-2c963f66a333',
    )
    type: ShopUnitType
    price: Optional[int] = Field(
        None,
        description='Целое число, для категории - это средняя цена всех дочерних товаров(включая товары подкатегорий). Если цена является не целым числом, округляется в меньшую сторону до целого числа. Если категория не содержит товаров цена равна null.',
    )

    class Config:
        use_enum_values = True

class ShopUnit(ShopUnitBase):
    date: str = Field(
        ...,
        description='Время последнего обновления элемента.',
        example='2022-05-28T21:12:01.000Z',
    )
    children: Optional[List[ShopUnit]] = Field(
        None,
        description='Список всех дочерних товаров\\категорий. Для товаров поле равно null.',
    )

    @validator("date", pre=True)
    def convert_time(cls, value: datetime) -> str:
        return date_to_string(value)
        
    class Config:
        orm_mode = True


class ShopUnitImport(ShopUnitBase):
    class Config:
        orm_mode = True


class ShopUnitImportRequest(BaseModel):
    items: List[ShopUnitImport] = Field(
        None, description='Импортируемые элементы'
    )
    updateDate: datetime = Field(
        None,
        description='Время обновления добавляемых товаров/категорий.',
        example='2022-05-28T21:12:01.000Z',
    )

    @validator("updateDate", pre=True)
    def validate_time(cls, value: Any) -> Any:
        if isinstance(value, str):
            string_to_date(value)
            return value
        else:
            raise TypeError

    class Config:
        orm_mode = True


class ShopUnitStatisticUnit(ShopUnitBase):
    date: str = Field(..., description='Время обновления элемента.')
    class Config:
        orm_mode = True
    
    @validator("date", pre=True)
    def convert_time(cls, value: datetime) -> str:
        return date_to_string(value)


class ShopUnitStatisticResponse(BaseModel):
    items: Optional[List[ShopUnitStatisticUnit]] = Field(
        None, description='История в произвольном порядке.'
    )
    class Config:
        orm_mode = True


class Error(BaseModel):
    code: int
    message: str
