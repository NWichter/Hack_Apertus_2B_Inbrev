.PHONY: run run-local offline-eval build test stop

IMAGE ?= inbrev:latest

run:
	docker compose up --build app

run-local: build
	docker compose --profile local up llm app-local gateway

offline-eval: build
	bash scripts/run_offline_eval.sh

build:
	docker compose build app

test: build
	docker run --rm --network none $(IMAGE) python -m pytest -q -p no:cacheprovider

stop:
	docker compose --profile local down
