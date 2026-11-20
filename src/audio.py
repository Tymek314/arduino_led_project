import soundcard as sc
import numpy as np
import threading
import py_loader
import web_server

# my speakers:
# speaker = sc.get_speaker("Speakers (Realtek(R) Audio)")
# speaker = sc.get_speaker("Plantronics C420-M")
# speaker = sc.get_speaker("Headphones (Meow)")

# to find your speakers run print(sc.all_speakers())

sample_rate: int = 48000
sample_size: int = int(sample_rate * 0.02)

band_magnitudeL = []
band_magnitudeR = []
cur_max_L: int = None
cur_max_r: int = None
Lbass: int = None
Rbass: int = None

band_edges: list[int] = [10, 25, 40, 50, 63, 80, 100, 125, 160, 200, 250, 315, 400, 500, 630, 750, 900, 1500, 2800, 3600, 5000]
band_colors: list[str] = [ #has to be exactly 3 digits on 0-255 scale for R, G, B
    "255,000,000",
    "255,128,000",
    "255,255,000",
    "128,255,000",
    "000,255,000",
    "000,255,128",
    "000,255,255",
    "000,192,255",
    "000,000,255",
    "128,000,255",
    "255,000,255",
    "255,105,180",
    "220,020,060",
    "255,215,000",
    "000,128,128",
    "000,000,128",
    "128,000,128",
    "165,042,042",
    "128,128,128",
    "255,255,255"]

audio_buffer = np.zeros((sample_size * 4, 2))
window = np.hanning(sample_size * 4)

def add_block(band_magnitudeL, band_magnitudeR, band_colors):
    py_loader.list_L = []
    py_loader.list_R = []
    cur_max_L = band_magnitudeL.index(max(band_magnitudeL))
    for i in range(0, int(max(band_magnitudeL) /sum(band_magnitudeL) *7)):
        py_loader.list_L.append(band_colors[cur_max_L])
    cur_max_R = band_magnitudeR.index(max(band_magnitudeR))
    for i in range(0, int(max(band_magnitudeR) /sum(band_magnitudeR) *7)):
        py_loader.list_R.append(band_colors[cur_max_R])
    return cur_max_L, cur_max_R


def do_bassss(band_magnitudeL, band_magnitudeR):
    if max(band_magnitudeL[0:4]) > 0 and sum(band_magnitudeL) > 0:
        Lbass = max(band_magnitudeL[0:4])
        py_loader.brightness_L = f"{int((Lbass/sum(band_magnitudeL)) *200) +1:03d}"
    if max(band_magnitudeR[0:4]) > 0 and sum(band_magnitudeR) > 0:
        Rbass = max(band_magnitudeR[0:4])
        py_loader.brightness_R = f"{int((Rbass/sum(band_magnitudeR)) *200) +1:03d}"
    return Lbass, Rbass


def run_audio(stop_event):
    speaker = sc.get_speaker(web_server.selected_speaker)
    global band_magnitudeL, band_magnitudeR
    while not stop_event.is_set():
        with sc.get_microphone(id=str(speaker.name), include_loopback=True).recorder(samplerate=sample_rate) as recorder:
            audio = recorder.record(numframes=sample_size)

        audio_buffer[:-sample_size] = audio_buffer[sample_size:]
        audio_buffer[-sample_size:] = audio

        windowed_L = audio_buffer[:, 0] *window
        windowed_R = audio_buffer[:, 1] *window

        freqs = np.fft.rfftfreq(len(audio_buffer.mean(axis=1)), d=1/sample_rate)
        mag_L = np.abs(np.fft.rfft(windowed_L))
        mag_R = np.abs(np.fft.rfft(windowed_R))
        
        mask = (freqs >= band_edges[0]) & (freqs <= band_edges[-1])
        freqs = freqs[mask]
        mag_L = mag_L[mask]
        mag_R = mag_R[mask]
        
        band_magnitudeL = []
        band_magnitudeR = []

        for i in range(len(band_edges) - 1):
            lo, hi = band_edges[i], band_edges[i + 1]
            idx = (freqs >= lo) & (freqs <= hi)

            band_magnitudeL.append(
                mag_L[idx].mean() if mag_L[idx].size else 0.0
            )
            band_magnitudeR.append(
                mag_R[idx].mean() if mag_R[idx].size else 0.0
            )

        if max(band_magnitudeR) > 0 and max(band_magnitudeL) > 0:
            cur_max_L, cur_max_R = do_bassss(band_magnitudeL, band_magnitudeR)
            Lbass, Rbass = add_block(band_magnitudeL[4:], band_magnitudeR[4:], band_colors)
            if web_server.audio_mode == 1 or web_server.audio_mode == 3:
                py_loader.load_pixels()
    pass


if __name__ == "__main__":

    import threading

    stop_event = threading.Event()

    run_audio(stop_event)
