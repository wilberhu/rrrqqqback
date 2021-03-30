from django.db import models

class Strategy(models.Model):
    owner = models.ForeignKey('auth.User', related_name='strategy', on_delete=models.CASCADE)

    created = models.DateTimeField(auto_now_add=True)
    modified = models.DateTimeField(auto_now=True)
    title = models.CharField(max_length=100, blank=True, default='')
    code = models.TextField()

    class Meta:
        ordering = ('created',)

    def save(self, *args, **kwargs):
        super(Strategy, self).save(*args, **kwargs)


class FilterOption(models.Model):
    owner = models.ForeignKey('auth.User', related_name='filter_option', on_delete=models.CASCADE)

    key = models.CharField(max_length=100, blank=False)
    label = models.CharField(max_length=100, blank=False)
    table = models.CharField(max_length=100, blank=False)
    method = models.CharField(max_length=100, blank=True, default='')

    class Meta:
        ordering = ('id',)

    def save(self, *args, **kwargs):
        super(FilterOption, self).save(*args, **kwargs)


class StockPicking(models.Model):
    name = models.CharField(max_length=100, blank=False)
    description = models.TextField(blank=True)
    owner = models.ForeignKey('auth.User', related_name='stock_picking', on_delete=models.CASCADE)
    start_time = models.DateField(null=True)
    end_time = models.DateField(null=True)
    created = models.DateTimeField(auto_now_add=True)
    modified = models.DateTimeField(auto_now=True)
    method = models.CharField(max_length=100, blank=False)
    filter = models.JSONField()

    class Meta:
        ordering = ('created',)

    def save(self, *args, **kwargs):
        super(StockPicking, self).save(*args, **kwargs)