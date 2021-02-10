import pandas as pd

def mainfunc(activities):
    fields = ['trade_date', 'ts_code', 'share']
    df = pd.DataFrame(columns=fields)
    for activity in activities:
        timestamp = activity['timestamp']
        for company in activity['companies']:
            df = df.append(pd.DataFrame([[timestamp, company['ts_code'], company['share']]], columns=fields), ignore_index=True)
    return df.to_dict('records')
