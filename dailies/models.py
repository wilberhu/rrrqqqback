from django.db import models

class CompanyDaily(models.Model):
    ts_code = models.CharField(max_length=100, blank=True, default='')
    trade_date = models.DateTimeField(null=True)
    close = models.FloatField()
    turnover_rate = models.FloatField()
    turnover_rate_f = models.FloatField()
    volume_ratio = models.FloatField()
    pe = models.FloatField()
    pe_ttm = models.FloatField()
    pb = models.FloatField()
    ps = models.FloatField()
    ps_ttm = models.FloatField()
    total_share = models.FloatField()
    float_share = models.FloatField()
    free_share = models.FloatField()
    total_mv = models.FloatField()
    circ_mv = models.FloatField()

    class Meta:
        # ordering = ('ts_code',)
        indexes = [
            models.Index(
                fields=['ts_code'],
                name='ts_code_company_daily_idx',
            )
        ]


# code,name,change,open,preclose,close,high,low,volume,amount
class IndexDaily(models.Model):
    ts_code = models.CharField(max_length=100, blank=True, default='')
    trade_date = models.DateTimeField(null=True)
    total_mv = models.FloatField()
    float_mv = models.FloatField()
    total_share = models.FloatField()
    float_share = models.FloatField()
    free_share = models.FloatField()
    turnover_rate = models.FloatField()
    turnover_rate_f = models.FloatField()
    pe = models.FloatField()
    pe_ttm = models.FloatField()
    pb = models.FloatField()

    class Meta:
        # ordering = ('ts_code',)
        indexes = [
            models.Index(
                fields=['ts_code'],
                name='ts_code_index_daily_idx',
            )
        ]

