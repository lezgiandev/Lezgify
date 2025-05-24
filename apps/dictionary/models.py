from django.contrib.auth.models import User
from django.utils.translation import gettext_lazy as _
from django.db import models


class Category(models.Model):
    name = models.CharField(
        max_length=100,
        verbose_name=_('Название категории'),
        help_text=_('Введите название категории слов')
    )
    objects = models.Manager()
    class Meta:
        verbose_name = _('Категория слов')
        verbose_name_plural = _('Категории слов')
        ordering = ['name']
    def __str__(self):
        return self.name


class PartOfSpeech(models.Model):
    name = models.CharField(
        max_length=50,
        verbose_name=_('Название части речи'),
        help_text=_('Введите название части речи слова')
    )
    objects = models.Manager()
    class Meta:
        verbose_name = _('Часть речи')
        verbose_name_plural = _('Части речи')
        ordering = ['name']
    def __str__(self):
        return self.name


class Word(models.Model):
    text = models.CharField(
        max_length=50,
        verbose_name=_('Текст слова'),
        help_text=_('Введите текст слова')
    )
    part_of_speech = models.ForeignKey(
        PartOfSpeech,
        on_delete=models.CASCADE,
        verbose_name=_('Часть речи'),
        help_text=_('Выберите часть речи слова')
    )
    category = models.ForeignKey(
        Category,
        on_delete=models.CASCADE,
        verbose_name=_('Категория'),
        help_text=_('Выберите категорию слова')
    )
    objects = models.Manager()
    class Meta:
        verbose_name = _('Слово')
        verbose_name_plural = _('Слова')
        ordering = ['text']
    def __str__(self):
        return self.text


class Origin(models.Model):
    language = models.CharField(
        max_length=50,
        verbose_name=_('Язык происхождения'),
        help_text=_('Введите название языка происхождения')
    )
    objects = models.Manager()
    class Meta:
        verbose_name = _('Язык происхождения')
        verbose_name_plural = _('Языки происхождения')
        ordering = ['language']
    def __str__(self):
        return self.language


class Translation(models.Model):
    text = models.CharField(
        max_length=50,
        verbose_name=_('Текст перевода'),
        help_text=_('Введите текст перевода слова')
    )
    audio = models.CharField(
        max_length=1000,
        verbose_name=_('Аудио перевода'),
        help_text=_('Введите ссылку на аудио перевода слова')
    )
    word = models.ForeignKey(
        Word,
        on_delete=models.CASCADE,
        verbose_name=_('Слово'),
        help_text=_('Выберите слово для перевода')
    )
    origin = models.ForeignKey(
        Origin,
        on_delete=models.CASCADE,
        verbose_name=_('Язык происхождения'),
        help_text=_('Выберите язык происхождения перевода')
    )
    objects = models.Manager()
    def __str__(self):
        return f"{self.word.text} - {self.text}"
    class Meta:
        verbose_name = _('Перевод слова')
        verbose_name_plural = _('Переводы слова')
        ordering = ['id']


class FavoriteWord(models.Model):
    user = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        verbose_name=_('Пользователь'),
        help_text=_('Выберите пользователя')
    )
    translation = models.ForeignKey(
        Translation,
        on_delete=models.CASCADE,
        verbose_name=_('Слово'),
        help_text=_('Выберите слово, которое хотите добавить в избранное')
    )
    objects = models.Manager()
    class Meta:
        unique_together = ('user', 'translation')
        verbose_name = _('Избранное слово')
        verbose_name_plural = _('Избранные слова')
        ordering = ['-id']
    def __str__(self):
        return f"{self.user.username} - {self.translation.text}"


class LearnedWord(models.Model):
    user = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        verbose_name=_('Пользователь'),
        help_text=_('Выберите пользователя')
    )
    translation = models.ForeignKey(
        Translation,
        on_delete=models.CASCADE,
        verbose_name=_('Слово'),
        help_text=_('Выберите слово, которое хотите добавить в выученное')
    )
    objects = models.Manager()
    class Meta:
        unique_together = ('user', 'translation')
        verbose_name = _('Выученное слово')
        verbose_name_plural = _('Выученные слова')
        ordering = ['-id']
    def __str__(self):
        return f"{self.user.username} - {self.translation.text}"
