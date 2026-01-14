from fastapi import FastAPI, HTTPException, BackgroundTasks
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import FileResponse
from gtts import gTTS
import os
import uuid
from pydub import AudioSegment, effects

app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

TEMP_DIR = "temp_audio"
if not os.path.exists(TEMP_DIR):
    os.makedirs(TEMP_DIR)

def remove_file(path: str):
    if os.path.exists(path):
        os.remove(path)

@app.get("/tts")
async def text_to_speech(background_tasks: BackgroundTasks, text: str, lang: str = "my", speed: float = 1.3):
    if not text:
        raise HTTPException(status_code=400, detail="Text is required")

    file_id = str(uuid.uuid4())
    file_path = os.path.join(TEMP_DIR, f"{file_id}.mp3")

    try:
        # ၁။ gTTS ဖြင့် အသံဖိုင်ထုတ်ယူခြင်း
        tts = gTTS(text=text, lang=lang)
        tts.save(file_path)

        # ၂။ Speed ပြောင်းလဲခြင်း (speed အသေထားချင်ရင် function ထဲမှာ 1.3 လို့ ပြင်ထားနိုင်သည်)
        if abs(speed - 1.0) > 0.01:
            try:
                audio = AudioSegment.from_file(file_path)
                # chunk_size ကို သတ်မှတ်ပေးခြင်းက ပိုပြီး တည်ငြိမ်စေပါသည်
                sped_up = effects.speedup(audio, playback_speed=speed, chunk_size=150, crossfade=25)
                sped_up.export(file_path, format="mp3")
            except Exception as e:
                print(f"Speed adjustment failed: {e}")
        
        background_tasks.add_task(remove_file, file_path)
        return FileResponse(file_path, media_type="audio/mpeg")
    
    except Exception as e:
        if os.path.exists(file_path):
            os.remove(file_path)
        raise HTTPException(status_code=500, detail=str(e))

if __name__ == "__main__":
    import uvicorn
    # Render အတွက် Port ကို dynamic ဖတ်ရန် ပြင်ဆင်ခြင်း
    port = int(os.environ.get("PORT", 8000))
    uvicorn.run(app, host="0.0.0.0", port=port)