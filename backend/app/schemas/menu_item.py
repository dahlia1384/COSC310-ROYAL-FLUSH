from pydantic import BaseModel, Field

class MenuItem(BaseModel):
    id: str
    restaurant_id: str
    name: str
    price: float = Field(ge=0)
    description: str | None = None
    available: bool = True

class MenuItemCreate(BaseModel):
    name: str = Field(min_length=1)
    price: float = Field(ge=0)
    description: str | None = None
    available: bool = True

class MenuItemUpdate(BaseModel):
    name: str = Field(min_length=1)
    price: float = Field(ge=0)
    description: str | None = None
    available: bool = True