from django.db import models
from pygments.lexers import get_all_lexers
from pygments.styles import get_all_styles

from pygments.lexers import get_lexer_by_name
from pygments.formatters.html import HtmlFormatter
from pygments import highlight

LEXERS = [item for item in get_all_lexers() if item[1]]
LANGUAGE_CHOICES = sorted([(item[1][0], item[0]) for item in LEXERS])
STYLE_CHOICES = sorted((item, item) for item in get_all_styles())

class Strategy(models.Model):
    owner = models.ForeignKey('auth.User', related_name='strategy', on_delete=models.CASCADE)
    highlighted = models.TextField()

    created = models.DateTimeField(auto_now_add=True)
    title = models.CharField(max_length=100, blank=True, default='')
    code = models.TextField()
    start_date = models.DateField(null=True)
    end_date = models.DateField(null=True)
    stock = models.FloatField()
    benchmark = models.CharField(max_length=100, blank=True, default='')
    result = models.TextField()

    class Meta:
        ordering = ('created',)

    def save(self, *args, **kwargs):
        super(Strategy, self).save(*args, **kwargs)


class Results(models.Model):
    error = models.BooleanField()
    Total_Returns = models.CharField(max_length=100, blank=True, default='')
    Annual_Returns = models.CharField(max_length=100, blank=True, default='')
    Benchmark_Returns = models.CharField(max_length=100, blank=True, default='')
    Benchmark_Annual = models.CharField(max_length=100, blank=True, default='')
    Alpha = models.CharField(max_length=100, blank=True, default='')
    Beta = models.CharField(max_length=100, blank=True, default='')
    Sharpe = models.CharField(max_length=100, blank=True, default='')
    Sortino = models.CharField(max_length=100, blank=True, default='')
    Information_Ratio = models.CharField(max_length=100, blank=True, default='')
    Volatility = models.CharField(max_length=100, blank=True, default='')
    MaxDrawdown = models.CharField(max_length=100, blank=True, default='')
    Tracking_Error = models.CharField(max_length=100, blank=True, default='')
    Downside_Risk = models.CharField(max_length=100, blank=True, default='')
    strategy = models.ForeignKey(Strategy, on_delete=models.CASCADE)

    class Meta:
        ordering = ('strategy',)

    def save(self, *args, **kwargs):
        super(Results, self).save(*args, **kwargs)