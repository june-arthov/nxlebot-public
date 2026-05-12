# OC+ Runtime Cloud — Makefile

.PHONY: build-sandbox run-api test clean

build-sandbox:
	docker build -t ocp-sandbox:latest ./sandbox

run-api:
	cd api && uvicorn main:app --reload --host 0.0.0.0 --port 8000

test:
	curl -X POST http://localhost:8000/execute \
		-H "Content-Type: application/json" \
		-d '{"script": "echo \"Hello OC+ Cloud!\"\nset NAME = \"Nyx\"\necho \"Hi $NAME\""}'

clean:
	docker rmi ocp-sandbox:latest 2>/dev/null || true
	rm -rf __pycache__ */__pycache__
