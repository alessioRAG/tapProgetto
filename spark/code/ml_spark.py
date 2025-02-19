from pyspark.sql import SparkSession
from pyspark.sql.functions import *
from pyspark.sql.types import *
from pyspark.ml.regression import LinearRegression
from pyspark.ml.feature import VectorAssembler
from pyspark.ml import Pipeline
from pyspark.ml.evaluation import RegressionEvaluator

# Inizializzazione della sessione Spark
spark = SparkSession.builder.appName("FantaHelp").getOrCreate()

# Caricamento dei dati dal file JSON
training = spark.read.format("json").options(header='true', inferschema='true', delimiter=",").load("/dataset/output_data/*.json")

training = training.withColumn("xG_per_partita", col("xG") / (col("PG") + 1e-6))
training = training.withColumn("xAG_per_partita", col("xAG") / (col("PG") + 1e-6))

# Feature assembler per i gol
featureassembler_gol = VectorAssembler(
    inputCols=["Reti", "xG_per_partita"],
    outputCol="features_gol"
)

# Feature assembler per gli assist
featureassembler_assist = VectorAssembler(
    inputCols=["Assist", "xAG_per_partita"],
    outputCol="features_assist"
)

# Creazione del modello di regressione lineare
training = training.withColumn(
    "label_gol",
    col("Reti") + (col("xG") / col("PG")) * (38 - col("PG"))
)
training = training.withColumn(
    "label_assist",
    col("Assist") + (col("xAG") / col("PG")) * (38 - col("PG"))
)

# Creazione dei modelli di regressione
lr_gol = LinearRegression(featuresCol="features_gol", labelCol="label_gol", predictionCol="prediction_gol")
lr_assist = LinearRegression(featuresCol="features_assist", labelCol="label_assist", predictionCol="prediction_assist")

# Creazione delle pipeline
pipeline_gol = Pipeline(stages=[featureassembler_gol, lr_gol])
pipeline_assist = Pipeline(stages=[featureassembler_assist, lr_assist])

# Addestramento dei modelli
model_gol = pipeline_gol.fit(training)
model_assist = pipeline_assist.fit(training)

# Previsioni
training_predictions_gol = model_gol.transform(training)
training_predictions_assist = model_assist.transform(training)

# Calcolo RMSE per i gol
evaluator_gol = RegressionEvaluator(labelCol="label_gol", predictionCol="prediction_gol", metricName="rmse")
rmse_gol = evaluator_gol.evaluate(training_predictions_gol)

# Calcolo RMSE per gli assist
evaluator_assist = RegressionEvaluator(labelCol="label_assist", predictionCol="prediction_assist", metricName="rmse")
rmse_assist = evaluator_assist.evaluate(training_predictions_assist)

# Stampa degli errori
print("Root Mean Squared Error (RMSE) per i Gol:", rmse_gol)
print("Root Mean Squared Error (RMSE) per gli Assist:", rmse_assist)

# Salvataggio dei modelli
model_gol.write().overwrite().save("/dataset/model/modello_gol_stagione")
model_assist.write().overwrite().save("/dataset/model/modello_assist_stagione")

# Stop di Spark
spark.stop()