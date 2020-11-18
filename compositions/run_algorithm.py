import os
import json
from strategies.models import Results
import pandas as pd
import numpy as np
import re
from rest_framework.reverse import reverse
import subprocess
import codecs

def make_algprithm(request, user, id, file_name):
    prefix = \
"""import os
import sys
sys.path.insert(0, os.path.abspath('../../../'))

# import matplotlib as plt
# plt.use('Agg')

from rqalpha import run_func
from rqalpha.api import *
import talib

config = """

    f = open(os.path.join("media/strategy", user, id, file_name), "r")
    lines = f.read()
    f.close()

    suffix = """

a = run_func(**globals())
# print(a)
    
    """

    config = {
        "base": {
            "accounts": {
            },
            "data_bundle_path": "../../../"+"./rqalpha/bundle"
        },
        "extra": {
            "log_level": "verbose",
        },
        "mod": {
            "sys_analyser": {
                "enabled": 1,
                "plot": 0,
            }
        }
    }
    # config["mod"]["sys_analyser"]["plot_save_file"] = os.path.join(py_folder, "result.jpg")
    config["mod"]["sys_analyser"]["plot_save_file"] = os.path.join(id, "result.jpg")
    if request.data['start_date'] and request.data['start_date'] != "":
        config["base"]["start_date"] = request.data['start_date']
    if request.data['end_date'] and request.data['end_date'] != "":
        config["base"]["end_date"] = request.data['end_date']
    if request.data['benchmark'] and request.data['benchmark'] != "":
        config["base"]["benchmark"] = request.data['benchmark']
    if request.data['stock'] and request.data['stock'] != "":
        config["base"]["accounts"]["stock"] = request.data['stock']

    code = prefix + json.dumps(config, indent=4) + "\n" + lines + suffix


    f = codecs.open(os.path.join("media/strategy", user, id, "algrithm.py"), "w", 'utf-8')
    f.write(code.encode('utf-8').decode('utf-8'))
    f.close()


def run_algorithm(request, user, id, code):
    title = re.sub('[^a-zA-Z0-9_]', '', request.data["title"].strip().replace(" ", "_"))

    py_folder = os.path.join("media/strategy", user, id)
    if not os.path.exists(py_folder):
        os.makedirs(py_folder)

    f = codecs.open(os.path.join(py_folder, title + ".py"), "w", 'utf-8')
    f.write(code.encode('utf-8').decode('utf-8'))
    f.close()

    make_algprithm(request, user, id, title + ".py")
    print("@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@")
    console_output = os.popen("cd " + os.path.join("media/strategy", user) + "\npython " + os.path.join(id, 'algrithm.py')).read()
    # p = subprocess.Popen(["python " + os.path.join(id, 'algrithm.py')], shell=True,stdout=subprocess.PIPE, cwd=os.path.realpath(os.path.join("media/strategy", user)))
    # console_output = p.stdout.readlines()
    print("@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@")
    print(console_output)

    f = open(os.path.join(py_folder, "result.json"))
    res = json.load(f)
    f.close()
    res['error'] = False
    res['strategy_id'] = id

    # 保存结果数据
    if Results.objects.filter(strategy_id=id).exists():
        Results.objects.filter(strategy_id=id).update(**res)
    else:
        Results.objects.create(**res)

    res["console_output"] = console_output
    # res['image'] = reverse('strategy-image-url', args=[id], request=request)

    result = pd.read_csv(os.path.join(py_folder, "result.csv")).fillna("")
    res["result"] = {}
    res["result"]["date"] = result["date"]
    res["result"]["portfolio"] = result["portfolio"]
    res["result"]["benchmark_portfolio"] = result["benchmark_portfolio"]
    res["result"]["daily_returns"] = result["daily_returns"]

    result_trade = pd.read_csv(os.path.join(py_folder, "result_trade.csv")).fillna("")
    result_side = pd.read_csv(os.path.join(py_folder, "result_side.csv")).fillna("")


    res["result"]["params_index"] = ["portfolio", "benchmark_portfolio", "daily_returns"] + result_trade.columns.tolist()[:-1]

    res["result"]["amount"] = np.transpose(result_trade[result_trade.columns.tolist()[:-1]].values)
    res["result"]["side"] = np.transpose(result_side[result_side.columns.tolist()[:-1]].values)
    return res