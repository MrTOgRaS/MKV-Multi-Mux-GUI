# -*- coding: utf-8 -*-
"""
MKV MultiMux GUI v1.0  —  by MrTOgRaS
MIT License
"""

import os
import sys
import re
import json
import threading
import subprocess
import tkinter as tk
from tkinter import filedialog, messagebox
import customtkinter as ctk
from tkinterdnd2 import DND_FILES, TkinterDnD
import webbrowser

# ─── AYARLAR (CONFIG) İÇİN FONKSİYONLAR ────────────────────────────────────────
CONFIG_FILE = "mkvbatch_settings.json"

def load_config():
    if os.path.exists(CONFIG_FILE):
        try:
            with open(CONFIG_FILE, "r", encoding="utf-8") as f:
                return json.load(f)
        except Exception:
            pass
    return {}

def save_config(data):
    try:
        with open(CONFIG_FILE, "w", encoding="utf-8") as f:
            json.dump(data, f, indent=4)
    except Exception:
        pass

def resource_path(relative_path):
    try:
        base_path = sys._MEIPASS
    except Exception:
        base_path = os.path.abspath(".")
    return os.path.join(base_path, relative_path)

# ─── DİL PAKETİ ────────────────────────────────────────────────────────────────
LANGS = {
    "English": {
        "app_title":      "MKV MultiMux GUI",
        "sub_title":      "Fast, Lossless & Batch Remux Tool",
        "lbl_exe":        "mkvmerge.exe :",
        "lbl_outdir":     "Output Folder:",
        "hint_outdir":    "(Leave empty to save in program folder)",
        "drop_hint":      "Drop Files or Folders Here\n\n(MP4, AVI, MOV, TS, WMV)",
        "btn_start":      "START CONVERSION",
        "btn_clear":      "Clear List",
        "btn_about":      "About",
        "log_ready":      "Ready.",
        "log_added":      "{} files added. Total: {}",
        "log_proc":       "[{}/{}] Processing: {}",
        "log_done":       "COMPLETED.",
        "log_err":        "ERROR: {}",
        "msg_done_t":     "Done",
        "msg_done_b":     "{} files successfully saved to:\n{}",
        "err_noexe":      "Please select the mkvmerge.exe path!",
        "err_nofiles":    "No valid files to process!"
    },
    "Türkçe": {
        "app_title":      "MKV MultiMux GUI",
        "sub_title":      "Hızlı, Kayıpsız ve Toplu Remux İşlemi",
        "lbl_exe":        "mkvmerge.exe :",
        "lbl_outdir":     "Çıktı Klasörü:",
        "hint_outdir":    "(Boş bırakılırsa programın yanına kaydeder)",
        "drop_hint":      "Dosyaları veya Klasörü Buraya Sürükleyin\n\n(MP4, AVI, MOV, TS, WMV)",
        "btn_start":      "DÖNÜŞTÜRMEYİ BAŞLAT",
        "btn_clear":      "Listeyi Temizle",
        "btn_about":      "Hakkında",
        "log_ready":      "Hazır.",
        "log_added":      "{} dosya eklendi. Toplam: {}",
        "log_proc":       "[{}/{}] İşleniyor: {}",
        "log_done":       "TAMAMLANDI.",
        "log_err":        "HATA: {}",
        "msg_done_t":     "Bitti",
        "msg_done_b":     "{} dosya başarıyla şuraya kaydedildi:\n{}",
        "err_noexe":      "Lütfen mkvmerge.exe yolunu seçin!",
        "err_nofiles":    "İşlenecek dosya bulunamadı!"
    },
    "Deutsch": {
        "app_title":      "MKV MultiMux GUI",
        "sub_title":      "Schnelles, verlustfreies Batch-Remux-Tool",
        "lbl_exe":        "mkvmerge.exe :",
        "lbl_outdir":     "Ausgabeordner:",
        "hint_outdir":    "(Leer lassen, um im Programmordner zu speichern)",
        "drop_hint":      "Dateien oder Ordner hier ablegen\n\n(MP4, AVI, MOV, TS, WMV)",
        "btn_start":      "KONVERTIERUNG STARTEN",
        "btn_clear":      "Liste leeren",
        "btn_about":      "Über",
        "log_ready":      "Bereit.",
        "log_added":      "{} Dateien hinzugefügt. Gesamt: {}",
        "log_proc":       "[{}/{}] Verarbeite: {}",
        "log_done":       "ABGESCHLOSSEN.",
        "log_err":        "FEHLER: {}",
        "msg_done_t":     "Fertig",
        "msg_done_b":     "{} Dateien erfolgreich gespeichert in:\n{}",
        "err_noexe":      "Bitte wählen Sie den mkvmerge.exe Pfad!",
        "err_nofiles":    "Keine Dateien zur Verarbeitung gefunden!"
    }
}

