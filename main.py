import argparse
import asyncio
import aiofiles
import logging
from pathlib import Path
import shutil
from watchdog.observers import Observer
from watchdog.events import FileSystemEventHandler

# Логування
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s]: %(message)s",
    handlers=[
        logging.FileHandler("file_sorter.log"),
        logging.StreamHandler()
    ]
)

# Створення папки за розширенням
async def ensure_folder(output_folder: Path, extension: str):
    target_folder = output_folder / (extension.lstrip('.') if extension else 'no_extension')
    target_folder.mkdir(parents=True, exist_ok=True)
    return target_folder

# Копіювання файлу
async def copy_file(file: Path, target_folder: Path):
    try:
        target_path = target_folder / file.name
        shutil.copy(file, target_path)
        logging.info(f"Copied: {file} → {target_path}")
    except Exception as e:
        logging.error(f"Failed to copy {file}: {e}")

# Читання папки
async def read_folder(source_folder: Path, output_folder: Path):
    tasks = []

    for file in source_folder.rglob('*'):
        if file.is_file():
            extension = file.suffix.lower() or "no_extension"
            target_folder = await ensure_folder(output_folder, extension)
            tasks.append(copy_file(file, target_folder))

    if tasks:
        await asyncio.gather(*tasks)

# Моніторингу змін у папці
class FolderHandler(FileSystemEventHandler):
    def __init__(self, source_folder: Path, output_folder: Path):
        self.source_folder = source_folder
        self.output_folder = output_folder

    def on_created(self, event):
        if event.is_directory:
            return
        file_path = Path(event.src_path)
        logging.info(f"New file detected: {file_path}")
        asyncio.run(self.process_file(file_path))

    async def process_file(self, file_path: Path):
        extension = file_path.suffix.lower() or "no_extension"
        target_folder = await ensure_folder(self.output_folder, extension)
        await copy_file(file_path, target_folder)

# Основна функція
async def main():
    parser = argparse.ArgumentParser(description="Asynchronously sort files by extension with monitoring.")
    parser.add_argument('source', type=str, help="Source folder path")
    parser.add_argument('output', type=str, help="Output folder path")
    args = parser.parse_args()

    source_folder = Path(args.source)
    output_folder = Path(args.output)

    if not source_folder.exists() or not source_folder.is_dir():
        logging.error("Source folder does not exist or is not a directory.")
        return

    output_folder.mkdir(parents=True, exist_ok=True)
    await read_folder(source_folder, output_folder)

    # Моніторинг змін (Watchdog)
    event_handler = FolderHandler(source_folder, output_folder)
    observer = Observer()
    observer.schedule(event_handler, path=str(source_folder), recursive=True)
    observer.start()
    logging.info("Monitoring started. Press Ctrl+C to stop.")

    try:
        while True:
            await asyncio.sleep(1)
    except KeyboardInterrupt:
        observer.stop()
        logging.info("Monitoring stopped.")

    observer.join()

if __name__ == "__main__":
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        logging.warning("Process interrupted by user.")