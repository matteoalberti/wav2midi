import os
import tempfile
import subprocess
from pathlib import Path

import torch
import torchaudio
import librosa
import numpy as np
import pretty_midi
import streamlit as st
from streamlit_elements import elements, mui, html

# ----------- CONFIG -----------
TITLE = "🎧 Audio to Drum MIDI Converter"
DESCRIPTION = "Upload a song, extract drums, convert to MIDI."
UPLOAD_EXTENSIONS = [".mp3", ".wav", ".flac"]

# ----------- UTILS -----------
def extract_drums(input_audio_path, output_dir):
    """
    Use Demucs to isolate drum track from input audio.
    """
    result = subprocess.run([
        "python3", "-m", "demucs", "--two-stems=drums", "--out", output_dir, input_audio_path
    ], capture_output=True)
    if result.returncode != 0:
        raise RuntimeError("Demucs failed: " + result.stderr.decode())

    song_name = Path(input_audio_path).stem
    return os.path.join(output_dir, "htdemucs", song_name, "drums.wav")

def audio_to_midi(audio_path, midi_out_path):
    y, sr = librosa.load(audio_path, sr=22050)
    onset_env = librosa.onset.onset_strength(y=y, sr=sr)
    onset_frames = librosa.onset.onset_detect(onset_envelope=onset_env, sr=sr)
    onset_times = librosa.frames_to_time(onset_frames, sr=sr)

    pm = pretty_midi.PrettyMIDI()
    drum = pretty_midi.Instrument(program=0, is_drum=True)
    for onset in onset_times:
        note = pretty_midi.Note(velocity=100, pitch=38, start=onset, end=onset + 0.1)
        drum.notes.append(note)
    pm.instruments.append(drum)
    pm.write(midi_out_path)

# ----------- STREAMLIT UI WITH ELEMENTS -----------
st.set_page_config(page_title=TITLE, layout="wide")

with elements("main"):
    mui.Typography(TITLE, variant="h4", sx={"mb": 2})
    mui.Typography(DESCRIPTION, variant="body1", sx={"mb": 4})

    uploaded_file = st.file_uploader("Upload a song file", type=[ext.strip(".") for ext in UPLOAD_EXTENSIONS])

    if uploaded_file:
        with mui.Alert("Processing audio... this may take up to 1 minute", severity="info"):
            with tempfile.TemporaryDirectory() as tmpdir:
                input_path = os.path.join(tmpdir, uploaded_file.name)
                with open(input_path, "wb") as f:
                    f.write(uploaded_file.read())

                try:
                    drums_path = extract_drums(input_path, tmpdir)
                    midi_path = os.path.join(tmpdir, "output.mid")
                    audio_to_midi(drums_path, midi_path)

                    mui.Alert("MIDI file generated successfully!", severity="success")
                    with open(midi_path, "rb") as f:
                        st.download_button("Download Drum MIDI", f, file_name="drums.mid", mime="audio/midi")
                except Exception as e:
                    mui.Alert(f"Something went wrong: {e}", severity="error")

    html.hr()
    html.p("Built with Demucs, Librosa, and PrettyMIDI", style={"fontSize": "0.9rem", "color": "gray"})