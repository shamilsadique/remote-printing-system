from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from django.contrib.auth.models import User
from .models import PrintOrder, UserDetail

# Extend UserAdmin to include UserDetail fields
class UserDetailInline(admin.StackedInline):  # Inline model to show UserDetail in UserAdmin
    model = UserDetail
    can_delete = False
    verbose_name_plural = 'Additional User Details'

class CustomUserAdmin(UserAdmin):
    inlines = (UserDetailInline,)  # Show UserDetail inside UserAdmin

# Unregister default User and register with extended admin
admin.site.unregister(User)
admin.site.register(User, CustomUserAdmin)

@admin.register(UserDetail)
class UserDetailAdmin(admin.ModelAdmin):
    list_display = ('user', 'phone', 'address')  # Show additional fields in the list
    search_fields = ('user__username', 'phone', 'address')
    list_filter = ('user__is_staff', 'user__is_superuser')  # Filter by user roles
    raw_id_fields = ('user',)  # Optimize large databases

@admin.register(PrintOrder)
class PrintOrderAdmin(admin.ModelAdmin):
    list_display = ('id', 'user', 'file', 'print_type', 'paper_size', 'copies','notes', 'order_date','total_amount','payment_status','order_status')  # Include user
    search_fields = ('user__username', 'print_type', 'paper_size')
    list_filter = ('print_type', 'paper_size', 'order_date')
    ordering = ('-order_date',)  # Show recent orders first
    list_editable = ('order_status',)
