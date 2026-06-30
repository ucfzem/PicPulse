import tkinter
import customtkinter as ctk
from tkinter import filedialog, messagebox
import threading
import queue
import os
from PIL import Image, ImageTk
import time

ctk.set_appearance_mode("system")
ctk.set_default_color_theme("blue")


class ImageAnalyzerUI(ctk.CTk):
    def __init__(self, processor):
        super().__init__()

        self.processor = processor
        self.source_dir = None
        self.is_running = False
        self.pause_event = threading.Event()
        self.pause_event.set()
        self.queue = queue.Queue()
        self.processed_count = 0
        self.results = []

        self.title("Smart Image Analyzer & Renamer")
        self.geometry("1100x720")
        self.minsize(900, 600)

        self._setup_ui()
        self._check_queue()

    def _setup_ui(self):
        self.grid_columnconfigure(0, weight=1)
        self.grid_rowconfigure(1, weight=1)

        header = ctk.CTkFrame(self, corner_radius=0)
        header.grid(row=0, column=0, sticky="ew", padx=0, pady=0)
        header.grid_columnconfigure(0, weight=1)

        ctk.CTkLabel(
            header, text="Smart Image Analyzer & Renamer",
            font=ctk.CTkFont(size=22, weight="bold")
        ).grid(row=0, column=0, pady=(12, 2))

        ctk.CTkLabel(
            header, text="AI Recognition · Lens Flare Detection · Intelligent Renaming",
            font=ctk.CTkFont(size=12), text_color="gray"
        ).grid(row=1, column=0, pady=(0, 10))

        main = ctk.CTkFrame(self)
        main.grid(row=1, column=0, sticky="nsew", padx=15, pady=10)
        main.grid_columnconfigure(0, weight=1)
        main.grid_rowconfigure(2, weight=1)

        controls = ctk.CTkFrame(main)
        controls.grid(row=0, column=0, sticky="ew", pady=(0, 10))
        controls.grid_columnconfigure(1, weight=1)

        ctk.CTkLabel(controls, text="Source Folder:", font=ctk.CTkFont(size=13)).grid(row=0, column=0, padx=(10, 5), pady=10, sticky="w")

        self.dir_entry = ctk.CTkEntry(controls, placeholder_text="Select a folder containing images...")
        self.dir_entry.grid(row=0, column=1, sticky="ew", padx=5, pady=10)

        self.browse_btn = ctk.CTkButton(controls, text="Browse", width=100, command=self._browse)
        self.browse_btn.grid(row=0, column=2, padx=5, pady=10)

        opts = ctk.CTkFrame(main)
        opts.grid(row=1, column=0, sticky="ew", pady=(0, 10))
        opts.grid_columnconfigure(1, weight=1)
        opts.grid_columnconfigure(3, weight=1)

        self.flare_var = ctk.BooleanVar(value=True)
        ctk.CTkCheckBox(opts, text="Add flare_ tag", variable=self.flare_var).grid(row=0, column=0, padx=(10, 20), pady=5, sticky="w")

        ctk.CTkLabel(opts, text="Flare threshold:").grid(row=0, column=1, padx=(0, 5), pady=5, sticky="e")
        self.flare_threshold = ctk.CTkSlider(opts, from_=0.1, to=0.9, number_of_steps=8)
        self.flare_threshold.set(0.3)
        self.flare_threshold.grid(row=0, column=2, padx=5, pady=5, sticky="ew")
        self.flare_val_label = ctk.CTkLabel(opts, text="0.3", width=30)
        self.flare_val_label.grid(row=0, column=3, padx=(0, 10), pady=5, sticky="w")
        self.flare_threshold.configure(command=lambda v: self.flare_val_label.configure(text=f"{v:.1f}"))

        self.dry_run_var = ctk.BooleanVar(value=True)
        ctk.CTkCheckBox(opts, text="Preview mode (no rename)", variable=self.dry_run_var).grid(row=0, column=4, padx=(20, 10), pady=5, sticky="w")

        content = ctk.CTkFrame(main)
        content.grid(row=2, column=0, sticky="nsew")
        content.grid_columnconfigure(0, weight=3)
        content.grid_columnconfigure(1, weight=2)
        content.grid_rowconfigure(0, weight=1)

        left_panel = ctk.CTkFrame(content)
        left_panel.grid(row=0, column=0, sticky="nsew", padx=(0, 5))
        left_panel.grid_rowconfigure(1, weight=1)
        left_panel.grid_columnconfigure(0, weight=1)

        ctk.CTkLabel(left_panel, text="Live Preview", font=ctk.CTkFont(size=14, weight="bold")).grid(row=0, column=0, pady=(8, 5))

        self.image_preview = ctk.CTkLabel(left_panel, text="No image selected", fg_color=("gray85", "gray25"), corner_radius=8)
        self.image_preview.grid(row=1, column=0, sticky="nsew", padx=10, pady=(0, 10))

        self.preview_info = ctk.CTkLabel(left_panel, text="", font=ctk.CTkFont(size=11))
        self.preview_info.grid(row=2, column=0, sticky="ew", padx=10, pady=(0, 10))

        right_panel = ctk.CTkFrame(content)
        right_panel.grid(row=0, column=1, sticky="nsew", padx=(5, 0))
        right_panel.grid_rowconfigure(1, weight=1)
        right_panel.grid_columnconfigure(0, weight=1)

        ctk.CTkLabel(right_panel, text="Processing Log", font=ctk.CTkFont(size=14, weight="bold")).grid(row=0, column=0, pady=(8, 5))

        self.log_text = ctk.CTkTextbox(right_panel, font=ctk.CTkFont(size=11), wrap="word")
        self.log_text.grid(row=1, column=0, sticky="nsew", padx=10, pady=(0, 10))

        progress_frame = ctk.CTkFrame(main)
        progress_frame.grid(row=3, column=0, sticky="ew", pady=(10, 0))
        progress_frame.grid_columnconfigure(0, weight=1)

        self.progress_bar = ctk.CTkProgressBar(progress_frame)
        self.progress_bar.grid(row=0, column=0, sticky="ew", padx=10, pady=(10, 2))
        self.progress_bar.set(0)

        self.status_label = ctk.CTkLabel(progress_frame, text="Ready. Select a folder and click Start.", font=ctk.CTkFont(size=11))
        self.status_label.grid(row=1, column=0, sticky="ew", padx=10, pady=(0, 5))

        action_frame = ctk.CTkFrame(main)
        action_frame.grid(row=4, column=0, sticky="ew", pady=(10, 0))
        action_frame.grid_columnconfigure(1, weight=1)

        self.start_btn = ctk.CTkButton(action_frame, text="▶ Start Processing", command=self._start_processing, width=140, height=36)
        self.start_btn.grid(row=0, column=0, padx=10, pady=10)

        self.pause_btn = ctk.CTkButton(action_frame, text="⏸ Pause", command=self._toggle_pause, width=100, height=36, state="disabled")
        self.pause_btn.grid(row=0, column=1, padx=5, pady=10, sticky="w")

        self.cancel_btn = ctk.CTkButton(action_frame, text="✕ Cancel", command=self._cancel, width=100, height=36, state="disabled", fg_color="darkred", hover_color="red")
        self.cancel_btn.grid(row=0, column=2, padx=5, pady=10, sticky="w")

        stats_frame = ctk.CTkFrame(action_frame)
        stats_frame.grid(row=0, column=3, padx=15, pady=10, sticky="e")
        self.stats_label = ctk.CTkLabel(stats_frame, text="Ready", font=ctk.CTkFont(size=11))
        self.stats_label.pack(padx=10, pady=2)

    def _browse(self):
        directory = filedialog.askdirectory(title="Select Image Folder")
        if directory:
            self.source_dir = directory
            self.dir_entry.delete(0, "end")
            self.dir_entry.insert(0, directory)
            count = len(self.processor.preview(directory))
            self.status_label.configure(text=f"Found {count} images in selected folder.")
            self.stats_label.configure(text=f"{count} images detected")

    def _log(self, message, color=None):
        tag = "default"
        if color == "green":
            tag = "green"
            self.log_text.tag_config("green", foreground="#2ecc71")
        elif color == "red":
            tag = "red"
            self.log_text.tag_config("red", foreground="#e74c3c")
        elif color == "blue":
            tag = "blue"
            self.log_text.tag_config("blue", foreground="#3498db")
        elif color == "orange":
            tag = "orange"
            self.log_text.tag_config("orange", foreground="#f39c12")
        self.log_text.insert("end", message + "\n", tag)
        self.log_text.see("end")

    def _update_preview(self, image_path, info_text):
        try:
            pil_img = Image.open(image_path)
            pil_img.thumbnail((320, 240), Image.LANCZOS)
            tk_img = ctk.CTkImage(light_image=pil_img, dark_image=pil_img, size=(320, 240))
            self.image_preview.configure(image=tk_img, text="")
            self.image_preview.image = tk_img
            self.preview_info.configure(text=info_text)
        except Exception:
            pass

    def _start_processing(self):
        source = self.dir_entry.get()
        if not source or not os.path.isdir(source):
            messagebox.showerror("Error", "Please select a valid source folder.")
            return

        self.is_running = True
        self.processed_count = 0
        self.results = []
        self.log_text.delete("1.0", "end")
        self.progress_bar.set(0)

        self.start_btn.configure(state="disabled")
        self.pause_btn.configure(state="normal", text="⏸ Pause")
        self.cancel_btn.configure(state="normal")
        self.browse_btn.configure(state="disabled")
        self.pause_event.set()

        self.processor.renamer.add_flare_tag = self.flare_var.get()
        self.processor.renamer.dry_run = self.dry_run_var.get()
        self.processor.flare_detector.threshold = self.flare_threshold.get()

        mode = "PREVIEW (no changes)" if self.dry_run_var.get() else "LIVE RENAME"
        self._log(f"▶ Started processing: {source}", "blue")
        self._log(f"Mode: {mode} | Flare tag: {self.flare_var.get()} | Threshold: {self.flare_threshold.get():.1f}", "blue")
        self._log("-" * 50)

        thread = threading.Thread(target=self._process_thread, args=(source,), daemon=True)
        thread.start()

    def _process_thread(self, source):
        try:
            for update in self.processor.process(source):
                self.queue.put(update)
        except Exception as e:
            self.queue.put({"type": "fatal_error", "error": str(e)})

    def _check_queue(self):
        try:
            while True:
                update = self.queue.get_nowait()
                self._handle_update(update)
        except queue.Empty:
            pass
        self.after(100, self._check_queue)

    def _handle_update(self, update):
        update_type = update.get("type")

        if update_type == "progress":
            current = update["current"]
            total = update["total"]
            self.progress_bar.set(current / total if total > 0 else 0)
            self.status_label.configure(text=f"Analyzing: {os.path.basename(update['image_path'])} ({current}/{total})")
            self.stats_label.configure(text=f"{current}/{total}")

        elif update_type == "result":
            self.processed_count += 1
            self.results.append(update)
            current = update["current"]
            total = update["total"]
            self.progress_bar.set(current / total if total > 0 else 0)

            keyword = update["keyword"]
            flare = " 🔆FLARE" if update["has_flare"] else ""
            conf = f"{update['confidence']*100:.0f}%"
            original = os.path.basename(update["original_path"])
            new_name = os.path.basename(update["new_path"])

            if update["renamed"]:
                self._log(f"  {original} → {new_name}  [{keyword} {conf}{flare}]", "green")
            else:
                self._log(f"  {original}  [{keyword} {conf}{flare}] (unchanged)", "orange")

            self.status_label.configure(text=f"Processed: {new_name} ({current}/{total})")
            self.stats_label.configure(text=f"{current}/{total} | Keyword: {keyword}")
            self._update_preview(update["original_path"], f"AI: {keyword} ({conf}) | Flare: {update['flare_score']:.2f}")

        elif update_type == "error":
            self._log(f"  ERROR: {update['image_path']} - {update['error']}", "red")
            self.processed_count += 1

        elif update_type == "fatal_error":
            self._log(f"  FATAL ERROR: {update['error']}", "red")

        elif update_type == "complete":
            total = update["total"]
            renamed = sum(1 for r in update["results"] if r.get("renamed"))
            flared = sum(1 for r in update["results"] if r.get("has_flare"))
            errors = sum(1 for r in update["results"] if r.get("status") == "error")

            self.progress_bar.set(1.0)
            self.status_label.configure(text=f"Complete! {renamed} renamed, {flared} flare detected, {errors} errors")
            self.stats_label.configure(text=f"✓ {total} done | {renamed} renamed | {flared} flares")
            self._log("-" * 50, "blue")
            self._log(f"✓ Processing complete! {total} images processed.", "green")
            self._log(f"  Renamed: {renamed} | Flare detected: {flared} | Errors: {errors}", "green" if errors == 0 else "orange")
            self._reset_controls()

    def _toggle_pause(self):
        if self.pause_event.is_set():
            self.pause_event.clear()
            self.pause_btn.configure(text="▶ Resume")
            self._log("⏸ Paused", "orange")
        else:
            self.pause_event.set()
            self.pause_btn.configure(text="⏸ Pause")
            self._log("▶ Resumed", "blue")

    def _cancel(self):
        self.is_running = False
        self.pause_event.set()
        self._log("✕ Cancelled by user", "red")
        self._reset_controls()

    def _reset_controls(self):
        self.start_btn.configure(state="normal")
        self.pause_btn.configure(state="disabled", text="⏸ Pause")
        self.cancel_btn.configure(state="disabled")
        self.browse_btn.configure(state="normal")
        self.is_running = False
