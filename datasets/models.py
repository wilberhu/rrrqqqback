from django.db import models

import datetime
import random
import os

def random_path(user):
    nowTime = datetime.datetime.now().strftime("%Y%m%d%H%M%S")
    randomNum = random.randint(0, 99)
    randomNum = "%02d"%randomNum
    return os.path.join("strategy", user.username, "datasets", str(nowTime) + randomNum)

def my_awesome_upload_function(instance, filename):
    return os.path.join(random_path(instance.owner), filename)

class Dataset(models.Model):

    name = models.CharField(max_length=100, blank=False)
    file = models.FileField(upload_to=my_awesome_upload_function)
    # file = models.FileField(upload_to='upload/%Y/%m/%d')
    path = models.CharField(max_length=100, blank=True, default='')
    owner = models.ForeignKey('auth.User', related_name='datasets', on_delete=models.CASCADE)
    created = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ('created',)

    def save(self, *args, **kwargs):
        super(Dataset, self).save(*args, **kwargs)

