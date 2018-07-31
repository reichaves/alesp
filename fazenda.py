from selenium import webdriver
from selenium.common.exceptions import NoAlertPresentException
from selenium.webdriver.support.select import Select
import pandas as pd

deputados_socios_empresas = pd.read_csv("resultados/empresas_deputados.csv",sep=',',encoding = 'utf-8',
                                        converters={'cnpj': lambda x: str(x),
                                                    'cpf': lambda x: str(x),
                                                    'documento': lambda x: str(x)})

profile = webdriver.FirefoxProfile()
browser = webdriver.Firefox(profile)
browser.implicitly_wait(10)

# Site that is accessed
browser.get('https://www.fazenda.sp.gov.br/SigeoLei131/Paginas/ConsultaDespesaAno.aspx?orgao=')

# List to store the data
pagamentos = []

for num, row in deputados_socios_empresas.iterrows():
    # Variable with code to search
    empresa = (row['cnpj']).strip()
    deputado = (row['nome_urna']).strip()

    # Search for each code in four years
    for vez in [2015, 2016, 2017, 2018]:
        ano = str(vez)

        # Select year
        Select(browser.find_element_by_name('ctl00$ContentPlaceHolder1$ddlAno')).select_by_visible_text(ano)

        # Fill in the code to search
        browser.find_element_by_xpath('//*[@id="ctl00_ContentPlaceHolder1_rblDoc_0"]').click()
        browser.find_element_by_xpath('//*[@id="ctl00_ContentPlaceHolder1_txtCPF"]').send_keys(empresa)
        browser.find_element_by_xpath('//*[@id="ctl00_ContentPlaceHolder1_btnPesquisar"]').click()

        try:
            found = True
            alert = browser.switch_to.alert
            alert.accept()
            found = False
            # Message shows that the code was not found that year
            print("CNPJ " + empresa + " não encontrado no ano " + ano)
            browser.find_element_by_xpath('//*[@id="ctl00_ContentPlaceHolder1_btnVoltar"]').click()
        except NoAlertPresentException:
            pass

        if found:
            results = browser.find_element_by_xpath("//table[@id='ctl00_ContentPlaceHolder1_gdvCredor']//tr[2]")
            cia = results.find_element_by_xpath("td[1]").text
            valor = results.find_element_by_xpath("td[2]").text

            #Message shows that the code was found that year
            print("CNPJ " + empresa + " encontrado no ano " + ano)

            # Fills dictionary with found data
            dicionario = {"cnpj": empresa,
                          "deputado_relacionado": deputado,
                          "ano": ano,
                          "empresa": cia,
                          "valor": valor,
                         }
            pagamentos.append(dicionario)


            # Go back one screen to do another search
            browser.find_element_by_xpath('//*[@id="ctl00_ContentPlaceHolder1_btnVoltar"]').click()

# Create the dataframe
df_pagamentos = pd.DataFrame(pagamentos)


pd.options.display.float_format = '{:,.2f}'.format

df_pagamentos.info()

df_pagamentos.reset_index()

df_pagamentos.to_csv('resultados/pagtos_estaduais_empresas_deputados.csv', index=False, decimal=',')
