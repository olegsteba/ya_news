import pytest

from django.conf import settings
from django.urls import reverse

from news.forms import CommentForm


pytestmark = [pytest.mark.django_db]


def test_news_count(client, news_list):
    """Количество новостей на главной странице."""
    url = reverse('news:home')
    response = client.get(url)
    object_list = response.context['object_list']
    news_count = object_list.count()
    assert news_count == settings.NEWS_COUNT_ON_HOME_PAGE


def test_news_order(client, news_list):
    """Сортировка новостей по дате, свежие новости в начале списка."""
    url = reverse('news:home')
    response = client.get(url)
    object_list = response.context['object_list']
    all_dates = [news.date for news in object_list]
    sorted_dates = sorted(all_dates, reverse=True)
    assert all_dates == sorted_dates


def test_comments_order(client, news, comment_list):
    """Сортировка комментариев от старых к новым."""
    url = reverse('news:detail', args=(news.id, ))
    response = client.get(url)
    assert 'news' in response.context
    news = response.context['news']
    all_comments = list(news.comment_set.all())
    all_timestamps = [comment.created for comment in all_comments]
    sorted_timestamps = sorted(all_timestamps)
    assert all_timestamps == sorted_timestamps


def test_client_has_comment_form(client, author_client, news):
    """Форма добавления комментариев к новостям:
    - не доступна анонимному пользователю;
    - доступна для авторизированных пользователей.
    """
    url = reverse('news:detail', args=(news.id, ))
    response = client.get(url)
    author_client_response = author_client.get(url)
    assert 'form' not in response.context
    assert isinstance(author_client_response.context['form'], CommentForm)
