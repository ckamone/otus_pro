from django.db import models
from django.contrib.auth.models import AbstractUser, User
from django.utils import timezone

# ''' Пользователь – элеĸтронная почта, ниĸнейм, пароль, аватарĸа, дата
# регистрации.
# Вопрос – заголовоĸ, содержание, автор, дата создания, тэги.
# Ответ – содержание, автор, дата написания, флаг правильного ответа.
# Тэг — слово тэга'''

# # Create your models here.
# class CustomUser(AbstractUser):
#     email = models.EmailField(_("email address"), unique=True)





    

class Question(models.Model):
    title = models.CharField('title', max_length=64)
    text = models.TextField(verbose_name='question', blank=False)
    author = models.ForeignKey(User, on_delete=models.PROTECT)
    created_at = models.DateTimeField(default=timezone.now)
    # tags = models.ManyToManyField(Tag, default=None, null=True)
    # tags = models.CharField(max_length=64)
    votes = models.IntegerField(default=0) # to sort by vote
    voters_up = models.TextField(default='') # to check if user voted already up
    voters_down = models.TextField(default='') # to check if user voted already down
    # reply = models.ForeignKey(Reply, default=None, on_delete=models.PROTECT, null=True)

    def __str__(self):
        # tags = [i.tag_name for i in self.tags.all()]
        return f"{self.title}"
    

class Tag(models.Model):
    tag_name = models.CharField('title', max_length=64)
    question = models.ManyToManyField(Question, default=None, null=True)

    def __str__(self):
        return f"{self.tag_name}"


class Reply(models.Model):
    text = models.TextField(verbose_name='reply', blank=False)
    created_at = models.DateTimeField(default=timezone.now)
    author = models.ForeignKey(User, on_delete=models.PROTECT)
    is_correct = models.BooleanField(default=False)
    votes = models.IntegerField(default=0)
    question = models.ForeignKey(Question, default=None, on_delete=models.PROTECT, null=True)
    voters_up = models.TextField(default='')
    voters_down = models.TextField(default='')
    

    def __str__(self):
        return f"{self.author} ({self.text})"