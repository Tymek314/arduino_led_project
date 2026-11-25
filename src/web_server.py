from fastapi import FastAPI, Request
from fastapi.responses import HTMLResponse
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
from fastapi import WebSocket
import asyncio

import threading
import soundcard as sc
import py_loader
import audio
from pydantic import BaseModel

app = FastAPI()

app.mount(
    "/static",
    StaticFiles(directory="static"),
    name="static"
)

templates = Jinja2Templates(directory="templates")

audio_thread = None
audio_stop_event = threading.Event()
selected_speaker = None
audio_mode = 0  # 0: off, 1: led, 2: web visualizer, 3: both


class AudioSettings(BaseModel):
    speaker: str
    audio_mode: int = 0
    connection_started: bool = False


def ensure_audio_running():
    global audio_thread
    if audio_thread is not None and audio_thread.is_alive():
        return False

    audio_stop_event.clear()
    audio_thread = threading.Thread(
        target=audio.run_audio,
        args=(audio_stop_event,),
        name="audio-analyzer",
        daemon=True,
    )
    audio_thread.start()
    return True


@app.get("/")
async def home(request: Request):
    return templates.TemplateResponse(
        request=request,
        name="index.html",
        context={}
    )


@app.post("/startconnection")
def start_conn():
    py_loader.start_connection()
    return {"status": "connected"}


@app.post("/startled")
def start_led():
    global audio_mode
    if audio_thread is not None and audio_thread.is_alive():
        if audio_mode == 0:
            audio_mode = 1
        elif audio_mode == 2:
            audio_mode = 3
        return {"status": "already_running"}

    if audio_mode == 0:
        audio_mode = 1
    elif audio_mode == 2:
        audio_mode = 3
    ensure_audio_running()
    return {"status": "ready"}


@app.post("/stopled")
def stop_led():
    global audio_mode
    audio_stop_event.set()
    if audio_mode == 1:
        audio_mode = 0
    elif audio_mode == 3:
        audio_mode = 2
    return {"status": "stopping"}


@app.post("/startvisualizer")
def start_visualizer():
    global audio_mode
    if audio_thread is not None and audio_thread.is_alive():
        if audio_mode == 0:
            audio_mode = 2
        elif audio_mode == 1:
            audio_mode = 3
        return {"status": "already_running"}

    if audio_mode == 0:
        audio_mode = 2
    elif audio_mode == 1:
        audio_mode = 3
    ensure_audio_running()
    return {"status": "ready"}


@app.post("/stopvisualizer")
def stop_visualizer():
    global audio_mode
    audio_stop_event.set()
    if audio_mode == 2:
        audio_mode = 0
    elif audio_mode == 3:
        audio_mode = 1
    return {"status": "stopping"}


@app.get("/speakers")
def get_speakers():
    speakers = sc.all_speakers()
    return [{"name": speaker.name} for speaker in speakers]


@app.post("/settings")
def update_settings(settings: AudioSettings):
    global selected_speaker
    selected_speaker = settings.speaker
    return {"status": "success", "speaker": selected_speaker}

@app.websocket("/ws")
async def websocket_endpoint(websocket: WebSocket):
    await websocket.accept()
    while True:
        data = {
            "left": audio.band_magnitudeL,
            "right": audio.band_magnitudeR,
            "cur_selected": [audio.Lbass, audio.Rbass, audio.cur_max_L, audio.cur_max_R]
        }
        await websocket.send_json(data)
        await asyncio.sleep(0.02)
