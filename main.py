from flask import Flask, render_template, request
import pandas as pd
from statsmodels.tsa.arima.model import ARIMA

app = Flask(__name__)
@app.route('/')
def login():
    return render_template('login.html')

@app.route('/home', methods=['GET', 'POST'])
def home():
    return render_template('homepage.html')

@app.route('/result', methods=['POST'])
def result():
    file = request.files['csv_file']
    if file:
        # Transforma o arquivo em um DataFrame
        df = pd.read_csv(file, sep=';', low_memory=False)
        print(df)
        df.dropna(subset=['CODIGO'], inplace=True)
        df['QUANTIDADE'].replace({',': '.'}, regex=True, inplace=True)
        df['QUANTIDADE'] = pd.to_numeric(df['QUANTIDADE'], errors='coerce')
        df['DATA'] = pd.to_datetime(df['DATA'], format="%d/%m/%Y")
        df['CODIGO'] = pd.to_numeric(df['CODIGO'], errors='coerce')
        products = df['CODIGO'].unique()
        porcentagem = 1 / 100
        qtd_products = porcentagem * len(products)
        qtd_products = int(qtd_products // 1)
        produtos_parte = products[:qtd_products]

        p = []

        c = 0
        for product in produtos_parte:
            c += 1

            try:
                # Filtrar os dados para apenas o produto atual
                product_data = df[df['CODIGO'] == product]

                # Agrupar as vendas por mês
                grouped = product_data.groupby(['DATA'])['QUANTIDADE'].sum().reset_index()

                # Criar uma série temporal indexada pela data
                ts = grouped.set_index('DATA')['QUANTIDADE']
                # Treinar o modelo ARIMA
                model = ARIMA(ts, order=(1, 1, 0))
                model_fit = model.fit()

                # Fazer previsões para os próximos 12 meses
                y_pred = model_fit.forecast(steps=12)
                p.append([product, y_pred])
            except:
                pass

        dfteste = pd.DataFrame(p, columns=['produto', 'previsao_vendas'])
        meses = ['MES_1', 'MES_2', 'MES_3', 'MES_4', 'MES_5', 'MES_6', 'MES_7', 'MES_8', 'MES_9', 'MES_10', 'MES_11',
                 'MES_12']
        n = []
        x = dfteste['previsao_vendas']
        for i in x:
            y = i.tolist()
            n.append(y)
        dfnovo = pd.DataFrame(n, columns=meses)
        dfnovo['PRODUTO'] = dfteste['produto']

        print(dfnovo)

        saida = dfnovo.to_json(orient='records')
        resultado = dfnovo.to_dict(orient='records')
        return render_template('result.html', data=resultado)
    return render_template('result.html', data=[])

if __name__ == '__main__':
    app.run(debug=True)


