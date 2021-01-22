from django.db import models

class Company(models.Model):
    symbol = models.CharField(max_length=100, blank=True, default='')
    ts_code = models.CharField(max_length=100, blank=True, default='')
    name = models.CharField(max_length=100, blank=True, default='')
    area = models.CharField(max_length=100, blank=True, null=True, default='')
    industry = models.CharField(max_length=100, blank=True, null=True, default='')
    fullname = models.CharField(max_length=100, blank=True, null=True, default='')
    enname = models.CharField(max_length=100, blank=True, null=True, default='')
    market = models.CharField(max_length=100, blank=True, null=True, default='')
    exchange = models.CharField(max_length=100, blank=True, null=True, default='')
    curr_type = models.CharField(max_length=100, blank=True, null=True, default='')
    list_status = models.CharField(max_length=100, blank=True, null=True, default='')
    list_date = models.DateTimeField(null=True)
    delist_date = models.DateTimeField(null=True)
    is_hs = models.CharField(max_length=10, blank=True, null=True, default='')

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
    fullname = models.CharField(max_length=100, blank=True, null=True, default='')
    market = models.CharField(max_length=100, blank=True, null=True, default='')
    publisher = models.CharField(max_length=100, blank=True, null=True, default='')
    index_type = models.CharField(max_length=100, blank=True, null=True, default='')
    category = models.CharField(max_length=100, blank=True, null=True, default='')
    base_date = models.DateTimeField(null=True)
    base_point = models.FloatField(null=True)
    list_date = models.DateTimeField(null=True)
    weight_rule = models.CharField(max_length=100, blank=True, null=True, default='')
    desc = models.TextField(blank=True, null=True, default='')
    exp_date = models.DateTimeField(null=True)

    class Meta:
        # ordering = ('ts_code',)
        indexes = [
            models.Index(
                fields=['ts_code'],
                name='ts_code_index_idx',
            )
        ]


class CompanyDaily(models.Model):
    ts_code = models.CharField(max_length=100, blank=True, default='')
    trade_date = models.DateTimeField(null=True)
    close = models.FloatField(null=True)
    turnover_rate = models.FloatField(null=True)
    turnover_rate_f = models.FloatField(null=True)
    volume_ratio = models.FloatField(null=True)
    pe = models.FloatField(null=True)
    pe_ttm = models.FloatField(null=True)
    pb = models.FloatField(null=True)
    ps = models.FloatField(null=True)
    ps_ttm = models.FloatField(null=True)
    total_share = models.FloatField(null=True)
    float_share = models.FloatField(null=True)
    free_share = models.FloatField(null=True)
    total_mv = models.FloatField(null=True)
    circ_mv = models.FloatField(null=True)

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
    total_mv = models.FloatField(null=True)
    float_mv = models.FloatField(null=True)
    total_share = models.FloatField(null=True)
    float_share = models.FloatField(null=True)
    free_share = models.FloatField(null=True)
    turnover_rate = models.FloatField(null=True)
    turnover_rate_f = models.FloatField(null=True)
    pe = models.FloatField(null=True)
    pe_ttm = models.FloatField(null=True)
    pb = models.FloatField(null=True)

    class Meta:
        # ordering = ('ts_code',)
        indexes = [
            models.Index(
                fields=['ts_code'],
                name='ts_code_index_daily_idx',
            )
        ]


class CompanyToday(models.Model):
    ts_code = models.CharField(max_length=100, blank=True, default='')
    trade_date = models.DateTimeField(null=True)
    open = models.FloatField(null=True)
    high = models.FloatField(null=True)
    low = models.FloatField(null=True)
    close = models.FloatField(null=True)
    pre_close = models.FloatField(null=True)
    change = models.FloatField(null=True)
    pct_chg = models.FloatField(null=True)
    vol = models.FloatField(null=True)
    amount = models.FloatField(null=True)

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
    close = models.FloatField(null=True)
    open = models.FloatField(null=True)
    high = models.FloatField(null=True)
    low = models.FloatField(null=True)
    pre_close = models.FloatField(null=True)
    change = models.FloatField(null=True)
    pct_chg = models.FloatField(null=True)
    vol = models.FloatField(null=True)
    amount = models.FloatField(null=True)

    class Meta:
        # ordering = ('ts_code',)
        indexes = [
            models.Index(
                fields=['ts_code'],
                name='ts_code_index_today_idx',
            )
        ]