LANG_ORDER = ["English", "Türkçe", "Deutsch"]

# ─── ABOUT PENCERESI (CUTCUT STİLİ) ────────────────────────────────────────────
def show_about(root):
    BG    = "#0f172a"
    CARD  = "#1e293b"
    ACC   = "#06b6d4"
    ACC2  = "#38bdf8"
    TXT   = "#f8fafc"
    DIM   = "#94a3b8"
    WARN  = "#f59e0b"
    OK    = "#10b981"
    FM    = "Segoe UI"

    win = tk.Toplevel(root)
    win.title("About — MKV MultiMux GUI")
    win.geometry("560x820")
    win.resizable(False, False)
    win.configure(bg=BG)
    win.grab_set()

    hdr = tk.Frame(win, bg=BG, pady=12)
    hdr.pack(fill="x")
    tk.Label(hdr, text="🎬 MKV MultiMux GUI v1.0", font=(FM, 17, "bold"), bg=BG, fg=ACC).pack()
    tk.Label(hdr, text="by MrTOgRaS", font=(FM, 9), bg=BG, fg=DIM).pack()

    body = tk.Frame(win, bg=BG, padx=26, pady=6)
    body.pack(fill="both", expand=True)

    def sep(col=None):
        tk.Frame(body, bg=col or "#334155", height=1).pack(fill="x", pady=6)

    def kv(label, value, vfg=None, bold=False):
        f = tk.Frame(body, bg=BG)
        f.pack(fill="x", pady=1)
        tk.Label(f, text=label, width=15, anchor="w", bg=BG, fg=DIM, font=(FM, 9, "bold")).pack(side="left")
        tk.Label(f, text=value, anchor="w", bg=BG, fg=vfg or TXT, font=(FM, 9, "bold" if bold else "normal")).pack(side="left")

    def section_title(txt, col=None):
        tk.Label(body, text=txt, bg=BG, fg=col or ACC, font=(FM, 9, "bold"), anchor="w").pack(fill="x", pady=(4,1))

    # [ PROGRAM INFO ]
    section_title("[ PROGRAM INFO ]")
    kv("Program",    "MKV MultiMux GUI")
    kv("Version",    "1.0")
    kv("Platform",   "Windows x64")

    sep()
    # [ DEPENDENCIES ]
    section_title("[ DEPENDENCIES ]")
    kv("customtkinter", "Modern UI elements — MIT")
    kv("tkinterdnd2",   "Drag & Drop support — MIT")
    kv("subprocess",    "mkvmerge bridge — stdlib")

    sep()
    # [ AUTHOR & CONTACT ]
    section_title("[ AUTHOR & CONTACT ]")
    kv("Author",  "Murat Ogras (MrTOgRaS)", TXT, bold=True)
    kv("E-Mail",  "mrtogras@proton.me", ACC2, bold=True)
    kv("Website", "www.mrtogras.com", ACC2, bold=True)

    sep()
    # [ LICENSE ] - Yeşil Kutu
    section_title("[ LICENSE ]", OK)
    lic_box = tk.Frame(body, bg="#064e3b", padx=12, pady=10, highlightthickness=1, highlightbackground=OK)
    lic_box.pack(fill="x", pady=(2,0))
    
    tk.Label(lic_box, text="MIT License", bg="#064e3b", fg=OK, font=(FM, 12, "bold"), anchor="w").pack(fill="x")
    tk.Label(lic_box, text="Copyright (c) 2026 Murat Ogras (MrTOgRaS)", bg="#064e3b", fg=TXT, font=(FM, 8), anchor="w").pack(fill="x", pady=(4,6))
    
    mit_text = ("Permission is hereby granted, free of charge, to any person\n"
                "obtaining a copy of this software to use, copy, modify, merge,\n"
                "publish, distribute, sublicense, and/or sell copies, subject to:\n\n"
                "The above copyright notice and this permission notice shall\n"
                "be included in all copies or substantial portions of the Software.")
    tk.Label(lic_box, text=mit_text, bg="#064e3b", fg="#a7f3d0", font=(FM, 8), justify="left", anchor="w").pack(fill="x")

    sep()
    # [ REGARDS ] - Turuncu Kutu
    regards_box = tk.Frame(body, bg="#451a03", padx=14, pady=10, highlightthickness=1, highlightbackground=WARN)
    regards_box.pack(fill="x", pady=(2, 6))
    tk.Label(regards_box, text="Regards to Bunkus!", bg="#451a03", fg=WARN, font=(FM, 13, "bold italic"), anchor="w").pack(fill="x")
    tk.Label(regards_box, text="Moritz Bunkus — creator of MKVToolNix & mkvmerge", bg="#451a03", fg="#fde68a", font=(FM, 8), anchor="w").pack(fill="x", pady=(2,0))
             
    link_lbl = tk.Label(regards_box, text="(MKVToolNix Download)", bg="#451a03", fg=ACC2, cursor="hand2", font=(FM, 8, "bold underline"), anchor="w")
    link_lbl.pack(fill="x", pady=(2,0))
    link_lbl.bind("<Button-1>", lambda e: webbrowser.open_new("https://mkvtoolnix.download/downloads.html#windows"))

    tk.Button(win, text="  Close  ", command=win.destroy, bg=ACC, fg="#0f172a", relief="flat", padx=20, pady=6, cursor="hand2", font=(FM, 9, "bold"), bd=0).pack(pady=5)


