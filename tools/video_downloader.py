import yt_dlp
import uuid
from pathlib import Path


def download_video(url: str) -> str | None:
    try:
        Path("../temp").mkdir(exist_ok=True)
        random_filename = str(uuid.uuid4())

        if "music.youtube.com" in url:
            ydl_opts = {
                "outtmpl": f"temp/{random_filename}.%(ext)s",
                "format": "bestaudio/best",
                "postprocessors": [
                    {
                        "key": "FFmpegExtractAudio",
                        "preferredcodec": "mp3",
                        "preferredquality": "192",
                    }
                ],
            }
        else:
            ydl_opts = {
                "outtmpl": f"temp/{random_filename}.%(ext)s",
                "format": "bestvideo[ext=mp4]+bestaudio[ext=m4a]/best[ext=mp4]/best",
            }

        with yt_dlp.YoutubeDL(ydl_opts) as ydl:
            info = ydl.extract_info(url, download=False)
            filename = ydl.prepare_filename(info)

            if "music.youtube.com" in url:
                filename = Path(filename).with_suffix(".mp3").as_posix()

            ydl.download([url])

            return filename

    # Потім якось визначу яка саме помилка тут ловиться.
    except Exception as e:
        print(f"❌ Не вдалося завантажити медіа. Помилка: {e}")
        return None
