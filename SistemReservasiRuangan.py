import tkinter as tk
from tkinter import messagebox
from tkinter import ttk

# Program GUI sederhana untuk Sistem Reservasi Ruangan
# Keterangan singkat:
# - Menyediakan daftar ruangan (kelas dan rapat)
# - Memungkinkan pengguna (peminjam) mengisi form dan memilih ruangan
# - Menyimpan reservasi dalam memori (list) dan menampilkan di tabel
# Komentar di seluruh file menggunakan bahasa Indonesia untuk membantu
# mahasiswa memahami alur dan fungsi tiap bagian kode.

# ================== CLASS USER ==================
# Kelas dasar untuk merepresentasikan pengguna sistem.
# Menyimpan id dan nama, serta menyediakan method login sederhana.
class User:
    def __init__(self, user_id, nama):
        self._user_id = user_id
        self._nama = nama

    def login(self):
        return True

class Peminjam(User):
    # Kelas turunan dari User untuk informasi peminjam (mahasiswa)
    # Menyimpan nomor identitas (mis. NIM) dan program studi (prodi)
    
    def __init__(self, user_id, nama, no_identitas, prodi):
        super().__init__(user_id, nama)
        self.no_identitas = no_identitas
        self.prodi = prodi

class Ruangan:
    def __init__(self, kode, nama, kapasitas):
        self.kode = kode
        self.nama = nama
        self.kapasitas = kapasitas

    def info(self):
        return f"{self.nama} | Kapasitas {self.kapasitas}"
    
class RuangKelas(Ruangan):
    def __init__(self, kode, nama, kapasitas, meja):
        super().__init__(kode, nama, kapasitas)
        self.meja = meja

    def info(self):
        return f"[KELAS] {self.nama} | Meja {self.meja}"
    
class RuangRapat(Ruangan):
    def __init__(self, kode, nama, kapasitas, fasilitas):
        super().__init__(kode, nama, kapasitas)
        self.fasilitas = fasilitas

    def info(self):
        return f"[RAPAT] {self.nama} | {self.fasilitas}"
    
class Reservasi:
    # Mewakili sebuah reservasi/booking.
    # Menyimpan peminjam, objek ruangan, tanggal, waktu, dan status.
    def __init__(self, peminjam, ruangan, tanggal, waktu):
        self.peminjam = peminjam
        self.ruangan = ruangan
        self.tanggal = tanggal
        self.waktu = waktu
        self.status = "Dikonfirmasi"

    def batalkan(self):
        self.status = "Dibatalkan"

