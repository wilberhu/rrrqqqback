import datetime
import pandas as pd
import os
import sys
sys.path.insert(0, os.path.abspath('.'))
os.environ.setdefault("DJANGO_SETTINGS_MODULE", "stock_api.settings")

from django.db import connection


from ifund import factorFilter
from ifund import formatResult
import backtrader as bt

def calculateShare(result, params):
    res = formatResult.formatResult2CN(result)


    if "activities" in result:
        res["activities"] = factorFilter.calculateShare(res['df'], params, result["activities"])["activities"]
    else:
        res["activities"] = factorFilter.calculateShare(res['df'], params)["activities"]
    del res['df']
    return res