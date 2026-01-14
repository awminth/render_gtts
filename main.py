from fastapi import FastAPI, HTTPException, BackgroundTasks
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import FileResponse
from gtts import gTTS
import os
import uuid

app = FastAPI()

# React ကနေ လှမ်းခေါ်လို့ရအောင် ခွင့်ပြုပေးခြင်း
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"], # Production မှာဆိုရင် React ရဲ့ URL (e.g. localhost:3000) ပဲ ထည့်ပါ
    allow_methods=["*"],
    allow_headers=["*"],
)

TEMP_DIR = "temp_audio"
if not os.path.exists(TEMP_DIR):
    os.makedirs(TEMP_DIR)

def remove_file(path: str):
    """အသံဖိုင် ပေးပို့ပြီးရင် ပြန်ဖျက်ပေးမယ့် function"""
    if os.path.exists(path):
        os.remove(path)

@app.get("/tts")
async def text_to_speech(background_tasks: BackgroundTasks, text: str, lang: str = "my", speed: float = 1.15):
    if not text:
        raise HTTPException(status_code=400, detail="Text is required")

    try:
        file_id = str(uuid.uuid4())
        file_path = os.path.join(TEMP_DIR, f"{file_id}.mp3")
        
        # gTTS အသုံးပြုခြင်း
        tts = gTTS(text=text, lang=lang)
        tts.save(file_path)

        # အသံကို ဆင့်နှုန်း တစ်ဆင့်မြန်အောင် ပြင်ချင်ရင် `speed` param (1.0 = normal)
        try:
            # speed ကို ရိုးရိုး သတ်မှတ်ထားခြင်း - 0.5 .. 3.0 အတွင်းသိမ်း
            if speed is None:
                speed = 1.0
            speed = float(speed)
            if speed <= 0:
                speed = 1.0
            if 0.5 <= speed <= 3.0 and abs(speed - 1.0) > 1e-6:
                try:
                    from pydub import AudioSegment, effects

                    audio = AudioSegment.from_file(file_path)
                    # pydub.effects.speedup preserves pitch better than simple frame_rate change
                    sped = effects.speedup(audio, playback_speed=speed)
                    sped.export(file_path, format="mp3")
                except Exception:
                    # If pydub/ffmpeg not available or fails, ignore and return original file
                    pass
        except Exception:
            pass
        
        # ဖိုင်ပို့ပြီးတာနဲ့ နောက်ကွယ်မှာ ပြန်ဖျက်ခိုင်းခြင်း (Storage မပြည့်အောင်)
        background_tasks.add_task(remove_file, file_path)
        
        return FileResponse(file_path, media_type="audio/mpeg")
    
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)