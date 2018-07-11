from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import Select
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import UnexpectedAlertPresentException
import pandas as pd

# Loads dataframe with codes to search
deputados_socios_empresas = pd.read_csv("resultados/empresas_deputados.csv",sep=',',encoding = 'utf-8', converters={'cnpj': lambda x: str(x), 'cpf': lambda x: str(x), 'documento': lambda x: str(x)})

url = 'https://www.fazenda.sp.gov.br/SigeoLei131/Paginas/ConsultaDespesaAno.aspx?orgao='

# List that goes the items found
pagamentos = []

def get_values(driver,link):

    for num, row in deputados_socios_empresas.iterrows():
        # Stores the code to search
        cnpj = (row['cnpj']).strip()

        driver.get(link)
        wait = WebDriverWait(driver, 10)
        item = wait.until(EC.visibility_of_element_located((By.CSS_SELECTOR, "select[name='ctl00$ContentPlaceHolder1$ddlAno']")))
        select = Select(item)

        # Do the searches in these four years
        for vez in [2015, 2016, 2017, 2018]:
            ano = str(vez)
            select.select_by_visible_text(ano)
            wait.until(EC.visibility_of_element_located((By.CSS_SELECTOR,'#ctl00_ContentPlaceHolder1_rblDoc_0'))).click()
            wait.until(EC.visibility_of_element_located((By.CSS_SELECTOR,'#ctl00_ContentPlaceHolder1_txtCPF'))).send_keys(cnpj)
            wait.until(EC.visibility_of_element_located((By.CSS_SELECTOR,'#ctl00_ContentPlaceHolder1_btnPesquisar'))).click()

            try:
                cia = wait.until(EC.visibility_of_element_located((By.XPATH, "//tr[contains(.//th,'Credor')]/following::a"))).text
                valor = wait.until(EC.visibility_of_element_located((By.XPATH, "//tr[contains(.//th[2],'Valor')]/following::td[2]"))).text

                dicionario = {"cnpj": cnpj,
                              "ano": ano,
                              "empresa": cia,
                              "valor": valor,
                             }
                pagamentos.append(dicionario)

                print("CNPJ " + empresa + " encontrado no ano " + ano)

            except UnexpectedAlertPresentException:
                driver.switch_to_alert().accept()
                print("CNPJ " + empresa + " não encontrado no ano " + ano)


if __name__ == '__main__':
    profile = webdriver.FirefoxProfile()
    driver = webdriver.Firefox(profile)
    try:
        get_values(driver,url)
    finally:
        driver.quit()
