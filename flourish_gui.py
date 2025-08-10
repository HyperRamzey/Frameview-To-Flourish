import tkinter as tk
from tkinter import filedialog, messagebox, simpledialog
from pathlib import Path
from typing import List

from flourish_maker import (
    MetricKind,
    compute_difference_series,
    compute_per_second_series,
    discover_input_files,
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
                name_a, series_a = compute_per_second_series(
                    selected[0], metric, fps_mode=fps_mode
                )
                name_b, series_b = compute_per_second_series(
                    selected[1], metric, fps_mode=fps_mode
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
                    name, series = compute_per_second_series(
                        p, metric, fps_mode=fps_mode
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
