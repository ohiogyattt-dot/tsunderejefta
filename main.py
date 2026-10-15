import os
import tkinter as tk
from datetime import datetime
from models import (RatingRepository, FILE_CSV, terapkan_tema, Tombol,
                    BG, SIDEBAR, SIDEBAR_HOVER, PRIMARY, PRIMARY_SOFT, TEXT, TEXT2,
                    MUTED, BORDER, CARD, SUCCESS, SUCCESS_SOFT, WARNING, DANGER,
                    STAR, FONT)
from tambah_rating import TambahRatingFrame
from tampil_rating import TampilRatingFrame


def potong(teks, n):
    return teks if len(teks) <= n else teks[:max(n - 1, 1)] + "…"


# ============================================================
#  HALAMAN DASHBOARD
# ============================================================
class DashboardFrame(tk.Frame):
    def __init__(self, parent, repo):
        super().__init__(parent, bg=BG)
        self.repo = repo
        kunci = ("total", "rata", "ulasan", "unggul")
        self.nilai = {k: tk.StringVar(value="-") for k in kunci}
        self.sub = {k: tk.StringVar(value="") for k in kunci}
        self._buat_ui()

    def _buat_ui(self):
        self.columnconfigure(0, weight=1)
        self.rowconfigure(1, weight=1)
        self.rowconfigure(2, weight=1)

        kpi = tk.Frame(self, bg=BG)
        kpi.grid(row=0, column=0, sticky="ew")
        daftar = [("total", "Total Hotel", "▦", PRIMARY, PRIMARY_SOFT),
                  ("rata", "Rata-rata Rating", "★", STAR, "#fef3c7"),
                  ("ulasan", "Total Ulasan", "✉", "#7c3aed", "#ede9fe"),
                  ("unggul", "Hotel Unggulan", "✔", SUCCESS, SUCCESS_SOFT)]
        for i, (k, judul, ikon, fg, soft) in enumerate(daftar):
            self._kpi(kpi, i, k, judul, ikon, fg, soft)

        baris1 = self._baris(1)
        self.cv_dist = self._kartu(baris1, 0, "Distribusi Rating", "Jumlah hotel per bintang")
        self.cv_top = self._kartu(baris1, 1, "Hotel Terbaik", "Rating tertinggi")
        baris2 = self._baris(2)
        self.cv_kota = self._kartu(baris2, 0, "Rating per Kota", "Rata-rata rating tiap kota")
        self.cv_kat = self._kartu(baris2, 1, "Komposisi Kategori", "Jumlah hotel per kategori")

        self.cv_dist.bind("<Configure>", lambda e: self._gambar_dist())
        self.cv_top.bind("<Configure>", lambda e: self._gambar_top())
        self.cv_kota.bind("<Configure>", lambda e: self._gambar_kota())
        self.cv_kat.bind("<Configure>", lambda e: self._gambar_kat())

    def _baris(self, row):
        f = tk.Frame(self, bg=BG)
        f.grid(row=row, column=0, sticky="nsew", pady=(12, 0))
        f.columnconfigure(0, weight=1, uniform="grafik")
        f.columnconfigure(1, weight=1, uniform="grafik")
        f.rowconfigure(0, weight=1)
        return f

    def _kpi(self, parent, kolom, kunci, judul, ikon, fg, soft):
        parent.columnconfigure(kolom, weight=1, uniform="kpi")
        card = tk.Frame(parent, bg=CARD, highlightbackground=BORDER, highlightthickness=1)
        card.grid(row=0, column=kolom, sticky="ew", padx=(0 if kolom == 0 else 14, 0))
        isi = tk.Frame(card, bg=CARD)
        isi.pack(fill="x", padx=20, pady=12)
        kiri = tk.Frame(isi, bg=CARD)
        kiri.pack(side="left", fill="x", expand=True)
        tk.Label(kiri, text=judul, bg=CARD, fg=MUTED, font=(FONT, 10)).pack(anchor="w")
        tk.Label(kiri, textvariable=self.nilai[kunci], bg=CARD, fg=TEXT,
                 font=(FONT, 22, "bold")).pack(anchor="w")
        tk.Label(kiri, textvariable=self.sub[kunci], bg=CARD, fg=MUTED,
                 font=(FONT, 9)).pack(anchor="w")
        tk.Label(isi, text=ikon, bg=soft, fg=fg, font=(FONT, 16),
                 padx=12, pady=6).pack(side="right", anchor="n")

    def _kartu(self, parent, kolom, judul, sub):
        card = tk.Frame(parent, bg=CARD, highlightbackground=BORDER, highlightthickness=1)
        card.grid(row=0, column=kolom, sticky="nsew", padx=(0 if kolom == 0 else 14, 0))
        kepala = tk.Frame(card, bg=CARD)
        kepala.pack(fill="x", padx=20, pady=(12, 4))
        tk.Label(kepala, text=judul, bg=CARD, fg=TEXT, font=(FONT, 12, "bold")).pack(side="left")
        tk.Label(kepala, text=sub, bg=CARD, fg=MUTED, font=(FONT, 9)).pack(
            side="left", padx=10, pady=(3, 0))
        cv = tk.Canvas(card, bg=CARD, highlightthickness=0)
        cv.pack(fill="both", expand=True, padx=20, pady=(0, 12))
        return cv

    # ---------------------------------------------------- Data
    def refresh(self):
        data = self.repo.data
        n = len(data)
        if n:
            rata = sum(d.rating for d in data) / n
            ulasan = sum(d.jumlah_ulasan for d in data)
            unggul = sum(1 for d in data if d.rating >= 4.5)
            kota = len({d.kota for d in data})
            self.nilai["total"].set(str(n))
            self.sub["total"].set(f"tersebar di {kota} kota")
            self.nilai["rata"].set(f"{rata:.2f}")
            self.sub["rata"].set("dari skala 5.0")
            self.nilai["ulasan"].set(f"{ulasan:,}")
            self.sub["ulasan"].set(f"rata-rata {ulasan / n:,.0f} per hotel")
            self.nilai["unggul"].set(str(unggul))
            self.sub["unggul"].set(f"{unggul / n * 100:.0f}% berating ≥ 4.5")
        else:
            for k in self.nilai:
                self.nilai[k].set("-")
                self.sub[k].set("Belum ada data")
        self._gambar_dist()
        self._gambar_top()
        self._gambar_kota()
        self._gambar_kat()

    # ---------------------------------------------------- Gambar grafik
    def _kosong(self, c, w, h):
        c.create_text(w / 2, h / 2, text="Belum ada data", fill=MUTED, font=(FONT, 10))

    def _hbar(self, c, items, maks, fmt, warna):
        c.delete("all")
        w, h = c.winfo_width(), c.winfo_height()
        if w < 140 or h < 30:
            return
        if not items:
            self._kosong(c, w, h)
            return
        muat = max(1, int(h // 22))
        items = items[:muat]
        kiri, kanan = 110, 56
        step = min(40, h / len(items))
        tebal = max(6, min(14, step * 0.5))
        for i, (label, nilai) in enumerate(items):
            yc = step * i + step / 2
            c.create_text(kiri - 10, yc, text=potong(label, 14), anchor="e",
                          fill=TEXT2, font=(FONT, 9))
            c.create_rectangle(kiri, yc - tebal / 2, w - kanan, yc + tebal / 2,
                               fill="#f1f5f9", outline="")
            lebar = (w - kanan - kiri) * (nilai / maks if maks else 0)
            c.create_rectangle(kiri, yc - tebal / 2, kiri + max(lebar, 2), yc + tebal / 2,
                               fill=warna, outline="")
            c.create_text(w - kanan + 8, yc, text=fmt(nilai), anchor="w",
                          fill=TEXT, font=(FONT, 9, "bold"))

    def _gambar_kota(self):
        per_kota = {}
        for d in self.repo.data:
            per_kota.setdefault(d.kota, []).append(d.rating)
        items = sorted(((k, sum(v) / len(v)) for k, v in per_kota.items()),
                       key=lambda x: -x[1])[:6]
        self._hbar(self.cv_kota, items, 5.0, lambda v: f"{v:.2f}", PRIMARY)

    def _gambar_kat(self):
        hitung = {}
        for d in self.repo.data:
            hitung[d.kategori] = hitung.get(d.kategori, 0) + 1
        items = sorted(hitung.items(), key=lambda x: -x[1])[:6]
        maks = max((v for _, v in items), default=1)
        self._hbar(self.cv_kat, items, maks, lambda v: f"{int(v)} hotel", "#7c3aed")

    def _gambar_dist(self):
        c = self.cv_dist
        c.delete("all")
        w, h = c.winfo_width(), c.winfo_height()
        if w < 140 or h < 70:
            return
        data = self.repo.data
        if not data:
            self._kosong(c, w, h)
            return
        hitung = {i: 0 for i in range(1, 6)}
        for d in data:
            hitung[min(5, max(1, int(d.rating + 0.5)))] += 1
        maks = max(hitung.values()) or 1
        warna = {1: DANGER, 2: "#f97316", 3: WARNING, 4: PRIMARY, 5: SUCCESS}
        bawah, atas = 24, 20
        slot = w / 5
        tebal = min(48, slot * 0.55)
        y1 = h - bawah
        for i in range(1, 6):
            n = hitung[i]
            cx = slot * (i - 1) + slot / 2
            tinggi = (h - bawah - atas) * n / maks
            y0 = y1 - max(tinggi, 2)
            c.create_rectangle(cx - tebal / 2, y0, cx + tebal / 2, y1,
                               fill=warna[i] if n else BORDER, outline="")
            c.create_text(cx, y0 - 9, text=str(n), fill=TEXT, font=(FONT, 10, "bold"))
            c.create_text(cx, y1 + 12, text=f"{i} ★", fill=MUTED, font=(FONT, 9))

    def _gambar_top(self):
        c = self.cv_top
        c.delete("all")
        w, h = c.winfo_width(), c.winfo_height()
        if w < 140 or h < 30:
            return
        top = sorted(self.repo.data, key=lambda d: (-d.rating, -d.jumlah_ulasan))[:5]
        if not top:
            self._kosong(c, w, h)
            return

        # Setiap baris minimal 24 px. Kalau ruang lega -> 2 baris teks, kalau sempit -> 1 baris ringkas.
        muat = max(1, int(h // 24))
        top = top[:muat]
        step = min(52, h / len(top))
        dua_baris = step >= 40
        r = 13 if dua_baris else 10

        for i, d in enumerate(top):
            yc = step * i + step / 2
            c.create_oval(2, yc - r, 2 + 2 * r, yc + r,
                          fill=STAR if i == 0 else "#e2e8f0", outline="")
            c.create_text(2 + r, yc, text=str(i + 1),
                          fill="#ffffff" if i == 0 else TEXT2,
                          font=(FONT, 10 if dua_baris else 9, "bold"))
            x_teks = 2 * r + 12

            c.create_text(w - 4, yc, text=f"★ {d.rating:.1f}", anchor="e",
                          fill=STAR, font=(FONT, 12 if dua_baris else 11, "bold"))

            if dua_baris:
                maks_char = max(10, int((w - x_teks - 70) / 7))
                c.create_text(x_teks, yc - 8, text=potong(d.nama_hotel, maks_char),
                              anchor="w", fill=TEXT, font=(FONT, 10, "bold"))
                c.create_text(x_teks, yc + 9,
                              text=potong(f"{d.kota}  •  {d.jumlah_ulasan:,} ulasan",
                                          maks_char + 6),
                              anchor="w", fill=MUTED, font=(FONT, 9))
            else:
                maks_char = max(8, int((w - x_teks - 70) / 8))
                item = c.create_text(x_teks, yc, text=potong(d.nama_hotel, maks_char),
                                     anchor="w", fill=TEXT, font=(FONT, 10, "bold"))
                x_kota = c.bbox(item)[2] + 8
                sisa = int((w - 70 - x_kota) / 6)
                if sisa >= 5:
                    c.create_text(x_kota, yc, text=potong(d.kota, sisa), anchor="w",
                                  fill=MUTED, font=(FONT, 9))


# ============================================================
#  APLIKASI UTAMA
# ============================================================
class App(tk.Tk):
    HALAMAN = [
        ("dashboard", "▦", "Dashboard", "Dashboard",
         "Ringkasan performa rating seluruh hotel"),
        ("daftar", "☰", "Data Hotel", "Data Hotel",
         "Cari, urutkan, ubah, dan hapus data rating"),
        ("tambah", "✚", "Input Data", "Input Data Hotel",
         "Tambahkan hotel baru atau perbarui data yang sudah ada"),
    ]

    def __init__(self):
        super().__init__()
        self.title("Sistem Rating Hotel")
        lebar = 1260
        tinggi = min(800, self.winfo_screenheight() - 90)
        x = max((self.winfo_screenwidth() - lebar) // 2, 0)
        y = max((self.winfo_screenheight() - tinggi) // 2 - 20, 0)
        self.geometry(f"{lebar}x{tinggi}+{x}+{y}")
        self.minsize(1100, 640)
        self.configure(bg=BG)
        terapkan_tema(self)

        self.repo = RatingRepository(FILE_CSV)
        self.toast_id = None
        self.aktif = None
        self.nav = {}
        self.var_bar = tk.StringVar()

        self._buat_sidebar()

        kanan = tk.Frame(self, bg=BG)
        kanan.pack(side="left", fill="both", expand=True)

        # status bar (dipasang dulu agar selalu di bawah)
        bar = tk.Frame(kanan, bg=CARD, highlightbackground=BORDER, highlightthickness=1)
        bar.pack(side="bottom", fill="x")
        tk.Label(bar, textvariable=self.var_bar, bg=CARD, fg=MUTED, font=(FONT, 9),
                 anchor="w", padx=28, pady=7).pack(fill="x")

        # header halaman
        top = tk.Frame(kanan, bg=BG)
        top.pack(fill="x", padx=28, pady=(18, 10))
        judul = tk.Frame(top, bg=BG)
        judul.pack(side="left")
        self.lbl_judul = tk.Label(judul, text="", bg=BG, fg=TEXT, font=(FONT, 20, "bold"))
        self.lbl_judul.pack(anchor="w")
        self.lbl_sub = tk.Label(judul, text="", bg=BG, fg=MUTED, font=(FONT, 10))
        self.lbl_sub.pack(anchor="w")
        Tombol(top, "＋  Hotel Baru", self.tambah_baru).pack(side="right")
        tk.Label(top, text=datetime.now().strftime("%d/%m/%Y"), bg=BG, fg=MUTED,
                 font=(FONT, 10)).pack(side="right", padx=18)

        wadah = tk.Frame(kanan, bg=BG)
        wadah.pack(fill="both", expand=True, padx=28, pady=(0, 16))
        wadah.rowconfigure(0, weight=1)
        wadah.columnconfigure(0, weight=1)

        self.dashboard = DashboardFrame(wadah, self.repo)
        self.tampil = TampilRatingFrame(wadah, self.repo, on_edit=self._edit,
                                        on_status=self.toast, on_ubah=self._data_berubah)
        self.tambah = TambahRatingFrame(wadah, self.repo, on_simpan=self._selesai_simpan,
                                        on_batal=lambda: self.tampilkan("daftar"))
        self.halaman = {"dashboard": self.dashboard, "daftar": self.tampil,
                        "tambah": self.tambah}
        for f in self.halaman.values():
            f.grid(row=0, column=0, sticky="nsew")

        self.lbl_toast = tk.Label(self, text="", bg=SUCCESS, fg="#ffffff",
                                  font=(FONT, 10, "bold"), padx=20, pady=12)

        self.bind("<Control-n>", lambda e: self.tambah_baru())
        self.bind("<Control-f>", lambda e: self._cari())
        self.bind("<F5>", lambda e: self.tampil.muat_ulang())

        self._update_bar()
        self.tampilkan("dashboard")

    # ---------------------------------------------------- Sidebar
    def _buat_sidebar(self):
        side = tk.Frame(self, bg=SIDEBAR, width=240)
        side.pack(side="left", fill="y")
        side.pack_propagate(False)

        logo = tk.Frame(side, bg=SIDEBAR)
        logo.pack(fill="x", padx=24, pady=(28, 28))
        tk.Label(logo, text="🏨", bg=PRIMARY, fg="#ffffff", font=(FONT, 16),
                 padx=8, pady=4).pack(side="left")
        teks = tk.Frame(logo, bg=SIDEBAR)
        teks.pack(side="left", padx=12)
        tk.Label(teks, text="RatingHotel", bg=SIDEBAR, fg="#ffffff",
                 font=(FONT, 14, "bold")).pack(anchor="w")
        tk.Label(teks, text="Management System", bg=SIDEBAR, fg="#94a3b8",
                 font=(FONT, 9)).pack(anchor="w")

        tk.Label(side, text="MENU", bg=SIDEBAR, fg="#64748b",
                 font=(FONT, 9, "bold")).pack(anchor="w", padx=28, pady=(0, 8))

        for kode, ikon, nama, _judul, _sub in self.HALAMAN:
            row = tk.Frame(side, bg=SIDEBAR, cursor="hand2")
            row.pack(fill="x")
            ind = tk.Frame(row, bg=SIDEBAR, width=4)
            ind.pack(side="left", fill="y")
            lbl = tk.Label(row, text=f"{ikon}     {nama}", bg=SIDEBAR, fg="#cbd5e1",
                           anchor="w", font=(FONT, 11, "bold"), padx=24, pady=13,
                           cursor="hand2")
            lbl.pack(side="left", fill="x", expand=True)
            for w in (row, lbl):
                w.bind("<Button-1>", lambda e, k=kode: self.tampilkan(k))
                w.bind("<Enter>", lambda e, k=kode: self._hover_nav(k, True))
                w.bind("<Leave>", lambda e, k=kode: self._hover_nav(k, False))
            self.nav[kode] = (row, ind, lbl)

        bawah = tk.Frame(side, bg=SIDEBAR)
        bawah.pack(side="bottom", fill="x", padx=24, pady=22)
        Tombol(bawah, "Keluar", self.destroy, gaya="danger").pack(fill="x")
        tk.Label(bawah, text="Ctrl+N  Hotel baru\nCtrl+F  Cari data\nF5  Muat ulang",
                 bg=SIDEBAR, fg="#64748b", font=(FONT, 9), justify="left",
                 anchor="w").pack(fill="x", pady=(0, 16), side="top")

    def _hover_nav(self, kode, masuk):
        if kode == self.aktif:
            return
        row, ind, lbl = self.nav[kode]
        warna = SIDEBAR_HOVER if masuk else SIDEBAR
        row.config(bg=warna)
        ind.config(bg=warna)
        lbl.config(bg=warna)

    # ---------------------------------------------------- Navigasi
    def tampilkan(self, kode):
        self.aktif = kode
        for k, (row, ind, lbl) in self.nav.items():
            if k == kode:
                row.config(bg=SIDEBAR_HOVER)
                lbl.config(bg=SIDEBAR_HOVER, fg="#ffffff")
                ind.config(bg="#818cf8")
            else:
                row.config(bg=SIDEBAR)
                lbl.config(bg=SIDEBAR, fg="#cbd5e1")
                ind.config(bg=SIDEBAR)
        for k, _ikon, _nama, judul, sub in self.HALAMAN:
            if k == kode:
                self.lbl_judul.config(text=judul)
                self.lbl_sub.config(text=sub)
        self.halaman[kode].tkraise()
        if kode == "dashboard":
            self.dashboard.refresh()
        elif kode == "daftar":
            self.tampil.refresh()

    def tambah_baru(self):
        self.tambah.bersihkan()
        self.tampilkan("tambah")

    def _cari(self):
        self.tampilkan("daftar")
        self.tampil.fokus_cari()

    # ---------------------------------------------------- Notifikasi & status
    def toast(self, teks, jenis="sukses"):
        self.lbl_toast.config(text=("✔  " if jenis == "sukses" else "✖  ") + teks,
                              bg=SUCCESS if jenis == "sukses" else DANGER)
        self.lbl_toast.place(relx=1.0, rely=1.0, x=-28, y=-56, anchor="se")
        self.lbl_toast.lift()
        if self.toast_id:
            self.after_cancel(self.toast_id)
        self.toast_id = self.after(3000, self.lbl_toast.place_forget)

    def _update_bar(self):
        simpan = self.repo.terakhir_simpan or "-"
        self.var_bar.set(f"●  {os.path.basename(FILE_CSV)}        "
                         f"{len(self.repo.data)} data        "
                         f"Terakhir disimpan: {simpan}")

    # ---------------------------------------------------- Callback
    def _edit(self, index):
        self.tambah.muat_edit(index)
        self.tampilkan("tambah")

    def _selesai_simpan(self, pesan, edit):
        self.toast(pesan)
        self.dashboard.refresh()
        self.tampil.refresh()
        self._update_bar()
        if edit:
            self.tampilkan("daftar")

    def _data_berubah(self):
        self.tambah.batal_edit_jika_perlu()
        self.dashboard.refresh()
        self._update_bar()


if __name__ == "__main__":
    try:
        import ctypes
        ctypes.windll.shcore.SetProcessDpiAwareness(1)
    except Exception:
        pass
    App().mainloop()