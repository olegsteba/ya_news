from django.contrib.auth import get_user_model
from django.test import TestCase, Client
from news.models import News

User = get_user_model()


class TestNews(TestCase):

    @classmethod
    def setUpTestData(cls):
        cls.news = News.objects.create(
            title='Заголовок новости',
            text='Тестовый текст',
        )

        # Создаем пользователя
        cls.user = User.objects.create(username='testUser')
        # Создаем объект клиента
        cls.user_client = Client()
        # Авторизация force_login()
        cls.user_client.force_login(cls.user)
        # Теперь запросы можем делать от пользователя testUser

    def test_successful_creation(self):
        # Проверяем создание новости
        news_count = News.objects.count()
        self.assertEqual(news_count, 1)

    def test_title(self):
        # Сравниваем что создали с ожиданием
        self.assertEqual(self.news.title, 'Заголовок новости')
