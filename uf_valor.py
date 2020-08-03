from selenium import webdriver
from selenium.webdriver.support.ui import Select
from datetime import datetime
from scipy import stats
import pandas as pd
import os
import time
import locale

#replace with .Firefox(), or with the browser of your c
# https://chromedriver.chromium.org/downloads
options = webdriver.ChromeOptions()
# options.add_argument("--incognito")
options.add_argument("--headless")
options.add_argument("--log-level=3")

url_base = 'https://si3.bcentral.cl/Indicadoressiete/secure/Indicadoresdiarios.aspx'
uf_link = '//*[@id="hypLnk1_1"]'
uf_years = '//*[@id="DrDwnFechas"]'
uf_table = '//*[@id="contenedor_serie"]'
uf_anio = '//*[@id="lblAnioValor"]'

driver = webdriver.Chrome(options=options)
driver.get(url_base)
driver.find_element_by_xpath(uf_link).click()

select = Select(driver.find_element_by_xpath(uf_years))
# values = [v.text for v in select.options]
opciones = select.options
tablas = []

for index in range(len(opciones)):
    select = Select(driver.find_element_by_xpath(uf_years))
    select.select_by_index(index)
    anio = driver.find_element_by_xpath(uf_anio).text
    print("Obteniendo {}".format(anio))
    tbl = driver.find_element_by_xpath(uf_table).get_attribute('outerHTML')
    tab = pd.melt(pd.read_html(tbl, decimal=",", thousands=".")[1], "Día", value_name="UF_valor")
    tab['anio'] = int(anio)
    tablas.append(tab)

UF = pd.concat(tablas)
UF[['anio', 'variable', 'Día']].apply(lambda x: "-".join(x.values.astype(str)), axis=1)
locale.setlocale(locale.LC_TIME, 'es_ES.UTF-8')
UF["fecha"] = pd.to_datetime( UF[['anio', 'variable', 'Día']].apply(lambda x: "-".join(x.values.astype(str)), axis=1) , format="%Y-%B-%d", errors='coerce')
UF[['fecha', 'UF_valor']].dropna().to_csv("../data/output/financieros/UF.csv", index=False)