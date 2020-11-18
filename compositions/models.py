from django.db import models

class Composition(models.Model):
    owner = models.ForeignKey('auth.User', related_name='composition', on_delete=models.CASCADE)
    highlighted = models.TextField()

    created = models.DateTimeField(auto_now_add=True)
    adjustments = models.TextField()
    stock = models.FloatField()
    benchmark = models.CharField(max_length=100, blank=True, default='')
    result = models.TextField()

    class Meta:
        ordering = ('created',)

    def save(self, *args, **kwargs):
        super(Composition, self).save(*args, **kwargs)
