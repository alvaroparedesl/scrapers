from selenium import webdriver
from selenium.webdriver.support.ui import Select
from auxiliar import str2bool
import argparse
import pandas as pd
import os
import locale

if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("-u", "--update", help="Just update data?", type=str2bool, default=False)
    args = parser.parse_args()

    options = webdriver.ChromeOptions() #replace with .Firefox(), or with the browser of your choose
    options.add_argument("--headless")
    options.add_argument("--log-level=3")

    url_base = 'https://si3.bcentral.cl/Indicadoressiete/secure/Indicadoresdiarios.aspx'
    uf_link = '//*[@id="hypLnk1_1"]'
    uf_years = '//*[@id="DrDwnFechas"]'
    uf_table = '//*[@id="contenedor_serie"]'
    uf_anio = '//*[@id="lblAnioValor"]'

    driver = webdriver.Chrome(options=options) #replace with .Firefox(), or with the browser of your choose
    driver.get(url_base)
    driver.find_element_by_xpath(uf_link).click()

    select = Select(driver.find_element_by_xpath(uf_years))
    opciones = select.options
    tablas = []
    miterator = [range(len(opciones))[-1]] if args.update else range(len(opciones))

    for index in miterator:
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
    UF["Fecha"] = pd.to_datetime( UF[['anio', 'variable', 'Día']].apply(lambda x: "-".join(x.values.astype(str)), axis=1) , format="%Y-%B-%d", errors='coerce')
    UF = UF[['Fecha', 'UF_valor']].dropna().set_index('Fecha')
    outname = os.path.join(os.getcwd(), "..", "data", "output", "financieros", "UF.csv")
    if args.update:
        temp = pd.read_csv(outname)
        temp.Fecha = pd.to_datetime(temp.Fecha)
        temp.set_index('Fecha', inplace=True)
        diff = UF.index.difference(temp.index, sort=False)
        temp.update(UF)
        if len(diff) > 0:
            pd.concat([temp, UF.loc[diff]]).to_csv(outname, index=True)
        else:
            temp.to_csv(outname, index=True)
    else:
        UF.to_csv(outname, index=True)