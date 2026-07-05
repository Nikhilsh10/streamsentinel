.PHONY: up down restart logs kafka-ui reset-offsets generate-data train

up:
	docker-compose up -d

down:
	docker-compose down -v

restart:
	docker-compose restart

logs:
	docker-compose logs -f

kafka-ui:
	@echo "Kafka UI available at http://localhost:8080"

reset-offsets:
	docker-compose exec kafka kafka-consumer-groups --bootstrap-server localhost:9092 --group anomaly-detectors-v1 --reset-offsets --to-latest --execute --all-topics

generate-data:
	python scripts/generate_training_data.py

train:
	python scripts/train_isolation_forest.py
	python scripts/train_autoencoder.py
	python scripts/evaluate_models.py
