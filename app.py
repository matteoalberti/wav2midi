import os
import tempfile
import subprocess
from pathlib import Path

import numpy as np
import torch
import torchaudio
import pretty_midi
import streamlit as st
from streamlit_elements import elements, mui, html
import scipy.io.wavfile as wav
from scipy.signal import find_peaks
from scipy.ndimage import gaussian_filter1d

# ----------- CONFIG -----------
TITLE = "🥁 WAV to Drum MIDI + Evaluation"
DESCRIPTION = "Upload a song and (optionally) its MIDI drum file for comparison."
UPLOAD_EXTENSIONS = [".mp3", ".wav", ".flac"]
MIDI_EXTENSIONS = [".mid", ".midi"]

# ----------- UTILS -----------
def extract_drums(input_audio_path, output_dir):
    result = subprocess.run([
        "python3", "-m", "demucs", "--two-stems=drums", "--out", output_dir, input_audio_path
    ], capture_output=True)
    if result.returncode != 0:
        raise RuntimeError("Demucs failed: " + result.stderr.decode())

    song_name = Path(input_audio_path).stem
    return os.path.join(output_dir, "htdemucs", song_name, "drums.wav")

def audio_to_midi_smart(audio_path, midi_out_path):
    sr, y = wav.read(audio_path)
    if len(y.shape) > 1:
        y = y.mean(axis=1)
    y = y / np.max(np.abs(y))
    envelope = np.abs(y)
    smoothed = gaussian_filter1d(envelope, sigma=1000)
    peaks, _ = find_peaks(smoothed, height=0.02, distance=sr*0.1)
    onset_times = peaks / sr

    pm = pretty_midi.PrettyMIDI()
    drum = pretty_midi.Instrument(program=0, is_drum=True)
    for onset in onset_times:
        note = pretty_midi.Note(velocity=100, pitch=38, start=onset, end=onset + 0.1)
        drum.notes.append(note)
    pm.instruments.append(drum)
    pm.write(midi_out_path)

def evaluate_generated_vs_reference(gen_midi_path, ref_midi_path):
    try:
        gen = pretty_midi.PrettyMIDI(gen_midi_path)
        ref = pretty_midi.PrettyMIDI(ref_midi_path)

        gen_times = sorted([note.start for inst in gen.instruments for note in inst.notes])
        ref_times = sorted([note.start for inst in ref.instruments for note in inst.notes])

        if not ref_times:
            return "Reference MIDI has no notes."

        tolerance = 0.1  # seconds
        matched = sum(any(abs(g - r) <= tolerance for r in ref_times) for g in gen_times)
        recall = matched / len(ref_times) * 100 if ref_times else 0
        precision = matched / len(gen_times) * 100 if gen_times else 0

        return f"Precision: {precision:.1f}%\nRecall: {recall:.1f}%\nMatched Notes: {matched}/{len(ref_times)}"
    except Exception as e:
        return f"Error comparing MIDI files: {e}"

# ----------- STREAMLIT UI -----------
st.set_page_config(page_title=TITLE, layout="wide")

with elements("main"):
    mui.Typography(TITLE, variant="h4", sx={"mb": 2})
    mui.Typography(DESCRIPTION, variant="body1", sx={"mb": 4})

    uploaded_audio = st.file_uploader("Upload a song file", type=[ext.strip(".") for ext in UPLOAD_EXTENSIONS])
    uploaded_midi = st.file_uploader("(Optional) Upload reference MIDI for evaluation", type=[ext.strip(".") for ext in MIDI_EXTENSIONS])

    if uploaded_audio:
        with mui.Alert("Processing audio...", severity="info"):
            with tempfile.TemporaryDirectory() as tmpdir:
                input_path = os.path.join(tmpdir, uploaded_audio.name)
                with open(input_path, "wb") as f:
                    f.write(uploaded_audio.read())

                ref_midi_path = None
                if uploaded_midi:
                    ref_midi_path = os.path.join(tmpdir, uploaded_midi.name)
                    with open(ref_midi_path, "wb") as f:
                        f.write(uploaded_midi.read())

                try:
                    drums_path = extract_drums(input_path, tmpdir)
                    midi_path = os.path.join(tmpdir, "output.mid")
                    audio_to_midi_smart(drums_path, midi_path)

                    mui.Alert("✅ MIDI file generated successfully!", severity="success")
                    with open(midi_path, "rb") as f:
                        st.download_button("Download Generated MIDI", f, file_name="drums.mid", mime="audio/midi")

                    if ref_midi_path:
                        result = evaluate_generated_vs_reference(midi_path, ref_midi_path)
                        st.markdown("### 🎯 Evaluation vs Reference MIDI")
                        st.code(result)

                except Exception as e:
                    mui.Alert(f"❌ Something went wrong: {e}", severity="error")

    html.hr()
    html.p("Built with Demucs, scipy, and PrettyMIDI", style={"fontSize": "0.9rem", "color": "gray"})
