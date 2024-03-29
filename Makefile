# Arguments to use the overriden docker-compose file
PROD_COMPOSE_ARGS := -f docker-compose.yml \
		-f docker-compose.production.yml

DEV_COMPOSE_ARGS := -f docker-compose.yml \
		-f docker-compose.development.yml

LINT_COMPOSE_ARGS := -f docker-compose.lint.yml \
		-p anti-poaching-lint

TEST_COMPOSE_ARGS := -f docker-compose.yml \
		-f docker-compose.test.yml

# The services that will be built and pushed all the time
SERVICES := api web
PUSH_SERVICES := api analytics-cli web
TEST_SERVICES := api
LINT_SERVICES := api-lint analytics-lint
IMAGES := $(addprefix pig208/anti-poaching-,$(addsuffix -dev,$(SERVICES)) $(addsuffix -prod,$(SERVICES)))
LATEST_IMAGES := $(addsuffix \:latest,$(IMAGES))
OPENAPI := http://api:8000/openapi.json

IMAGE_REVISION ?= 046a321
CLIENT_VERSION ?= 0.0.5
THIS_FILE := $(lastword $(MAKEFILE_LIST))
SECRETS_DIR := secrets
SECRET_NAMES := pg_password pg_user
DEV_SECRETS := $(addprefix $(SECRETS_DIR)/dev/,$(SECRET_NAMES))
PROD_SECRETS := $(addprefix $(SECRETS_DIR)/prod/,$(SECRET_NAMES))

export DOCKER_BUILDKIT = 1
export COMPOSE_DOCKER_CLI_BUILD = 1
export REVISION = $(IMAGE_REVISION)
export COMPOSE_IGNORE_ORPHANS = True

help:
	@echo "make build - Build all dependencies"
	@echo "make push-latest - Push and update the docker registry"
	@echo "make run-dev - Run the dev build"
	@echo "make run-prod - Run the prod build"
	@echo 'make MESSAGE="migration revision message" generate-migration - Auto generate a new alembic migration'

build: build-prod build-dev build-lint build-client build-analytics-cli

all-secrets: $(PROD_SECRETS) $(DEV_SECRETS)

$(SECRETS_DIR):
	mkdir -p secrets

$(SECRETS_DIR)/%: $(SECRETS_DIR)
	mkdir -p $@

