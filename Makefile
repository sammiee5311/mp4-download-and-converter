create-env:
	python3 -m venv venv

install-dep:
	source venv/bin/activate && \
		pip install requirements.txt

start:
	source venv/bin/activate && \
		python main.py

all: create-env install-dep start