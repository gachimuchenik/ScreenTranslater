# Python scripts for image translation

## Что можно запустить:

### ClipboardTranslate.py
Получает картинки, переводит их отдает результат перевода в http-endpoint /get_new_text
```
usage: Clipboard Transate [-h] [-c CONFIG_PATH]

Get screenshot from clipboard and translates it.

optional arguments:
  -h, --help            show this help message and exit
  -c CONFIG_PATH, --config-path CONFIG_PATH
  ```

### SingleImage.py
Принимает на вход картинку, переводит её и пишет результат перевода в консоль
```
usage: Translate single image [-h] [-c CONFIG_PATH] input

positional arguments:
  input

optional arguments:
  -h, --help            show this help message and exit
  -c CONFIG_PATH, --config-path CONFIG_PATH
```

## Конфиги запуска
```
[DataGetter] ; параметры получателя картинок, можно получать из буфера обмена либо из папки
type = clipboard ; clipboard или folder

[ClipboardGetter] ; параметры получения картинок из буфера обмена, работает если DataGetter.type = clipboard
use_fake_image_getter = False ; заглушка для дебага, взегда возвращает None

[FolderGetter]  ; параметры получения картинок из буфера обмена, работает если DataGetter.type = folder
folder_path = ./images ; путь к папке с картинками относительно запущенного файла


[Tesseract] ; параметры Tesseract-ocr
tesseract_path = C:\Program Files\Tesseract-OCR\tesseract.exe ; абсолютный путь к исполняемому файлу
tesseract_custom_conf = --psm 11 ; ???

[Preprocessing] ; параметры препроцессинга изображений
coordinates = 250,770,1600,1000 ; координаты вырезаемой области
grayscale_threshold = 200 ; 

[Network] ; параметры вебсервера
host = 127.0.0.1
port = 5000

[System] ; общие системные параметры
;оставь пустым, если хочешь писать в консоль
log_path = log.log ; путь к файлу с логами относительно запущенного файла, если не задано — вывод в консоль
log_level = INFO ; уровень логов
empty_log_on_start = True ; очищать логи при старте

[DataProcessor]
max_buffer_length = 20 ; максимальное число картинок в очереди Processor
```

## Общая схема работы

### Processor

Основной класс обработки -- Processor. В конструкторе принимает 2 параметра, которые определяют его работу:
1. data_getter
    объект класса, в котором есть функция get_data, которая возвращает новые данные
2. data_processor
    объект класса, в котором есть функция process_data, которая как-то обрабатывает данные

Processor читает новые данные из data_getter, кладет в очередь, данные из которой обрабатывает data_processor, результат обработки можно получить вызвав функцию get_processed_data.
