from django.db import models


class Composition(models.Model):
    name = models.CharField(max_length=100, blank=False)
    description = models.TextField(blank=True)
    owner = models.ForeignKey('auth.User', related_name='composition', on_delete=models.CASCADE)
    created = models.DateTimeField(auto_now_add=True)
    modified = models.DateTimeField(auto_now=True)
    allfund = models.FloatField()
    comission = models.FloatField()
    activities = models.JSONField()

    class Meta:
        ordering = ('created',)

    def save(self, *args, **kwargs):
        super(Composition, self).save(*args, **kwargs)
