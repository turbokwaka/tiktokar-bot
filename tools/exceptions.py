class DownloaderError(Exception):
    """Базовий клас для помилок завантажувача."""

    pass


class NoMediaFoundError(DownloaderError):
    """Викликається, коли за посиланням не знайдено медіа."""

    pass


class DownloadFailedError(DownloaderError):
    """Викликається, коли завантаження зазнало невдачі з технічних причин."""

    pass
