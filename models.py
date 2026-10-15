import csv
import os
import tkinter as tk
from datetime import datetime
from tkinter import ttk, messagebox

FILE_CSV = os.path.join(os.path.dirname(os.path.abspath(__file__)), "hotel_rating.csv")
HEADER = ["Nama Hotel", "Kota", "Rating (1-5)", "Jumlah Ulasan", "Kategori"]
KATEGORI = ["Bintang 1", "Bintang 2", "Bintang 3", "Bintang 4", "Bintang 5",
            "Resort", "Villa", "Homestay"]

# ---------------- Palet warna ----------------
BG = "#f8fafc"
SIDEBAR = "#0f172a"
SIDEBAR_HOVER = "#1e293b"
PRIMARY = "#4f46e5"
PRIMARY_HOVER = "#4338ca"
PRIMARY_SOFT = "#eef2ff"
TEXT = "#0f172a"
TEXT2 = "#334155"
MUTED = "#64748b"
BORDER = "#e2e8f0"
CARD = "#ffffff"
SUCCESS = "#059669"
SUCCESS_SOFT = "#d1fae5"
WARNING = "#d97706"
DANGER = "#dc2626"
DANGER_HOVER = "#b91c1c"
STAR = "#f59e0b"
FONT = "Segoe UI"


def info_status(rating):
    """Mengembalikan (label, warna) berdasarkan nilai rating."""
    if rating >= 4.5:
        return "Sangat Baik", SUCCESS
    if rating >= 4.0:
        return "Baik", PRIMARY
    if rating >= 3.0:
        return "Cukup", WARNING
    return "Kurang", DANGER


# ---------------- Widget tombol ----------------
class Tombol(tk.Label):
    GAYA = {
        "primary": (PRIMARY, PRIMARY_HOVER, "#ffffff"),
        "danger": (DANGER, DANGER_HOVER, "#ffffff"),
        "ghost": (CARD, "#f1f5f9", TEXT2),
        "soft": (PRIMARY_SOFT, "#e0e7ff", PRIMARY),
    }

    def __init__(self, parent, text, command=None, gaya="primary"):
        bg, hover, fg = self.GAYA[gaya]
        super().__init__(parent, text=text, bg=bg, fg=fg, font=(FONT, 10, "bold"),
                         padx=16, pady=8, cursor="hand2", highlightthickness=1,
                         highlightbackground=BORDER if gaya == "ghost" else bg)
        self.gaya = gaya
        self.bg_normal = bg
        self.bg_hover = hover
        self.fg_normal = fg
        self.aksi = command
        self.aktif = True
        self.bind("<Enter>", self._masuk)
        self.bind("<Leave>", self._keluar)
        self.bind("<Button-1>", self._klik)

    def _warna(self, bg):
        self.config(bg=bg)
        if self.gaya != "ghost":
            self.config(highlightbackground=bg)

    def _masuk(self, _e):
        if self.aktif:
            self._warna(self.bg_hover)

    def _keluar(self, _e):
        if self.aktif:
            self._warna(self.bg_normal)

    def _klik(self, _e):
        if self.aktif and self.aksi:
            self.aksi()

    def atur_aktif(self, aktif):
        self.aktif = aktif
        if aktif:
            self._warna(self.bg_normal)
            self.config(fg=self.fg_normal, cursor="hand2")
        else:
            self._warna("#e2e8f0")
            self.config(fg="#94a3b8", cursor="arrow")

    def ubah_teks(self, teks):
        self.config(text=teks)


# ---------------- Dialog konfirmasi ----------------
def konfirmasi(parent, judul, pesan, teks_ya="Ya", bahaya=False):
    top = parent.winfo_toplevel()
    dlg = tk.Toplevel(top)
    dlg.withdraw()
    dlg.title(judul)
    dlg.configure(bg=CARD)
    dlg.resizable(False, False)
    dlg.transient(top)
    hasil = {"ok": False}

    def tutup(ok):
        hasil["ok"] = ok
        dlg.destroy()

    kotak = tk.Frame(dlg, bg=CARD)
    kotak.pack(fill="x", padx=28, pady=(24, 0))
    tk.Label(kotak, text=judul, bg=CARD, fg=TEXT, font=(FONT, 13, "bold"),
             anchor="w").pack(fill="x")
    tk.Label(kotak, text=pesan, bg=CARD, fg=MUTED, font=(FONT, 10), wraplength=340,
             justify="left", anchor="w").pack(fill="x", pady=(8, 0))

    baris = tk.Frame(dlg, bg=CARD)
    baris.pack(fill="x", padx=28, pady=(18, 22))
    Tombol(baris, teks_ya, lambda: tutup(True),
           gaya="danger" if bahaya else "primary").pack(side="right")
    Tombol(baris, "Batal", lambda: tutup(False), gaya="ghost").pack(
        side="right", padx=(0, 10))

    dlg.bind("<Escape>", lambda e: tutup(False))
    if not bahaya:
        dlg.bind("<Return>", lambda e: tutup(True))
    dlg.protocol("WM_DELETE_WINDOW", lambda: tutup(False))

    dlg.update_idletasks()
    x = top.winfo_rootx() + (top.winfo_width() - dlg.winfo_reqwidth()) // 2
    y = top.winfo_rooty() + (top.winfo_height() - dlg.winfo_reqheight()) // 2
    dlg.geometry(f"+{max(x, 0)}+{max(y, 0)}")
    dlg.deiconify()
    dlg.focus_force()
    try:
        dlg.wait_visibility()
        dlg.grab_set()
    except tk.TclError:
        pass
    dlg.wait_window()
    return hasil["ok"]


