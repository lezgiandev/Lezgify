from django.contrib.auth.models import User
from django.db import models
from django.utils.translation import gettext_lazy as _


class Category(models.Model):
    name = models.CharField(
        max_length=100,
        verbose_name=_('Название категории'),
        help_text=_('Введите название категории источника')
    )
    objects = models.Manager()
    class Meta:
        verbose_name = _('Категория источника')
        verbose_name_plural = _('Категории источников')
        ordering = ['name']
    def __str__(self):
        return self.name


class Source(models.Model):
    text = models.CharField(
        max_length=255,
        verbose_name=_('Название источника'),
        help_text=_('Введите название источника')
    )
    link = models.CharField(
        max_length=1000,
        verbose_name=_('Текст ссылки на источник'),
        help_text=_('Введите ссылку на источник')
    )
    category = models.ForeignKey(
        Category,
        on_delete=models.CASCADE,
        verbose_name=_('Категория'),
        help_text=_('Выберите категорию источника')
    )
    objects = models.Manager()
    class Meta:
        verbose_name = _('Источник')
        verbose_name_plural = _('Источники')
        ordering = ['text']
    def __str__(self):
        return self.text


class MarkedSource(models.Model):
    user = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        verbose_name=_('Пользователь'),
        help_text=_('Выберите пользователя')
    )
    source = models.ForeignKey(
        Source,
        on_delete=models.CASCADE,
        verbose_name=_('Источник'),
        help_text=_('Выберите источник')
    )
    objects = models.Manager()
    class Meta:
        unique_together = ('user', 'source')
        verbose_name = _('Отмеченный источник')
        verbose_name_plural = _('Отмеченные источники')
        ordering = ['-id']
    def __str__(self):
        return f"{self.user.username} - {self.source.text}"
