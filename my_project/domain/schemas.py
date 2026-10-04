from pydantic import BaseModel
from typing import Optional
from decimal import Decimal
from datetime import date

from pydantic import ConfigDict
from typing import List

class FilmBase(BaseModel):
    title: str
    year: int
    description: str
    budget: Decimal

class FilmCreate(FilmBase):
    pass

class FilmUpdate(BaseModel):
    title: Optional[str] = None
    year: Optional[int] = None
    description: Optional[str] = None
    budget: Optional[Decimal] = None

class FilmResponse(FilmBase):
    id: int
    
    class Config:
        from_attributes = True


class UserBase(BaseModel):
    nick_name: str
    email: str

class UserCreate(UserBase):
    registration_date: date
    human_id: int

class UserUpdate(BaseModel):
    nick_name: Optional[str] = None
    email: Optional[str] = None
    registration_date: Optional[date] = None

class UserResponse(UserBase):
    id: int
    registration_date: date

    class Config:
        from_attributes = True
        

class ReviewBase(BaseModel):
    film_id: int
    user_id: int
    review_text: str
    review_date: date

class ReviewCreate(ReviewBase):
    pass

class ReviewUpdate(BaseModel):
    review_text: Optional[str] = None

class ReviewResponse(ReviewBase):
    pass

    class Config:
        from_attributes = True


class UserPublicResponse(BaseModel):
    
    nick_name: str
    
    model_config = ConfigDict(from_attributes=True)


class ReviewWithUserResponse(BaseModel):
    review_text: str
    review_date: date
    user: UserPublicResponse
    
    model_config = ConfigDict(from_attributes=True)
    

class FilmWithReviewsResponse(BaseModel):
    id: int
    title: str
    year: int
    reviews: List[ReviewWithUserResponse] = []
    
    model_config = ConfigDict(from_attributes=True)

class ReviewCreateSP(BaseModel):
    title: str
    nick_name: str
    review_text: str
    review_date: date