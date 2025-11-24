from ninja import Schema
from typing import Optional
from datetime import datetime


class UserRegisterSchema(Schema):
    username: str
    password: str


class UserLoginSchema(Schema):
    username: str
    password: str


class TokenResponseSchema(Schema):
    token: str


class CategorySchema(Schema):
    id: int
    name: str
    created_at: datetime

    class Config:
        from_attributes = True


class ArticleCreateSchema(Schema):
    title: str
    content: str
    category_id: Optional[int] = None


class ArticleUpdateSchema(Schema):
    title: Optional[str] = None
    content: Optional[str] = None
    category_id: Optional[int] = None


class ArticleSchema(Schema):
    id: int
    title: str
    content: str
    author_id: int
    author_username: str
    category: Optional[CategorySchema] = None
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True


class CommentCreateSchema(Schema):
    article_id: int
    content: str


class CommentUpdateSchema(Schema):
    content: str


class CommentSchema(Schema):
    id: int
    article_id: int
    article_title: str
    author_id: int
    author_username: str
    content: str
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True

