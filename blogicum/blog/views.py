from typing import Any

from django.contrib.auth import get_user_model
from django.contrib.auth.mixins import LoginRequiredMixin
from django.db.models import Count
from django.shortcuts import get_object_or_404, redirect
from django.urls import reverse_lazy
from django.views.generic import (
    CreateView, DeleteView, DetailView, ListView, UpdateView
)

from blogicum.constants import PAGINATE_VALUE
from blogicum.utils import paginate
from .forms import CommentForm, PostForm
from .models import Category, Comment, Post


class PostListView(ListView):
    """Вывести на главной странице опубликованные, последние по дате посты."""

    model = Post
    template_name = 'blog/index.html'
    paginate_by = PAGINATE_VALUE
    queryset = Post.published_posts_query.all().annotate(
        Count('comments')
    ).order_by('-pub_date')


class PostDetailView(DetailView):
    """Отобразить запрошенный по id, опубликованный, не отложенный пост."""

    model = Post
    pk_url_kwarg = 'post_pk'
    queryset = Post.post_fk_joined_query.all()

    def get_context_data(self, **kwargs) -> dict[str, Any]:
        context = super().get_context_data(**kwargs)
        if self.object.author != self.request.user:
            self.object = get_object_or_404(
                Post.published_posts_query.all(),
                pk=self.kwargs['post_pk']
            )
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


class PostBaseMixin(LoginRequiredMixin):
    """Базовый класс для работы с постами."""

    model = Post
    pk_url_kwarg = 'post_pk'

    def dispatch(self, request, *args, **kwargs):
        instance = get_object_or_404(
            Post.post_fk_joined_query.all(),
            pk=kwargs['post_pk']
        )
        if instance.author != request.user:
            return redirect(instance)
        return super().dispatch(request, *args, **kwargs)


class PostUpdateView(PostBaseMixin, UpdateView):
    """Редактирование обьекта поста его автором."""

    form_class = PostForm


class PostDeleteView(PostBaseMixin, DeleteView):
    """Удаление обьекта поста его автором."""

    template_name = 'blog/post_form.html'

    def get_success_url(self):
        return reverse_lazy(
            'blog:profile',
            kwargs={'username': self.request.user.username}
        )


class CategoryDetailView(DetailView):
    """Отобразить описание категории и список постов запрошенной категории."""

    model = Category
    slug_url_kwarg = 'category'
    queryset = Category.objects.filter(
        is_published=True
    )

    def get_context_data(self, **kwargs: Any) -> dict[str, Any]:
        context = super().get_context_data(**kwargs)
        context['page_obj'] = paginate(
            self.request,
            Post.published_posts_query.filter(
                category__exact=self.object
            ).annotate(
                Count('comments')
            ).order_by('-pub_date'),
            PAGINATE_VALUE
        )
        return context


class ProfileBaseMixin:
    """Базовый класс для работы с профилем пользователя."""

    model = get_user_model()
    slug_url_kwarg = 'username'
    slug_field = 'username'


class ProfileDetailView(ProfileBaseMixin, DetailView):
    """Информация о пользователе и показ его публикаций."""

    template_name = 'blog/profile.html'
    profile_posts = None

    def get_context_data(self, **kwargs: Any) -> dict[str, Any]:
        context = super().get_context_data(**kwargs)
        if self.request.user == self.object:
            self.profile_posts = Post.post_fk_joined_query.all()
        else:
            self.profile_posts = Post.published_posts_query.all()
        context['profile'] = self.object
        context['page_obj'] = paginate(
            self.request,
            self.profile_posts.filter(
                author__exact=self.object
            ).annotate(
                Count('comments')
            ).order_by('-pub_date'),
            PAGINATE_VALUE
        )
        return context


class ProfileUpdateView(LoginRequiredMixin, ProfileBaseMixin, UpdateView):
    """Редактирование обьекта пользователя."""

    template_name = 'blog/user_edit.html'
    fields = ['username', 'first_name', 'last_name', 'email']

    def get_queryset(self):
        """Пользователь может редактировать только свой профиль."""
        return self.model.objects.filter(
            username=self.request.user.username
        )

    def get_success_url(self):
        return reverse_lazy(
            'blog:profile',
            kwargs={'username': self.object.username}
        )


class CommentBaseMixin(LoginRequiredMixin):
    """Базовый класс для работы с комментариями."""

    model = Comment

    def get_queryset(self):
        """Пользователь может работать только со своими комментариями."""
        return self.model.objects.filter(
            post__pk=self.kwargs['post_pk'],
            author=self.request.user
        )


class CommentCreateView(LoginRequiredMixin, CreateView):
    """Создание обьекта комментария к посту."""

    post_obj = None
    model = Comment
    form_class = CommentForm

    def dispatch(self, request, *args, **kwargs):
        self.post_obj = get_object_or_404(
            Post.published_posts_query.all(),
            pk=kwargs['post_pk']
        )
        return super().dispatch(request, *args, **kwargs)

    def form_valid(self, form):
        form.instance.author = self.request.user
        form.instance.post = self.post_obj
        return super().form_valid(form)


class CommentUpdateView(CommentBaseMixin, UpdateView):
    """Редактирование обьекта комментария его автором."""

    form_class = CommentForm
    pk_url_kwarg = 'comment_pk'


class CommentDeleteView(CommentBaseMixin, DeleteView):
    """Удаление обьекта комментария его автором."""

    pk_url_kwarg = 'comment_pk'
    template_name = 'blog/comment_form.html'

    def get_success_url(self):
        return reverse_lazy(
            'blog:post_detail',
            kwargs={'post_pk': self.object.post.pk}
        )
