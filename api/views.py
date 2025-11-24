from ninja import Router
from ninja.errors import HttpError
from django.contrib.auth import authenticate
from django.shortcuts import get_object_or_404
from .models import User, Article, Comment, Category
from .schemas import (
    UserRegisterSchema, UserLoginSchema, TokenResponseSchema,
    ArticleCreateSchema, ArticleUpdateSchema, ArticleSchema,
    CommentCreateSchema, CommentUpdateSchema, CommentSchema,
    CategorySchema
)
from .auth import get_user_from_token
import logging

logger = logging.getLogger('api')

auth_router = Router()
articles_router = Router()
comments_router = Router()


@auth_router.post('/register', response=TokenResponseSchema)
def register(request, data: UserRegisterSchema):
    if User.objects.filter(username=data.username).exists():
        logger.warning(f'Попытка регистрации с существующим username: {data.username}')
        raise HttpError(400, 'Пользователь с таким username уже существует')
    
    user = User.objects.create_user(username=data.username, password=data.password)
    token = user.generate_token()
    logger.info(f'Пользователь зарегистрирован: {data.username}')
    return {'token': token}


@auth_router.post('/login', response=TokenResponseSchema)
def login(request, data: UserLoginSchema):
    user = authenticate(username=data.username, password=data.password)
    if not user:
        logger.warning(f'Неудачная попытка входа: {data.username}')
        raise HttpError(401, 'Неверный username или password')
    
    if not user.token:
        token = user.generate_token()
    else:
        token = user.token
    
    logger.info(f'Пользователь вошел: {data.username}')
    return {'token': token}


@articles_router.get('', response=list[ArticleSchema])
def list_articles(request):
    articles = Article.objects.select_related('author', 'category').all()
    logger.info('Получен список статей')
    return [
        ArticleSchema(
            id=a.id,
            title=a.title,
            content=a.content,
            author_id=a.author.id,
            author_username=a.author.username,
            category=CategorySchema(id=a.category.id, name=a.category.name, created_at=a.category.created_at) if a.category else None,
            created_at=a.created_at,
            updated_at=a.updated_at
        ) for a in articles
    ]


@articles_router.post('', response=ArticleSchema)
def create_article(request, data: ArticleCreateSchema):
    user = get_user_from_token(request)
    if not user:
        logger.warning('Попытка создания статьи без авторизации')
        raise HttpError(401, 'Требуется авторизация')
    
    category = None
    if data.category_id:
        try:
            category = Category.objects.get(id=data.category_id)
        except Category.DoesNotExist:
            logger.warning(f'Категория не найдена: {data.category_id}')
            raise HttpError(400, 'Категория не найдена')
    
    article = Article.objects.create(
        title=data.title,
        content=data.content,
        author=user,
        category=category
    )
    logger.info(f'Статья создана: {article.id} пользователем {user.username}')
    return ArticleSchema(
        id=article.id,
        title=article.title,
        content=article.content,
        author_id=article.author.id,
        author_username=article.author.username,
        category=CategorySchema(id=category.id, name=category.name, created_at=category.created_at) if category else None,
        created_at=article.created_at,
        updated_at=article.updated_at
    )


@articles_router.get('/{article_id}', response=ArticleSchema)
def get_article(request, article_id: int):
    article = get_object_or_404(Article, id=article_id)
    logger.info(f'Получена статья: {article_id}')
    return ArticleSchema(
        id=article.id,
        title=article.title,
        content=article.content,
        author_id=article.author.id,
        author_username=article.author.username,
        category=CategorySchema(id=article.category.id, name=article.category.name, created_at=article.category.created_at) if article.category else None,
        created_at=article.created_at,
        updated_at=article.updated_at
    )


@articles_router.put('/{article_id}', response=ArticleSchema)
def update_article(request, article_id: int, data: ArticleUpdateSchema):
    user = get_user_from_token(request)
    if not user:
        logger.warning('Попытка обновления статьи без авторизации')
        raise HttpError(401, 'Требуется авторизация')
    
    article = get_object_or_404(Article, id=article_id)
    if article.author != user:
        logger.warning(f'Попытка обновления чужой статьи: {article_id} пользователем {user.username}')
        raise HttpError(403, 'Вы можете редактировать только свои статьи')
    
    if data.title is not None:
        article.title = data.title
    if data.content is not None:
        article.content = data.content
    if data.category_id is not None:
        try:
            article.category = Category.objects.get(id=data.category_id)
        except Category.DoesNotExist:
            logger.warning(f'Категория не найдена: {data.category_id}')
            raise HttpError(400, 'Категория не найдена')
    
    article.save()
    logger.info(f'Статья обновлена: {article_id} пользователем {user.username}')
    return ArticleSchema(
        id=article.id,
        title=article.title,
        content=article.content,
        author_id=article.author.id,
        author_username=article.author.username,
        category=CategorySchema(id=article.category.id, name=article.category.name, created_at=article.category.created_at) if article.category else None,
        created_at=article.created_at,
        updated_at=article.updated_at
    )


