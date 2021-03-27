import datetime
import pandas as pd
import os
import sys
sys.path.insert(0, os.path.abspath('.'))
os.environ.setdefault("DJANGO_SETTINGS_MODULE", "stock_api.settings")

from django.db import connection

from rest_framework.reverse import reverse

from ifund import factorFilter
import backtrader as bt

def calculateShare(request, result, params):
    res = {
        'df': {},
        'path': '',
        'columns': [],
        'activities': []
    }
    res['columns'] = result['columns']
    res['path'] = reverse('strategy-portfolio-download', request=request, args=[result['path']])
    group_data = result['df'].groupby(result['df']['date'])
    for date, group in group_data:
        group['index'] = group.index
        res['df'][str(date)] = {
            'results': group.to_dict('records'),
            'count': group.shape[0]
        }

    df = result['df']
    df = df.rename(columns = {"date": "end_date"})
    df["end_date"] = df["end_date"].apply(lambda x:str(x))

    res["activities"] = factorFilter.calculateShare(df, params)["activities"]
    return res