$(DEV_SECRETS): $(SECRETS_DIR)/dev
	export TMP=$@; echo test$${TMP##*/} > $@

$(PROD_SECRETS): $(SECRETS_DIR)/prod
	export TMP=$@; echo test$${TMP##*/} > $@

.PHONY: build-dev
build-dev:
	@echo "Building dev revision ${REVISION}"
	docker compose $(DEV_COMPOSE_ARGS) build $(SERVICES) --parallel

.PHONY: build-prod
build-prod:
	@echo "Building prod revision ${REVISION}"
	docker compose $(PROD_COMPOSE_ARGS) build $(SERVICES) --parallel

.PHONY: build-lint
build-lint:
	docker compose $(LINT_COMPOSE_ARGS) build $(LINT_SERVICES) --parallel

.PHONY: build-client
build-client:
	@mkdir -p client
	docker compose $(DEV_COMPOSE_ARGS) build client builder

.PHONY: build-analytics-cli
build-analytics-cli:
	docker compose $(DEV_COMPOSE_ARGS) build analytics-cli

.PHONY: update-revision
update-revision:
	@set -e; \
		NEW_REVISION=$$(git rev-parse --short HEAD); \
		sed -i "0,/IMAGE_REVISION ?= */{s/IMAGE_REVISION ?= .*/IMAGE_REVISION ?= $${NEW_REVISION}/}" $(THIS_FILE); \
		test $${NEW_REVISION} = $(IMAGE_REVISION) && echo "revision unchanged" || echo "$(IMAGE_REVISION) => $${NEW_REVISION}"

.PHONY: generate-migration
generate-migration:
	docker compose ${DEV_COMPOSE_ARGS} run api alembic revision --autogenerate -m "$(MESSAGE)"

.PHONY: generate-client
generate-client:
	docker compose $(DEV_COMPOSE_ARGS) run --rm client \
		generate -i $(OPENAPI) -g python -o /client/home \
		--additional-properties=generateSourceCodeOnly=true,packageVersion=$(CLIENT_VERSION)
	docker compose $(DEV_COMPOSE_ARGS) run --rm builder

.PHONY: upload-client
upload-client: client/dist/*$(CLIENT_VERSION)*
	docker compose $(DEV_COMPOSE_ARGS) run --rm builder twine upload dist/*$(CLIENT_VERSION)*
	
.PHONY: push
push:
	@echo pushing $(REVISION)
	docker compose $(DEV_COMPOSE_ARGS) push $(PUSH_SERVICES)
	docker compose $(PROD_COMPOSE_ARGS) push $(PUSH_SERVICES)

$(LATEST_IMAGES):
	@echo $@ | docker tag $$(sed "s/latest/$(REVISION)/") $@

tag-latest: $(LATEST_IMAGES)  # Tag latest images assuming images of the current revision all exist

.PHONY: push-latest
push-latest:
	@$(MAKE) -f $(THIS_FILE) build
	@$(MAKE) -f $(THIS_FILE) tag-latest
	@$(MAKE) -f $(THIS_FILE) push
	@IMAGE_REVISION=latest $(MAKE) -f $(THIS_FILE) push

.PHONY: bump-image
bump-revision:
	git add $(THIS_FILE)
	git commit -m "docker: Bump image revision"

.PHONY: run-dev
run-dev: $(DEV_SECRETS)
	docker compose $(DEV_COMPOSE_ARGS) up -d --force-recreate $(SERVICES)

.PHONY: run-dev-interactive
run-dev-interactive: $(DEV_SECRETS)
	docker compose $(DEV_COMPOSE_ARGS) up api

.PHONY: inspect-dev-db
inspect-dev-db: $(DEV_SECRETS)
	docker compose $(DEV_COMPOSE_ARGS) run db bash

.PHONY: run-tests
run-tests: $(DEV_SECRETS)
	@echo Preparing tests... Please make sure that the dev services are running
	docker compose $(TEST_COMPOSE_ARGS) run $(TEST_SERVICES) pytest -vvv

.PHONY: run-tests-no-tty
run-tests-no-tty: $(DEV_SECRETS)
	@echo Preparing tests... Please make sure that the dev services are running
	docker compose $(TEST_COMPOSE_ARGS) run -T $(TEST_SERVICES) pytest -vvv

.PHONY: run-prod
run-prod: $(PROD_SECRETS)
	docker compose $(PROD_COMPOSE_ARGS) up -d $(SERVICES)

.PHONY: run-lint
run-lint:
	docker compose $(LINT_COMPOSE_ARGS) up $(LINT_SERVICES)

.PHONY: run-analytics-analyze
run-analytics-analyze:
	docker compose $(DEV_COMPOSE_ARGS) run --rm analytics-cli analytics.analyze \
		$(TARGET) --out analytics/data/output.json \
		--host nlp

.PHONY: run-analytics-sync
run-analytics-sync:
	docker compose $(DEV_COMPOSE_ARGS) run --rm analytics-cli analytics.sync \
		analyzed analytics/data/output.json

.PHONY: run-nlp
run-nlp:
	docker compose $(DEV_COMPOSE_ARGS) up -d nlp

.PHONY: clean-containers
clean-containers:
	docker compose down
	docker compose $(DEV_COMPOSE_ARGS) rm
	docker compose $(PROD_COMPOSE_ARGS) rm
	docker compose $(LINT_COMPOSE_ARGS) rm

.PHONY: clean-db
clean-db:
	docker compose down db
	docker volume rm anti-poaching-platform_pgdata
	docker volume rm anti-poaching-platform_pgdataprod

.PHONY: clean-dist
clean-dist:
	rm -rf client/dist client/passerine_client.egg-info
