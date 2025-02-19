from pyspark.sql import SparkSession
from pyspark.sql.functions import col, from_json, when, col, expr, to_timestamp
from pyspark.sql.types import IntegerType, FloatType, StringType, StructType, StructField
import shutil
import os
from pyspark.ml import PipelineModel
from elasticsearch import Elasticsearch

def delete_checkpoint_dir(path):
    if os.path.exists(path):
        shutil.rmtree(path)
        
#Configurazione del Kafka e dello schema
kafka_server = "PLAINTEXT://kafka:9092"

"""es = Elasticsearch([{'host': '10.0.100.3', 'port': 9200, 'scheme': 'http'}])
if es.indices.exists(index=elastic_topic):
    es.indices.delete(index=elastic_topic)
    print(f"Indice {elastic_topic} cancellato con successo.")
else:
    print(f"L'indice {elastic_topic} non esiste.")"""

schema_squadre = StructType([
    StructField("Squadra", StringType(), True),
    StructField("PG", StringType(), True),
    StructField("@timestamp", StringType(), True)
])

schema_giocatori = StructType([
    StructField("Giocatore", StringType(), True),
    StructField("Ruolo", StringType(), True),
    StructField("Squadra", StringType(), True),
    StructField("Reti", StringType(), True),
    StructField("Assist", StringType(), True),
    StructField("xG", StringType(), True),
    StructField("xAG", StringType(), True),
    StructField("@timestamp", StringType(), True)
])

#Creazione della sessione Spark
spark = SparkSession.builder \
    .appName("FantaHelp") \
    .config("spark.sql.streaming.checkpointLocation", "/tmp/checkpoints") \
    .getOrCreate()

#Caricamento dei dati da Kafka
df_squadre = spark \
    .readStream \
    .format("kafka") \
    .option("kafka.bootstrap.servers", kafka_server) \
    .option("subscribe", "datiSquadre") \
    .option("startingOffsets", "earliest") \
    .load()

df_giocatori = spark \
    .readStream \
    .format("kafka") \
    .option("kafka.bootstrap.servers", kafka_server) \
    .option("subscribe", "datiGiocatori") \
    .option("startingOffsets", "earliest") \
    .load()

#Conversione dei dati da Kafka in formato JSON con schema
df_squadre = df_squadre.selectExpr("CAST(value AS STRING) as json") \
    .select(from_json(col("json"), schema_squadre).alias("data")) \
    .select("data.*")

df_giocatori = df_giocatori.selectExpr("CAST(value AS STRING) as json") \
    .select(from_json(col("json"), schema_giocatori).alias("data")) \
    .select("data.*")

df_squadre = df_squadre.withColumn("PG", 
                   when(col("PG").rlike("^\d+$"), col("PG").cast(IntegerType()))
                   .otherwise(0))

df_giocatori = df_giocatori.withColumn("Reti", 
                   when(col("Reti").rlike("^\d+$"), col("Reti").cast(IntegerType()))
                   .otherwise(0))

df_giocatori = df_giocatori.withColumn("Assist", 
                   when(col("Assist").rlike("^\d+$"), col("Assist").cast(IntegerType())) 
                   .otherwise(0))

df_giocatori = df_giocatori.withColumn("xG", 
                   when(col("xG").rlike("^\d+(\.\d+)?$"), col("xG").cast(FloatType()))
                   .otherwise(0.0))

df_giocatori = df_giocatori.withColumn("xAG", 
                   when(col("xAG").rlike("^\d+(\.\d+)?$"), col("xAG").cast(FloatType())) 
                   .otherwise(0.0))

df_squadre = df_squadre.withColumnRenamed("@timestamp","squadreTimestamp")
df_giocatori = df_giocatori.withColumnRenamed("@timestamp","giocatoriTimestamp")
df_squadre = df_squadre.withColumn("squadreTimestamp", to_timestamp(col("squadreTimestamp")))
df_giocatori = df_giocatori.withColumn("giocatoriTimestamp", to_timestamp(col("giocatoriTimestamp")))

df_squadreWithWatermark = df_squadre.withWatermark("squadreTimestamp", "30 minutes")
df_giocatoriWithWatermark = df_giocatori.withWatermark("giocatoriTimestamp", "30 minutes")

df_giocatoriWithWatermark = df_giocatoriWithWatermark.withColumnRenamed("Squadra", "SquadraGiocatori")

serving=df_squadreWithWatermark.alias("squadre").join(
    df_giocatoriWithWatermark.alias("giocatori"),
    expr("""
        squadre.Squadra = giocatori.SquadraGiocatori AND
        squadre.squadreTimestamp <= giocatori.giocatoriTimestamp AND
        giocatori.giocatoriTimestamp <= squadre.squadreTimestamp + interval 10 seconds
    """)
)

serving = serving.withColumn("xG_per_partita", col("xG") / (col("PG") + 1e-6))
serving = serving.withColumn("xAG_per_partita", col("xAG") / (col("PG") + 1e-6))

if os.path.exists("/dataset/output_data"):
    shutil.rmtree("/dataset/output_data")

if os.path.exists("/dataset/checkpoints"):
    shutil.rmtree("/dataset/checkpoints")

"""query = serving \
    .writeStream \
    .format("json") \   #usata per l'addestramento
    .outputMode("append") \
    .option("path", "/dataset/output_data") \
    .option("checkpointLocation", "/dataset/checkpoints") \
    .start()
query.awaitTermination()"""

modelPath_gol = "/dataset/model/modello_gol_stagione"
modelPath_assist = "/dataset/model/modello_assist_stagione"

model_gol = PipelineModel.load(modelPath_gol)  #carico il modello
model_assist = PipelineModel.load(modelPath_assist)  #carico il modello

#applica il modello al dataset di input 
predictDf_gol = model_gol.transform(serving).select('Giocatore','Ruolo','Squadra','Reti','xG', 'prediction_gol')
predictDf_assist = model_assist.transform(serving).select('Giocatore','Ruolo', 'Squadra','Assist','xAG', 'prediction_assist')

#mando ad elastic
delete_checkpoint_dir("/dataset/gol/checkpoints")
delete_checkpoint_dir("/dataset/assist/checkpoints")

query_elastic_gol = predictDf_gol \
    .writeStream \
    .format("org.elasticsearch.spark.sql") \
    .option("checkpointLocation", "/dataset/gol/checkpoints") \
    .option("es.nodes", "10.0.100.24") \
    .option("es.port", "9200") \
    .option("es.nodes.wan.only", "true") \
    .option("es.index.auto.create", "true") \
    .start("fantahelp")

query_elastic_assist = predictDf_assist \
    .writeStream \
    .format("org.elasticsearch.spark.sql") \
    .option("checkpointLocation", "/dataset/assist/checkpoints") \
    .option("es.nodes", "10.0.100.24") \
    .option("es.port", "9200") \
    .option("es.nodes.wan.only", "true") \
    .option("es.index.auto.create", "true") \
    .start("fantahelp")

query_elastic_gol.awaitTermination()
query_elastic_assist.awaitTermination()