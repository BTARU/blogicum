from django.contrib.auth import get_user_model
from django.db import models
from django.db.models.query import QuerySet
from django.utils import timezone
from django.urls import reverse

from core.models import BaseModel
from core.constants import (
    SLUG_FIELD_MAX_LENGTH, TEXT_FIELD_MAX_LENGTH, TRUNCATE_AMOUNT
)


class PublishedPostsManager(models.Manager):
    """Запрос на опубликованные посты."""

    def get_queryset(self) -> QuerySet:
        return super().get_queryset().select_related(
            'author', 'location', 'category'
        ).filter(
            is_published=True,
            category__is_published=True,
            pub_date__lt=timezone.now(),
        )


class PostForeignKeyManager(models.Manager):
    """Стандартный запрос на посты с обьединением внешних таблиц."""

    def get_queryset(self) -> QuerySet:
        return super().get_queryset().select_related(
            'author', 'location', 'category'
        )


class Category(BaseModel):
    """Модель категории постов блога."""

    title = models.CharField(
        max_length=TEXT_FIELD_MAX_LENGTH,
        verbose_name='Заголовок'
    )
    slug = models.SlugField(
        max_length=SLUG_FIELD_MAX_LENGTH,
        unique=True,
        verbose_name='Идентификатор',
        help_text=(
            'Идентификатор страницы для URL; '
            'разрешены символы латиницы, цифры, дефис и подчёркивание.'
        )
    )
    description = models.TextField(
        verbose_name='Описание'
    )

    class Meta(BaseModel.Meta):
        verbose_name = 'категория'
        verbose_name_plural = 'Категории'

    def __str__(self):
        return self.title[:TRUNCATE_AMOUNT]


class Location(BaseModel):
    """Модель информации о местоположении для поста блога."""

    name = models.CharField(
        max_length=TEXT_FIELD_MAX_LENGTH,
        verbose_name='Название места'
    )

    class Meta(BaseModel.Meta):
        verbose_name = 'местоположение'
        verbose_name_plural = 'Местоположения'

    def __str__(self):
        return self.name[:TRUNCATE_AMOUNT]


class Post(BaseModel):
    """Модель поста блога."""

    title = models.CharField(
        max_length=TEXT_FIELD_MAX_LENGTH,
        verbose_name='Заголовок'
    )
    text = models.TextField(
        verbose_name='Текст'
    )
    pub_date = models.DateTimeField(
        verbose_name='Дата и время публикации',
        help_text=(
            'Если установить дату и время в будущем — '
            'можно делать отложенные публикации.'
        )
    )
    author = models.ForeignKey(
        get_user_model(),
        verbose_name='Автор публикации',
        on_delete=models.CASCADE,
        related_name='posts'
    )
    location = models.ForeignKey(
        Location,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        verbose_name='Местоположение',
        related_name='posts'
    )
    category = models.ForeignKey(
        Category,
        on_delete=models.SET_NULL,
        null=True,
        verbose_name='Категория',
        related_name='posts'
    )
    image = models.ImageField(
        'Фото',
        blank=True,
        upload_to='post_images'
    )

    objects = models.Manager()
    published_posts = PublishedPostsManager()
    posts_fk_joined = PostForeignKeyManager()

    class Meta:
        verbose_name = 'публикация'
        verbose_name_plural = 'Публикации'
        ordering = ('-pub_date', 'title')

    def __str__(self):
        return self.title[:TRUNCATE_AMOUNT]

    def get_absolute_url(self):
        return reverse(
            'blog:post_detail',
            kwargs={'post_pk': self.pk}
        )


class Comment(models.Model):
    """Модель комментария для поста."""

    text = models.TextField(
        verbose_name='Текст комментария'
    )
    post = models.ForeignKey(
        Post,
        on_delete=models.CASCADE,
        related_name='comments'
    )
    created_at = models.DateTimeField(
        auto_now_add=True,
        verbose_name='Добавлено'
    )
    author = models.ForeignKey(
        get_user_model(),
        verbose_name='Автор комментария',
        on_delete=models.CASCADE,
        related_name='comments'
    )

    class Meta:
        ordering = ('created_at',)
        verbose_name = 'комментарий'
        verbose_name_plural = 'Комментарии'

    def __str__(self):
        return (f'От {self.author.username} {self.created_at:%F %T} '
                f'к {self.post}')

    def get_absolute_url(self):
        return reverse(
            'blog:post_detail',
            kwargs={'post_pk': self.post.pk}
        )
