install:
	pip install -r requirements.txt

download:
	python -m src.download --ini 2025-01 --fim 2025-12

clean:
	python -m src.clean

aggregate:
	python -m src.aggregate

load:
	python -m src.db

all: download clean aggregate load

sample:
	python -m src.make_sample && python -m src.clean && python -m src.aggregate

test:
	pytest -q

api:
	uvicorn src.api.main:app --host 0.0.0.0 --port 8000

.PHONY: install download clean aggregate load all sample test api
