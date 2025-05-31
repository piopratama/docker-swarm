
# 🧩 Sharding & Replication Demo with Docker Compose and Swarm

Proyek ini adalah demo sederhana untuk memahami konsep **sharding horizontal**, **replikasi database**, dan **failover**, dikemas dalam stack Docker yang mudah dijalankan.

---

## 🧠 Fitur

- ✅ Write sharding (shard1 & shard2 berdasarkan jumlah data)
- ✅ Read dari 2 replica (replica1 dan replica2)
- ✅ Replikasi otomatis dari shard → replica (dengan delay)
- ✅ Failover otomatis jika salah satu shard tidak bisa diakses
- ✅ UI sederhana HTML + JavaScript
- ✅ Mendukung mode lokal, Docker Compose, dan Docker Swarm

---

## 🧱 Arsitektur

```
+------------+          +----------+          +-----------+
|  Frontend  | <------> | Backend  | <------> | Databases |
+------------+          +----------+          +-----------+

Write Flow:
        data-1...5   →   shard1
        data-6+      →   shard2
        Replikasi    →   replica1, replica2

Read Flow:
        backend pulls from replica1 + replica2 (combined)
```

---

## ⚙️ Struktur Folder

```
.
├── backend/                # Flask API (write, read, replicate)
├── frontend/               # Static HTML & JS
├── init/init.sql           # Schema initializer (PostgreSQL)
├── docker-compose.yml      # For local development
├── docker-compose-swarm.yml# For Docker Swarm deployment
├── README.md               # This file
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
- **Replikasi**: Otomatis setiap 5–10 detik (default: 5 detik)
- **Failover**: Stop salah satu shard → backend otomatis pakai shard lain

---

## ⚠️ Catatan Teknis

- CORS aktif di backend (`flask_cors`)
- Variabel `RUN_ENV=local` dibutuhkan saat menjalankan backend di luar Docker
- Frontend otomatis deteksi backend (`BASE_URL`) berdasarkan `window.location`

---

## 🧩 Pengembangan Lanjutan (Opsional)

- Gunakan hash ID atau UUID untuk sharding logic
- Tambahkan Redis sebagai penampung queue atau write buffer
- Tambahkan monitoring dengan Grafana, Prometheus, atau Portainer
- Gunakan Traefik atau nginx sebagai reverse proxy dan load balancer

---

## 📬 Kontribusi

Fork & modifikasi proyek ini untuk kebutuhan demo arsitektur microservices, database design, atau HA simulation.
