import pytest
from datetime import datetime, timedelta

from django.conf import settings
from django.utils import timezone
from django.test.client import Client

from news.models import News, Comment
from news.forms import BAD_WORDS


@pytest.fixture
def author(django_user_model):
    """Автор комментария."""
    return django_user_model.objects.create(username='Автор')


@pytest.fixture
def not_author(django_user_model):
    """Простой пользователь."""
    return django_user_model.objects.create(username='Не автор')


@pytest.fixture
def author_client(author):
    """Авторизация автора."""
    client = Client()
    client.force_login(author)
    return client


@pytest.fixture
def not_author_client(not_author):
    """Авторизация простого пользователя."""
    client = Client()
    client.force_login(not_author)
    return client


@pytest.fixture
def news():
    """Объект новости."""
    news = News.objects.create(title='Заголовок новости', text='Текст новости')
    return news


@pytest.fixture
def news_id_for_args(news):
    """Возвращает кортедж ID новости."""
    return (news.pk, )


@pytest.fixture
def news_list():
    """Список из 11 объектов Новости"""
    news_list = News.objects.bulk_create(
        News(
            title=f'Новость {index}',
            text='Текст новости',
            date=datetime.today() - timedelta(days=index),
        )
        for index in range(settings.NEWS_COUNT_ON_HOME_PAGE + 1)
    )
    return news_list


@pytest.fixture
def comment(author, news):
    """Объект комментарий."""
    comment = Comment.objects.create(
        news=news,
        author=author,
        text='Текст комментария',
    )
    return comment


@pytest.fixture
def comment_id_for_args(comment):
    """Возвращает кортедж ID комментарий."""
    return (comment.pk, )


@pytest.fixture
def comment_list(author, news):
    """Список из 10 комментариев к новости."""
    for index in range(10):
        comment = Comment.objects.create(
            news=news,
            author=author,
            text=f'Комментарий {index}',
        )
        comment.created = timezone.now() + timedelta(days=index)
        comment.save()
    return comment_list


@pytest.fixture
def form_data():
    """Значение формы комментария."""
    return {
        'text': 'Новый комментарий',
    }


@pytest.fixture
def bad_words_data():
    """Запрещенные слова."""
    return {
        'text': f'Какой-то текст, {BAD_WORDS[0]}, и еще.'
    }
