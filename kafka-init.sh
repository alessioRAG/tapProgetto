#!/bin/bash

sleep 10

kafka-topics --create --bootstrap-server kafka:9092 --replication-factor 1 --partitions 1 --topic datiRiot || echo "Topic già creato o errore"

exec "$@"