ifndef VERSION
export VERSION=$(shell python3 -m versioningit)
endif
export TAG=$(shell echo $(VERSION) | cut -d+ -f1 | sed "s/\.dev/-dev/")

DOCKER?=docker
TARGET=industrial-jitterdebugger
PYTHON_TARGET=industrial_jitterdebugger

.PHONY: version
version:
	@echo "VERSION=$(VERSION)"
	@echo "TAG=$(TAG)"

# ensure that we're in a venv
venv:
	@test -n "${VIRTUAL_ENV}" || (echo "need a venv"; exit 1)

dev: venv
	pip install build uv versioningit
	uv pip install -r pyproject.toml

.PHONY: lint
lint:
	flake8 $(PYTHON_TARGET)

.PHONY: update
update: venv
	uv pip install --upgrade -r pyproject.toml
	uv pip freeze --exclude-editable > requirements.txt

.PHONY: wheel
wheel: venv
	rm -rf build
	uv build -b requirements.txt --wheel
	@echo "=============================="
	@echo "Check for updated dependencies"
	@echo "=============================="
	uv pip freeze --exclude-editable > requirements_current.txt
	uv pip install --upgrade -r pyproject.toml
	uv pip freeze --exclude-editable > requirements_latest.txt
	if ! diff -q requirements_current.txt requirements_latest.txt ; then \
	  @echo "INFO: there are updated dependencies (not included in this build):"; \
	  diff --color -u requirements_current.txt requirements_latest.txt || true; \
	fi

.PHONY: docker
docker: version wheel
	cp dist/$(PYTHON_TARGET)-$(VERSION)*.whl docker/
	cd docker && $(DOCKER) build --build-arg VERSION=$(VERSION) -t $(TARGET):$(TAG) .

.PHONY: compose-up
compose-up: docker
	docker compose -f app/$(TARGET)/docker-compose.yml up

.PHONY: compose-down
compose-down:
	docker compose -f app/$(TARGET)/docker-compose.yml down

.PHONY: app
app: version docker
	go run github.com/thediveo/tiap/cmd/tiap@latest -i -o $(TARGET)_$(TAG).app --app-version $(TAG) app
