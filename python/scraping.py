from io import StringIO
import pandas as pd
import json
import os
import time

from bs4 import BeautifulSoup
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.chrome.service import Service
from webdriver_manager.chrome import ChromeDriverManager

def impostaDriver():
    chrome_options = Options()
    chrome_options.add_argument('--no-sandbox')
    chrome_options.add_argument('--headless')
    chrome_options.add_argument('--disable-dev-shm-usage')

    # Imposta il driver con Chrome installato nel container Docker
    driver_path = ChromeDriverManager().install()
    print(f"Driver path: {driver_path}")

    service=Service(driver_path)
    driver = webdriver.Chrome(service=service, options=chrome_options)
    return driver

def ottieniHTML(driver, url):
    driver.get(url)
    driver.implicitly_wait(5)
    return BeautifulSoup(driver.page_source, 'html.parser')

def salva_tabella_squadre_csv(soup, percorso):
    tabella_squadre = soup.find("table", {"id": "stats_squads_standard_for"})
    tabella_squadreNorm = str(tabella_squadre).replace(',', '.')
    squadra_df = pd.read_html(StringIO(str(tabella_squadreNorm)), decimal=".")[0]
    #squadra_df.to_csv("./python/dati/serie_a_squad.csv", index=False, encoding="utf-8")
    squadra_df.to_csv(percorso, index=False, encoding="utf-8")
    print(f"Tabelle squadre salvate in {percorso}")
    return squadra_df

def salva_tabella_giocatori_csv(soup, percorso):
    tabella_giocatori = soup.find("table", {"id": "stats_standard"})
    tabella_giocatoriNorm = str(tabella_giocatori).replace(',', '.')
    players_df = pd.read_html(StringIO(str(tabella_giocatoriNorm)), decimal=".")[0]
    #players_df.to_csv("./python/dati/serie_a_players.csv", index=False, encoding="utf-8")
    players_df.to_csv(percorso, index=False, encoding="utf-8")
    print(f"Tabelle giocatori salvate in {percorso}")
    return players_df

def pulisci_tabelle_squadre(percorsoVecchio, percorsoNuovo):
    path_squadre = percorsoVecchio
    df_squadre = pd.read_csv(path_squadre)
    df_squadre.to_csv(percorsoNuovo, index=False)
    path_squadre2 = percorsoNuovo
    df_squadre = pd.read_csv(path_squadre2, skiprows=1)
    df_squadre.to_csv(percorsoNuovo, index=False)
    colonne_da_lasciare = [col for col in df_squadre.columns if "squadra" in col.lower() or "PG" in col]
    if colonne_da_lasciare:
        df_squadre = df_squadre[colonne_da_lasciare]
        print("File CSV squadre modificato e colonne rimosse.")
    else:
        print("Nessuna colonna da rimuovere trovata.")
    df_squadre = df_squadre.where(pd.notnull(df_squadre), None)
    df_squadre.to_csv(percorsoNuovo, index=False)
    os.remove(percorsoVecchio)
    return df_squadre

def pulisci_tabelle_giocatori(percorsoVecchio, percorsoNuovo):
    path_giocatori = percorsoVecchio
    df_giocatori = pd.read_csv(path_giocatori)
    colonne_da_rimuovere = [col for col in df_giocatori.columns if "progressione" in col.lower() or "per 90 minuti" in col.lower() or "unnamed: 36" in col.lower() or "età" in col.lower()]
    if colonne_da_rimuovere:
        df_giocatori.drop(columns=colonne_da_rimuovere, inplace=True)
        print("File CSV giocatori modificato e colonne rimosse.")
    else:
        print("Nessuna colonna da rimuovere trovata.")
    df_giocatori.to_csv(percorsoNuovo, index=False)
    path_giocatori2 = percorsoNuovo
    df_giocatori = pd.read_csv(path_giocatori2, skiprows=1)
    df_giocatori = df_giocatori.where(pd.notnull(df_giocatori), None)
    df_giocatori.to_csv(percorsoNuovo, index=False)
    os.remove(percorsoVecchio)
    return df_giocatori

def dataFrametoDict(df):
    data = df.to_dict(orient="records")
    return data

def csvToJSON(percorsoJSON, data):
    # Scrivi il JSON su file
    with open(percorsoJSON, mode='w', encoding='utf-8') as json_file:
        json.dump(data, json_file, indent=4, ensure_ascii=False)
    print(f"File JSON salvato in {percorsoJSON}.")

    # Carica i dati dal file JSON
    with open(percorsoJSON, 'r', encoding='utf-8') as f:
        data = json.load(f)

    # Scrivi i singoli oggetti in un nuovo file JSON, uno per riga
    with open(percorsoJSON, 'w', encoding='utf-8') as f:
        for item in data:
            json.dump(item, f, ensure_ascii=False)
            f.write('\n')

def esegui(url, percorsoOutput, percorsoSquadre, percorsoGiocatori, percorsoSquadreNuovo, percorsoGiocatoriNuovo, percorsoSquadreJSON, percorsoGiocatoriJSON):
    os.makedirs(percorsoOutput, exist_ok=True)
    driver = impostaDriver()
    soup = ottieniHTML(driver, url)
    salva_tabella_squadre_csv(soup, percorsoSquadre)
    salva_tabella_giocatori_csv(soup, percorsoGiocatori)
    df_squadre = pulisci_tabelle_squadre(percorsoSquadre, percorsoSquadreNuovo)
    df_giocatori = pulisci_tabelle_giocatori(percorsoGiocatori, percorsoGiocatoriNuovo)
    data_squadre = dataFrametoDict(df_squadre)
    data_giocatori = dataFrametoDict(df_giocatori)
    csvToJSON(percorsoSquadreJSON, data_squadre)
    csvToJSON(percorsoGiocatoriJSON, data_giocatori)

#Seria A
url = 'https://fbref.com/it/comp/11/stats/Statistiche-di-Serie-A'
percorsoBase = os.path.abspath(os.path.dirname(__file__))
percorsoOutput = os.path.join(percorsoBase, 'datiSerieA')
percorsoSquadre = os.path.join(percorsoOutput, 'serie_a_squad.csv')
percorsoGiocatori = os.path.join(percorsoOutput, 'serie_a_players.csv')
percorsoSquadreNuovo = os.path.join(percorsoOutput, 'serie_a_squad_mod.csv')
percorsoGiocatoriNuovo = os.path.join(percorsoOutput, 'serie_a_players_mod.csv')
percorsoSquadreJSON = os.path.join(percorsoOutput, 'serie_a_squad_mod.json')
percorsoGiocatoriJSON = os.path.join(percorsoOutput, 'serie_a_players_mod.json')
esegui(url, percorsoOutput, percorsoSquadre, percorsoGiocatori, percorsoSquadreNuovo, percorsoGiocatoriNuovo, percorsoSquadreJSON, percorsoGiocatoriJSON)