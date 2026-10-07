install:
	pip install -r requirements.txt
download:
	python -m src.download --ini 2023-01 --fim 2024-12
clean:
	python -m src.clean
aggregate:
	python -m src.aggregate
all: download clean aggregate
sample:
	python -m src.make_sample && python -m src.clean && python -m src.aggregate
test:
	pytest -q
api:
	uvicorn src.api.main:app --host 0.0.0.0 --port 8000 --reload
app:
	streamlit run src/app/Home.py --server.port 8501 --server.address 0.0.0.0
