{
 "cells": [
  {
   "cell_type": "markdown",
   "id": "e0960106-ee14-4c1b-9b2a-eec47edb13dc",
   "metadata": {},
   "source": [
    "# FantaHelp: Analisi e Previsione delle Performance dei Giocatori\n",
    "\n",
    "Questo progetto implementa una pipeline di elaborazione dei dati per l'analisi e la previsione delle performance dei calciatori. \n",
    "La pipeline include componenti per la raccolta dei dati, l'addestramento del modello di previsione, e la visualizzazione dei risultati.\n",
    "\n",
    "## Descrizione del Progetto\n",
    "\n",
    "L'obiettivo del progetto **FantaHelp** è quello di aiutare i fantallenatori a prendere decisioni più informate nella scelta dei giocatori, basandosi non solo sui dati storici di gol e assist, ma anche sui **gol e assist attesi**.\n",
    "\n",
    "## Architettura della Pipeline\n",
    "\n",
    "1. **Producer**: Simula la produzione di flussi di dati sui giocatori e le squadre, e invia i dati a Logstash.\n",
    "2. **Logstash**: Sistema di ingestion dei dati per inviarli ai topic Kafka.\n",
    "3. **Kafka**: Broker di messaggi per la gestione dei flussi di dati tra i vari componenti della pipeline.\n",
    "4. **Apache Spark**: Motore di elaborazione dei dati per l'addestramento dei modelli di previsione basati su regressione lineare per i gol e gli assist attesi.\n",
    "5. **Elasticsearch**: Sistema di ricerca e indicizzazione per l'archiviazione dei risultati delle previsioni.\n",
    "6. **Kibana**: Strumento di visualizzazione per esplorare e analizzare i risultati tramite grafici interattivi.\n",
    "\n",
    "## Installazione\n",
    "\n",
    "Per avviare la pipeline, segui questi passaggi:\n",
    "\n",
    "1. Clona il repository\n",
    "2. Dopo esserti posizionato nella cartella corretta, la prima volta avvia il progetto con docker-compose up --build\n",
    "\n",
    "Attenzione: Potrebbe essere necessario scaricare il file \"spark-3.5.4-bin-hadoop3\" ed inserirlo nella cartella setup all'interno della cartella spark\n"
   ]
  }
 ],
 "metadata": {
  "kernelspec": {
   "display_name": "Python 3 (ipykernel)",
   "language": "python",
   "name": "python3"
  },
  "language_info": {
   "codemirror_mode": {
    "name": "ipython",
    "version": 3
   },
   "file_extension": ".py",
   "mimetype": "text/x-python",
   "name": "python",
   "nbconvert_exporter": "python",
   "pygments_lexer": "ipython3",
   "version": "3.12.4"
  }
 },
 "nbformat": 4,
 "nbformat_minor": 5
}
