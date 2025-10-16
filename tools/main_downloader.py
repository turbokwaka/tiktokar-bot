# main_downloader.py

from yt_dlp.utils import DownloadError, ExtractorError

from tools.image_downloader import download_images
from tools.video_downloader import download_video
from tools.exceptions import NoMediaFoundError, DownloadFailedError


def main_downloader(url: str) -> list[str]:
    """
    Головна функція завантаження.
    Повертає список шляхів до файлів або викликає виняток.
    """
    try:
        video_file = download_video(url)
        if video_file:
            return [video_file]
    except ExtractorError:
        pass
    except DownloadError as e:
        raise DownloadFailedError(f"Помилка завантаження відео: {e}")
    except Exception as e:
        print(f"Неочікувана помилка у video_downloader: {e}")
        pass

    try:
        image_files = download_images(url)
        if image_files:
            return image_files
    except Exception as e:
        raise DownloadFailedError(f"Помилка завантаження зображень: {e}")

    raise NoMediaFoundError("За цим посиланням не вдалося знайти відео або зображення.")
