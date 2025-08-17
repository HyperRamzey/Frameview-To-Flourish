import tkinter as tk
from tkinter import filedialog, messagebox, simpledialog
from pathlib import Path
from typing import List, Tuple

from flourish_maker import (
    MetricKind,
    compute_difference_series,
    compute_per_second_series,
    discover_input_files,
    trim_csv_passthrough,
    write_flourish_wide_csv,
)


LANG_TEXTS = {
    "en": {
        "title": "FrameView → Flourish CSV Builder",
        "language": "Language:",
        "input_dir": "Input directory",
        "browse": "Browse…",
        "glob": "Glob pattern:",
        "refresh": "Refresh",
        "select_logs": "Select logs (multiple allowed)",
        "select_all": "Select all",
        "clear": "Clear",
        "metric": "Metric",
        "type": "Type:",
        "custom_header": "Custom header:",
        "fps_mode": "FPS mode:",
        "fps_per_mean": "Per-frame mean",
        "fps_count": "Count",
        "compare": "Compare mode (exactly 2 logs)",
        "enable_compare": "Enable compare",
        "diff_only": "Difference only row",
        "output": "Output",
        "generate": "Generate",
        "status_found": "Found {n} file(s)",
        "status_compare": "Compare mode: select exactly 2 logs",
        "err_scan": "Failed to scan directory",
        "err_need_two": "Compare mode requires exactly 2 selected logs",
        "err_select_one": "Select at least one log to process",
        "done_file": "File written:",
        "metric_opts": [
            ("Average FPS (display)", "avg_fps"),
            ("Present FPS", "present_fps"),
            ("Display FPS", "display_fps"),
            ("Custom column…", "__custom__"),
        ],
        "fps_opts": [
            ("Per-frame mean", "per-frame-mean"),
            ("Count", "count"),
        ],
        "tt_dir": "Folder with FrameView CSV logs (e.g., in)",
        "tt_glob": "Optional file pattern (e.g., FrameView_*Log.csv)",
        "tt_files": "Select any combination of logs to include",
        "tt_select_all": "Select all listed logs",
        "tt_clear": "Clear the selection",
        "tt_metric_type": (
            "Metric selection:\n"
            "- Average FPS (display): time‑weighted FPS per second using "
            "MsBetweenDisplayChange (1000×frames/sum_ms).\n"
            "- Present FPS: uses MsBetweenPresents (same formula).\n"
            "- Display FPS: explicit display‑time FPS.\n"
            "- Custom column: averages the chosen numeric CSV header per second."
        ),
        "tt_custom": (
            "Exact CSV header name. The value is averaged per second.\n"
            "Example: GPU0Util(%)"
        ),
        "tt_fps_mode": (
            "Per‑frame mean: time‑weighted FPS per second = "
            "1000×frames/sum_ms.\n"
            "Count: number of frames/presents per second (not FPS)."
        ),
        "tt_enable_compare": (
            "Enable A/B compare. Select exactly two logs. Adds a third row with "
            "per‑second % difference relative to the first: 100×(B/A − 1)."
        ),
        "tt_diff_only": "Output only the % difference row (no originals)",
        "tt_output": "Destination CSV file path",
        "tt_generate": "Create Flourish CSV",
        "trim": "Trim",
        "trim_start": "Start (sec):",
        "trim_end": "End (sec):",
        "trim_configure": "Configure…",
        "trim_title": "Configure Trim Settings",
        "trim_global": "Apply to all selected files",
        "trim_individual": "Configure individually",
        "trim_per_file": "Per-file Settings",
        "tt_trim": (
            "Trim seconds from the beginning and end of data. "
            "Click Configure to set per-file settings."
        ),
        "trim_passthrough": "Trim File",
        "tt_trim_passthrough": "Create trimmed copy of this file without conversion",
        "rename_title": "Rename label",
        "rename_prompt": (
            "Enter name of column (label) for:\n{file}\n"
            "Leave empty for default: {default}"
        ),
    },
    "ru": {
        "title": "FrameView → Конвертер в Flourish CSV",
        "language": "Язык:",
        "input_dir": "Папка с логами",
        "browse": "Выбрать…",
        "glob": "Шаблон файлов:",
        "refresh": "Обновить",
        "select_logs": "Выберите логи (можно несколько)",
        "select_all": "Выделить все",
        "clear": "Снять выделение",
        "metric": "Метрика",
        "type": "Тип:",
        "custom_header": "Произвольная колонка:",
        "fps_mode": "Режим FPS:",
        "fps_per_mean": "Среднее по кадрам",
        "fps_count": "Количество кадров",
        "compare": "Сравнение (ровно 2 лога)",
        "enable_compare": "Включить сравнение",
        "diff_only": "Только строка разницы",
        "output": "Выходной файл",
        "generate": "Сформировать",
        "status_found": "Найдено файлов: {n}",
        "status_compare": "Режим сравнения: выберите ровно 2 лога",
        "err_scan": "Не удалось прочитать папку",
        "err_need_two": "Для сравнения нужно выбрать ровно 2 лога",
        "err_select_one": "Выберите хотя бы один лог",
        "done_file": "Файл создан:",
        "metric_opts": [
            ("Средний FPS (display)", "avg_fps"),
            ("FPS по Present", "present_fps"),
            ("FPS по Display", "display_fps"),
            ("Произвольная колонка…", "__custom__"),
        ],
        "fps_opts": [
            ("Среднее по кадрам", "per-frame-mean"),
            ("Количество кадров", "count"),
        ],
        "tt_dir": "Папка с CSV логами FrameView (например, in)",
        "tt_glob": "Необязательный шаблон (например, FrameView_*Log.csv)",
        "tt_files": "Выберите нужные логи",
        "tt_select_all": "Выделить все файлы",
        "tt_clear": "Очистить выбор",
        "tt_metric_type": (
            "Выбор метрики:\n"
            "- Средний FPS (display): средневзвешенный по времени FPS за секунду "
            "по MsBetweenDisplayChange (1000×кадры/сумма мс).\n"
            "- FPS по Present: MsBetweenPresents (та же формула).\n"
            "- FPS по Display: явный расчёт по времени отображения.\n"
            "- Произвольная колонка: среднее значение выбранной колонки за секунду."
        ),
        "tt_custom": (
            "Точное имя колонки CSV. Значение усредняется за секунду.\n"
            "Пример: GPU0Util(%)"
        ),
        "tt_fps_mode": (
            "Среднее по кадрам: 1000×кадры/сумма мс за секунду.\n"
            "Количество кадров: число презентов в секунду (не FPS)."
        ),
        "tt_enable_compare": (
            "A/B сравнение. Выберите ровно 2 лога. Добавит третью строку "
            "с %‑разницей по секундам относительно первого: 100×(B/A − 1)."
        ),
        "tt_diff_only": "Вывести только строку %‑разницы (без исходных рядов)",
        "tt_output": "Путь к результирующему CSV",
        "tt_generate": "Создать Flourish CSV",
        "trim": "Обрезка",
        "trim_start": "Начало (сек):",
        "trim_end": "Конец (сек):",
        "trim_configure": "Настроить…",
        "trim_title": "Настройки обрезки",
        "trim_global": "Применить ко всем выбранным файлам",
        "trim_individual": "Настроить индивидуально",
        "trim_per_file": "Настройки для каждого файла",
        "tt_trim": (
            "Обрезать секунды с начала и конца данных. "
            "Нажмите Настроить для индивидуальных настроек."
        ),
        "trim_passthrough": "Обрезать файл",
        "tt_trim_passthrough": "Создать обрезанную копию файла без конвертации",
        "rename_title": "Переименовать подпись",
        "rename_prompt": (
            "Введите имя колонки (подписи) для:\n{file}\n"
            "Оставьте пустым для значения по умолчанию: {default}"
        ),
    },
}