@articles_router.delete('/{article_id}')
def delete_article(request, article_id: int):
    user = get_user_from_token(request)
    if not user:
        logger.warning('Попытка удаления статьи без авторизации')
        raise HttpError(401, 'Требуется авторизация')
    
    article = get_object_or_404(Article, id=article_id)
    if article.author != user:
        logger.warning(f'Попытка удаления чужой статьи: {article_id} пользователем {user.username}')
        raise HttpError(403, 'Вы можете удалять только свои статьи')
    
    article.delete()
    logger.info(f'Статья удалена: {article_id} пользователем {user.username}')
    return {'success': True}


@comments_router.get('', response=list[CommentSchema])
def list_comments(request):
    comments = Comment.objects.select_related('article', 'author').all()
    logger.info('Получен список комментариев')
    return [
        CommentSchema(
            id=c.id,
            article_id=c.article.id,
            article_title=c.article.title,
            author_id=c.author.id,
            author_username=c.author.username,
            content=c.content,
            created_at=c.created_at,
            updated_at=c.updated_at
        ) for c in comments
    ]


@comments_router.post('', response=CommentSchema)
def create_comment(request, data: CommentCreateSchema):
    user = get_user_from_token(request)
    if not user:
        logger.warning('Попытка создания комментария без авторизации')
        raise HttpError(401, 'Требуется авторизация')
    
    article = get_object_or_404(Article, id=data.article_id)
    comment = Comment.objects.create(
        article=article,
        author=user,
        content=data.content
    )
    logger.info(f'Комментарий создан: {comment.id} пользователем {user.username}')
    return CommentSchema(
        id=comment.id,
        article_id=comment.article.id,
        article_title=comment.article.title,
        author_id=comment.author.id,
        author_username=comment.author.username,
        content=comment.content,
        created_at=comment.created_at,
        updated_at=comment.updated_at
    )


@comments_router.get('/{comment_id}', response=CommentSchema)
def get_comment(request, comment_id: int):
    comment = get_object_or_404(Comment, id=comment_id)
    logger.info(f'Получен комментарий: {comment_id}')
    return CommentSchema(
        id=comment.id,
        article_id=comment.article.id,
        article_title=comment.article.title,
        author_id=comment.author.id,
        author_username=comment.author.username,
        content=comment.content,
        created_at=comment.created_at,
        updated_at=comment.updated_at
    )


@comments_router.put('/{comment_id}', response=CommentSchema)
def update_comment(request, comment_id: int, data: CommentUpdateSchema):
    user = get_user_from_token(request)
    if not user:
        logger.warning('Попытка обновления комментария без авторизации')
        raise HttpError(401, 'Требуется авторизация')
    
    comment = get_object_or_404(Comment, id=comment_id)
    if comment.author != user:
        logger.warning(f'Попытка обновления чужого комментария: {comment_id} пользователем {user.username}')
        raise HttpError(403, 'Вы можете редактировать только свои комментарии')
    
    comment.content = data.content
    comment.save()
    logger.info(f'Комментарий обновлен: {comment_id} пользователем {user.username}')
    return CommentSchema(
        id=comment.id,
        article_id=comment.article.id,
        article_title=comment.article.title,
        author_id=comment.author.id,
        author_username=comment.author.username,
        content=comment.content,
        created_at=comment.created_at,
        updated_at=comment.updated_at
    )


@comments_router.delete('/{comment_id}')
def delete_comment(request, comment_id: int):
    user = get_user_from_token(request)
    if not user:
        logger.warning('Попытка удаления комментария без авторизации')
        raise HttpError(401, 'Требуется авторизация')
    
    comment = get_object_or_404(Comment, id=comment_id)
    if comment.author != user:
        logger.warning(f'Попытка удаления чужого комментария: {comment_id} пользователем {user.username}')
        raise HttpError(403, 'Вы можете удалять только свои комментарии')
    
    comment.delete()
    logger.info(f'Комментарий удален: {comment_id} пользователем {user.username}')
    return {'success': True}

