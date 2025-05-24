from django.contrib.auth.models import User
from django.utils.translation import gettext_lazy as _
from django.db import models


class Category(models.Model):
    name = models.CharField(
        max_length=100,
        verbose_name=_('Название категории'),
        help_text=_('Введите название категории книг')
    )
    objects = models.Manager()
    class Meta:
        verbose_name = _('Категория книг')
        verbose_name_plural = _('Категории книг')
        ordering = ['name']
    def __str__(self):
        return self.name


class Book(models.Model):
    title = models.CharField(
        max_length=100,
        verbose_name=_('Название книги'),
        help_text=_('Введите название книги')
    )
    author = models.CharField(
        max_length=100,
        verbose_name=_('Имя автора'),
        help_text=_('Введите имя автора')
    )
    category = models.ForeignKey(
        Category,
        on_delete=models.CASCADE,
        verbose_name=_('Категория'),
        help_text=_('Выберите категорию книги')
    )
    logo = models.CharField(
        max_length=1000,
        verbose_name=_('Изображение книги'),
        help_text=_('Введите ссылку на изображение книги')
    )
    objects = models.Manager()
    class Meta:
        verbose_name = _('Книга')
        verbose_name_plural = _('Книги')
        ordering = ['title']
    def __str__(self):
        return self.title


class Sentence(models.Model):
    text = models.CharField(
        max_length=255,
        verbose_name=_('Текст предложения'),
        help_text=_('Введите текст предложения на русском')
    )
    audio = models.CharField(
        max_length=255,
        verbose_name=_('Озвучка предложения'),
        help_text=_('Введи ссылку на аудио озвучку предложения')
    )
    translate = models.CharField(
        max_length=255,
        verbose_name=_('Перевод предложения'),
        help_text=_('Введите перевод предложения на лезгинский')
    )
    book = models.ForeignKey(
        Book,
        on_delete=models.CASCADE,
        verbose_name=_('Книга'),
        help_text=_('Выберите книгу предложения')
    )
    objects = models.Manager()
    class Meta:
        verbose_name = _('Предложение')
        verbose_name_plural = _('Предложения')
        ordering = ['id']
    def __str__(self):
        return f"{self.book.title} sentence added"


class Bookmark(models.Model):
    user = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        verbose_name=_('Пользователь'),
        help_text=_('Выберите пользователя')
    )
    book = models.ForeignKey(
        Book,
        on_delete=models.CASCADE,
        verbose_name=_('Книга'),
        help_text=_('Выберите книгу предложения')
    )
    sentence = models.ForeignKey(
        Sentence,
        on_delete=models.CASCADE,
        verbose_name=_('Предложение'),
        help_text=_('Выберите предложение')
    )
    objects = models.Manager()
    class Meta:
        unique_together = ('user', 'sentence', 'book')
        verbose_name = _('Закладка')
        verbose_name_plural = _('Закладки')
        ordering = ['-id']
    def __str__(self):
        return f"{self.user.username} - {self.book.title} - {self.sentence.id}"


class CompletedBook(models.Model):
    user = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        verbose_name=_('Пользователь'),
        help_text=_('Выберите пользователя')
    )
    book = models.ForeignKey(
        Book,
        on_delete=models.CASCADE,
        verbose_name=_('Книга'),
        help_text=_('Выберите книгу')
    )
    objects = models.Manager()
    class Meta:
        unique_together = ('user', 'book')
        verbose_name = _('Прочитанная книга')
        verbose_name_plural = _('Прочитанные книги')
        ordering = ['-id']
    def __str__(self):
        return f"{self.user.username} - {self.book.title}"
