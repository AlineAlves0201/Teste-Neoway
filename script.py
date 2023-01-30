# IMPORT VARIAVEIS
import jsonlines
import requests
from bs4 import BeautifulSoup


def main():
    ufs = get_ufs()
    # ufs = ['AL','RJ']
    get_content_by_ufs(ufs)


def get_ufs():
    url = 'https://www2.correios.com.br/sistemas/buscacep/buscaFaixaCep.cfm'
    data = {}
    response = requests.get(url, data)
    soup = BeautifulSoup(response.text, 'html.parser')

    # Extract the data from the table
    select = soup.find_all('select', {'class': 'f1col'})
    rows = select[0].find_all('option')
    ufs = []
    for row in rows:
        if row['value'] == '':
            continue
        ufs.append(row['value'])
    return ufs


def get_content_by_ufs(ufs):
    url = 'https://www2.correios.com.br/sistemas/buscacep/resultadoBuscaFaixaCEP.cfm'

    count = 0  # servira de indice futuramente
    records = []
    qtdrow = 50
    for uf in ufs:
        isfindnext = True
        pagini = 1
        pagfim = qtdrow
        while isfindnext:

            data = {
                'UF': uf,
                'qtdrow': qtdrow,
                'pagini': pagini,
                'pagfim': pagfim
            }

            # Envie uma solicitação GET para o site com os parâmetros especificados
            response = requests.post(url, data)

            # Analisar a resposta HTML
            soup = BeautifulSoup(response.text, 'html.parser')

            # Extrair os dados da tabela
            table = soup.find_all('table', {'class': 'tmptabela'})

            tableIndex = len(table) - 1

            try:
                rows = table[tableIndex].find_all('tr')
            except:
                break

            # Localizar localidade e faixa_cep com indice (mapeamento de dados)
            countForPage = 1
            for row in rows:
                cells = row.find_all('td')
                # IF para remover linhas em branco do HTML
                if len(cells) == 0:
                    continue
                line = [cell.text for cell in cells]
                content = {
                    'id': count,
                    'UF': uf,
                    'localidade': line[0],
                    'faixa_cep': line[1]
                }
                records.append(content)
                count += 1
                countForPage += 1

            pagini += qtdrow
            pagfim += qtdrow

    # Formatar para JSONL
    with jsonlines.open('output.jsonl', 'w') as writer:
        writer.write_all(records)


main()