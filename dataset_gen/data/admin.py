from django.contrib import admin

from .models import *

# @admin.register(Valid)
# class ValidAdmin(admin.ModelAdmin):
#     pass

@admin.register(Skill)
class SkillAdmin(admin.ModelAdmin):
    pass

@admin.register(Ner)
class NerAdmin(admin.ModelAdmin):
    list_display = ['name', 'description', 'abbr', 'color', 'order']
    ordering = ['order', 'name']

def check_during_false(modeladmin, request, queryset):
    queryset.update(during=False)

def check_processed_false(modeladmin, request, queryset):
    queryset.update(processed=False)

@admin.register(Phrase)
class PhraseAdmin(admin.ModelAdmin):
    list_display = ['id', 'text', 'processed', 'valid', 'during', 'during_start']
    list_display_links = ['text']
    list_filter = ['valid', 'during', 'processed']
    search_fields = ['text']
    ordering = ['id']
    actions = [check_during_false, check_processed_false]

    check_during_false.short_description = u'Снять пометку "Обрабатывается"'
    check_processed_false.short_description = u'Снять пометку "Размечено"'
