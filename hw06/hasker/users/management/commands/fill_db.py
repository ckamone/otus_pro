from django.core.management.base import BaseCommand
from users.models import CustomUser
from django.contrib.auth.models import User

class Command(BaseCommand):
    help = 'Fill DB'

    def handle(self, *args, **options):
        print('prestart')
        CustomUser.objects.all().delete()
        User.objects.all().delete()

        print('start')
         # 2 CREATE
        print('create new Type')
        u1 = User.objects.create(username='tester', password='tst')
        print(u1)
        u1_av = CustomUser.objects.create(user=u1, avatar='kk1.jpg')
        print(u1_av.avatar)

        #filter
        users_filt = CustomUser.objects.filter(user=u1.pk)
        print(users_filt)