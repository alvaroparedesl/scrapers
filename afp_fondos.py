from selenium import webdriver
from selenium.webdriver.support.ui import Select
import numpy as np
import pandas as pd
import os
import sys
import re

# activos = 'https://www.spensiones.cl/inf_estadistica/series_afp/fondos_pensiones//activos_fondos_pensiones.xls'
# pasivos = 'https://www.spensiones.cl/inf_estadistica/series_afp/fondos_pensiones//pasivos_fondos_pensiones.xls'
# activos del fondo - pasivo exigible del fondo. La fecha siempre es 1ero del mes, pero da igual: corresponde realmente al último día hábil de ese mes. Revisar en: https://www.spensiones.cl/apps/valoresCuotaFondo/calculaCuofon.php
# rentabilidad = https://www.spensiones.cl/portal/institucional/594/articles-10298_recurso_1.pdf

options = webdriver.ChromeOptions()
options.add_argument("--headless")
options.add_argument("--log-level=3")
# options.add_argument("user-data-dir={}".format(os.path.join(os.getcwd(), 'temp'))) #Path to your chrome profile
options.add_experimental_option("prefs", {
  "download.default_directory": format(os.path.join(os.getcwd(), 'temp')),
  "download.prompt_for_download": False,
})

url_base = 'https://www.spensiones.cl/apps/valoresCuotaFondo/vcfAFP.php'  # valores cuota
afp_year = '//*[@id="main"]/div/div[2]/div/div[2]/table[2]/tbody/tr[11]/td/table/tbody/tr/td[5]/select'
afp_excel = '//*[@id="main"]/div/div[2]/div/div[2]/table[2]/tbody/tr[11]/td/table/tbody/tr/td[3]/a'
afp_fondos = {'A': '//*[@id="main"]/div/div[2]/div/div[2]/form[1]/div/button[1]',
              'B': '//*[@id="main"]/div/div[2]/div/div[2]/form[1]/div/button[2]',
              'C': '//*[@id="main"]/div/div[2]/div/div[2]/form[1]/div/button[3]',
              'D': '//*[@id="main"]/div/div[2]/div/div[2]/form[1]/div/button[4]',
              'E': '//*[@id="main"]/div/div[2]/div/div[2]/form[1]/div/button[5]'}

driver = webdriver.Chrome(options=options)
driver.get(url_base)

for fondo in afp_fondos:
    driver.get(url_base)
    driver.find_element_by_xpath(afp_fondos[fondo]).click()
    select = Select(driver.find_element_by_xpath(afp_year))
    opciones = select.options
    
    for index in range(len(opciones)):
        print("Scraping {}, part {}".format(fondo, index))
        select = Select(driver.find_element_by_xpath(afp_year))
        select.select_by_index(index)
        driver.find_element_by_xpath(afp_excel).click()
        
csvs = [i for i in os.listdir(os.path.join(os.getcwd(), 'temp')) if i.endswith('csv')]
files = []

for csv in csvs:
    # file = os.path.join(os.getcwd(), 'temp', csvs[-1])
    file = os.path.join(os.getcwd(), 'temp', csv)
    fondo = re.search("[A-Z]", csv)
    if fondo:
        fondo = fondo.group()
    else:
        sys.exit("Type of investment not found!")
    with open(file,'r') as fh: # files are not big, so we can loop trough all lines
        header = []
        confirm = []
        provi = []
        fechas = []
        blanks = []
        for i, row in enumerate(fh):
            if row.lower().startswith("valores conf"):
                confirm.append(i)
            if row.lower().startswith("valores provi"):
                provi.append(i)
            if row.lower().startswith("fecha"):
                fechas.append(i)
                header.append(row)
            if row[0] in (None, "", "\n"):
                blanks.append(i)
                
        total = confirm + provi
        if len(total) != len(fechas): sys.exit("confirmed + provisional do not match the number of starting rows (fechas)")
        
        for i, f in enumerate(fechas):
            print("Reading {}, part {}".format(csv, i))
            ns = (np.array(blanks) - f) > 0
            nrow = blanks[np.argmax(ns)] - f if ns.any() else None
            type = 1 if total[np.argmin(abs(np.array(total) - f))] in confirm else 0
            
            if nrow:
                temp = pd.read_csv(file, sep=";", thousands=".", decimal=",", header=0, skiprows=f+1, nrows=nrow-1)
            else:
                temp = pd.read_csv(file, sep=";", thousands=".", decimal=",", header=0, skiprows=f+1)
     
            up_level = header[i].replace("\n", "").replace(";;",";").split(";")
            if (temp.shape[1]) == (len(up_level)*2 - 1):
                up_level = [up_level[0]] + np.repeat(up_level[1:], 2).tolist()
                lw_level = temp.columns.to_list()
                lw_level[0] = ''
                lw_level = [re.sub(r'\.[0-9]+$', '', vv) for vv in lw_level]
            else:
                sys.exit("AFPs names do not match the dimension of the table")
            
            temp.columns = pd.MultiIndex.from_tuples(list(zip(up_level, lw_level)), names=['AFP', 'Variable'])
            temp = temp.assign(Confirmado = type, Fondo=fondo)
            files.append(temp)

ans = pd.concat(files).set_index(["Fondo", "Fecha", "Confirmado"]).stack().reset_index("Confirmado")
ans.to_csv(os.path.join(os.getcwd(), '..', 'data', 'output', 'financieros', "afps_rentabilidad.csv"), index=True)