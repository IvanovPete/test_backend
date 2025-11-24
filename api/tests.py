from django.test import TestCase
from django.contrib.auth import get_user_model
from .models import Article, Comment, Category
import json

User = get_user_model()


class AuthTests(TestCase):
    def setUp(self):
        self.user_data = {
            'username': 'testuser',
            'password': 'testpass123'
        }

    def test_register_success(self):
        response = self.client.post('/api/auth/register', 
            json.dumps({'username': 'newuser', 'password': 'password123'}),
            content_type='application/json')
        self.assertEqual(response.status_code, 200)
        self.assertIn('token', response.json())

    def test_register_duplicate_username(self):
        User.objects.create_user(username='existing', password='pass')
        response = self.client.post('/api/auth/register',
            json.dumps({'username': 'existing', 'password': 'password123'}),
            content_type='application/json')
        self.assertEqual(response.status_code, 400)

    def test_login_success(self):
        User.objects.create_user(username='testuser', password='testpass123')
        response = self.client.post('/api/auth/login',
            json.dumps({'username': 'testuser', 'password': 'testpass123'}),
            content_type='application/json')
        self.assertEqual(response.status_code, 200)
        self.assertIn('token', response.json())

    def test_login_wrong_password(self):
        User.objects.create_user(username='testuser', password='testpass123')
        response = self.client.post('/api/auth/login',
            json.dumps({'username': 'testuser', 'password': 'wrongpass'}),
            content_type='application/json')
        self.assertEqual(response.status_code, 401)


class ArticleTests(TestCase):
    def setUp(self):
        self.user = User.objects.create_user(username='author', password='pass123')
        self.user.token = 'test-token-123'
        self.user.save()
        self.category = Category.objects.create(name='Технологии')

    def test_create_article_success(self):
        response = self.client.post('/api/articles',
            json.dumps({'title': 'Test Article', 'content': 'Content here', 'category_id': self.category.id}),
            content_type='application/json', HTTP_AUTHORIZATION='Bearer test-token-123')
        self.assertEqual(response.status_code, 200)
        self.assertEqual(Article.objects.count(), 1)

    def test_create_article_unauthorized(self):
        response = self.client.post('/api/articles',
            json.dumps({'title': 'Test Article', 'content': 'Content here'}),
            content_type='application/json')
        self.assertEqual(response.status_code, 401)

    def test_list_articles(self):
        Article.objects.create(title='Article 1', content='Content', author=self.user)
        Article.objects.create(title='Article 2', content='Content', author=self.user)
        response = self.client.get('/api/articles')
        self.assertEqual(response.status_code, 200)
        self.assertEqual(len(response.json()), 2)

    def test_get_article(self):
        article = Article.objects.create(title='Test', content='Content', author=self.user)
        response = self.client.get(f'/api/articles/{article.id}')
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.json()['title'], 'Test')

    def test_update_own_article(self):
        article = Article.objects.create(title='Old', content='Old', author=self.user)
        response = self.client.put(f'/api/articles/{article.id}',
            json.dumps({'title': 'New Title', 'content': 'New Content'}),
            content_type='application/json', HTTP_AUTHORIZATION='Bearer test-token-123')
        self.assertEqual(response.status_code, 200)
        article.refresh_from_db()
        self.assertEqual(article.title, 'New Title')

    def test_update_other_article(self):
        other_user = User.objects.create_user(username='other', password='pass')
        article = Article.objects.create(title='Test', content='Content', author=other_user)
        response = self.client.put(f'/api/articles/{article.id}',
            json.dumps({'title': 'Hacked'}),
            content_type='application/json', HTTP_AUTHORIZATION='Bearer test-token-123')
        self.assertEqual(response.status_code, 403)

    def test_delete_own_article(self):
        article = Article.objects.create(title='Test', content='Content', author=self.user)
        response = self.client.delete(f'/api/articles/{article.id}', HTTP_AUTHORIZATION='Bearer test-token-123')
        self.assertEqual(response.status_code, 200)
        self.assertEqual(Article.objects.count(), 0)

    def test_delete_other_article(self):
        other_user = User.objects.create_user(username='other', password='pass')
        article = Article.objects.create(title='Test', content='Content', author=other_user)
        response = self.client.delete(f'/api/articles/{article.id}', HTTP_AUTHORIZATION='Bearer test-token-123')
        self.assertEqual(response.status_code, 403)


class CommentTests(TestCase):
    def setUp(self):
        self.user = User.objects.create_user(username='author', password='pass123')
        self.user.token = 'test-token-123'
        self.user.save()
        self.article = Article.objects.create(title='Test Article', content='Content', author=self.user)

    def test_create_comment_success(self):
        response = self.client.post('/api/comments',
            json.dumps({'article_id': self.article.id, 'content': 'Great article!'}),
            content_type='application/json', HTTP_AUTHORIZATION='Bearer test-token-123')
        self.assertEqual(response.status_code, 200)
        self.assertEqual(Comment.objects.count(), 1)

    def test_create_comment_unauthorized(self):
        response = self.client.post('/api/comments',
            json.dumps({'article_id': self.article.id, 'content': 'Comment'}),
            content_type='application/json')
        self.assertEqual(response.status_code, 401)

    def test_list_comments(self):
        Comment.objects.create(article=self.article, author=self.user, content='Comment 1')
        Comment.objects.create(article=self.article, author=self.user, content='Comment 2')
        response = self.client.get('/api/comments')
        self.assertEqual(response.status_code, 200)
        self.assertEqual(len(response.json()), 2)

    def test_get_comment(self):
        comment = Comment.objects.create(article=self.article, author=self.user, content='Test')
        response = self.client.get(f'/api/comments/{comment.id}')
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.json()['content'], 'Test')

    def test_update_own_comment(self):
        comment = Comment.objects.create(article=self.article, author=self.user, content='Old')
        response = self.client.put(f'/api/comments/{comment.id}',
            json.dumps({'content': 'New'}),
            content_type='application/json', HTTP_AUTHORIZATION='Bearer test-token-123')
        self.assertEqual(response.status_code, 200)
        comment.refresh_from_db()
        self.assertEqual(comment.content, 'New')

    def test_update_other_comment(self):
        other_user = User.objects.create_user(username='other', password='pass')
        comment = Comment.objects.create(article=self.article, author=other_user, content='Test')
        response = self.client.put(f'/api/comments/{comment.id}',
            json.dumps({'content': 'Hacked'}),
            content_type='application/json', HTTP_AUTHORIZATION='Bearer test-token-123')
        self.assertEqual(response.status_code, 403)

    def test_delete_own_comment(self):
        comment = Comment.objects.create(article=self.article, author=self.user, content='Test')
        response = self.client.delete(f'/api/comments/{comment.id}', HTTP_AUTHORIZATION='Bearer test-token-123')
        self.assertEqual(response.status_code, 200)
        self.assertEqual(Comment.objects.count(), 0)

    def test_delete_other_comment(self):
        other_user = User.objects.create_user(username='other', password='pass')
        comment = Comment.objects.create(article=self.article, author=other_user, content='Test')
        response = self.client.delete(f'/api/comments/{comment.id}', HTTP_AUTHORIZATION='Bearer test-token-123')
        self.assertEqual(response.status_code, 403)

