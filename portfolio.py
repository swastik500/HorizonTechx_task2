"""Pure portfolio math, independent from the GUI and database."""
def enrich(stocks):
    result=[]
    for stock in stocks:
        row=dict(stock)
        row['investment']=row['quantity']*row['purchase_price']
        row['value']=row['quantity']*row['current_price']
        row['profit']=row['value']-row['investment']
        row['profit_pct']=(row['profit']/row['investment']*100) if row['investment'] else 0.0
        result.append(row)
    return result

def summary(stocks):
    rows=enrich(stocks)
    investment=sum(s['investment'] for s in rows)
    value=sum(s['value'] for s in rows)
    profit=value-investment
    companies=len(rows)
    return {'investment':investment,'value':value,'profit':profit,
            'profit_pct':profit/investment*100 if investment else 0.0,
            'shares':sum(s['quantity'] for s in rows),'companies':companies,
            'top':max(rows,key=lambda s:s['profit_pct']) if rows else None,
            'worst':min(rows,key=lambda s:s['profit_pct']) if rows else None,'stocks':rows}
