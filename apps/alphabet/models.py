from django.contrib.auth.models import User
from django.utils.translation import gettext_lazy as _
from django.db import models


class Letter(models.Model):
    letter = models.CharField(
        max_length=10,
        verbose_name=_('Буква'),
        help_text=_('Введите букву алфавита')
    )
    audio = models.CharField(
        max_length=1000,
        verbose_name=_('Аудио буквы'),
        help_text=_('Введите ссылку на аудио буквы')
    )
    objects = models.Manager()
    class Meta:
        verbose_name = _('Буква')
        verbose_name_plural = _('Буквы')
        ordering = ['id']
    def __str__(self):
        return self.letter


class LearnedLetter(models.Model):
    user = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        verbose_name=_('Пользователь'),
        help_text = _('Выберите пользователя')
    )
    letter = models.ForeignKey(
        Letter,
        on_delete=models.CASCADE,
        verbose_name=_('Буква'),
        help_text=_('Выберите букву')
    )
    objects = models.Manager()
    class Meta:
        verbose_name = _('Прогресс изучения алфавита')
        unique_together = ('user', 'letter')
        verbose_name_plural = _('Прогресс изучения алфавита')
        ordering = ['-id']
    def __str__(self):
        return f"{self.user.username} изучил {self.letter}"
