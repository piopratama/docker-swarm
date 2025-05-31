# 🧩 Sharding, Replication & Search Demo with Docker Compose and Swarm

Proyek ini adalah demo sederhana untuk memahami konsep **sharding horizontal**, **replikasi database**, **failover**, dan **pencarian terdistribusi**, dikemas dalam stack Docker yang mudah dijalankan.

---

## 🧠 Fitur

- ✅ Write sharding (shard1 & shard2 berdasarkan jumlah data)
- ✅ Read dari 2 replica (replica1 dan replica2)
- ✅ Replikasi otomatis dari shard → replica (dengan delay)
- ✅ Failover otomatis jika salah satu shard tidak bisa diakses
- ✅ Pencarian berbasis Elasticsearch (search by `data`)
- ✅ UI sederhana HTML + JavaScript
- ✅ Mendukung mode lokal, Docker Compose, dan Docker Swarm

---

## 🔍 Kenapa Menggunakan Elasticsearch?

Sharding membuat data tersebar di beberapa database. Jika kita ingin mencari data tertentu (misalnya `"data-4"`), maka:

- Tanpa Elasticsearch, backend harus **melakukan query ke semua shard dan replica**, dan menyatukan hasilnya sendiri (inefisien dan lambat).
- Elasticsearch memungkinkan backend **melakukan pencarian global** secara cepat, cukup melalui satu endpoint (`/search?q=data-4`), tanpa perlu scan seluruh shard satu per satu.

### ⚖️ Alternatif tanpa Elasticsearch

Jika kamu ingin menghindari penggunaan Elasticsearch:

- Bisa lakukan pencarian manual dengan query SQL ke semua shard (dan/atau replica), lalu filter di backend (Python).
- Kelemahannya:
  - Tidak scalable
  - Performa pencarian menurun seiring jumlah data/shard bertambah
  - Tidak mendukung fitur lanjutan seperti fuzzy match, full-text search, dsb

---

## 🧱 Arsitektur

```
+------------+          +----------+          +-----------+          +---------------+
|  Frontend  | <------> | Backend  | <------> | Databases | <------> | Elasticsearch |
+------------+          +----------+          +-----------+          +---------------+

Write Flow:
        data-1...5   →   shard1
        data-6+      →   shard2
        Replikasi    →   replica1, replica2
        Indexing     →   Elasticsearch

Read Flow:
        /read   → Pull dari replica1 & replica2
        /search → Cari dari Elasticsearch
```

---

## ⚙️ Struktur Folder

```
.
├── backend/                # Flask API (write, read, replicate, search)
├── frontend/               # Static HTML & JS
├── init/init.sql           # Schema initializer (PostgreSQL)
├── docker-compose.yml      # Untuk development lokal
├── docker-compose-swarm.yml# Untuk Docker Swarm deployment
├── README.md               # Dokumentasi
```

---

## 🚀 Menjalankan

### 1. Mode Lokal / Docker Compose

```bash
docker-compose up --build
```

Buka browser: [http://localhost:8080](http://localhost:8080)

📌 Untuk reset:

```bash
docker-compose down -v
```

---

### 2. Mode Docker Swarm

```bash
docker build -t swarmdemo_backend ./backend
docker build -t swarmdemo_frontend ./frontend

docker swarm init
docker stack deploy -c docker-compose-swarm.yml sharddemo
```

Cek service:

```bash
docker service ls
```

Akses frontend: [http://localhost:8080](http://localhost:8080)

Hapus stack:

```bash
docker stack rm sharddemo
```

---

## 🧪 Pengujian

- **Write**: Klik tombol `Write Data` → data disimpan ke shard1 (1–5), shard2 (6+)
- **Read**: Klik tombol `Read Data` → data dari replica1 & replica2 ditampilkan
- **Search**: Gunakan `/search?q=data-4` → backend ambil dari Elasticsearch
- **Replikasi**: Otomatis setiap 10 detik
- **Failover**: Stop salah satu shard → backend otomatis pakai shard lain

---

## ⚠️ Catatan Teknis

- CORS aktif di backend (`flask_cors`)
- Variabel `RUN_ENV=local` dibutuhkan saat menjalankan backend di luar Docker
- Frontend otomatis deteksi backend (`BASE_URL`) berdasarkan `window.location`
- Data di-index ke Elasticsearch saat `write`, untuk kebutuhan pencarian

---

## 🧩 Pengembangan Lanjutan (Opsional)

- Gunakan hash ID atau UUID untuk sharding logic
- Tambahkan Redis sebagai penampung queue atau write buffer
- Tambahkan monitoring dengan Grafana, Prometheus, atau Portainer
- Gunakan Traefik atau nginx sebagai reverse proxy dan load balancer
- Tambahkan fitur update/delete sinkron dengan Elasticsearch

---

## 📬 Kontribusi

Fork & modifikasi proyek ini untuk kebutuhan demo arsitektur microservices, database design, atau HA simulation.
