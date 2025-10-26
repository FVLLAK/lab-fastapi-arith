-include .env
PYTHON ?= python
PIP ?= pip
APP ?= src.app.main:app
HOST ?= 0.0.0.0
PORT ?= 8000
IMAGE_NAME ?= lab1
CONTAINER_NAME ?= lab1

.PHONY: setup test run docker-build docker-run docker-stop docker-push watch watch-git
setup: ; $(PYTHON) -m venv .venv && . .venv/bin/activate && $(PIP) install -r requirements.txt
test: ; pytest -q
run: ; uvicorn $(APP) --host $(HOST) --port $(PORT)
docker-build: ; docker build -t $(IMAGE_NAME):latest .
docker-run: docker-stop ; docker run -d --rm --name $(CONTAINER_NAME) -p $(PORT):8000 $(IMAGE_NAME):latest
docker-stop: ; -docker rm -f $(CONTAINER_NAME)
docker-push: ; echo "$$DOCKERHUB_TOKEN" | docker login -u "$$DOCKERHUB_USERNAME" --password-stdin && docker tag "$(IMAGE_NAME):latest" "$(IMAGE_NAME):$(IMAGE_TAG)" && docker push "$(IMAGE_NAME):latest" && docker push "$(IMAGE_NAME):$(IMAGE_TAG)"
watch: ; IMAGE_NAME=$(IMAGE_NAME) PORT=$(PORT) CONTAINER_NAME=$(CONTAINER_NAME) bash scripts/watch_build_deploy.sh
watch-git: ; IMAGE_NAME=$(IMAGE_NAME) PORT=$(PORT) CONTAINER_NAME=$(CONTAINER_NAME) bash scripts/watch_git_build_deploy.sh
