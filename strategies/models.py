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


class StockFilter(models.Model):
    owner = models.ForeignKey('auth.User', related_name='stock_filter', on_delete=models.CASCADE)

    created = models.DateTimeField(auto_now_add=True)
    modified = models.DateTimeField(auto_now=True)
    title = models.CharField(max_length=100, blank=True, default='')
    type = models.CharField(max_length=100, blank=True, default='')
    code = models.TextField()
    name_cn = models.CharField(max_length=100, blank=True, default='')
    description = models.CharField(max_length=500, blank=True, default='')
    submit_time = models.DateTimeField(null=True, blank=True)
    result_id = models.IntegerField(null=True, blank=True)

    class Meta:
        ordering = ('created',)

    def save(self, *args, **kwargs):
        super(StockFilter, self).save(*args, **kwargs)


class StockFilterResult(models.Model):
    modified = models.DateTimeField(auto_now=True)
    path = models.CharField(max_length=100, blank=True, default='')
    stock_filter = models.ForeignKey(StockFilter, on_delete=models.CASCADE)

    class Meta:
        ordering = ('modified',)

    def save(self, *args, **kwargs):
        super(StockFilterResult, self).save(*args, **kwargs)