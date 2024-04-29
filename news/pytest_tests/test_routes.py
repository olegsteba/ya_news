import pytest

from http import HTTPStatus

from django.urls import reverse
from pytest_django.asserts import assertRedirects


@pytest.mark.django_db
@pytest.mark.parametrize(
    'name, args',
    (
        ('news:home', None),
        ('news:detail', pytest.lazy_fixture('news_id_for_args')),
        ('users:login', None),
        ('users:logout', None),
        ('users:signup', None)
    ),
)
def test_home_availability_for_anonymous_user(client, name, args):
    """Страницы доступны анонимному пользователю:
    - главная страница;
    - страница авторизации;
    - страница выхода;
    - страница регистрации.
    """
    url = reverse(name, args=args)
    response = client.get(url)
    assert response.status_code == HTTPStatus.OK


@pytest.mark.parametrize(
    'name, args',
    (
        ('news:edit', pytest.lazy_fixture('comment_id_for_args')),
        ('news:delete', pytest.lazy_fixture('comment_id_for_args')),
    ),
)
def test_page_availability_for_author(author_client, name, args):
    """Страницы доступные автору:
    - страница редактированя комментария;
    - страница удаления комментария.
    """
    url = reverse(name, args=args)
    response = author_client.get(url)
    assert response.status_code == HTTPStatus.OK


@pytest.mark.parametrize(
    'parametrized_client, expected_status',
    (
        (pytest.lazy_fixture('not_author_client'), HTTPStatus.NOT_FOUND),
        (pytest.lazy_fixture('author_client'), HTTPStatus.OK),
    ),
)
@pytest.mark.parametrize(
    'name',
    ('news:edit', 'news:delete'),
)
def test_page_availability_for_different_users(
    parametrized_client, name, comment_id_for_args, expected_status
):
    """Доступность страниц для автора комментария мтатус 200,
    для клиента статус 404:
    - страница редактирования комментария;
    - страница удаления комментария.
    """
    url = reverse(name, args=comment_id_for_args)
    response = parametrized_client.get(url)
    assert response.status_code == expected_status


@pytest.mark.parametrize(
    'name',
    ('news:edit', 'news:delete'),
)
def test_redirects_for_anonymous_client(client, name, comment_id_for_args):
    """Перенаправление на страницу авторизации анонимного пользователя
    при открытии страниц:
    - страница редактирования комментария;
    - страница удаления комментария.
    """
    logint_url = reverse('users:login')
    url = reverse(name, args=comment_id_for_args)
    expected_url = f'{logint_url}?next={url}'
    response = client.get(url)
    assertRedirects(response, expected_url)
