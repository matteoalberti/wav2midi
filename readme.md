# 🥁 Audio to Drum MIDI Converter

Converti una canzone audio in un file MIDI contenente la traccia di batteria.  
Utilizza **Demucs** per isolare la batteria e una pipeline basata su **Librosa** e **PrettyMIDI** per generare il file `.mid`.  
Interfaccia realizzata con **Streamlit Elements**.

---

## 🚀 Come usare (Mac, Linux, Windows)

### 1. Clona il repo e crea un ambiente virtuale:
```bash
git clone https://github.com/tuo-user/wav2midi.git
cd wav2midi
python3 -m venv wav2midi
source wav2midi/bin/activate  # su macOS/Linux
```

### 2. Installa le dipendenze:
```bash
pip install --upgrade pip
pip install torch torchaudio --index-url https://download.pytorch.org/whl/cpu
pip install -r requirements.txt --no-deps
```

### 3. Avvia l'app:
```bash
streamlit run app.py
```

### 4. (Facoltativo) Condividi con un amico usando ngrok:
```bash
ngrok http 8501
```

---

## 🎧 Esempio di test input

Puoi usare loop di batteria royalty-free da:
- https://www.looperman.com/loops/cats/free-drum-loops-samples-sounds-wavs-download
- https://orangefreesounds.com/loops/drum-loops/

Cerca file `.wav` con batteria chiara e regolare, es: 90–100 BPM.

---

## ⚙️ Tecnologie usate
- [Demucs](https://github.com/facebookresearch/demucs)
- [Librosa](https://librosa.org/)
- [PrettyMIDI](https://github.com/craffel/pretty-midi)
- [Streamlit Elements](https://github.com/okld/streamlit-elements)

---

## 📂 Output
- File `.mid` contenente la **traccia percussiva isolata**
- Note su canale MIDI per drumkit standard (kick/snare/hi-hat)

---

## 🛠 Makefile disponibile

Per velocizzare:
```bash
make init     # crea e installa ambiente wav2midi
make run      # avvia l'app
make share    # apre ngrok su porta 8501
make clean    # pulizia ambiente
```

---

## 📥 Input supportato
- `.mp3`, `.wav`, `.flac`

---

## ✅ Output atteso
- File `drums.mid` scaricabile dopo l’elaborazione