from django.db import models

class Company(models.Model):
    symbol = models.CharField(max_length=100, blank=True, default='')
    ts_code = models.CharField(max_length=100, blank=True, default='')
    name = models.CharField(max_length=100, blank=True, default='')
    area = models.CharField(max_length=100, blank=True, default='')
    industry = models.CharField(max_length=100, blank=True, default='')
    fullname = models.CharField(max_length=100, blank=True, default='')
    enname = models.CharField(max_length=100, blank=True, default='')
    market = models.CharField(max_length=100, blank=True, default='')
    exchange = models.CharField(max_length=100, blank=True, default='')
    curr_type = models.CharField(max_length=100, blank=True, default='')
    list_status = models.CharField(max_length=100, blank=True, default='')
    list_date = models.DateTimeField(null=True)
    delist_date = models.DateTimeField(null=True)
    is_hs = models.CharField(max_length=10, blank=True, default='')

    class Meta:
        # ordering = ('symbol',)
        indexes = [
            models.Index(
                fields=['symbol'],
                name='symbol_idx',
            ),
            models.Index(
                fields=['ts_code'],
                name='ts_code_company_idx',
            )
        ]


class Index(models.Model):
    ts_code = models.CharField(max_length=100, blank=True, default='')
    name = models.CharField(max_length=100, blank=True, default='')
    fullname = models.CharField(max_length=100, blank=True, default='')
    market = models.CharField(max_length=100, blank=True, default='')
    publisher = models.CharField(max_length=100, blank=True, default='')
    index_type = models.CharField(max_length=100, blank=True, default='')
    category = models.CharField(max_length=100, blank=True, default='')
    base_date = models.DateTimeField(null=True)
    base_point = models.FloatField()
    list_date = models.DateTimeField(null=True)
    weight_rule = models.CharField(max_length=100, blank=True, default='')
    desc = models.TextField(blank=True, default='')
    exp_date = models.DateTimeField(null=True)

    class Meta:
        # ordering = ('ts_code',)
        indexes = [
            models.Index(
                fields=['ts_code'],
                name='ts_code_index_idx',
            )
        ]
