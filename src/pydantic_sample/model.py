# models.py
from pydantic import BaseModel

class Person(BaseModel):
    _is_pydantic_model_ = True
    name: str
    age: int
    email: str | None = None

class Address(BaseModel):
    _is_pydantic_model_ = True
    street: str
    city: str
    zip_code: str

class Company(BaseModel):
    _is_pydantic_model_ = True
    name: str
    address: Address
    employees: list[Person] = []

class NonModelClass:
    pass