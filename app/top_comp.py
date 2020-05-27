import requests
import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
import io

companies = ['AAPL','AMZN','GOOG','MSFT','TSLA']
listofdf = []

def do_plot():
    for item in companies:
        histprices = requests.get(f"https://financialmodelingprep.com/api/v3/historical-price-full/{item}?serietype=line&apikey=a5bee999241cc8d8f9f2281f838312e0")
        histprices = histprices.json()
        histprices = histprices['historical']
        histpricesdf = pd.DataFrame.from_dict(histprices)
        histpricesdf = histpricesdf.rename({'close': item}, axis=1)
        listofdf.append(histpricesdf)
    dfs = [df.set_index('date') for df in listofdf]
    histpriceconcat = pd.concat(dfs, axis=1)
    histpriceconcat1 = histpriceconcat.drop(histpriceconcat.index[100:])
    histpriceconcat1.index.rename('date', inplace=True)
    histpriceconcat2 = histpriceconcat1.sort_values(["date"], ascending=True)
    histpriceconcat2 = histpriceconcat2/histpriceconcat2.iloc[0]
    for i, col in enumerate(histpriceconcat.columns):
        histpriceconcat2[col]
    sns.set_style("white")
    g = sns.lineplot(data=histpriceconcat2, palette="husl", linewidth=2.5)
    for ind, label in enumerate(g.get_xticklabels()):
        if ind % 15== 0:  # every 15th label is kept
            label.set_visible(True)
        else:
            label.set_visible(False)
    plt.title('Price Evolution Comparison')
    plt.xticks(rotation=70)
    plt.tight_layout()
    bytes_image = io.BytesIO()
    plt.savefig(bytes_image, format='png')
    bytes_image.seek(0)
    return bytes_image