class Tooltip:
    def __init__(self, widget: tk.Widget, text: str, delay_ms: int = 600) -> None:
        self.widget = widget
        self.text = text
        self.delay_ms = delay_ms
        self._after_id = None
        self._tip = None
        widget.bind("<Enter>", self._on_enter)
        widget.bind("<Leave>", self._on_leave)

    def _on_enter(self, _event: tk.Event) -> None:  # type: ignore[name-defined]
        self._after_id = self.widget.after(self.delay_ms, self._show)

    def _on_leave(self, _event: tk.Event) -> None:  # type: ignore[name-defined]
        if self._after_id is not None:
            self.widget.after_cancel(self._after_id)
            self._after_id = None
        self._hide()

    def _show(self) -> None:
        if self._tip is not None:
            return
        x = self.widget.winfo_rootx() + 20
        y = self.widget.winfo_rooty() + self.widget.winfo_height() + 10
        tip = tk.Toplevel(self.widget)
        self._tip = tip
        self._tip.wm_overrideredirect(True)
        self._tip.configure(bg="#2d2d30")
        label = tk.Label(
            self._tip,
            text=self.text,
            bg="#2d2d30",
            fg="#d4d4d4",
            padx=8,
            pady=4,
            justify="left",
            wraplength=360,
        )
        label.pack()
        self._tip.wm_geometry(f"+{x}+{y}")

    def _hide(self) -> None:
        if self._tip is not None:
            self._tip.destroy()
            self._tip = None


