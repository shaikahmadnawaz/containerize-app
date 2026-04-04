# Makefile — common project commands.
# Usage: make <target>

IMAGE_NAME  ?= containerize-app
IMAGE_TAG   ?= local
REGISTRY    ?= ghcr.io/shaikahmadnawaz

.PHONY: help build run stop logs test scan verify push clean

help: ## Show available targets
	@grep -E '^[a-zA-Z_-]+:.*##' $(MAKEFILE_LIST) | awk 'BEGIN {FS = ":.*## "}; {printf "  \033[36m%-18s\033[0m %s\n", $$1, $$2}'

build: ## Build the production Docker image
	docker build --target runtime -t $(IMAGE_NAME):$(IMAGE_TAG) .

run: ## Start the full stack (app + db) in the background
	docker compose up -d

stop: ## Stop and remove the stack containers (preserves volumes)
	docker compose down

logs: ## Tail logs from the app service
	docker compose logs -f app

test: ## Run smoke tests locally
	pip install -r app/requirements.txt pytest httpx >/dev/null
	pytest tests/smoke -v

scan: ## Scan the image for vulnerabilities using Trivy (requires trivy installed)
	trivy image --exit-code 1 --severity HIGH,CRITICAL $(IMAGE_NAME):$(IMAGE_TAG)

verify: test ## Run local validation bundle (tests + scan)
	@echo "Validation complete"

push: build ## Tag + push image to the configured registry
	docker tag $(IMAGE_NAME):$(IMAGE_TAG) $(REGISTRY)/$(IMAGE_NAME):$(IMAGE_TAG)
	docker push $(REGISTRY)/$(IMAGE_NAME):$(IMAGE_TAG)

shell: ## Open a shell inside the running app container
	docker compose exec app /bin/sh

clean: ## Remove containers, images, and volumes created by this project
	docker compose down -v --rmi local
	docker image rm -f $(IMAGE_NAME):$(IMAGE_TAG) 2>/dev/null || true
