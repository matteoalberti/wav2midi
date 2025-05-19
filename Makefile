VENV=wav2midi

init:
	python3 -m venv $(VENV)
	source $(VENV)/bin/activate && \
	pip install --upgrade pip && \
	pip install torch torchaudio --index-url https://download.pytorch.org/whl/cpu && \
	pip install -r requirements.txt --no-deps

run:
	source $(VENV)/bin/activate && \
	streamlit run app.py

share:
	ngrok http 8501

clean:
	rm -rf $(VENV)
	find . -type d -name "__pycache__" -exec rm -r {} +