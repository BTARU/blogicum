from django.urls import path

from . import views

app_name = 'blog'

urlpatterns = [
    path(
        'posts/<int:post_pk>/',
        views.PostDetailView.as_view(),
        name='post_detail'
    ),
    path(
        'posts/create/',
        views.PostCreateView.as_view(),
        name="create_post"
    ),
    path(
        'posts/<int:post_pk>/edit/',
        views.PostUpdateView.as_view(),
        name='edit_post'
    ),
    path(
        'posts/<int:post_pk>/delete/',
        views.PostDeleteView.as_view(),
        name='delete_post'
    ),

    path(
        'posts/<int:post_pk>/comment/',
        views.CommentCreateView.as_view(),
        name='add_comment'
    ),
    path(
        'posts/<int:post_pk>/edit_comment/<int:comment_pk>',
        views.CommentUpdateView.as_view(),
        name='edit_comment'
    ),
    path(
        'posts/<int:post_pk>/delete_comment/<int:comment_pk>',
        views.CommentDeleteView.as_view(),
        name='delete_comment'
    ),

    path(
        'profile/<str:username>/',
        views.ProfileDetailView.as_view(),
        name='profile'
    ),
    path(
        'profile/<str:username>/edit/',
        views.ProfileUpdateView.as_view(),
        name='edit_profile'
    ),

    path(
        'category/<slug:category>/',
        views.CategoryDetailView.as_view(),
        name='category_posts'
    ),
    path(
        '',
        views.PostListView.as_view(),
        name='index'
    ),
]
