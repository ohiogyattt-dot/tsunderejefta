import tkinter as tk
from tkinter import ttk
from models import (RatingHotel, RatingRepository, Tombol, konfirmasi, info_status,
                    KATEGORI, FILE_CSV, terapkan_tema,
                    BG, CARD, TEXT, TEXT2, MUTED, BORDER, PRIMARY, PRIMARY_SOFT,
                    SUCCESS, WARNING, DANGER, STAR, FONT)


class TambahRatingFrame(tk.Frame):
    def __init__(self, parent, repo, on_simpan=None, on_batal=None):
        super().__init__(parent, bg=BG)
        self.repo = repo
        self.on_simpan = on_simpan
        self.on_batal = on_batal
        self.edit_index = None

        self.var_nama = tk.StringVar()
        self.var_kota = tk.StringVar()
        self.var_rating = tk.StringVar(value="4.0")
        self.var_ulasan = tk.StringVar()
        self.var_kategori = tk.StringVar(value="Bintang 4")

        self.err = {}      # kunci -> StringVar pesan error
        self.gaya = {}     # kunci -> (style normal, style error)
        self.widget = {}   # kunci -> widget

        self.pv_nama = tk.StringVar()
        self.pv_kota = tk.StringVar()
        self.pv_bintang = tk.StringVar()
        self.pv_nilai = tk.StringVar()
        self.pv_info = tk.StringVar()
        self.pv_kategori = tk.StringVar()
        self.pv_status = tk.StringVar()

        self._buat_ui()

        for kunci, var in (("nama", self.var_nama), ("kota", self.var_kota),
                           ("rating", self.var_rating), ("ulasan", self.var_ulasan)):
            var.trace_add("write", lambda *_a, k=kunci: self._bersih_error(k))
        for var in (self.var_nama, self.var_kota, self.var_rating,
                    self.var_ulasan, self.var_kategori):
            var.trace_add("write", lambda *_a: self._update_preview())
        self._update_preview()

    # ---------------------------------------------------- UI
    def _buat_ui(self):
        self.columnconfigure(0, weight=3, uniform="kolom")
        self.columnconfigure(1, weight=2, uniform="kolom")
        self.rowconfigure(0, weight=1)

        # ===== Kartu form
        form = tk.Frame(self, bg=CARD, highlightbackground=BORDER, highlightthickness=1)
        form.grid(row=0, column=0, sticky="nsew", padx=(0, 18))
        isi = tk.Frame(form, bg=CARD)
        isi.pack(fill="both", expand=True, padx=32, pady=24)

        self.lbl_judul = tk.Label(isi, text="Tambah Hotel Baru", bg=CARD, fg=TEXT,
                                  font=(FONT, 15, "bold"), anchor="w")
        self.lbl_judul.pack(fill="x")
        self.lbl_sub = tk.Label(isi, text="Lengkapi data di bawah ini, lalu simpan.",
                                bg=CARD, fg=MUTED, font=(FONT, 10), anchor="w")
        self.lbl_sub.pack(fill="x", pady=(2, 4))

        self.ent_nama = self._field(
            isi, "nama", "Nama Hotel",
            ttk.Entry(isi, textvariable=self.var_nama, style="TEntry"),
            "TEntry", "Error.TEntry")
        self._field(
            isi, "kota", "Kota",
            ttk.Entry(isi, textvariable=self.var_kota, style="TEntry"),
            "TEntry", "Error.TEntry")

        baris = tk.Frame(isi, bg=CARD)
        baris.pack(fill="x")
        baris.columnconfigure(0, weight=1, uniform="dua")
        baris.columnconfigure(1, weight=1, uniform="dua")
        kiri = tk.Frame(baris, bg=CARD)
        kiri.grid(row=0, column=0, sticky="ew", padx=(0, 8))
        kanan = tk.Frame(baris, bg=CARD)
        kanan.grid(row=0, column=1, sticky="ew", padx=(8, 0))

        self._field(
            kiri, "rating", "Rating (1.0 - 5.0)",
            ttk.Spinbox(kiri, from_=1, to=5, increment=0.1, format="%.1f",
                        textvariable=self.var_rating, style="TSpinbox"),
            "TSpinbox", "Error.TSpinbox")
        self._field(
            kanan, "ulasan", "Jumlah Ulasan",
            ttk.Entry(kanan, textvariable=self.var_ulasan, style="TEntry"),
            "TEntry", "Error.TEntry")

        self.cmb_kategori = ttk.Combobox(isi, textvariable=self.var_kategori,
                                         values=KATEGORI, state="readonly")
        self._field(isi, "kategori", "Kategori", self.cmb_kategori, "TCombobox", None)

        for kunci in ("nama", "kota", "rating", "ulasan"):
            self.widget[kunci].bind("<Return>", lambda e: self.simpan())

        tombol = tk.Frame(isi, bg=CARD)
        tombol.pack(fill="x", pady=(20, 0))
        self.btn_simpan = Tombol(tombol, "Simpan Hotel", self.simpan)
        self.btn_simpan.pack(side="left")
        self.btn_batal = Tombol(tombol, "Reset Form", self.batal, gaya="ghost")
        self.btn_batal.pack(side="left", padx=10)
        tk.Label(tombol, text="Tekan Enter untuk menyimpan", bg=CARD, fg=MUTED,
                 font=(FONT, 9)).pack(side="right")

        # ===== Kartu pratinjau
        prev = tk.Frame(self, bg=CARD, highlightbackground=BORDER, highlightthickness=1)
        prev.grid(row=0, column=1, sticky="nsew")
        tk.Label(prev, text="PRATINJAU KARTU", bg=CARD, fg=MUTED,
                 font=(FONT, 9, "bold")).pack(anchor="w", padx=28, pady=(24, 12))

        kartu = tk.Frame(prev, bg=CARD, highlightbackground=BORDER, highlightthickness=1)
        kartu.pack(fill="x", padx=28)
        self.pv_band = tk.Frame(kartu, bg=PRIMARY, height=6)
        self.pv_band.pack(fill="x")
        dalam = tk.Frame(kartu, bg=CARD)
        dalam.pack(fill="x", padx=22, pady=18)

        tk.Label(dalam, textvariable=self.pv_nama, bg=CARD, fg=TEXT,
                 font=(FONT, 15, "bold"), wraplength=260, justify="left",
                 anchor="w").pack(fill="x")
        tk.Label(dalam, textvariable=self.pv_kota, bg=CARD, fg=MUTED,
                 font=(FONT, 10), anchor="w").pack(fill="x", pady=(2, 12))
        tk.Label(dalam, textvariable=self.pv_bintang, bg=CARD, fg=STAR,
                 font=(FONT, 20), anchor="w").pack(fill="x")
        tk.Label(dalam, textvariable=self.pv_nilai, bg=CARD, fg=TEXT,
                 font=(FONT, 30, "bold"), anchor="w").pack(fill="x")
        tk.Label(dalam, textvariable=self.pv_info, bg=CARD, fg=MUTED,
                 font=(FONT, 10), anchor="w").pack(fill="x", pady=(0, 12))

        chips = tk.Frame(dalam, bg=CARD)
        chips.pack(fill="x")
        self.lbl_status = tk.Label(chips, textvariable=self.pv_status, bg=PRIMARY,
                                   fg="#ffffff", font=(FONT, 9, "bold"), padx=12, pady=3)
        self.lbl_status.pack(side="left")
        tk.Label(chips, textvariable=self.pv_kategori, bg=PRIMARY_SOFT, fg=PRIMARY,
                 font=(FONT, 9, "bold"), padx=12, pady=3).pack(side="left", padx=8)

        # Panduan
        tk.Label(prev, text="PANDUAN PENILAIAN", bg=CARD, fg=MUTED,
                 font=(FONT, 9, "bold")).pack(anchor="w", padx=28, pady=(22, 8))
        panduan = [("4.5 - 5.0", "Sangat Baik", SUCCESS), ("4.0 - 4.4", "Baik", PRIMARY),
                   ("3.0 - 3.9", "Cukup", WARNING), ("1.0 - 2.9", "Kurang", DANGER)]
        for rentang, label, warna in panduan:
            r = tk.Frame(prev, bg=CARD)
            r.pack(fill="x", padx=28, pady=2)
            tk.Label(r, text="●", bg=CARD, fg=warna, font=(FONT, 10)).pack(side="left")
            tk.Label(r, text=label, bg=CARD, fg=TEXT2, font=(FONT, 10)).pack(
                side="left", padx=8)
            tk.Label(r, text=rentang, bg=CARD, fg=MUTED, font=(FONT, 10)).pack(side="right")

    def _field(self, parent, kunci, label, widget, normal, error):
        tk.Label(parent, text=label, bg=CARD, fg=TEXT2,
                 font=(FONT, 10, "bold")).pack(anchor="w", pady=(12, 4))
        widget.pack(fill="x")
        pesan = tk.StringVar()
        tk.Label(parent, textvariable=pesan, bg=CARD, fg=DANGER, font=(FONT, 9),
                 anchor="w").pack(fill="x")
        self.err[kunci] = pesan
        self.gaya[kunci] = (normal, error)
        self.widget[kunci] = widget
        return widget

    # ---------------------------------------------------- Pratinjau
    def _update_preview(self):
        self.pv_nama.set(self.var_nama.get().strip() or "Nama Hotel")
        self.pv_kota.set("📍 " + (self.var_kota.get().strip() or "Kota"))
        try:
            r = float(self.var_rating.get().replace(",", "."))
            r = max(0.0, min(5.0, r))
        except ValueError:
            r = 0.0
        penuh = int(r + 0.5)
        self.pv_bintang.set("★" * penuh + "☆" * (5 - penuh))
        self.pv_nilai.set(f"{r:.1f}")
        try:
            ulasan = int(self.var_ulasan.get().strip())
        except ValueError:
            ulasan = 0
        self.pv_info.set(f"dari 5.0  •  {ulasan:,} ulasan")
        self.pv_kategori.set(self.var_kategori.get().upper())
        if r > 0:
            label, warna = info_status(r)
        else:
            label, warna = "BELUM DINILAI", MUTED
        self.pv_status.set(label.upper())
        self.lbl_status.config(bg=warna)
        self.pv_band.config(bg=warna)

    # ---------------------------------------------------- Validasi
    def _bersih_error(self, kunci):
        self.err[kunci].set("")
        self.widget[kunci].configure(style=self.gaya[kunci][0])

    def _salah(self, kunci, pesan):
        self.err[kunci].set(pesan)
        self.widget[kunci].configure(style=self.gaya[kunci][1])

    def _validasi(self):
        for kunci in ("nama", "kota", "rating", "ulasan"):
            self._bersih_error(kunci)
        ok = True

        nama = self.var_nama.get().strip()
        if not nama:
            self._salah("nama", "Nama hotel wajib diisi.")
            ok = False
        elif len(nama) < 3:
            self._salah("nama", "Nama hotel minimal 3 karakter.")
            ok = False

        kota = self.var_kota.get().strip()
        if not kota:
            self._salah("kota", "Kota wajib diisi.")
            ok = False

        rating = 0.0
        try:
            rating = float(self.var_rating.get().replace(",", "."))
            if not 1 <= rating <= 5:
                raise ValueError
        except ValueError:
            self._salah("rating", "Isi angka 1.0 sampai 5.0.")
            ok = False

        ulasan = 0
        teks_ulasan = self.var_ulasan.get().strip()
        if not teks_ulasan:
            self._salah("ulasan", "Jumlah ulasan wajib diisi.")
            ok = False
        else:
            try:
                ulasan = int(teks_ulasan)
                if ulasan < 0:
                    raise ValueError
            except ValueError:
                self._salah("ulasan", "Isi bilangan bulat ≥ 0.")
                ok = False

        if not ok:
            return None
        return RatingHotel(nama, kota, round(rating, 1), ulasan, self.var_kategori.get())

    def _duplikat(self, item):
        for d in self.repo.data:
            if (d.nama_hotel.lower() == item.nama_hotel.lower()
                    and d.kota.lower() == item.kota.lower()):
                return True
        return False

    # ---------------------------------------------------- Aksi
    def simpan(self):
        item = self._validasi()
        if not item:
            return

        if self.edit_index is None:
            if self._duplikat(item) and not konfirmasi(
                    self, "Data mungkin ganda",
                    f"Hotel '{item.nama_hotel}' di {item.kota} sudah ada. "
                    "Tetap tambahkan sebagai data baru?", "Tetap Tambahkan"):
                return
            if self.repo.tambah(item):
                self.bersihkan()
                if self.on_simpan:
                    self.on_simpan(f"Hotel '{item.nama_hotel}' berhasil ditambahkan.", False)
        else:
            if self.repo.ubah(self.edit_index, item):
                self.bersihkan()
                if self.on_simpan:
                    self.on_simpan(f"Data '{item.nama_hotel}' berhasil diperbarui.", True)

    def muat_edit(self, index):
        item = self.repo.data[index]
        self.edit_index = index
        nilai = list(KATEGORI)
        if item.kategori not in nilai:
            nilai.append(item.kategori)
        self.cmb_kategori["values"] = nilai

        self.var_nama.set(item.nama_hotel)
        self.var_kota.set(item.kota)
        self.var_rating.set(f"{item.rating:.1f}")
        self.var_ulasan.set(str(item.jumlah_ulasan))
        self.var_kategori.set(item.kategori)

        self.lbl_judul.config(text="Edit Data Hotel")
        self.lbl_sub.config(text=f"Mengubah data: {item.nama_hotel}")
        self.btn_simpan.ubah_teks("Simpan Perubahan")
        self.btn_batal.ubah_teks("Batal Edit")
        self.ent_nama.focus_set()

    def bersihkan(self):
        self.edit_index = None
        self.cmb_kategori["values"] = KATEGORI
        self.var_nama.set("")
        self.var_kota.set("")
        self.var_rating.set("4.0")
        self.var_ulasan.set("")
        self.var_kategori.set("Bintang 4")
        self.lbl_judul.config(text="Tambah Hotel Baru")
        self.lbl_sub.config(text="Lengkapi data di bawah ini, lalu simpan.")
        self.btn_simpan.ubah_teks("Simpan Hotel")
        self.btn_batal.ubah_teks("Reset Form")
        self.ent_nama.focus_set()

    def batal(self):
        sedang_edit = self.edit_index is not None
        self.bersihkan()
        if sedang_edit and self.on_batal:
            self.on_batal()

    def batal_edit_jika_perlu(self):
        if self.edit_index is not None:
            self.bersihkan()


if __name__ == "__main__":
    root = tk.Tk()
    root.title("Input Data Hotel")
    root.geometry("1000x640")
    root.configure(bg=BG)
    terapkan_tema(root)
    TambahRatingFrame(root, RatingRepository(FILE_CSV)).pack(
        fill="both", expand=True, padx=24, pady=24)
    root.mainloop()