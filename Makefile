DCO_YAML := ./docker/docker-compose.yml
DCO_CMD := docker-compose -f $(DCO_YAML) --project-directory .

.PHONY: help
help:
	@echo "********************************"
	@echo "LOOKER SCRIPTS\n"
	@echo "Usage"
	@echo "  - run\t\tstart the client container"
	@echo "  - status\tsee running containers"
	@echo "  - build\tbuild the image"
	@echo "********************************"

.PHONY: run
run:
	@ $(DCO_CMD) run --rm looker-api-client bash

.PHONY: ps
ps:
	@ $(DCO_CMD) ps

.PHONY: status
status: ps

.PHONY: build
build:
	@ $(DCO_CMD) build
