import pytest

from http import HTTPStatus
from pytest_django.asserts import assertFormError

from django.urls import reverse

from news.models import Comment
from news.forms import BAD_WORDS, WARNING

pytestmark = [pytest.mark.django_db]

COMMENT_NEW_DATA_FORM = {
    'text': 'Новый комментарий',
}
BAD_WORDS_DATA = {
    'text': f'Какой-то текст, {BAD_WORDS[0]}, и еще.'
}


@pytest.mark.parametrize(
    'parametrized_client, expected_comment_count',
    (
        (pytest.lazy_fixture('author_client'), 1),
        (pytest.lazy_fixture('client'), 0),
    ),
)
@pytest.mark.parametrize(
    'name',
    (
        ('news:detail'),
    )
)
def test_user_comment_create(
    parametrized_client, name, news, expected_comment_count
):
    """Создание комментариев:
    - авторизированный пользователь может отправить комментарий;
    - анонимный пользователь не может отправить комментарий.
    """
    url = reverse(name, args=(news.id, ))
    parametrized_client.post(url, data=COMMENT_NEW_DATA_FORM)
    assert Comment.objects.count() == expected_comment_count


@pytest.mark.parametrize(
    'name',
    (
        ('news:detail'),
    )
)
def test_user_cant_use_bad_words(author_client, name, news):
    """Комментарий содержет запрещенные слова."""
    url = reverse(name, args=(news.id, ))
    response = author_client.post(url, data=BAD_WORDS_DATA)
    assertFormError(response, form='form', field='text', errors=WARNING)
    assert Comment.objects.count() == 0


@pytest.mark.parametrize(
    'name',
    (
        ('news:edit'),
    )
)
def test_author_can_edit_comment(author_client, name, comment):
    """Редактирование комментария автором."""
    url = reverse(name, args=(comment.id, ))
    author_client.post(url, data=COMMENT_NEW_DATA_FORM)
    comment.refresh_from_db()
    assert comment.text == COMMENT_NEW_DATA_FORM['text']


@pytest.mark.parametrize(
    'name',
    (
        ('news:edit'),
    )
)
def test_other_cant_edit_comment(
    not_author_client, name, comment
):
    """Редактирование чужих комментария невозможно."""
    url = reverse(name, args=(comment.id, ))
    response = not_author_client.post(url, data=COMMENT_NEW_DATA_FORM)
    assert response.status_code == HTTPStatus.NOT_FOUND
    comment_from_db = Comment.objects.get(id=comment.id)
    assert comment.text == comment_from_db.text


@pytest.mark.parametrize(
    'name',
    (
        ('news:delete'),
    )
)
def test_author_can_delete_comment(author_client, name, comment):
    """Удаление комментария автором."""
    url = reverse(name, args=(comment.id, ))
    author_client.post(url)
    assert Comment.objects.count() == 0


@pytest.mark.parametrize(
    'name',
    (
        ('news:delete'),
    )
)
def test_other_cant_edit_comment(not_author_client, name, comment):
    """Удаление чужих комментария невозможно."""
    url = reverse(name, args=(comment.id, ))
    response = not_author_client.post(url)
    assert response.status_code == HTTPStatus.NOT_FOUND
    assert Comment.objects.count() == 1
