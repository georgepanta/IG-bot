import os
import ffmpeg
import numpy as np
import cv2
from aiogram import Bot, Dispatcher, types
from aiogram.types import InputFile
from moviepy.editor import VideoFileClip, vfx
from pydub import AudioSegment

# Your Telegram bot token (Directly added as requested)
TOKEN = "7592297710:AAEhGzPJnfK5fQhakQYQUzVOaTtwpvYNodc"

bot = Bot(token=TOKEN)
dp = Dispatcher(bot)

# Function to change speed & pitch
def process_video(input_path, output_path, speed=1.0):
    # Adjust video speed
    video = VideoFileClip(input_path)
    new_video = video.fx(vfx.speedx, speed)

    # Adjust audio pitch
    audio = AudioSegment.from_file(input_path)
    new_audio = audio._spawn(audio.raw_data, overrides={"frame_rate": int(audio.frame_rate * speed)})
    new_audio = new_audio.set_frame_rate(audio.frame_rate)

    temp_audio_path = "temp_audio.mp3"
    new_audio.export(temp_audio_path, format="mp3")

    # Save the final video
    new_video.write_videofile(output_path, audio=temp_audio_path, codec="libx264", fps=video.fps)

    os.remove(temp_audio_path)

# Function to mirror video
def mirror_video(input_path, output_path):
    cap = cv2.VideoCapture(input_path)
    fourcc = cv2.VideoWriter_fourcc(*"mp4v")
    out = cv2.VideoWriter(output_path, fourcc, cap.get(cv2.CAP_PROP_FPS),
                          (int(cap.get(cv2.CAP_PROP_FRAME_WIDTH)), int(cap.get(cv2.CAP_PROP_FRAME_HEIGHT))))

    while cap.isOpened():
        ret, frame = cap.read()
        if not ret:
            break
        mirrored_frame = cv2.flip(frame, 1)  # Horizontal flip
        out.write(mirrored_frame)

    cap.release()
    out.release()

# Function to modify HSL and saturation
def adjust_hsl(input_path, output_path, saturation_factor=1.2):
    cap = cv2.VideoCapture(input_path)
    fourcc = cv2.VideoWriter_fourcc(*"mp4v")
    out = cv2.VideoWriter(output_path, fourcc, cap.get(cv2.CAP_PROP_FPS),
                          (int(cap.get(cv2.CAP_PROP_FRAME_WIDTH)), int(cap.get(cv2.CAP_PROP_FRAME_HEIGHT))))

    while cap.isOpened():
        ret, frame = cap.read()
        if not ret:
            break
        hsv = cv2.cvtColor(frame, cv2.COLOR_BGR2HSV)
        hsv[:, :, 1] = np.clip(hsv[:, :, 1] * saturation_factor, 0, 255)  # Adjust saturation
        new_frame = cv2.cvtColor(hsv, cv2.COLOR_HSV2BGR)
        out.write(new_frame)

    cap.release()
    out.release()

@dp.message_handler(content_types=types.ContentType.VIDEO)
async def handle_video(message: types.Message):
    file_id = message.video.file_id
    file_info = await bot.get_file(file_id)
    file_path = file_info.file_path

    input_path = f"downloads/{file_id}.mp4"
    output_path = f"processed/{file_id}.mp4"

    await bot.download_file(file_path, input_path)

    process_video(input_path, output_path, speed=1.1)
    mirror_video(output_path, output_path)
    adjust_hsl(output_path, output_path, saturation_factor=1.1)

    await message.reply_video(InputFile(output_path))

    os.remove(input_path)
    os.remove(output_path)

if __name__ == "__main__":
    from aiogram import executor
    executor.start_polling(dp)
