from typing import Any

from django.contrib.auth import get_user_model
from django.contrib.auth.mixins import LoginRequiredMixin, UserPassesTestMixin
from django.db.models import Count, Q
from django.shortcuts import get_object_or_404, redirect
from django.urls import reverse_lazy
from django.utils import timezone
from django.views.generic import (
    CreateView, DeleteView, DetailView, ListView, UpdateView
)

from core.constants import PAGINATE_VALUE
from .forms import CommentForm, PostForm
from .models import Category, Comment, Post


class PostListMixin(ListView):
    """Базовый класс для вывода множества постов."""

    paginate_by = PAGINATE_VALUE


class PostListView(PostListMixin):
    """Вывести на главной странице опубликованные, последние по дате посты."""

    template_name = 'blog/index.html'
    queryset = Post.published_posts.all().annotate(
        Count('comments')
    ).order_by('-pub_date')


class PostDetailView(DetailView):
    """Вывести обьект поста с блоком комментариев."""

    pk_url_kwarg = 'post_pk'

    def get_object(self, queryset=None):
        return get_object_or_404(
            Post.posts_fk_joined.filter(
                (~Q(author=self.request.user.pk)
                 & Q(is_published=True)
                 & Q(category__is_published=True)
                 & Q(pub_date__lt=timezone.now())
                 )
                | Q(author=self.request.user.pk)
            ),
            pk=self.kwargs['post_pk']
        )

    def get_context_data(self, **kwargs) -> dict[str, Any]:
        context = super().get_context_data(**kwargs)
        if self.request.user.is_authenticated:
            context['form'] = CommentForm()
        context['comments'] = (
            self.object.comments.select_related('author')
        )
        return context


class PostCreateView(LoginRequiredMixin, CreateView):
    """Добавление обьекта поста."""

    model = Post
    form_class = PostForm

    def form_valid(self, form):
        form.instance.author = self.request.user
        return super().form_valid(form)

    def get_success_url(self):
        return reverse_lazy(
            'blog:profile',
            kwargs={'username': self.object.author.username}
        )


class PostEditMixin(LoginRequiredMixin, UserPassesTestMixin):
    """Базовый класс для работы с постами."""

    model = Post
    pk_url_kwarg = 'post_pk'

    def test_func(self):
        """Если не выполняется. Редактирование только для автора поста."""
        return self.get_object().author == self.request.user

    def handle_no_permission(self):
        """If not test_func(). Редирект на get_absolute_url модели."""
        return redirect(self.get_object())


class PostUpdateView(PostEditMixin, UpdateView):
    """Редактирование обьекта поста его автором."""

    form_class = PostForm


class PostDeleteView(PostEditMixin, DeleteView):
    """Удаление обьекта поста его автором."""

    template_name = 'blog/post_form.html'

    def get_success_url(self):
        return reverse_lazy(
            'blog:profile',
            kwargs={'username': self.request.user.username}
        )


class CategoryListView(PostListMixin):
    """Отобразить описание категории и список постов запрошенной категории."""

    template_name = 'blog/category_detail.html'
    category_obj = None

    def get_queryset(self):
        self.category_obj = get_object_or_404(
            Category.objects.filter(
                is_published=True
            ),
            slug=self.kwargs['category']
        )
        return Post.published_posts.filter(
            category__exact=self.category_obj
        ).annotate(
            Count('comments')
        ).order_by('-pub_date')

    def get_context_data(self, **kwargs: Any) -> dict[str, Any]:
        context = super().get_context_data(**kwargs)
        context['category'] = self.category_obj
        return context


class ProfileListView(PostListMixin):
    """Информация о пользователе и показ его публикаций."""

    template_name = 'blog/profile.html'
    profile = None

    def get_queryset(self):
        self.profile = get_object_or_404(
            get_user_model(),
            username=self.kwargs['username']
        )
        return Post.posts_fk_joined.filter(
            (~Q(author=self.request.user.pk)
             & Q(is_published=True)
             & Q(category__is_published=True)
             & Q(pub_date__lt=timezone.now())
             & Q(author=self.profile)
             )
            | Q(author=self.profile)
        ).annotate(
            Count('comments')
        ).order_by('-pub_date')

    def get_context_data(self, **kwargs: Any) -> dict[str, Any]:
        context = super().get_context_data(**kwargs)
        context['profile'] = self.profile
        return context


class ProfileUpdateView(LoginRequiredMixin, UpdateView):
    """Редактирование обьекта пользователя."""

    slug_url_kwarg = 'username'
    slug_field = 'username'
    template_name = 'blog/user_edit.html'
    fields = ['username', 'first_name', 'last_name', 'email']

    def get_queryset(self):
        """Пользователь может редактировать только свой профиль."""
        return get_user_model().objects.filter(
            username=self.request.user.username
        )

    def get_success_url(self):
        return reverse_lazy(
            'blog:profile',
            kwargs={'username': self.object.username}
        )


class CommentEditMixin(LoginRequiredMixin):
    """Базовый класс для работы с комментариями."""

    pk_url_kwarg = 'comment_pk'

    def get_queryset(self):
        """Пользователь может работать только со своими комментариями."""
        return Comment.objects.filter(
            post__pk=self.kwargs['post_pk'],
            author=self.request.user
        )


class CommentCreateView(LoginRequiredMixin, CreateView):
    """Создание обьекта комментария к посту."""

    form_class = CommentForm

    def get_object(self, queryset=None):
        return get_object_or_404(
            Post.published_posts.all(),
            pk=self.kwargs['post_pk']
        )

    def form_valid(self, form):
        form.instance.author = self.request.user
        form.instance.post = self.get_object()
        return super().form_valid(form)


class CommentUpdateView(CommentEditMixin, UpdateView):
    """Редактирование обьекта комментария его автором."""

    form_class = CommentForm


class CommentDeleteView(CommentEditMixin, DeleteView):
    """Удаление обьекта комментария его автором."""

    template_name = 'blog/comment_form.html'

    def get_success_url(self):
        return reverse_lazy(
            'blog:post_detail',
            kwargs={'post_pk': self.object.post.pk}
        )