def apply_dark_theme(root: tk.Tk) -> None:
    bg = "#1e1e1e"
    fg = "#d4d4d4"
    root.configure(bg=bg)
    try:
        root.option_add("*Background", bg)
        root.option_add("*Foreground", fg)
        root.option_add("*Entry.Background", "#252526")
        root.option_add("*Entry.Foreground", fg)
        root.option_add("*Entry.InsertBackground", fg)
        root.option_add("*Listbox.Background", "#252526")
        root.option_add("*Listbox.Foreground", fg)
        root.option_add("*Button.Background", "#3c3c3c")
        root.option_add("*Button.Foreground", fg)
        root.option_add("*Toplevel*Background", "#2d2d30")
    except Exception:
        pass


class TrimConfigDialog(tk.Toplevel):
    def __init__(self, parent: tk.Tk, selected_files: List[Path], 
                 trim_settings: dict, t: dict) -> None:
        super().__init__(parent)
        self.parent = parent
        self.selected_files = selected_files
        self.trim_settings = trim_settings
        self.t = t
        self.entries: dict[str, Tuple[tk.Entry, tk.Entry]] = {}
        
        self.title(self.t["trim_title"])
        self.geometry("600x400")
        self.resizable(True, True)
        
        # Make dialog modal
        self.transient(parent)
        self.grab_set()
        
        self._build_dialog()
        
        # Center on parent
        self.geometry("+%d+%d" % (
            parent.winfo_rootx() + 50,
            parent.winfo_rooty() + 50
        ))

    def _build_dialog(self) -> None:
        # Instructions
        instruction = tk.Label(
            self, 
            text="Configure trim settings for each selected file:",
            font=("TkDefaultFont", 10, "bold")
        )
        instruction.pack(pady=10)
        
        # Scrollable frame for file settings
        canvas = tk.Canvas(self)
        scrollbar = tk.Scrollbar(self, orient="vertical", command=canvas.yview)
        scrollable_frame = tk.Frame(canvas)
        
        scrollable_frame.bind(
            "<Configure>",
            lambda e: canvas.configure(scrollregion=canvas.bbox("all"))
        )
        
        canvas.create_window((0, 0), window=scrollable_frame, anchor="nw")
        canvas.configure(yscrollcommand=scrollbar.set)
        
        # Headers
        header_frame = tk.Frame(scrollable_frame)
        header_frame.pack(fill="x", padx=10, pady=5)
        
        tk.Label(header_frame, text="File", width=40, anchor="w").grid(
            row=0, column=0, sticky="w"
        )
        tk.Label(header_frame, text=self.t["trim_start"], width=12).grid(
            row=0, column=1
        )
        tk.Label(header_frame, text=self.t["trim_end"], width=12).grid(
            row=0, column=2
        )
        tk.Label(header_frame, text="Action", width=12).grid(
            row=0, column=3
        )
        
        # File entries
        for i, file_path in enumerate(self.selected_files):
            file_frame = tk.Frame(scrollable_frame)
            file_frame.pack(fill="x", padx=10, pady=2)
            
            # Get current settings or defaults
            file_key = str(file_path)
            if file_key in self.trim_settings:
                start_val, end_val = self.trim_settings[file_key]
            else:
                start_val, end_val = 0.0, 0.0
            
            # File name
            tk.Label(
                file_frame, 
                text=file_path.name, 
                width=40, 
                anchor="w"
            ).grid(row=0, column=0, sticky="w")
            
            # Start trim entry
            start_var = tk.DoubleVar(value=start_val)
            start_entry = tk.Entry(file_frame, textvariable=start_var, width=10)
            start_entry.grid(row=0, column=1, padx=5)
            
            # End trim entry  
            end_var = tk.DoubleVar(value=end_val)
            end_entry = tk.Entry(file_frame, textvariable=end_var, width=10)
            end_entry.grid(row=0, column=2, padx=5)
            
            # Trim passthrough button
            trim_btn = tk.Button(
                file_frame,
                text=self.t["trim_passthrough"],
                command=lambda fp=file_path, se=start_entry, ee=end_entry: 
                self._trim_file_passthrough(fp, se, ee)
            )
            trim_btn.grid(row=0, column=3, padx=5)
            Tooltip(trim_btn, self.t["tt_trim_passthrough"])
            
            self.entries[file_key] = (start_entry, end_entry)
        
        canvas.pack(side="left", fill="both", expand=True, padx=10)
        scrollbar.pack(side="right", fill="y")
        
        # Buttons
        button_frame = tk.Frame(self)
        button_frame.pack(fill="x", padx=10, pady=10)
        
        tk.Button(
            button_frame, 
            text="OK", 
            command=self._save_settings
        ).pack(side="right", padx=5)
        
        tk.Button(
            button_frame, 
            text="Cancel", 
            command=self.destroy
        ).pack(side="right", padx=5)
        
        tk.Button(
            button_frame, 
            text="Reset All", 
            command=self._reset_all
        ).pack(side="left", padx=5)

    def _save_settings(self) -> None:
        # Save all settings
        for file_key, (start_entry, end_entry) in self.entries.items():
            try:
                start_val = float(start_entry.get())
                end_val = float(end_entry.get())
                if start_val >= 0 and end_val >= 0:
                    self.trim_settings[file_key] = (start_val, end_val)
            except ValueError:
                pass  # Skip invalid entries
        self.destroy()

    def _reset_all(self) -> None:
        # Reset all entries to 0
        for start_entry, end_entry in self.entries.values():
            start_entry.delete(0, tk.END)
            start_entry.insert(0, "0.0")
            end_entry.delete(0, tk.END)
            end_entry.insert(0, "0.0")

    def _trim_file_passthrough(self, file_path: Path, start_entry: tk.Entry, 
                              end_entry: tk.Entry) -> None:
        """Trim a single file and save as new CSV without conversion."""
        try:
            start_val = float(start_entry.get())
            end_val = float(end_entry.get())
            
            if start_val < 0 or end_val < 0:
                messagebox.showerror("Error", "Trim values must be non-negative")
                return
            
            # Generate output filename
            stem = file_path.stem
            suffix = file_path.suffix
            if start_val > 0 or end_val > 0:
                trim_suffix = f"_trim_{start_val:.1f}s_{end_val:.1f}s"
            else:
                trim_suffix = "_trim"
            output_path = file_path.parent / f"{stem}{trim_suffix}{suffix}"
            
            # Perform the trim
            success = trim_csv_passthrough(
                file_path, output_path, start_val, end_val
            )
            
            if success:
                messagebox.showinfo(
                    "Success", 
                    f"Trimmed file saved as:\n{output_path.name}"
                )
            else:
                messagebox.showerror(
                    "Error", 
                    "Failed to trim file. Check that the file has valid time data."
                )
                
        except ValueError:
            messagebox.showerror("Error", "Invalid trim values entered")


