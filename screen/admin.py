from django.contrib import admin
from .models import Post, Comment


@admin.register(Post)
class PostAdmin(admin.ModelAdmin):
    list_display = ('title', 'author', 'created_at')
    list_select_related = ('author',)
    search_fields = ('title',)


admin.site.register(Comment)