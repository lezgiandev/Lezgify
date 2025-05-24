from django.contrib.auth.models import User
from django.utils.translation import gettext_lazy as _
from django.db import models


class Category(models.Model):
    name = models.CharField(
        max_length=100,
        verbose_name=_('Название категории'),
        help_text=_('Введите название категории фразы')
    )
    objects = models.Manager()
    class Meta:
        verbose_name = _('Категория фразы')
        verbose_name_plural = _('Категории фраз')
        ordering = ['name']
    def __str__(self):
        return self.name


class Phrase(models.Model):
    text = models.CharField(
        max_length=50,
        verbose_name=_('Текст фразы'),
        help_text=_('Введите текст фразы')
    )
    category = models.ForeignKey(
        Category,
        on_delete=models.CASCADE,
        verbose_name=_('Категория'),
        help_text=_('Выберите категорию фразы')
    )
    objects = models.Manager()
    class Meta:
        verbose_name = _('Фраза')
        verbose_name_plural = _('Фразы')
        ordering = ['text']
    def __str__(self):
        return self.text


class Translation(models.Model):
    text = models.CharField(
        max_length=50,
        verbose_name=_('Текст перевода'),
        help_text=_('Введите текст перевода фразы')
    )
    audio = models.CharField(
        max_length=1000,
        verbose_name=_('Аудио перевода'),
        help_text=_('Введите ссылку на аудио перевода фразы')
    )
    phrase = models.ForeignKey(
        Phrase,
        on_delete=models.CASCADE,
        verbose_name=_('Фраза'),
        help_text=_('Выберите фразу для перевода')
    )
    objects = models.Manager()
    def __str__(self):
        return f"{self.phrase.text} - {self.text}"
    class Meta:
        verbose_name = _('Перевод фразы')
        verbose_name_plural = _('Переводы фраз')
        ordering = ['id']


class FavoritePhrase(models.Model):
    user = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        verbose_name=_('Пользователь'),
        help_text=_('Выберите пользователя')
    )
    translation = models.ForeignKey(
        Translation,
        on_delete=models.CASCADE,
        verbose_name=_('Фраза'),
        help_text=_('Выберите фразу, которую хотите добавить в избранное')
    )
    objects = models.Manager()
    class Meta:
        unique_together = ('user', 'translation')
        verbose_name = _('Избранная фраза')
        verbose_name_plural = _('Избранные фразы')
        ordering = ['-id']
    def __str__(self):
        return f"{self.user.username} - {self.translation.text}"


class LearnedPhrase(models.Model):
    user = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        verbose_name=_('Пользователь'),
        help_text=_('Выберите пользователя')
    )
    translation = models.ForeignKey(
        Translation,
        on_delete=models.CASCADE,
        verbose_name=_('Фраза'),
        help_text=_('Выберите фразу, которую хотите добавить в выученное')
    )
    objects = models.Manager()
    class Meta:
        unique_together = ('user', 'translation')
        verbose_name = _('Выученная фраза')
        verbose_name_plural = _('Выученные фразы')
        ordering = ['-id']
    def __str__(self):
        return f"{self.user.username} - {self.translation.text}"
