from django.db import models

class CompanyToday(models.Model):
    ts_code = models.CharField(max_length=100, blank=True, default='')
    trade_date = models.DateTimeField(null=True)
    open = models.FloatField()
    high = models.FloatField()
    low = models.FloatField()
    close = models.FloatField()
    pre_close = models.FloatField()
    change = models.FloatField()
    pct_chg = models.FloatField()
    vol = models.FloatField()
    amount = models.FloatField()

    class Meta:
        # ordering = ('ts_code',)
        indexes = [
            models.Index(
                fields=['ts_code'],
                name='ts_code_company_today_idx',
            )
        ]


# code,name,change,open,preclose,close,high,low,volume,amount
class IndexToday(models.Model):
    ts_code = models.CharField(max_length=100, blank=True, default='')
    trade_date = models.DateTimeField(null=True)
    close = models.FloatField()
    open = models.FloatField()
    high = models.FloatField()
    low = models.FloatField()
    pre_close = models.FloatField()
    change = models.FloatField()
    pct_chg = models.FloatField()
    vol = models.FloatField()
    amount = models.FloatField()

    class Meta:
        # ordering = ('ts_code',)
        indexes = [
            models.Index(
                fields=['ts_code'],
                name='ts_code_index_today_idx',
            )
        ]

