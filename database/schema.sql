-- ===================================================
-- HERMAN MUSIK - DATABASE SCHEMA (MySQL)
-- Jalankan: mysql -u root -p < schema.sql
-- ===================================================

CREATE DATABASE IF NOT EXISTS herman_musik
  CHARACTER SET utf8mb4
  COLLATE utf8mb4_unicode_ci;

USE herman_musik;

-- ===================================================
-- TABEL: permintaan
-- Menyimpan data dari form kontak / pesanan masuk
-- ===================================================
CREATE TABLE IF NOT EXISTS permintaan (
    id            INT AUTO_INCREMENT PRIMARY KEY,
    nama          VARCHAR(100)  NOT NULL,
    no_wa         VARCHAR(20)   NOT NULL,
    tanggal_acara DATE          NULL,
    jumlah_tamu   VARCHAR(50)   DEFAULT '',
    jenis_acara   VARCHAR(100)  DEFAULT '',
    pesan         TEXT          DEFAULT '',
    status        ENUM('baru', 'diproses', 'selesai', 'batal') DEFAULT 'baru',
    dibuat_pada   DATETIME      NOT NULL DEFAULT CURRENT_TIMESTAMP
) ENGINE=InnoDB;


-- ===================================================
-- TABEL: produk
-- Katalog produk / layanan yang ditawarkan
-- ===================================================
CREATE TABLE IF NOT EXISTS produk (
    id          INT AUTO_INCREMENT PRIMARY KEY,
    nama        VARCHAR(150)    NOT NULL,
    deskripsi   TEXT            DEFAULT '',
    harga       BIGINT          NOT NULL COMMENT 'Harga dalam Rupiah',
    satuan      VARCHAR(50)     DEFAULT 'per hari',
    gambar_url  VARCHAR(500)    DEFAULT '',
    badge       VARCHAR(50)     DEFAULT NULL COMMENT 'Contoh: Terlaris, Eksklusif',
    aktif       TINYINT(1)      DEFAULT 1
) ENGINE=InnoDB;

-- Data awal produk
INSERT INTO produk (nama, deskripsi, harga, satuan, gambar_url, badge) VALUES
('Taratak Adat Batak',
 'Taratak khas Batak dengan ornamen ulos dan dekorasi adat lengkap. Cocok untuk pesta adat, marhata sinamot, dan pesta unjuk.',
 750000, 'per 1 set/hari',
 'https://images.unsplash.com/photo-1464366400600-7168b8af9bc3?w=600&q=80',
 'Terlaris'),

('Tenda Pesta Modern',
 'Tenda besar untuk pesta kecil seperti marhata sinamot, Tardidi, Syukuran, dll. Tersedia ukuran 10x20, 15x30 hingga 20x40 meter.',
 500000, 'per 1 tenda/hari',
 'https://images.unsplash.com/photo-1478146059778-26028b07395a?w=600&q=80',
 NULL),

('Taratak VIP Premium',
 'Taratak mewah berlapis kain premium, lampu kristal, backdrop bunga segar. Sempurna untuk resepsi dan foto prewedding.',
 8500000, 'per hari termasuk dekorasi',
 'https://images.unsplash.com/photo-1550005809-91ad75fb315f?w=600&q=80',
 'Eksklusif'),

('Kursi',
 'Tersedia untuk 100 hingga 500 tamu.',
 4000, 'per kursi/hari (min. 50 pcs)',
 'https://images.unsplash.com/photo-1606800052052-a08af7148866?w=600&q=80',
 NULL),

('Sound System & Lighting',
 'Paket sound system outdoor dan indoor. Tersedia operator berpengalaman. Cocok untuk hiburan gondang, keyboard, dan DJ.',
 2000000, 'per hari include operator',
 'https://images.unsplash.com/photo-1597586124394-fbd6ef244026?w=600&q=80',
 NULL),

('Genset & Instalasi Listrik',
 'Genset silent 10KVA–100KVA untuk menjamin kelancaran pesta Anda. Termasuk operator dan instalasi kabel lengkap.',
 850000, 'per hari include BBM 8 jam',
 'https://images.unsplash.com/photo-1511795409834-ef04bbd61622?w=600&q=80',
 NULL);


-- ===================================================
-- TABEL: paket
-- Paket bundling produk
-- ===================================================
CREATE TABLE IF NOT EXISTS paket (
    id           INT AUTO_INCREMENT PRIMARY KEY,
    nama         VARCHAR(150)  NOT NULL,
    harga        BIGINT        NOT NULL,
    kapasitas    VARCHAR(100)  DEFAULT '',
    unggulan     TINYINT(1)    DEFAULT 0 COMMENT '1 = ditampilkan sebagai featured'
) ENGINE=InnoDB;

-- Data awal paket
INSERT INTO paket (nama, harga, kapasitas, unggulan) VALUES
('Paket Buat Nikahan', 9000000, '800 tamu', 0),
('Paket Taratak Adat', 12000000, '200–300 tamu', 1),
('Paket Royal', 25000000, '400–600 tamu', 0);


