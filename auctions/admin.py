from django.contrib import admin
from .models import Category, Listing, Comment, User

# Register your models here.

class UserAdmin(admin.ModelAdmin):
    filter_horizontal = ("watchlist",)

admin.site.register(User, UserAdmin)
admin.site.register(Category)
admin.site.register(Listing)
admin.site.register(Comment)