.PHONY: run run-local build test offline-check eval triage-seed stop

IMAGE ?= inbrev:latest

run:
	docker compose up --build app

run-local:
	LLM_BASE_URL=http://llm:8080/v1 docker compose --profile local up --build

build:
	docker compose build app

test: build
	docker run --rm --network none $(IMAGE) python -m pytest -q

offline-check: build
	docker run --rm --network none $(IMAGE) sh -c "python -m pytest -q && python -m inbrev eval data/seed/messages.seed.jsonl --baselines"

eval: build
	docker run --rm --network none $(IMAGE) python -m inbrev eval data/seed/messages.seed.jsonl --baselines

triage-seed: build
	docker compose run --rm app python -m inbrev triage data/seed/messages.seed.jsonl --out /app/runs/seed.jsonl

stop:
	docker compose down