-- ===================================================
-- TABEL: paket_item
-- Isi / fitur per paket
-- ===================================================
CREATE TABLE IF NOT EXISTS paket_item (
    id       INT AUTO_INCREMENT PRIMARY KEY,
    paket_id INT NOT NULL,
    item     VARCHAR(255) NOT NULL,
    FOREIGN KEY (paket_id) REFERENCES paket(id) ON DELETE CASCADE
) ENGINE=InnoDB;

-- Isi paket 1: Buat Nikahan
INSERT INTO paket_item (paket_id, item) VALUES
(1, 'Taratak 3 set'),
(1, 'Tenda pesta ukuran 6×12 meter 2'),
(1, '100 kursi plastik jika diperlukan'),
(1, 'Sound system basic'),
(1, 'Genset & Instalasi Listrik'),
(1, 'Kameramen & Videografer'),
(1, 'Perabotan yang digunakan saat acara'),
(1, 'Tukang masak nasi lengkap dengan alat-alat'),
(1, 'Pasang & bongkar oleh tim');

-- Isi paket 2: Taratak Adat
INSERT INTO paket_item (paket_id, item) VALUES
(2, 'Taratak adat Batak/Melayu lengkap'),
(2, '200 kursi + 25 meja bundar'),
(2, 'Dekorasi ulos & ornamen adat'),
(2, 'Sound system basic + operator'),
(2, 'Genset + instalasi listrik'),
(2, 'Lampu hias & backdrop pelaminan'),
(2, 'Pasang & bongkar oleh tim');

-- Isi paket 3: Royal
INSERT INTO paket_item (paket_id, item) VALUES
(3, 'Taratak VIP premium + tenda besar'),
(3, '400 kursi chiavari + 50 meja'),
(3, 'Dekorasi mewah + bunga segar'),
(3, 'Sound system lengkap + lighting'),
(3, 'Genset 50KVA + full instalasi'),
(3, 'Pelaminan dekorasi premium'),
(3, 'Karpet merah VIP + backdrop foto'),
(3, 'Tim on-site sepanjang acara');


-- ===================================================
-- TABEL: users
-- Pengguna & admin sistem
-- ===================================================
CREATE TABLE IF NOT EXISTS users (
    id INT AUTO_INCREMENT PRIMARY KEY,
    username VARCHAR(50) UNIQUE NOT NULL,
    email VARCHAR(100) UNIQUE NOT NULL,
    password VARCHAR(255) NOT NULL COMMENT 'Password di-hash dengan werkzeug.security',
    role ENUM('admin', 'user') DEFAULT 'user',
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP
) ENGINE=InnoDB;

-- Seed: Admin default
-- Username: admin_herman | Password (plaintext): Admin@123 (untuk testing, GANTI setelah setup!)
INSERT INTO users (username, email, password, role) VALUES
('admin_herman', 'admin@hermansmusik.id', 'scrypt:32768:8:1$k0klvnI0T9YVRJSm$4fa08939d374f29f6163598f4617032f5bfc0d0f70f149207a75d4cb99164ffb5bf128132cad2a5c761a3702f55c6dbd787033cb0f7ca1a5f38d5b3c843bbc42', 'admin');

-- ===================================================
-- TABEL: testimoni
-- Testimoni dari pelanggan
-- ===================================================
CREATE TABLE IF NOT EXISTS testimoni (
    id         INT AUTO_INCREMENT PRIMARY KEY,
    nama       VARCHAR(100)  NOT NULL,
    lokasi     VARCHAR(150)  DEFAULT '',
    teks       TEXT          NOT NULL,
    bintang    TINYINT       DEFAULT 5,
    tampilkan  TINYINT(1)    DEFAULT 0 COMMENT '0=pending, 1=tampil di website',
    dibuat_pada DATETIME     DEFAULT CURRENT_TIMESTAMP
) ENGINE=InnoDB;

-- Data awal testimoni
INSERT INTO testimoni (nama, lokasi, teks, bintang, tampilkan) VALUES
('Sintia br. Manurung', 'Medan · Pesta Unjuk 2024',
 'Taratak adatnya bagus banget, ornamen ulosnya pas sekali dengan tema adat Batak kami. Tim pemasangannya cepat, datang tepat waktu. Pesta anak kami jadi sangat berkesan!',
 5, 1),
('Robert Simanjuntak', 'Pematang Siantar · Resepsi 2024',
 'Kami pakai Paket Royal untuk 500 tamu undangan. Tenda dan dekorasinya mewah, sound systemnya jernih, genset tidak pernah mati. Rekomendasi banget untuk yang mau pesta besar!',
 5, 1),
('Fatimah Lubis', 'Padang Sidempuan · Akad Nikah 2023',
 'Harga terjangkau tapi kualitasnya tidak murahan. Kursinya bersih, tenda tidak bocor pas hujan. Petugasnya juga ramah dan sigap. Terima kasih Raja Taratak!',
 5, 1);
