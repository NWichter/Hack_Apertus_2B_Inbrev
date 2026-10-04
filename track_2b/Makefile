.PHONY: run run-local offline-eval build test offline-check eval triage-seed stop

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

offline-check: build
	docker run --rm --network none $(IMAGE) sh -c "python -m pytest -q -p no:cacheprovider && python -m inbrev eval data/seed/messages.seed.jsonl --baselines"

eval: build
	docker run --rm --network none $(IMAGE) python -m inbrev eval data/seed/messages.seed.jsonl --baselines

triage-seed: build
	docker compose run --rm app python -m inbrev triage data/seed/messages.seed.jsonl --out /app/runs/seed.jsonl

stop:
	docker compose --profile local down
