from django.contrib import admin
from django.urls import path
from ninja import NinjaAPI
from api.views import auth_router, articles_router, comments_router
import logging

logger = logging.getLogger('api')

api = NinjaAPI(title='Blog API', version='1.0.0')

api.add_router('/auth', auth_router)
api.add_router('/articles', articles_router)
api.add_router('/comments', comments_router)

urlpatterns = [
    path('admin/', admin.site.urls),
    path('api/', api.urls),
]

