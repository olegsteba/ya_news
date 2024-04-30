import pytest

from http import HTTPStatus
from pytest_django.asserts import assertFormError

from django.urls import reverse

from news.models import Comment
from news.forms import WARNING

pytestmark = [pytest.mark.django_db]


@pytest.mark.parametrize(
    'parametrized_client, expected_comment_count',
    (
        (pytest.lazy_fixture('author_client'), 1),
        (pytest.lazy_fixture('client'), 0),
    ),
)
@pytest.mark.parametrize(
    'name, args',
    (
        ('news:detail', pytest.lazy_fixture('news_id_for_args')),
    )
)
def test_user_comment_create(
    parametrized_client, name, args, expected_comment_count, form_data
):
    """Создание комментариев:
    - авторизированный пользователь может отправить комментарий;
    - анонимный пользователь не может отправить комментарий.
    """
    url = reverse(name, args=args)
    parametrized_client.post(url, data=form_data)
    assert Comment.objects.count() == expected_comment_count


@pytest.mark.parametrize(
    'name, args',
    (
        ('news:detail', pytest.lazy_fixture('news_id_for_args')),
    )
)
def test_user_cant_use_bad_words(author_client, name, args, bad_words_data):
    """Комментарий содержет запрещенные слова."""
    url = reverse(name, args=args)
    response = author_client.post(url, data=bad_words_data)
    assertFormError(response, form='form', field='text', errors=WARNING)
    assert Comment.objects.count() == 0


@pytest.mark.parametrize(
    'name, args',
    (
        ('news:edit', pytest.lazy_fixture('comment_id_for_args')),
    )
)
def test_author_can_edit_comment(
    author_client, name, args, form_data, comment
):
    """Редактирование комментария автором."""
    url = reverse(name, args=args)
    author_client.post(url, form_data)
    comment.refresh_from_db()
    assert comment.text == form_data['text']


@pytest.mark.parametrize(
    'name, args',
    (
        ('news:edit', pytest.lazy_fixture('comment_id_for_args')),
    )
)
def test_other_cant_edit_comment(
    not_author_client, name, args, form_data, comment
):
    """Редактирование чужих комментария невозможно."""
    url = reverse(name, args=args)
    response = not_author_client.post(url, form_data)
    assert response.status_code == HTTPStatus.NOT_FOUND
    comment_from_db = Comment.objects.get(id=comment.id)
    assert comment.text == comment_from_db.text


@pytest.mark.parametrize(
    'name, args',
    (
        ('news:delete', pytest.lazy_fixture('comment_id_for_args')),
    )
)
def test_author_can_delete_comment(author_client, name, args):
    """Удаление комментария автором."""
    url = reverse(name, args=args)
    author_client.post(url)
    assert Comment.objects.count() == 0


@pytest.mark.parametrize(
    'name, args',
    (
        ('news:delete', pytest.lazy_fixture('comment_id_for_args')),
    )
)
def test_other_cant_edit_comment(not_author_client, name, args):
    """Удаление чужих комментария невозможно."""
    url = reverse(name, args=args)
    response = not_author_client.post(url)
    assert response.status_code == HTTPStatus.NOT_FOUND
    assert Comment.objects.count() == 1
