import tkinter as tk
from tkinter import ttk, filedialog
from models import (RatingRepository, Tombol, konfirmasi, info_status, FILE_CSV,
                    terapkan_tema, BG, CARD, TEXT, MUTED, BORDER, DANGER, FONT)


class TampilRatingFrame(tk.Frame):
    COLUMNS = {
        "no": ("NO", 55, "center"),
        "nama": ("NAMA HOTEL", 260, "w"),
        "kota": ("KOTA", 140, "w"),
        "kategori": ("KATEGORI", 110, "w"),
        "rating": ("RATING", 90, "center"),
        "ulasan": ("ULASAN", 90, "center"),
        "status": ("STATUS", 120, "w"),
    }

    def __init__(self, parent, repo, on_edit=None, on_status=None, on_ubah=None):
        super().__init__(parent, bg=BG)
        self.repo = repo
        self.on_edit = on_edit
        self.on_status = on_status
        self.on_ubah = on_ubah
        self.sort_col = None
        self.sort_rev = False

        self.var_cari = tk.StringVar()
        self.var_kota = tk.StringVar(value="Semua Kota")
        self.var_kat = tk.StringVar(value="Semua Kategori")
        self.var_info = tk.StringVar()

        self._buat_ui()
        self.var_cari.trace_add("write", lambda *_: self.refresh())
        self.refresh()

    # ---------------------------------------------------- UI
    def _buat_ui(self):
        kartu = tk.Frame(self, bg=CARD, highlightbackground=BORDER, highlightthickness=1)
        kartu.pack(fill="both", expand=True)
        kartu.columnconfigure(0, weight=1)
        kartu.rowconfigure(1, weight=1)

        # --- toolbar atas
        bar = tk.Frame(kartu, bg=CARD)
        bar.grid(row=0, column=0, columnspan=2, sticky="ew", padx=18, pady=16)
        tk.Label(bar, text="🔍", bg=CARD, fg=MUTED, font=(FONT, 11)).pack(side="left")
        self.ent_cari = ttk.Entry(bar, textvariable=self.var_cari, width=30, style="TEntry")
        self.ent_cari.pack(side="left", padx=(6, 12))
        self.cmb_kota = ttk.Combobox(bar, textvariable=self.var_kota, state="readonly",
                                     width=16)
        self.cmb_kota.pack(side="left")
        self.cmb_kota.bind("<<ComboboxSelected>>", lambda e: self.refresh())
        self.cmb_kat = ttk.Combobox(bar, textvariable=self.var_kat, state="readonly",
                                    width=16)
        self.cmb_kat.pack(side="left", padx=10)
        self.cmb_kat.bind("<<ComboboxSelected>>", lambda e: self.refresh())
        Tombol(bar, "Reset", self.reset_filter, gaya="soft").pack(side="left")

        Tombol(bar, "Ekspor CSV", self.ekspor, gaya="ghost").pack(side="right")
        Tombol(bar, "Muat Ulang", self.muat_ulang, gaya="ghost").pack(side="right", padx=10)

        # --- tabel
        self.tree = ttk.Treeview(kartu, columns=list(self.COLUMNS), show="headings",
                                 selectmode="browse")
        for kode, (judul, lebar, anchor) in self.COLUMNS.items():
            self.tree.heading(kode, text=judul, anchor="center" if anchor == "center" else "w",
                              command=lambda c=kode: self.urutkan(c))
            self.tree.column(kode, width=lebar, anchor=anchor, stretch=(kode == "nama"))
        self.tree.tag_configure("genap", background="#f8fafc")
        self.tree.tag_configure("ganjil", background=CARD)
        self.tree.tag_configure("kurang", foreground=DANGER)
        sb = ttk.Scrollbar(kartu, orient="vertical", command=self.tree.yview)
        self.tree.configure(yscrollcommand=sb.set)
        self.tree.grid(row=1, column=0, sticky="nsew", padx=(18, 0))
        sb.grid(row=1, column=1, sticky="ns", padx=(0, 18))
        self.tree.bind("<<TreeviewSelect>>", lambda e: self._update_tombol())
        self.tree.bind("<Double-1>", lambda e: self.edit())
        self.tree.bind("<Return>", lambda e: self.edit())
        self.tree.bind("<Delete>", lambda e: self.hapus())

        self.lbl_kosong = tk.Label(self.tree, text="", bg=CARD, fg=MUTED, font=(FONT, 11))

        # --- toolbar bawah
        bawah = tk.Frame(kartu, bg=CARD)
        bawah.grid(row=2, column=0, columnspan=2, sticky="ew", padx=18, pady=16)
        self.btn_edit = Tombol(bawah, "Edit Terpilih", self.edit)
        self.btn_edit.pack(side="left")
        self.btn_hapus = Tombol(bawah, "Hapus Terpilih", self.hapus, gaya="danger")
        self.btn_hapus.pack(side="left", padx=10)
        tk.Label(bawah, text="Tip: klik 2x baris untuk edit  •  tombol Delete untuk hapus",
                 bg=CARD, fg=MUTED, font=(FONT, 9)).pack(side="left", padx=10)
        tk.Label(bawah, textvariable=self.var_info, bg=CARD, fg=TEXT,
                 font=(FONT, 10, "bold")).pack(side="right")

    # ---------------------------------------------------- Logika
    def _status(self, teks, jenis="sukses"):
        if self.on_status:
            self.on_status(teks, jenis)

    def _idx_terpilih(self):
        sel = self.tree.selection()
        return int(sel[0]) if sel else None

    def _update_tombol(self):
        aktif = bool(self.tree.selection())
        self.btn_edit.atur_aktif(aktif)
        self.btn_hapus.atur_aktif(aktif)

    def fokus_cari(self):
        self.ent_cari.focus_set()
        self.ent_cari.select_range(0, "end")

    def reset_filter(self):
        self.var_cari.set("")
        self.var_kota.set("Semua Kota")
        self.var_kat.set("Semua Kategori")
        self.refresh()

    def urutkan(self, kolom):
        if self.sort_col == kolom:
            self.sort_rev = not self.sort_rev
        else:
            self.sort_col, self.sort_rev = kolom, False
        self.refresh()

    def _kunci(self, pair):
        idx, d = pair
        return {"no": idx, "nama": d.nama_hotel.lower(), "kota": d.kota.lower(),
                "kategori": d.kategori.lower(), "rating": d.rating,
                "ulasan": d.jumlah_ulasan, "status": d.rating}[self.sort_col]

    def refresh(self):
        data = self.repo.data

        opsi_kota = ["Semua Kota"] + sorted({d.kota for d in data}, key=str.lower)
        opsi_kat = ["Semua Kategori"] + sorted({d.kategori for d in data}, key=str.lower)
        self.cmb_kota["values"] = opsi_kota
        self.cmb_kat["values"] = opsi_kat
        if self.var_kota.get() not in opsi_kota:
            self.var_kota.set("Semua Kota")
        if self.var_kat.get() not in opsi_kat:
            self.var_kat.set("Semua Kategori")

        kata = self.var_cari.get().strip().lower()
        pilih_kota = self.var_kota.get()
        pilih_kat = self.var_kat.get()
        tampil = []
        for idx, d in enumerate(data):
            if pilih_kota != "Semua Kota" and d.kota != pilih_kota:
                continue
            if pilih_kat != "Semua Kategori" and d.kategori != pilih_kat:
                continue
            if kata and kata not in (d.nama_hotel + " " + d.kota + " " + d.kategori).lower():
                continue
            tampil.append((idx, d))
        if self.sort_col:
            tampil.sort(key=self._kunci, reverse=self.sort_rev)

        terpilih = self.tree.selection()
        self.tree.delete(*self.tree.get_children())
        for n, (idx, d) in enumerate(tampil, start=1):
            label, _warna = info_status(d.rating)
            tag = ["genap" if n % 2 == 0 else "ganjil"]
            if d.rating < 3:
                tag.append("kurang")
            self.tree.insert("", "end", iid=str(idx), tags=tuple(tag),
                             values=(n, d.nama_hotel, d.kota, d.kategori,
                                     f"★ {d.rating:.1f}", f"{d.jumlah_ulasan:,}", label))
        if terpilih and self.tree.exists(terpilih[0]):
            self.tree.selection_set(terpilih[0])
        self._update_tombol()

        for kode, (judul, *_sisa) in self.COLUMNS.items():
            panah = ""
            if kode == self.sort_col:
                panah = "  ▼" if self.sort_rev else "  ▲"
            self.tree.heading(kode, text=judul + panah)

        if tampil:
            self.lbl_kosong.place_forget()
        else:
            if data:
                self.lbl_kosong.config(text="Tidak ada hasil yang cocok dengan filter.")
            else:
                self.lbl_kosong.config(
                    text="Belum ada data hotel.\nKlik menu Input Data untuk menambahkan.")
            self.lbl_kosong.place(relx=0.5, rely=0.5, anchor="center")

        self.var_info.set(f"Menampilkan {len(tampil)} dari {len(data)} hotel")

    def edit(self):
        idx = self._idx_terpilih()
        if idx is not None and self.on_edit:
            self.on_edit(idx)

    def hapus(self):
        idx = self._idx_terpilih()
        if idx is None:
            return
        item = self.repo.data[idx]
        if konfirmasi(self, "Hapus data hotel?",
                      f"Data '{item.nama_hotel}' ({item.kota}) akan dihapus permanen "
                      "dari file CSV.", "Ya, Hapus", bahaya=True):
            if self.repo.hapus(idx):
                self.refresh()
                self._status(f"Hotel '{item.nama_hotel}' berhasil dihapus.")
                if self.on_ubah:
                    self.on_ubah()

    def ekspor(self):
        path = filedialog.asksaveasfilename(
            defaultextension=".csv", initialfile="ekspor_rating_hotel.csv",
            filetypes=[("File CSV", "*.csv")])
        if path and self.repo.ekspor(path):
            self._status("Data berhasil diekspor.")

    def muat_ulang(self):
        self.repo.load()
        self.refresh()
        if self.on_ubah:
            self.on_ubah()
        self._status(f"Data dimuat ulang ({len(self.repo.data)} hotel).")


if __name__ == "__main__":
    root = tk.Tk()
    root.title("Data Hotel")
    root.geometry("1050x650")
    root.configure(bg=BG)
    terapkan_tema(root)
    TampilRatingFrame(root, RatingRepository(FILE_CSV)).pack(
        fill="both", expand=True, padx=24, pady=24)
    root.mainloop()