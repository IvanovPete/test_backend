from django.contrib import admin
from .models import User, Article, Comment, Category


@admin.register(User)
class UserAdmin(admin.ModelAdmin):
    list_display = ['username', 'email', 'is_staff', 'date_joined']
    list_filter = ['is_staff', 'is_superuser', 'date_joined']
    search_fields = ['username', 'email']


@admin.register(Category)
class CategoryAdmin(admin.ModelAdmin):
    list_display = ['name', 'created_at']
    search_fields = ['name']


@admin.register(Article)
class ArticleAdmin(admin.ModelAdmin):
    list_display = ['title', 'author', 'category', 'created_at', 'updated_at']
    list_filter = ['category', 'created_at']
    search_fields = ['title', 'content']
    readonly_fields = ['created_at', 'updated_at']


@admin.register(Comment)
class CommentAdmin(admin.ModelAdmin):
    list_display = ['article', 'author', 'created_at', 'updated_at']
    list_filter = ['created_at']
    search_fields = ['content']
    readonly_fields = ['created_at', 'updated_at']

