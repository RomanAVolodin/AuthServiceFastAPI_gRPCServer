from django.contrib import admin

from movies.models import FilmWork, Genre, GenreFilmWork, Person, PersonFilmWork


class GenreFilmWorkInline(admin.TabularInline):
    model = GenreFilmWork
    autocomplete_fields = ('genre',)


class PersonFilmWorkInline(admin.TabularInline):
    model = PersonFilmWork
    autocomplete_fields = ('person',)


@admin.register(Person)
class PersonAdmin(admin.ModelAdmin):
    search_fields = ('full_name',)


@admin.register(Genre)
class GenreAdmin(admin.ModelAdmin):
    list_display = (
        'name',
        'description',
    )
    list_filter = ('name',)
    search_fields = ('name',)


@admin.register(FilmWork)
class FilmWorkAdmin(admin.ModelAdmin):
    class Media:
        css = {'all': ('css/custom_admin.css',)}  # Include extra css

    inlines = (GenreFilmWorkInline, PersonFilmWorkInline)

    list_display = (
        'title',
        'type',
        'creation_date',
        'rating',
    )

    list_filter = ('type',)

    search_fields = (
        'title',
        'description',
    )
