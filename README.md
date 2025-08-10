## FrameView → Flourish data builder

Small toolkit to convert NVIDIA FrameView logs into a Flourish-ready wide CSV for “Bar chart race” and other timeline-style visualizations.

### Features
- Combine multiple FrameView per-frame logs into one CSV (one row per test)
- Choose metric:
  - avg_fps (default, from display time)
  - present_fps (from MsBetweenPresents)
  - display_fps (from MsBetweenDisplayChange)
  - column:<ExactHeader> (e.g., column:GPU0Util(%)) averaged per second
- FPS modes:
  - per-frame-mean: average FPS per second using 1000 × frames / sum(ms)
  - count: frames per second (useful for debugging or variable refresh capture)
- Compare mode: two logs → adds a third row with per‑second % difference relative to the first
- Streams large CSVs; bins by whole seconds from each run’s first timestamp
- Trims all rows to the shortest run length (as in “Graphs data manager”)

### GUI
1. Pick input directory (default `in`), optionally adjust glob
2. Select one or more logs
3. Choose metric (or “custom column”) and FPS mode
4. Optionally enable Compare (exactly two logs), choose “difference only”
5. Choose output path and Generate

### Flourish import
1. Create a “Bar chart race” visualization
2. Go to Data → Upload and select the generated CSV
3. Ensure first column is bound as name/category; remaining columns as timeline
4. Adjust “Timeline duration” to match the seconds of your test scene

References:
- Graphs data manager behavior and workflow: [PC‑01: Graphs data manager](https://pc-01.tech/graphs-data-manager/)
- Flourish data binding/help: [Flourish Help Center](https://helpcenter.flourish.studio/hc/en-us/articles/8761545383183-Adding-data-to-a-template?utm_source=openai)

### Compare mode
- A/B testing of drivers, game patches, settings, overclocks, or hardware
- Works with any metric; the % difference row shows `100 * (B/A − 1)` per second relative to baseline A

### Handling different run lengths
- Each run starts at its own first `TimeInSeconds`
- Frames are binned into whole‑second buckets (0–1s → “1”, etc.)
- All rows are truncated to the shortest common length so timelines align

### Known limitations
- Decimal parsing expects `.`; if locale uses `,`, it is auto‑handled in most cases

---

## Конвертер данных FrameView → Flourish

Набор инструментов для преобразования логов NVIDIA FrameView в CSV‑файл формата Flourish (“Bar chart race” и другие таймлайн‑шаблоны). В комплекте CLI и графический интерфейс (Tkinter).

### Возможности
- Объединение нескольких логов в один CSV (каждая строка — отдельный тест)
- Выбор метрики:
  - avg_fps (по умолчанию, на основе времени отображения кадра)
  - present_fps (на основе MsBetweenPresents)
  - display_fps (на основе MsBetweenDisplayChange)
  - column:<ИмяКолонки> (например, column:GPU0Util(%)) — среднее значение за секунду
- Режимы FPS:
  - per-frame-mean: среднее FPS за секунду как 1000 × кадры / сумма(мс)
  - count: количество кадров в секунду
- Режим сравнения: два лога → третья строка с %‑разницей по секундам относительно первого
- Потоковая обработка больших CSV; группировка по секундам от первого кадра
- Усечение всех рядов до длины самого короткого теста (как в “Graphs data manager”)

### Графический интерфейс (GUI)
1. Выберите папку с логами (по умолчанию `in`), при необходимости укажите шаблон (glob)
2. Отметьте нужные файлы
3. Выберите метрику (или “custom column”) и режим FPS
4. При необходимости включите сравнение (строго 2 лога), можно оставить только строку разницы
5. Укажите путь сохранения и нажмите Generate

### Импорт в Flourish
1. Создайте визуализацию “Bar chart race”
2. Вкладка Data → Upload, загрузите созданный CSV
3. Первая колонка — имя/категория, остальные — шаги таймлайна
4. В настройках выставьте длительность таймлайна в секундах

Ссылки:
- Описание и логика “Graphs data manager”: [PC‑01: Graphs data manager](https://pc-01.tech/graphs-data-manager/)
- Справка по загрузке данных в Flourish: [Flourish Help Center](https://helpcenter.flourish.studio/hc/en-us/articles/8761545383183-Adding-data-to-a-template?utm_source=openai)

### Для чего нужен режим сравнения
- A/B сравнение драйверов, патчей, настроек, разгона, железа
- Работает с любой метрикой; строка %‑разницы считает `100 * (B/A − 1)` по каждой секунде относительно A

### Разная длина тестов
- Старт от первого `TimeInSeconds` в каждом логе
- Группировка кадров по целым секундам (0–1s → “1”, и т.д.)
- Усекаем до самого короткого теста, чтобы синхронизировать таймлайны

### Ограничения
- Десятичный разделитель — точка; запятая обрабатывается автоматически в большинстве случаев


