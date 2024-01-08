from django.contrib import admin

from .models import Category, Comment, Location, Post

admin.site.empty_value_display = 'Не задано'


class PostInline(admin.StackedInline):
    """Добавить в раздел связанные посты."""

    model = Post
    extra = 0


class CommentInline(admin.StackedInline):
    """Добавить в раздел связанные комментарии."""

    model = Comment
    extra = 0


@admin.register(Post)
class PostAdmin(admin.ModelAdmin):
    """Настройка раздела Постов админ-панели."""

    list_display = (
        'title',
        'is_published',
        'category',
        'pub_date',
        'author',
        'location',
    )
    list_editable = (
        'is_published',
        'category'
    )
    inlines = (
        CommentInline,
    )
    search_fields = ('title',)
    list_filter = ('is_published',)


@admin.register(Category)
class CategoryAdmin(admin.ModelAdmin):
    """Настройка раздела Категории админ-панели."""

    list_display = (
        'title',
        'is_published',
        'slug',
        'description',
    )
    list_editable = (
        'is_published',
    )
    search_fields = ('title',)
    list_filter = ('is_published',)
    inlines = (
        PostInline,
    )


@admin.register(Location)
class LocationAdmin(admin.ModelAdmin):
    """Настройка раздела Местоположения админ-панели."""

    list_display = (
        'name',
        'is_published',
    )
    list_editable = (
        'is_published',
    )
    list_filter = ('is_published',)
    search_fields = ('title',)
    inlines = (
        PostInline,
    )


@admin.register(Comment)
class CommentAdmin(admin.ModelAdmin):
    """Управление комментариями к постам в админ-панели."""

    search_fields = ('post__title', 'author__username')
    list_filter = ('author',)
    list_display = ('created_at', 'post', 'author')
