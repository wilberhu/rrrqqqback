from django.db import models

class Company(models.Model):
    symbol = models.CharField(max_length=100, blank=True, default='')
    ts_code = models.CharField(primary_key=True, max_length=100)
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
                fields=['ts_code'],
                name='ts_code_company_idx',
            )
        ]


class Index(models.Model):
    ts_code = models.CharField(primary_key=True, max_length=100)
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


class CompanyDailyBasic(models.Model):
    ts_code = models.CharField(max_length=100)
    trade_date = models.DateField(null=True)
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
        unique_together = ("ts_code", "trade_date")
        indexes = [
            models.Index(
                fields=['ts_code', 'trade_date'],
                name='ts_code_trade_date_c_d_b_idx',
            ),
            models.Index(
                fields=['ts_code'],
                name='ts_code_c_d_b_idx',
            ),
            models.Index(
                fields=['trade_date'],
                name='trade_date_c_d_b_idx',
            )
        ]


class IndexDailyBasic(models.Model):
    ts_code = models.CharField(max_length=100)
    trade_date = models.DateField(null=True)
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
        unique_together = ("ts_code", "trade_date")
        indexes = [
            models.Index(
                fields=['ts_code', 'trade_date'],
                name='ts_code_trade_date_i_d_b_idx',
            ),
            models.Index(
                fields=['ts_code'],
                name='ts_code_i_d_b_idx',
            ),
            models.Index(
                fields=['trade_date'],
                name='trade_date_i_d_b_idx',
            )
        ]


class CompanyDaily(models.Model):
    ts_code = models.CharField(max_length=100)
    trade_date = models.DateField(null=True)
    open = models.FloatField(null=True)
    high = models.FloatField(null=True)
    low = models.FloatField(null=True)
    close = models.FloatField(null=True)
    pre_close = models.FloatField(null=True)
    change = models.FloatField(null=True)
    pct_chg = models.FloatField(null=True)
    vol = models.FloatField(null=True)
    amount = models.FloatField(null=True)
    adj_factor = models.FloatField(null=True)

    class Meta:
        # ordering = ('ts_code',)
        unique_together = ("ts_code", "trade_date")
        indexes = [
            models.Index(
                fields=['ts_code', 'trade_date'],
                name='ts_code_trade_date_c_d_idx',
            ),
            models.Index(
                fields=['ts_code'],
                name='ts_code_c_d_idx',
            ),
            models.Index(
                fields=['trade_date'],
                name='trade_date_c_d_idx',
            )
        ]


class IndexDaily(models.Model):
    ts_code = models.CharField(max_length=100)
    trade_date = models.DateField(null=True)
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
        unique_together = ("ts_code", "trade_date")
        indexes = [
            models.Index(
                fields=['ts_code', 'trade_date'],
                name='ts_code_trade_date_i_d_idx',
            ),
            models.Index(
                fields=['ts_code'],
                name='ts_code_i_d_idx',
            ),
            models.Index(
                fields=['trade_date'],
                name='trade_date_i_d_idx',
            )
        ]


class FundBasic(models.Model):
    ts_code = models.CharField(primary_key=True, max_length=100)
    name = models.CharField(max_length=100, blank=True, null=True, default='')
    management = models.CharField(max_length=100, blank=True, null=True, default='')
    custodian = models.CharField(max_length=100, blank=True, null=True, default='')
    fund_type = models.CharField(max_length=100, blank=True, null=True, default='')
    found_date = models.CharField(max_length=100, blank=True, null=True, default='')
    due_date = models.CharField(max_length=100, blank=True, null=True, default='')
    list_date = models.CharField(max_length=100, blank=True, null=True, default='')
    issue_date = models.CharField(max_length=100, blank=True, null=True, default='')
    delist_date = models.CharField(max_length=100, blank=True, null=True, default='')

    issue_amount = models.FloatField(null=True)
    m_fee = models.FloatField(null=True)
    c_fee = models.FloatField(null=True)
    duration_year = models.FloatField(null=True)
    p_value = models.FloatField(null=True)
    min_amount = models.FloatField(null=True)
    exp_return = models.FloatField(null=True)

    benchmark = models.TextField(blank=True, null=True, default='')

    status = models.CharField(max_length=100, blank=True, null=True, default='')
    invest_type = models.CharField(max_length=100, blank=True, null=True, default='')
    type = models.CharField(max_length=100, blank=True, null=True, default='')
    trustee = models.CharField(max_length=100, blank=True, null=True, default='')
    purc_startdate = models.CharField(max_length=100, blank=True, null=True, default='')
    redm_startdate = models.CharField(max_length=100, blank=True, null=True, default='')
    market = models.CharField(max_length=100, blank=True, null=True, default='')

    class Meta:
        # ordering = ('ts_code',)
        indexes = [
            models.Index(
                fields=['ts_code'],
                name='ts_code_fund_basic_idx',
            )
        ]


class FundDaily(models.Model):
    ts_code = models.CharField(max_length=100)
    trade_date = models.DateField(null=True)

    open = models.FloatField(null=True)
    close = models.FloatField(null=True)
    high = models.FloatField(null=True)
    low = models.FloatField(null=True)
    pre_close = models.FloatField(null=True)
    change = models.FloatField(null=True)
    pct_chg = models.FloatField(null=True)
    vol = models.FloatField(null=True)
    amount = models.FloatField(null=True)
    adj_factor = models.FloatField(null=True)

    class Meta:
        # ordering = ('ts_code',)
        unique_together = ("ts_code", "trade_date")
        indexes = [
            models.Index(
                fields=['ts_code', 'trade_date'],
                name='ts_code_trade_date_f_d_idx',
            ),
            models.Index(
                fields=['ts_code'],
                name='ts_code_f_d_idx',
            ),
            models.Index(
                fields=['trade_date'],
                name='trade_date_f_d_idx',
            )
        ]


class FundNav(models.Model):
    ts_code = models.CharField(max_length=100)

    ann_date = models.DateField(null=True, default='')
    nav_date = models.DateField(null=True)

    unit_nav = models.FloatField(null=True)
    accum_nav = models.FloatField(null=True)
    accum_div = models.FloatField(null=True)
    net_asset = models.FloatField(null=True)
    total_netasset = models.FloatField(null=True)
    adj_nav = models.FloatField(null=True)

    class Meta:
        # ordering = ('ts_code',)
        unique_together = ("ts_code", "nav_date")
        indexes = [
            models.Index(
                fields=['ts_code', 'nav_date'],
                name='ts_code_nav_date_f_n_idx',
            ),
            models.Index(
                fields=['ts_code'],
                name='ts_code_f_n_idx',
            ),
            models.Index(
                fields=['nav_date'],
                name='nav_date_f_n_idx',
            )
        ]