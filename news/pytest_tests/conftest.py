import pytest

from django.test.client import Client

from news.models import News, Comment


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
