<p align="center">
    <img width="70px" src="static/images/icons/logo.svg" alt="Program Card">
</p>
<h1 align="center">OpiniScope</h1>

## Apa itu OpiniScope ?

OpiniScope adalah sebuah platform teknologi berbasis website yang menggunakan machine learning untuk menganalisis sentimen terkait Pemilu 2024. Dengan keunggulan dalam kecerdasan buatannya, OpiniScope dapat secara efektif memproses pesan-pesan yang tersebar di Twitter, sehingga memberikan pemahaman yang lebih mendalam tentang opini publik terkait Pemilu 2024.

## Fitur-Fitur OpiniScope

- **Analisis Sentimen Single Input**\
  Fitur ini memungkinkan pengguna untuk mengirimkan satu koemtar atau teks tertentu yang kemudian dianalisis oleh OpiniScope. Misalnya, pengguna dapat memasukkan satu tweet berita yang berkaitan dengan Pemilu 2024. OpiniScope akan menggunakan teknologi machine learning-nya untuk menganalisis sentimen dari teks tersebut dan memberikan pemahaman tentang bagaimana opini publik merespons pesan tersebut.
- **Analisis Sentimen Multiple Inputs**\
  Fitur ini memungkinkan pengguna untuk mengunggah banyak komentar atau teks sekaligus dalam format file CSV dengan syarat bahwa file tersebut harus memiliki kolom yang bernama 'komentar'. Dalam kolom 'komentar', pengguna diharapkan mengisikan data komentar yang ingin dianalisis. Setelah pengguna berhasil mengunggah file, sistem akan langsung melakukan proses analisis dan menampilkan hasil analisis sentimen dengan rincian jumlah data yang digunakan, tabel hasil klasifikasi, dan memberikan opsi kepada pengguna untuk mengunduh hasil klasifikasi dalam bentuk file CSV. Pengguna juga dapat melihat hasil analisis sentimen dari teks yang telah dimasukkan, beserta hasil preprocessing-nya.

## Jalankan aplikasi OpiniScope

1. Install semua depedensi library yang digunakan (direkomendasikan menggunakan Python versi 3.12)
2. Membuat Virtual environment dengan perintah:

```shell
For mac/unix users: python3 -m venv env
For windows users: py -m venv env
```

3. Aktifkan lingkungan virtual dengan perintah:

```shell
For mac/unix users: python3 -m venv env
For windows users: py -m venv env
```

4. Jalankan Aplikasi

```shell
flask run
```

5. Akses Aplikasi\
   Buka browser web dan arahkan ke alamat yang ditampilkan di terminal setelah menjalankan perintah flask run. Biasanya, alamat ini adalah http://127.0.0.1:5000.
