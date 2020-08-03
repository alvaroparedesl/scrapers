from selenium import webdriver
from selenium.webdriver.support.ui import Select
from datetime import datetime
from scipy import stats
import pandas as pd
import os
import time
import locale

# activos = 'https://www.spensiones.cl/inf_estadistica/series_afp/fondos_pensiones//activos_fondos_pensiones.xls'
# pasivos = 'https://www.spensiones.cl/inf_estadistica/series_afp/fondos_pensiones//pasivos_fondos_pensiones.xls'
# activos del fondo - pasivo exigible del fondo. La fecha siempre es 1ero del mes, pero da igual: corresponde realmente al último día hábil de ese mes. Revisar en: https://www.spensiones.cl/apps/valoresCuotaFondo/calculaCuofon.php

# https://chromedriver.chromium.org/downloads
options = webdriver.ChromeOptions()
# options.add_argument("--incognito")
options.add_argument("--headless")
options.add_argument("--log-level=3")
# options.add_argument("user-data-dir={}".format(os.path.join(os.getcwd(), 'temp'))) #Path to your chrome profile
options.add_experimental_option("prefs", {
  "download.default_directory": format(os.path.join(os.getcwd(), 'temp')),
  "download.prompt_for_download": False,
})


# https://www.spensiones.cl/apps/centroEstadisticas/paginaCuadrosCCEE.php?menu=sci&menuN1=estfinfp&menuN2=NOID
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
    driver.find_element_by_xpath(afp_fondos[fondo]).click()
    select = Select(driver.find_element_by_xpath(afp_year))
    opciones = select.options
    
    for index in range(len(opciones)):
        select = Select(driver.find_element_by_xpath(afp_year))
        select.select_by_index(index)
        driver.find_element_by_xpath(afp_excel).click()
    kk