class App(tk.Tk):
    def __init__(self) -> None:
        super().__init__()
        # Language state
        self.lang = "en"
        self.t = LANG_TEXTS[self.lang]
        apply_dark_theme(self)
        self.title(self.t["title"])
        self.geometry("1024x700")
        try:
            self.state("zoomed")
        except Exception:
            pass

        # Inputs state
        self.dir_var = tk.StringVar(value=str(Path("in").resolve()))
        self.glob_var = tk.StringVar(value="*.csv")
        # Initialize with localized labels
        default_metric_label = LANG_TEXTS[self.lang]["metric_opts"][0][0]
        self.metric_choice_var = tk.StringVar(value=default_metric_label)
        self.custom_column_var = tk.StringVar(value="GPU0Util(%)")
        default_fps_label = LANG_TEXTS[self.lang]["fps_opts"][0][0]
        self.fps_mode_var = tk.StringVar(value=default_fps_label)
        self.compare_mode_var = tk.BooleanVar(value=False)
        self.difference_only_var = tk.BooleanVar(value=False)
        self.output_var = tk.StringVar(value=str(Path("flourish_out.csv").resolve()))
        
        # Trim settings
        self.trim_start_var = tk.DoubleVar(value=0.0)
        self.trim_end_var = tk.DoubleVar(value=0.0)
        # Per-file trim settings: file_path -> (start_sec, end_sec)
        self.trim_settings: dict[str, Tuple[float, float]] = {}

        self._build_ui()
        self._refresh_file_list()

    def _build_ui(self) -> None:
        # Language selector
        topbar = tk.Frame(self)
        topbar.pack(fill="x", padx=10, pady=(10, 0))
        tk.Label(topbar, text=self.t["language"]).pack(side="left")
        self.lang_var = tk.StringVar(value=self.lang)
        lang_menu = tk.OptionMenu(
            topbar, self.lang_var, "en", "ru", command=self._switch_lang
        )
        lang_menu.pack(side="left", padx=8)
        Tooltip(lang_menu, "Switch UI language / Переключить язык")

        # Directory chooser
        dir_frame = tk.LabelFrame(self, text=self.t["input_dir"])
        dir_frame.pack(fill="x", padx=10, pady=8)

        tk.Entry(dir_frame, textvariable=self.dir_var).pack(
            side="left", fill="x", expand=True, padx=(8, 4), pady=8
        )
        tk.Button(dir_frame, text=self.t["browse"], command=self._choose_dir).pack(
            side="left", padx=(4, 8)
        )

        # Glob
        glob_frame = tk.Frame(self)
        glob_frame.pack(fill="x", padx=10)
        tk.Label(glob_frame, text=self.t["glob"]).pack(side="left", padx=(0, 6))
        tk.Entry(glob_frame, textvariable=self.glob_var, width=40).pack(
            side="left", padx=(0, 6)
        )
        tk.Button(
            glob_frame, text=self.t["refresh"], command=self._refresh_file_list
        ).pack(side="left")

        # Files list
        files_frame = tk.LabelFrame(self, text=self.t["select_logs"])
        files_frame.pack(fill="both", expand=True, padx=10, pady=8)

        list_container = tk.Frame(files_frame)
        list_container.pack(fill="both", expand=True)

        self.files_list = tk.Listbox(
            list_container,
            selectmode=tk.EXTENDED,
            height=12,
        )
        self.files_list.pack(side="left", fill="both", expand=True)
        scrollbar = tk.Scrollbar(list_container, orient="vertical")
        scrollbar.config(command=self.files_list.yview)
        self.files_list.config(yscrollcommand=scrollbar.set)
        scrollbar.pack(side="right", fill="y")

        btns = tk.Frame(files_frame)
        btns.pack(fill="x", pady=(6, 0))
        tk.Button(btns, text=self.t["select_all"], command=self._select_all).pack(
            side="left", padx=(0, 6)
        )
        tk.Button(btns, text=self.t["clear"], command=self._clear_selection).pack(
            side="left"
        )

        # Metric
        metric_frame = tk.LabelFrame(self, text=self.t["metric"])
        metric_frame.pack(fill="x", padx=10, pady=8)

        tk.Label(metric_frame, text=self.t["type"]).grid(
            row=0, column=0, sticky="w", padx=8, pady=6
        )
        # populate metric options by labels
        labels_metric = [label for (label, _key) in self.t["metric_opts"]]
        self.metric_menu = tk.OptionMenu(
            metric_frame,
            self.metric_choice_var,
            *labels_metric,
            command=self._on_metric_changed,
        )
        self.metric_menu.grid(row=0, column=1, sticky="w")

        tk.Label(metric_frame, text=self.t["custom_header"]).grid(
            row=0, column=2, sticky="w", padx=8
        )
        self.custom_entry = tk.Entry(
            metric_frame,
            textvariable=self.custom_column_var,
            width=30,
            state="disabled",
        )
        self.custom_entry.grid(row=0, column=3, sticky="w")

        tk.Label(metric_frame, text=self.t["fps_mode"]).grid(
            row=1, column=0, sticky="w", padx=8, pady=6
        )
        labels_fps = [label for (label, _key) in self.t["fps_opts"]]
        self.fps_menu = tk.OptionMenu(
            metric_frame,
            self.fps_mode_var,
            *labels_fps,
        )
        self.fps_menu.grid(row=1, column=1, sticky="w")
        # Tooltips for metric controls
        Tooltip(self.metric_menu, self.t["tt_metric_type"])
        Tooltip(self.custom_entry, self.t["tt_custom"])
        Tooltip(self.fps_menu, self.t["tt_fps_mode"])

        # Compare
        compare_frame = tk.LabelFrame(self, text=self.t["compare"])
        compare_frame.pack(fill="x", padx=10, pady=8)
        self.chk_compare = tk.Checkbutton(
            compare_frame,
            text=self.t["enable_compare"],
            variable=self.compare_mode_var,
            command=self._on_compare_changed,
        )
        self.chk_compare.pack(side="left", padx=8, pady=6)
        self.chk_diff_only = tk.Checkbutton(
            compare_frame,
            text=self.t["diff_only"],
            variable=self.difference_only_var,
        )
        self.chk_diff_only.pack(side="left", padx=8)
        # Tooltips for compare controls
        Tooltip(self.chk_compare, self.t["tt_enable_compare"])
        Tooltip(self.chk_diff_only, self.t["tt_diff_only"])

        # Trim
        trim_frame = tk.LabelFrame(self, text=self.t["trim"])
        trim_frame.pack(fill="x", padx=10, pady=8)
        
        tk.Label(trim_frame, text=self.t["trim_start"]).grid(
            row=0, column=0, sticky="w", padx=8, pady=6
        )
        tk.Entry(
            trim_frame, textvariable=self.trim_start_var, width=10
        ).grid(row=0, column=1, sticky="w")
        
        tk.Label(trim_frame, text=self.t["trim_end"]).grid(
            row=0, column=2, sticky="w", padx=8
        )
        tk.Entry(
            trim_frame, textvariable=self.trim_end_var, width=10
        ).grid(row=0, column=3, sticky="w")
        
        self.trim_configure_btn = tk.Button(
            trim_frame, 
            text=self.t["trim_configure"], 
            command=self._configure_trim
        )
        self.trim_configure_btn.grid(row=0, column=4, sticky="w", padx=8)
        
        # Tooltip for trim controls
        Tooltip(trim_frame, self.t["tt_trim"])

        # Output
        out_frame = tk.LabelFrame(self, text=self.t["output"])
        out_frame.pack(fill="x", padx=10, pady=8)
        tk.Entry(out_frame, textvariable=self.output_var).pack(
            side="left", fill="x", expand=True, padx=(8, 4), pady=8
        )
        tk.Button(out_frame, text=self.t["browse"], command=self._choose_output).pack(
            side="left", padx=(4, 8)
        )

        # Actions
        actions = tk.Frame(self)
        actions.pack(fill="x", padx=10, pady=(0, 10))
        tk.Button(actions, text=self.t["generate"], command=self._generate).pack(
            side="left"
        )
        tk.Button(actions, text="Rename…", command=self._rename_selected).pack(
            side="left", padx=(8, 0)
        )
        self.status_var = tk.StringVar(value="")
        tk.Label(actions, textvariable=self.status_var, anchor="w").pack(
            side="left", padx=12
        )

    def _choose_dir(self) -> None:
        sel = filedialog.askdirectory(initialdir=self.dir_var.get() or ".")
        if sel:
            self.dir_var.set(sel)
            self._refresh_file_list()

    def _choose_output(self) -> None:
        sel = filedialog.asksaveasfilename(
            title=self.t["output"],
            defaultextension=".csv",
            filetypes=[("CSV files", "*.csv"), ("All files", "*.*")],
            initialfile=Path(self.output_var.get()).name or "flourish_out.csv",
            initialdir=str(Path(self.output_var.get()).parent.resolve()),
        )
        if sel:
            self.output_var.set(sel)

    def _switch_lang(self, value: str) -> None:
        self.lang = "ru" if value == "ru" else "en"
        self.t = LANG_TEXTS[self.lang]
        # Rebuild UI to apply new labels
        for child in self.winfo_children():
            child.destroy()
        self._build_ui()
        self._refresh_file_list()

    def _refresh_file_list(self) -> None:
        self.files_list.delete(0, tk.END)
        directory = Path(self.dir_var.get())
        glob = self.glob_var.get().strip() or None
        try:
            files = discover_input_files(directory, glob)
        except Exception as exc:  # noqa: BLE001
            messagebox.showerror("Error", f"{self.t['err_scan']}:\n{exc}")
            return
        for p in files:
            self.files_list.insert(tk.END, str(p.resolve()))
        self.status_var.set(self.t["status_found"].format(n=len(files)))

    def _select_all(self) -> None:
        self.files_list.select_set(0, tk.END)

    def _clear_selection(self) -> None:
        self.files_list.selection_clear(0, tk.END)

    def _on_metric_changed(self, *_: object) -> None:
        if self.metric_choice_var.get() in (
            "custom column",
            "Custom column…",
            "Произвольная колонка…",
        ):
            self.custom_entry.configure(state="normal")
        else:
            self.custom_entry.configure(state="disabled")

    def _on_compare_changed(self) -> None:
        if self.compare_mode_var.get():
            self.status_var.set(self.t["status_compare"])
        else:
            self.status_var.set("")

    def _read_selected_files(self) -> List[Path]:
        selection = [self.files_list.get(i) for i in self.files_list.curselection()]
        return [Path(s) for s in selection]

    def _resolve_metric_value(self) -> str:
        choice_label = self.metric_choice_var.get()
        # Map UI label → internal key
        choice = next(
            (key for (label, key) in self.t["metric_opts"] if label == choice_label),
            choice_label,
        )
        if choice in ("__custom__", "custom column"):
            hdr = self.custom_column_var.get().strip()
            if not hdr:
                raise ValueError("Custom column header cannot be empty")
            return f"{MetricKind.COLUMN_PREFIX}{hdr}"
        return choice

    def _generate(self) -> None:
        try:
            out_path = Path(self.output_var.get())
            metric = self._resolve_metric_value()
            # map fps mode label to value if needed
            fps_label = self.fps_mode_var.get()
            fps_mode = next(
                (v for lbl, v in self.t["fps_opts"] if lbl == fps_label),
                fps_label,
            )
            compare = self.compare_mode_var.get()
            diff_only = self.difference_only_var.get()
            selected = self._read_selected_files()

            if compare:
                if len(selected) != 2:
                    raise ValueError("Compare mode requires exactly 2 selected logs")

                rows = []
                trim_start_a, trim_end_a = self._get_trim_settings(selected[0])
                trim_start_b, trim_end_b = self._get_trim_settings(selected[1])
                name_a, series_a = compute_per_second_series(
                    selected[0], metric, fps_mode=fps_mode,
                    trim_start=trim_start_a, trim_end=trim_end_a
                )
                name_b, series_b = compute_per_second_series(
                    selected[1], metric, fps_mode=fps_mode,
                    trim_start=trim_start_b, trim_end=trim_end_b
                )
                lbls = getattr(self, "custom_labels", {})
                name_a = lbls.get(str(selected[0]), name_a)
                name_b = lbls.get(str(selected[1]), name_b)
                diff_series = compute_difference_series(series_a, series_b)

                if diff_only:
                    rows = [("%", diff_series)]
                else:
                    rows = [
                        (name_a, series_a),
                        (name_b, series_b),
                        ("%", diff_series),
                    ]
            else:
                if len(selected) == 0:
                    raise ValueError("Select at least one log to process")
                rows = []
                for p in selected:
                    trim_start, trim_end = self._get_trim_settings(p)
                    name, series = compute_per_second_series(
                        p, metric, fps_mode=fps_mode,
                        trim_start=trim_start, trim_end=trim_end
                    )
                    # Apply user-provided label if present
                    lbls = getattr(self, "custom_labels", {})
                    label = lbls.get(str(p), name)
                    rows.append((label, series))

            write_flourish_wide_csv(out_path, rows)
            self.status_var.set(f"{self.t['done_file']} {out_path}")
            messagebox.showinfo(self.t["done_file"], str(out_path))
        except Exception as exc:  # noqa: BLE001
            messagebox.showerror("Error", str(exc))

    def _configure_trim(self) -> None:
        # Open trim configuration dialog
        selected_paths = self._read_selected_files()
        if not selected_paths:
            messagebox.showinfo("Info", "No files selected")
            return
            
        # Create trim configuration dialog
        dialog = TrimConfigDialog(self, selected_paths, self.trim_settings, self.t)
        self.wait_window(dialog)

    def _get_trim_settings(self, file_path: Path) -> Tuple[float, float]:
        """Get trim settings for a specific file (start, end)"""
        file_key = str(file_path)
        if file_key in self.trim_settings:
            return self.trim_settings[file_key]
        return self.trim_start_var.get(), self.trim_end_var.get()

    def _rename_selected(self) -> None:
        # Ask for custom labels per selected file
        selected_paths = self._read_selected_files()
        if not selected_paths:
            messagebox.showinfo("Info", "No files selected")
            return
        # Store mapping filename -> custom label in-memory for this run
        self.custom_labels = getattr(self, "custom_labels", {})
        for p in selected_paths:
            default = p.stem
            prompt = self.t["rename_prompt"].format(file=str(p), default=default)
            name = simpledialog.askstring(self.t["rename_title"], prompt)
            if name is None:
                continue
            name = name.strip()
            if name:
                self.custom_labels[str(p)] = name


def main() -> None:
    app = App()
    app.mainloop()


if __name__ == "__main__":
    main()