class ReservasiApp:
    # Kelas aplikasi GUI utama yang membangun antarmuka Tkinter
    # dan menyimpan state aplikasi (daftar ruangan, daftar reservasi, user aktif).
    def __init__(self, root):
        self.root = root
        self.root.title("Sistem Reservasi Ruangan Fakultas Vokasi")
        self.root.geometry("1000x800")
        self.root.minsize(1000, 800)

        # Buat wrapper scrollable: canvas + scrollbar + inner frame
        # Digunakan agar seluruh form dan tabel dapat discroll ketika jendela
        # berukuran kecil atau konten melebihi tinggi jendela.
        self.main_frame = tk.Frame(self.root)
        self.main_frame.pack(fill="both", expand=True)

        self.canvas = tk.Canvas(self.main_frame)
        self.v_scroll = ttk.Scrollbar(self.main_frame, orient="vertical", command=self.canvas.yview)
        self.v_scroll.pack(side=tk.RIGHT, fill=tk.Y)
        self.canvas.pack(side=tk.LEFT, fill="both", expand=True)
        self.canvas.configure(yscrollcommand=self.v_scroll.set)

        self.scrollable_frame = tk.Frame(self.canvas)
        self._canvas_window = self.canvas.create_window((0, 0), window=self.scrollable_frame, anchor='nw')

        # Update scrollregion saat konten berubah dan sesuaikan lebar inner frame
        self.scrollable_frame.bind("<Configure>", lambda e: self.canvas.configure(scrollregion=self.canvas.bbox("all")))
        self.canvas.bind("<Configure>", lambda e: self.canvas.itemconfig(self._canvas_window, width=e.width))

        # Tambahkan dukungan mousewheel (Windows)
        # Memudahkan navigasi daftar dengan roda mouse
        self.canvas.bind_all("<MouseWheel>", lambda e: self.canvas.yview_scroll(int(-1 * (e.delta / 120)), "units"))

        # Inisialisasi user sementara (peminjam). Field akan diupdate dari form.
        self.user = Peminjam(1, "", "20231234", "")

        # Daftar ruangan yang tersedia di sistem (di-hardcode untuk contoh)
        # Terdiri dari beberapa RuangKelas dan RuangRapat
        self.ruangan_list = [
            RuangKelas("RK01", "Ruang K2.01.01", 30, 15),
            RuangKelas("RK02", "Ruang K2.01.02", 40, 20),
            RuangKelas("RK03", "Ruang K2.01.03", 40, 20),
            RuangKelas("RK04", "Ruang K2.01.04", 40, 20),
            RuangKelas("RK05", "Ruang K2.01.05", 40, 20),
            RuangKelas("RK06", "Ruang K10.02.01", 40, 20),
            RuangKelas("RK07", "Ruang K10.02.02", 40, 20),
            RuangKelas("RK08", "Ruang K10.02.03", 40, 20),
            RuangKelas("RK09", "Ruang K10.02.04", 40, 20),
            RuangRapat("RR01", "Ruang K9.02.01", 40, "Proyektor, AC"),
            RuangRapat("RR02", "Ruang K9.02.02", 40, "Proyektor, AC"),
            RuangRapat("RR03", "Ruang K9.02.03", 40, "Proyektor, AC"),
            RuangRapat("RR04", "Ruang K9.02.04", 30, "Proyektor, AC"),
            RuangRapat("RR05", "Ruang K9.02.05", 40, "Proyektor, AC"),
            RuangRapat("RR06", "Ruang K10.03.01", 100, "Proyektor, AC")
            ]

        # Daftar reservasi yang dibuat selama runtime aplikasi (disimpan di memori)
        self.reservasi_list = []
        self.build_ui()

    def on_select_kelas(self, event):
        if event.widget == self.tree_kelas:
            self.tree_rapat.selection_remove(self.tree_rapat.selection())

    def on_select_rapat(self, event):
        if event.widget == self.tree_rapat:
            self.tree_kelas.selection_remove(self.tree_kelas.selection())


    def build_ui(self):
        parent = self.scrollable_frame

        # ================== TITLE ==================
        title = tk.Label(
            parent,
            text="Sistem Reservasi Ruangan Fakultas Vokasi",
            font=("Helvetica", 16, "bold")
        )
        title.pack(pady=10)

        # ================== FORM INPUT ==================
        # Bagian form untuk mengisi data peminjam dan waktu reservasi
        frame_form = tk.LabelFrame(parent, text="Form Data Peminjam", padx=15, pady=15)
        frame_form.pack(fill="x", padx=15, pady=5)

        frame_form.columnconfigure(1, weight=1)

        # Nama
        tk.Label(frame_form, text="Nama Peminjam").grid(row=0, column=0, sticky="w", pady=5)
        self.entry_nama = tk.Entry(frame_form)
        self.entry_nama.grid(row=0, column=1, sticky="ew", pady=5)

        # NIM
        tk.Label(frame_form, text="NIM").grid(row=1, column=0, sticky="w", pady=5)
        self.entry_nim = tk.Entry(frame_form)
        self.entry_nim.grid(row=1, column=1, sticky="ew", pady=5)

        # Prodi
        tk.Label(frame_form, text="Program Studi").grid(row=2, column=0, sticky="w", pady=5)
        self.entry_prodi = tk.Entry(frame_form)
        self.entry_prodi.grid(row=2, column=1, sticky="ew", pady=5)

        # Tanggal
        tk.Label(frame_form, text="Tanggal").grid(row=3, column=0, sticky="w", pady=5)
        self.entry_tanggal = tk.Entry(frame_form)
        self.entry_tanggal.grid(row=3, column=1, sticky="ew", pady=5)

        # Waktu
        tk.Label(frame_form, text="Waktu").grid(row=4, column=0, sticky="w", pady=5)
        self.entry_waktu = tk.Entry(frame_form)
        self.entry_waktu.grid(row=4, column=1, sticky="ew", pady=5)

        # ================== PILIH RUANGAN ==================
        # Bagian ini menampilkan dua tabel: Ruang Kelas dan Ruang Rapat.
        # Pengguna memilih salah satu baris di salah satu tabel untuk memilih ruangan.
        frame_ruangan = tk.LabelFrame(parent, text="Pilih Ruangan", padx=15, pady=10)
        frame_ruangan.pack(fill="x", padx=15, pady=5)

        frame_kiri = tk.LabelFrame(frame_ruangan, text="Ruang Kelas")
        frame_kiri.pack(side=tk.LEFT, fill="both", expand=True, padx=5)

        frame_kanan = tk.LabelFrame(frame_ruangan, text="Ruang Rapat")
        frame_kanan.pack(side=tk.RIGHT, fill="both", expand=True, padx=5)

        # Treeview untuk Ruang Kelas (Nama, Kapasitas, Meja)
        cols_kelas = ("nama", "kapasitas", "meja")
        kelas_table_frame = tk.Frame(frame_kiri)
        kelas_table_frame.pack(fill="both", expand=True)
        scroll_kelas = ttk.Scrollbar(kelas_table_frame, orient="vertical")
        scroll_kelas.pack(side=tk.RIGHT, fill="y")
        self.tree_kelas = ttk.Treeview(kelas_table_frame, columns=cols_kelas, show="headings", height=5, selectmode="browse", yscrollcommand=scroll_kelas.set)
        for c, lbl in [("nama", "Nama"), ("kapasitas", "Kapasitas"), ("meja", "Meja")]:
            self.tree_kelas.heading(c, text=lbl)
            self.tree_kelas.column(c, anchor="w")
        self.tree_kelas.pack(side=tk.LEFT, fill="both", expand=True)
        scroll_kelas.config(command=self.tree_kelas.yview)

        # Treeview untuk Ruang Rapat (Nama, Kapasitas, Fasilitas)
        cols_rapat = ("nama", "kapasitas", "fasilitas")
        rapat_table_frame = tk.Frame(frame_kanan)
        rapat_table_frame.pack(fill="both", expand=True)
        scroll_rapat = ttk.Scrollbar(rapat_table_frame, orient="vertical")
        scroll_rapat.pack(side=tk.RIGHT, fill="y")
        self.tree_rapat = ttk.Treeview(rapat_table_frame, columns=cols_rapat, show="headings", height=5, selectmode="browse", yscrollcommand=scroll_rapat.set)
        for c, lbl in [("nama", "Nama"), ("kapasitas", "Kapasitas"), ("fasilitas", "Fasilitas")]:
            self.tree_rapat.heading(c, text=lbl)
            self.tree_rapat.column(c, anchor="w")
        self.tree_rapat.pack(side=tk.LEFT, fill="both", expand=True)
        scroll_rapat.config(command=self.tree_rapat.yview)

        self.tree_kelas.bind("<<TreeviewSelect>>", self.on_select_kelas)
        self.tree_rapat.bind("<<TreeviewSelect>>", self.on_select_rapat)

        # Isi data ke masing-masing Treeview, gunakan kode sebagai iid
        # iid akan digunakan untuk mencari objek Ruangan berdasarkan kode.
        for r in self.ruangan_list:
            if isinstance(r, RuangKelas):
                self.tree_kelas.insert("", tk.END, iid=r.kode, values=(r.nama, r.kapasitas, r.meja))
            elif isinstance(r, RuangRapat):
                self.tree_rapat.insert("", tk.END, iid=r.kode, values=(r.nama, r.kapasitas, r.fasilitas))


        # ================== BUTTON ==================
        # Tombol untuk men-trigger pembuatan reservasi dari data form
        frame_button = tk.Frame(parent)
        frame_button.pack(pady=10)

        tk.Button(
            frame_button,
            text="Tambah Reservasi",
            width=20,
            bg="#4CAF50",
            fg="white",
            command=self.tambah_reservasi
        ).pack()

        # ================== DAFTAR RESERVASI ==================
        # Tabel ini menampilkan semua reservasi yang telah dibuat.
        frame_reservasi = tk.LabelFrame(parent, text="Daftar Reservasi", padx=15, pady=10)
        frame_reservasi.pack(fill="both", expand=False, padx=15, pady=5)

        columns = ("nama", "prodi", "ruangan", "tanggal", "waktu", "status")

        # Frame khusus tabel
        frame_table = tk.Frame(frame_reservasi)
        frame_table.pack(fill="x", expand=False)

        scroll_y = ttk.Scrollbar(frame_table, orient="vertical")
        scroll_y.pack(side="right", fill="y")

        self.tree = ttk.Treeview(frame_table, columns=columns, show="headings", height=5, yscrollcommand=scroll_y.set)
        self.tree.pack(side="left", fill="both", expand=False)

        scroll_y.config(command=self.tree.yview)

        self.tree.heading("nama", text="Nama (NIM)")
        self.tree.heading("prodi", text="Prodi")
        self.tree.heading("ruangan", text="Ruangan")
        self.tree.heading("tanggal", text="Tanggal")
        self.tree.heading("waktu", text="Waktu")
        self.tree.heading("status", text="Status")

        for col in columns:
            self.tree.column(col, anchor="center")


        # FRAME BUTTON (WAJIB DI BAWAH)
        frame_reservasi_actions = tk.Frame(frame_reservasi)
        frame_reservasi_actions.pack(fill="x", pady=(10, 5))

        tk.Button(
            frame_reservasi_actions,
            text="Batalkan Reservasi",
            width=25,
            bg="#F44336",
            fg="white",
            command=self.batalkan_reservasi
        ).pack(anchor="center")



    def populate_ruangan_listbox(self):
        """Populate ruangan listbox dengan kategori"""
        # Method removed — selection is handled via separate listboxes
        return

    def tambah_reservasi(self):
        # Tentukan ruangan berdasarkan Treeview yang dipilih (pakai iid=kode)
        ruangan = None
        sel_kelas = self.tree_kelas.selection()
        sel_rapat = self.tree_rapat.selection()
        if sel_kelas:
            kode = sel_kelas[0]
            ruangan = next((r for r in self.ruangan_list if r.kode == kode), None)
        elif sel_rapat:
            kode = sel_rapat[0]
            ruangan = next((r for r in self.ruangan_list if r.kode == kode), None)
        else:
            messagebox.showwarning("Error", "Pilih ruangan terlebih dahulu")
            return

        # Ambil semua input pengguna terlebih dahulu dari field form
        nama = self.entry_nama.get().strip()
        prodi = self.entry_prodi.get().strip()
        tanggal = self.entry_tanggal.get().strip()
        waktu = self.entry_waktu.get().strip()

        # Validasi input sederhana: pastikan field penting terisi
        if not nama or not prodi:
            messagebox.showwarning("Error", "Nama dan Prodi harus diisi")
            return

        if not tanggal or not waktu:
            messagebox.showwarning("Error", "Semua data harus diisi")
            return
        
        # Update data peminjam dari form (menggantikan nilai pada objek user)
        self.user._nama = nama
        self.user.prodi = prodi
        nim = self.entry_nim.get().strip()
        if nim:
            self.user.no_identitas = nim

        # Cek bentrok jadwal: jika ada reservasi dengan ruangan, tanggal, dan waktu sama
        for r in self.reservasi_list:
            if r.ruangan.kode == ruangan.kode and r.tanggal == tanggal and r.waktu == waktu:
                messagebox.showerror("Gagal", "Ruangan sudah dipesan pada waktu tersebut")
                return

        reservasi = Reservasi(self.user, ruangan, tanggal, waktu)
        self.reservasi_list.append(reservasi)
        self.update_table()


    def update_table(self):
        # Refresh isi tabel daftar reservasi
        for item in self.tree.get_children():
            self.tree.delete(item)

        for i, r in enumerate(self.reservasi_list):
            self.tree.insert("", tk.END, iid=str(i), values=(
                f"{r.peminjam._nama} ({r.peminjam.no_identitas})",
                r.peminjam.prodi,
                r.ruangan.nama,
                r.tanggal,
                r.waktu,
                r.status
            ))


    def batalkan_reservasi(self):
        # Batalkan reservasi yang dipilih di tabel (ubah status menjadi 'Dibatalkan')
        selection = self.tree.selection()
        if not selection:
            messagebox.showwarning("Error", "Pilih reservasi terlebih dahulu untuk dibatalkan")
            return

        iid = selection[0]
        try:
            idx = int(iid)
        except ValueError:
            messagebox.showerror("Error", "Gagal menentukan reservasi terpilih")
            return

        pilih = messagebox.askyesno("Konfirmasi", "Batalkan reservasi terpilih?")
        if not pilih:
            return

        self.reservasi_list[idx].status = "Dibatalkan"
        self.update_table()

# ================== RUN APPLICATION ==================
root = tk.Tk()
app = ReservasiApp(root)
root.mainloop()