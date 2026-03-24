from pydantic import BaseModel, Field

class Restaurant(BaseModel):
    id: str
    name: str
    cuisine: str | None = None
    address: str | None = None
    rating: float | None = Field(default=None, ge=0, le=5)

class RestaurantCreate(BaseModel):
    name: str = Field(min_length=1)
    cuisine: str | None = None
    address: str | None = None
    rating: float | None = Field(default=None, ge=0, le=5)

class RestaurantUpdate(BaseModel):
    name: str = Field(min_length=1)
    cuisine: str | None = None
    address: str | None = None
    rating: float | None = Field(default=None, ge=0, le=5)