import uuid

from django.core.validators import MaxValueValidator, MinValueValidator
from django.db import models
from django.utils.translation import gettext_lazy as _


class UUIDMixin(models.Model):
    id = models.UUIDField(primary_key=True, editable=False, default=uuid.uuid4)

    class Meta:
        abstract = True


class TimeStampedMixin(models.Model):
    created = models.DateTimeField(auto_now_add=True)
    modified = models.DateTimeField(auto_now=True)

    class Meta:
        abstract = True


class Genre(UUIDMixin, TimeStampedMixin):
    name = models.CharField(_('name'), max_length=255)
    description = models.TextField(_('description'), blank=True)

    class Meta:
        db_table = 'genre'
        verbose_name = _('Genre')
        verbose_name_plural = _('Genres')

    def __str__(self):
        return self.name


class FilmWork(UUIDMixin, TimeStampedMixin):
    class Type(models.TextChoices):
        MOVIE = 'movie'

        TV_SHOW = 'tv_show'

    title = models.CharField(_('title'), max_length=255)
    description = models.TextField(_('description'), blank=True)
    creation_date = models.DateField(_('creation_date'), blank=True)
    rating = models.FloatField(blank=True, validators=[MinValueValidator(0), MaxValueValidator(100)])
    type = models.CharField(_('type'), choices=Type.choices, max_length=10)
    genres = models.ManyToManyField('Genre', through='GenreFilmWork')
    persons = models.ManyToManyField('Person', through='PersonFilmWork')

    class Meta:
        db_table = 'film_work'
        verbose_name = _('Movie')
        verbose_name_plural = _('Movies')

    def __str__(self):
        return self.title


class GenreFilmWork(UUIDMixin):
    film_work = models.ForeignKey('FilmWork', on_delete=models.CASCADE)
    genre = models.ForeignKey('Genre', on_delete=models.CASCADE)
    created = models.DateTimeField(auto_now_add=True)

    class Meta:
        db_table = 'genre_film_work'
        verbose_name = _('Movie genre')
        verbose_name_plural = _('Movie genres')
        constraints = [models.UniqueConstraint(fields=['film_work', 'genre'], name='unique_film_genre')]


class Person(UUIDMixin, TimeStampedMixin):
    full_name = models.CharField(max_length=100)

    class Meta:
        db_table = 'person'
        verbose_name = _('Person')
        verbose_name_plural = _('Persons')

    def __str__(self):
        return self.full_name


class PersonFilmWork(UUIDMixin):
    class Role(models.TextChoices):
        ACTOR = 'actor'
        DIRECTOR = 'director'
        WRITER = 'writer'

    film_work = models.ForeignKey('FilmWork', on_delete=models.CASCADE)
    person = models.ForeignKey('Person', on_delete=models.CASCADE)
    role = models.TextField(_('role'), null=True, choices=Role.choices)
    created = models.DateTimeField(auto_now_add=True)

    class Meta:
        db_table = 'person_film_work'
        verbose_name = _("Movie's person")
        verbose_name_plural = _("Movie's persons")
        constraints = [models.UniqueConstraint(fields=['film_work', 'person', 'role'], name='unique_person')]