# ---------------- Tema ttk ----------------
def terapkan_tema(root):
    root.option_add("*TCombobox*Listbox.font", (FONT, 10))
    root.option_add("*TCombobox*Listbox.selectBackground", PRIMARY)
    root.option_add("*TCombobox*Listbox.selectForeground", "#ffffff")

    s = ttk.Style(root)
    s.theme_use("clam")
    s.configure(".", font=(FONT, 10), background=BG)
    s.configure("Card.TFrame", background=CARD)

    for nama in ("TEntry", "TCombobox", "TSpinbox"):
        s.configure(nama, padding=(10, 8), fieldbackground=CARD, foreground=TEXT,
                    bordercolor=BORDER, lightcolor=BORDER, darkcolor=BORDER,
                    arrowcolor=MUTED, insertcolor=TEXT)
        s.map(nama, bordercolor=[("focus", PRIMARY)], lightcolor=[("focus", PRIMARY)],
              darkcolor=[("focus", PRIMARY)])
    s.map("TCombobox", fieldbackground=[("readonly", CARD)],
          selectbackground=[("readonly", CARD)], selectforeground=[("readonly", TEXT)])

    for nama in ("Error.TEntry", "Error.TSpinbox"):
        s.configure(nama, bordercolor=DANGER, lightcolor=DANGER, darkcolor=DANGER)
        s.map(nama, bordercolor=[("focus", DANGER)], lightcolor=[("focus", DANGER)],
              darkcolor=[("focus", DANGER)])

    s.layout("Treeview", [("Treeview.treearea", {"sticky": "nswe"})])
    s.configure("Treeview", rowheight=40, font=(FONT, 10), background=CARD,
                fieldbackground=CARD, foreground=TEXT, borderwidth=0)
    s.configure("Treeview.Heading", font=(FONT, 9, "bold"), background="#f1f5f9",
                foreground=MUTED, padding=(10, 10), relief="flat", borderwidth=0)
    s.map("Treeview.Heading", background=[("active", "#e2e8f0")])
    s.map("Treeview", background=[("selected", PRIMARY_SOFT)],
          foreground=[("selected", TEXT)])

    s.configure("Vertical.TScrollbar", background="#cbd5e1", troughcolor="#f1f5f9",
                bordercolor="#f1f5f9", arrowcolor=MUTED, relief="flat")
    s.map("Vertical.TScrollbar", background=[("active", "#94a3b8")])


# ---------------- Model ----------------
class RatingHotel:
    def __init__(self, nama_hotel, kota, rating, jumlah_ulasan, kategori="Bintang 4"):
        self.nama_hotel = nama_hotel
        self.kota = kota
        self.rating = float(rating)
        self.jumlah_ulasan = int(jumlah_ulasan)
        self.kategori = kategori

    def to_list(self):
        return [self.nama_hotel, self.kota, f"{self.rating:g}",
                self.jumlah_ulasan, self.kategori]

    def __str__(self):
        return (f"{self.nama_hotel} ({self.kota}) - Rating: {self.rating}/5.0 "
                f"({self.jumlah_ulasan} ulasan) - {self.kategori}")


class Pengulas:
    def __init__(self, id_pengulas, nama, email):
        self.id = id_pengulas
        self.nama = nama
        self.email = email

    def to_list(self):
        return [self.id, self.nama, self.email]

    def __str__(self):
        return f"{self.nama} ({self.id}) - {self.email}"


# ---------------- Penyimpanan CSV ----------------
class RatingRepository:
    """Menyimpan data di memori dan menyinkronkannya ke file CSV."""

    def __init__(self, path=FILE_CSV):
        self.path = path
        self.data = []
        self.terakhir_simpan = ""
        self.load()

    def load(self):
        self.data = []
        if not os.path.exists(self.path):
            return
        try:
            with open(self.path, newline="", encoding="utf-8-sig") as f:
                reader = csv.reader(f)
                next(reader, None)
                for row in reader:
                    if len(row) < 4 or not row[0].strip():
                        continue
                    try:
                        rating = float(row[2].replace(",", "."))
                    except ValueError:
                        rating = 0.0
                    try:
                        ulasan = int(float(row[3]))
                    except ValueError:
                        ulasan = 0
                    kategori = row[4].strip() if len(row) > 4 and row[4].strip() else "Bintang 4"
                    self.data.append(RatingHotel(row[0].strip(), row[1].strip(),
                                                 rating, ulasan, kategori))
        except Exception as e:
            messagebox.showerror("Gagal membaca file", str(e))

    def _tulis(self, path, encoding="utf-8"):
        with open(path, "w", newline="", encoding=encoding) as f:
            writer = csv.writer(f)
            writer.writerow(HEADER)
            for item in self.data:
                writer.writerow(item.to_list())

    def save(self):
        try:
            self._tulis(self.path)
            self.terakhir_simpan = datetime.now().strftime("%H:%M:%S")
            return True
        except PermissionError:
            messagebox.showerror(
                "Gagal menyimpan",
                "File hotel_rating.csv sedang dibuka di program lain (mis. Excel).\n"
                "Tutup dulu lalu coba lagi.")
        except Exception as e:
            messagebox.showerror("Gagal menyimpan", str(e))
        return False

    def ekspor(self, path):
        try:
            self._tulis(path, encoding="utf-8-sig")
            return True
        except Exception as e:
            messagebox.showerror("Gagal ekspor", str(e))
            return False

    def tambah(self, item):
        self.data.append(item)
        if self.save():
            return True
        self.data.pop()
        return False

    def ubah(self, index, item):
        lama = self.data[index]
        self.data[index] = item
        if self.save():
            return True
        self.data[index] = lama
        return False

    def hapus(self, index):
        item = self.data.pop(index)
        if self.save():
            return True
        self.data.insert(index, item)
        return False