# ─── ANA UYGULAMA ──────────────────────────────────────────────────────────────
ctk.set_appearance_mode("Dark")
ctk.set_default_color_theme("blue")

class MKVBatchApp:
    def __init__(self):
        self.root = TkinterDnD.Tk()
        self.root.title("🎬 MKV MultiMux GUI v1.0")
        self.root.geometry("850x780")
        self.root.minsize(800, 700)
        self.root.configure(bg="#242424")

        try:
            self.root.iconbitmap(resource_path("icon.ico"))
        except:
            pass
            
        self.config_data = load_config()
        self.files_to_process = []
        self.is_processing = False

        # Değişkenler (Kayıtlı veriler varsa otomatik yüklenir)
        self.lang_var = ctk.StringVar(value=self.config_data.get("language", "English"))
        self.mkv_exe = ctk.StringVar(value=self.config_data.get("mkvmerge_path", ""))
        self.out_dir = ctk.StringVar(value=self.config_data.get("output_path", ""))

        # Herhangi biri değiştiğinde anında ayar dosyasına kaydeder
        self.lang_var.trace_add("write", self._save_settings)
        self.mkv_exe.trace_add("write", self._save_settings)
        self.out_dir.trace_add("write", self._save_settings)

        self.setup_ui()
        self.apply_lang()

    def _save_settings(self, *args):
        self.config_data["language"] = self.lang_var.get()
        self.config_data["mkvmerge_path"] = self.mkv_exe.get()
        self.config_data["output_path"] = self.out_dir.get()
        save_config(self.config_data)

    def T(self, k):
        return LANGS[self.lang_var.get()].get(k, k)

    def setup_ui(self):
        # ── HEADER ──
        self.hdr_frame = ctk.CTkFrame(self.root, fg_color="transparent")
        self.hdr_frame.pack(fill="x", pady=(15, 0), padx=20)
        
        # Dil Seçimi
        self.lang_frame = ctk.CTkFrame(self.hdr_frame, fg_color="transparent")
        self.lang_frame.pack(side="right")
        for lng in LANG_ORDER:
            ctk.CTkRadioButton(self.lang_frame, text=lng, variable=self.lang_var, value=lng, 
                               command=self.apply_lang, font=("Segoe UI", 11)).pack(side="left", padx=5)

        self.header = ctk.CTkLabel(self.root, text="", font=("Segoe UI", 28, "bold"), text_color="#3b8ed0")
        self.header.pack()
        self.sub_header = ctk.CTkLabel(self.root, text="", font=("Segoe UI", 13), text_color="gray")
        self.sub_header.pack(pady=(0, 15))

        # ── PATHS (Yol Ayarları) ──
        self.paths_frame = ctk.CTkFrame(self.root, fg_color="#2b2b2b", corner_radius=10)
        self.paths_frame.pack(fill="x", padx=40, pady=10)

        # EXE Yolu
        row1 = ctk.CTkFrame(self.paths_frame, fg_color="transparent")
        row1.pack(fill="x", padx=15, pady=(15, 5))
        self.lbl_exe = ctk.CTkLabel(row1, text="", width=120, anchor="w", font=("Segoe UI", 12))
        self.lbl_exe.pack(side="left")
        ctk.CTkEntry(row1, textvariable=self.mkv_exe, fg_color="#1a1a1a", border_color="#333").pack(side="left", fill="x", expand=True, padx=10)
        ctk.CTkButton(row1, text="...", width=40, command=self.browse_exe, fg_color="#3b8ed0").pack(side="left")

        # Çıktı Klasörü
        row2 = ctk.CTkFrame(self.paths_frame, fg_color="transparent")
        row2.pack(fill="x", padx=15, pady=(5, 5))
        self.lbl_outdir = ctk.CTkLabel(row2, text="", width=120, anchor="w", font=("Segoe UI", 12))
        self.lbl_outdir.pack(side="left")
        ctk.CTkEntry(row2, textvariable=self.out_dir, fg_color="#1a1a1a", border_color="#333", placeholder_text="Default: App_Folder/MKV_Output").pack(side="left", fill="x", expand=True, padx=10)
        ctk.CTkButton(row2, text="...", width=40, command=self.browse_out, fg_color="#3b8ed0").pack(side="left")

        self.lbl_outhint = ctk.CTkLabel(self.paths_frame, text="", font=("Segoe UI", 11, "italic"), text_color="#777")
        self.lbl_outhint.pack(pady=(0, 10))

        # ── SÜRÜKLE BIRAK ALANI ──
        self.drop_frame = ctk.CTkFrame(self.root, width=700, height=140, border_width=2, border_color="#1f538d", fg_color="#1a1a1a")
        self.drop_frame.pack(pady=10, padx=40, fill="x")
        self.drop_frame.pack_propagate(False)

        self.drop_label = ctk.CTkLabel(self.drop_frame, text="", font=("Segoe UI", 15, "italic"), text_color="#888888")
        self.drop_label.pack(expand=True)

        self.drop_frame.drop_target_register(DND_FILES)
        self.drop_frame.dnd_bind('<<Drop>>', self.handle_drop)

        # ── BUTONLAR ──
        self.btn_frame = ctk.CTkFrame(self.root, fg_color="transparent")
        self.btn_frame.pack(pady=10)

        self.start_btn = ctk.CTkButton(self.btn_frame, text="", command=self.process_files, state="disabled", 
                                      fg_color="#27ae60", hover_color="#2ecc71", width=200, height=45, font=("Segoe UI", 14, "bold"))
        self.start_btn.grid(row=0, column=0, padx=10)

        self.clear_btn = ctk.CTkButton(self.btn_frame, text="", command=self.clear_list, 
                                      fg_color="#e74c3c", hover_color="#c0392b", width=140, height=45, font=("Segoe UI", 14))
        self.clear_btn.grid(row=0, column=1, padx=10)

        self.about_btn = ctk.CTkButton(self.btn_frame, text="", command=lambda: show_about(self.root), 
                                      fg_color="#4b5563", hover_color="#374151", width=100, height=45, font=("Segoe UI", 14))
        self.about_btn.grid(row=0, column=2, padx=10)

        # ── LOG KUTUSU ──
        self.log_box = ctk.CTkTextbox(self.root, height=180, font=("Consolas", 12), fg_color="#1a1a1a", border_width=1, border_color="#333")
        self.log_box.pack(pady=(10, 5), padx=40, fill="x")
        
        self.footer = ctk.CTkLabel(self.root, text="Copyright © 2026 Murat Oğraş | mkvmerge Powered", font=("Segoe UI", 10), text_color="#555555")
        self.footer.pack(side="bottom", pady=10)

    def apply_lang(self):
        t = LANGS[self.lang_var.get()]
        self.header.configure(text=t["app_title"])
        self.sub_header.configure(text=t["sub_title"])
        
        self.lbl_exe.configure(text=t["lbl_exe"])
        self.lbl_outdir.configure(text=t["lbl_outdir"])
        self.lbl_outhint.configure(text=t["hint_outdir"])
        
        if len(self.files_to_process) == 0:
            self.drop_label.configure(text=t["drop_hint"], text_color="#888888")
        else:
            self.drop_label.configure(text=t["log_added"].format(len(self.files_to_process), len(self.files_to_process)), text_color="#27ae60")
            
        self.start_btn.configure(text=t["btn_start"])
        self.clear_btn.configure(text=t["btn_clear"])
        self.about_btn.configure(text=t["btn_about"])
        
        if not self.is_processing:
            self.log_box.delete("1.0", "end")
            self.log(t["log_ready"])

    def browse_exe(self):
        p = filedialog.askopenfilename(filetypes=[("EXE", "*.exe")])
        if p: self.mkv_exe.set(p)

    def browse_out(self):
        d = filedialog.askdirectory()
        if d: self.out_dir.set(d)

    def handle_drop(self, event):
        if self.is_processing: return
        raw_data = event.data
        paths = re.findall(r'\{(.*?)\}', raw_data) or re.findall(r'\"(.*?)\"', raw_data) or raw_data.split()

        added_count = 0
        valid_ext = ('.mp4', '.avi', '.mov', '.ts', '.wmv', '.flv', '.m4v', '.mkv', '.webm')

        for path in paths:
            clean_path = path.strip('"{ }')
            if os.path.exists(clean_path):
                if os.path.isdir(clean_path):
                    for f in os.listdir(clean_path):
                        if f.lower().endswith(valid_ext):
                            full_path = os.path.join(clean_path, f)
                            if full_path not in self.files_to_process:
                                self.files_to_process.append(full_path)
                                added_count += 1
                elif clean_path.lower().endswith(valid_ext):
                    if clean_path not in self.files_to_process:
                        self.files_to_process.append(clean_path)
                        added_count += 1
        
        if added_count > 0:
            self.start_btn.configure(state="normal")
            self.drop_label.configure(text=self.T("log_added").format(added_count, len(self.files_to_process)), text_color="#27ae60")
        else:
            self.log(self.T("err_nofiles"))

    def log(self, message):
        self.log_box.insert("end", f"> {message}\n")
        self.log_box.see("end")

    def clear_list(self):
        if self.is_processing: return
        self.files_to_process.clear()
        self.log_box.delete("1.0", "end")
        self.start_btn.configure(state="disabled")
        self.drop_label.configure(text=self.T("drop_hint"), text_color="#888888")
        self.log(self.T("log_ready"))

    def _process_thread(self):
        self.is_processing = True
        self.start_btn.configure(state="disabled")
        self.clear_btn.configure(state="disabled")
        
        success_count = 0
        total = len(self.files_to_process)
        
        # Çıktı klasörü ayarı
        out_target = self.out_dir.get().strip()
        if not out_target:
            out_target = os.path.join(os.path.abspath("."), "MKV_Output")
            
        if not os.path.exists(out_target):
            os.makedirs(out_target, exist_ok=True)

        for i, file_path in enumerate(self.files_to_process, 1):
            base_name = os.path.splitext(os.path.basename(file_path))[0]
            output_file = os.path.join(out_target, f"{base_name}.mkv")
            
            counter = 1
            while os.path.exists(output_file):
                output_file = os.path.join(out_target, f"{base_name}_{counter}.mkv")
                counter += 1
                
            self.log(self.T("log_proc").format(i, total, os.path.basename(file_path)))
            
            try:
                cmd = [self.mkv_exe.get(), "-o", output_file, file_path]
                subprocess.run(cmd, check=True, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL, creationflags=0x08000000)
                self.log(self.T("log_done"))
                success_count += 1
            except Exception as e:
                self.log(self.T("log_err").format(os.path.basename(file_path)))

        messagebox.showinfo(self.T("msg_done_t"), self.T("msg_done_b").format(success_count, out_target))
        
        self.is_processing = False
        self.clear_list()
        self.clear_btn.configure(state="normal")

    def process_files(self):
        if not self.mkv_exe.get() or not os.path.isfile(self.mkv_exe.get()):
            messagebox.showerror("Error", self.T("err_noexe"))
            return
            
        if not self.files_to_process:
            return
            
        threading.Thread(target=self._process_thread, daemon=True).start()

    def run(self):
        self.root.mainloop()

if __name__ == "__main__":
    app = MKVBatchApp()
    app.run()