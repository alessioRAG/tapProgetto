# FantaHelp: Analisi e Previsione delle Performance dei Giocatori

Questo progetto implementa una pipeline di elaborazione dei dati per l'analisi e la previsione delle performance dei calciatori. 
La pipeline include componenti per la raccolta dei dati, l'addestramento del modello di previsione, e la visualizzazione dei risultati.

## Descrizione del Progetto

L'obiettivo del progetto **FantaHelp** è quello di aiutare i fantallenatori a prendere decisioni più informate nella scelta dei giocatori, basandosi non solo sui dati storici di gol e assist, ma anche sui **gol e assist attesi**.

## Architettura della Pipeline

1. **Producer**: Simula la produzione di flussi di dati sui giocatori e le squadre, e invia i dati a Logstash.
2. **Logstash**: Sistema di ingestion dei dati per inviarli ai topic Kafka.
3. **Kafka**: Broker di messaggi per la gestione dei flussi di dati tra i vari componenti della pipeline.
4. **Apache Spark**: Motore di elaborazione dei dati per l'addestramento dei modelli di previsione basati su regressione lineare per i gol e gli assist attesi.
5. **Elasticsearch**: Sistema di ricerca e indicizzazione per l'archiviazione dei risultati delle previsioni.
6. **Kibana**: Strumento di visualizzazione per esplorare e analizzare i risultati tramite grafici interattivi.

## Installazione

Per avviare la pipeline, segui questi passaggi:

1. Clona il repository
2. Dopo esserti posizionato nella cartella corretta, la prima volta avvia il progetto con docker-compose up --build

Attenzione: Potrebbe essere necessario scaricare il file "spark-3.5.4-bin-hadoop3" ed inserirlo nella cartella setup all'interno della cartella spark
