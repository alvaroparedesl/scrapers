# Web Scrapers

Este repositorio fue generado con la idea de mantener una actualización constante de diversas bases de datos de interés nacionales (Chile).

## Entorno

Estos scrapers utilizan Selenium cuando en la mayoría de los casos (cuando la página web necesita renderizar Javascript por ejemplo). Las pruebas se han hecho utilizando [Chromedriver](https://chromedriver.chromium.org/downloads), pero evntualmente se podría usar cualquiera. Es importante descargar este driver y dejarlo en la ruta de ejcución [más información](https://selenium-python.readthedocs.io/).

Es recomendable (pero no obligatorio), instalar [Anaconda](https://www.anaconda.com/products/individual), y utilizar un entorno virtual, con la siguiente configuración (más información sobre la creación de ambientes [aquí](https://docs.conda.io/projects/conda/en/latest/user-guide/tasks/manage-environments.html)):

```
conda create -n scraper python=3.8 selenium pandas
conda activate scraper
```

## Datos

1. [uf_valor.py](uf_valor.py):
2. [afp_fondos.py](afp_fondos.py):

