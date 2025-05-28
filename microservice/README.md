
# 🚀 Microservice Demo: FastAPI, PostgreSQL, Redis Stream, Docker

Contoh proyek arsitektur microservice event-driven sederhana menggunakan **FastAPI**, **PostgreSQL**, **Redis Streams**, dan **Docker**.  
Frontend statis HTML untuk simulasi request.

---

## 📂 Struktur Project

```
microservice/
│
├── docker-compose.yml
├── init/
│   ├── user/
│   │   └── init.sql
│   └── order/
│       └── init.sql
│
├── user_service/
│   ├── app.py
│   ├── requirements.txt
│   └── Dockerfile
│
├── order_service/
│   ├── app.py
│   ├── consumer.py
│   ├── requirements.txt
│   └── Dockerfile
│
└── frontend/
    └── index.html
```

---

## ✨ **Konsep Workflow**

1. **Buat user** via `/user` → data masuk ke DB dan publish ke Redis stream.
2. **Consumer** (`consumer.py`) baca event user baru → otomatis buat order di DB order.
3. **Manual order** via `/order` juga bisa.
4. **Summary** dari order via `/summary`.

---

## 💻 Langkah Pengembangan & Instalasi

### 1. **Membuat Database & Init Table**

**Manual (tanpa Docker Compose):**

- Jalankan PostgreSQL untuk `user_db` dan `order_db` di Docker, misal:
    ```bash
    docker run -d --name user_db -e POSTGRES_USER=user -e POSTGRES_PASSWORD=userpass -e POSTGRES_DB=user_db -p 5432:5432 postgres:15

    docker run -d --name order_db -e POSTGRES_USER=order -e POSTGRES_PASSWORD=orderpass -e POSTGRES_DB=order_db -p 5433:5432 postgres:15
    ```
- Jalankan Redis:
    ```bash
    docker run -d --name redis -p 6379:6379 redis:7
    ```

- **Init table** (dari file SQL di `/init/user/init.sql` dan `/init/order/init.sql`).  
  Contoh isi `init.sql` untuk users:
    ```sql
    CREATE TABLE IF NOT EXISTS users (
      id UUID PRIMARY KEY,
      name TEXT,
      email TEXT
    );
    ```

  ...dan untuk orders:
    ```sql
    CREATE TABLE IF NOT EXISTS orders (
      id UUID PRIMARY KEY,
      user_id UUID,
      product_name TEXT,
      total_price FLOAT
    );
    ```

  Import manual dengan:
    ```bash
    psql -h localhost -p 5432 -U user -d user_db -f ./init/user/init.sql
    psql -h localhost -p 5433 -U order -d order_db -f ./init/order/init.sql
    ```

---

### 2. **Install Dependency (Python)**

Masuk ke masing-masing folder service, lalu:
```bash
pip install -r requirements.txt
```
**(Sudah otomatis support Python 3.12+ dan redis-py baru!)**

---

### 3. **Menjalankan Service Secara Manual**

**user_service**:
```bash
cd user_service
uvicorn app:app --reload
```

**order_service**:
```bash
cd order_service
uvicorn app:app --reload --port 8001
```

**consumer (worker Redis):**
```bash
cd order_service
python consumer.py
```

---

### 4. **Menjalankan Docker Compose**

Jalankan semua service dengan satu perintah:
```bash
docker-compose up --build
```
> Semua ENV akan otomatis terisi, port mapping sesuai kebutuhan.

---

### 5. **Menjalankan Frontend**

Jalankan frontend (di folder `frontend/`):

- **Manual:**  
  Double click `index.html`
- **Atau via simple web server**:
    ```bash
    python -m http.server 5500
    ```
  Buka: [http://localhost:5500/index.html](http://localhost:5500/index.html)

---

### 6. **Mengecek Redis & PostgreSQL di Host**

#### **Cek Redis:**
- **Pastikan Redis yang aktif hanya dari Docker** (bukan Redis lokal!).
- Cari proses Redis di host:
    ```powershell
    netstat -aon | findstr :6379
    tasklist | findstr redis
    ```
  Jika ada dua, matikan Redis lokal:
    ```powershell
    Stop-Service -Name redis
    ```
  atau via Task Manager (admin):
    - Ctrl+Shift+Esc → Tab Details → Cari redis-server.exe → End Task (admin privilege).

#### **Cek Redis Docker:**
```bash
docker ps | grep redis
docker exec -it redis redis-cli ping
```

#### **Cek isi Redis:**
```bash
docker exec -it redis redis-cli
127.0.0.1:6379> XRANGE user_created - +
```

#### **Cek isi PostgreSQL Docker:**
```bash
docker exec -it user_db psql -U user -d user_db
user_db=# SELECT * FROM users;
```
```bash
docker exec -it order_db psql -U order -d order_db
order_db=# SELECT * FROM orders;
```

---

### 7. **Troubleshooting Redis Versi dan Koneksi**

- **Pastikan Redis versi 6+** (`redis:7` di Docker)
- **Jika error "unknown command XREADGROUP"**  
  → Biasanya karena masih ada Redis lokal lama (v4 ke bawah) di host.
- Solusi:
    - Matikan Redis lokal
    - Pakai IP Docker Redis jika perlu (`docker inspect -f '{{range.NetworkSettings.Networks}}{{.IPAddress}}{{end}}' redis`)
    - Ubah `REDIS_HOST` di `.env`/ENV/service sesuai IP/hostname yang benar

---

### 8. **Ringkasan API**

- **POST** `/user` (user_service, port 8000): tambah user (dan kirim event ke Redis)
- **POST** `/order` (order_service, port 8001): tambah order manual
- **GET** `/summary` (order_service, port 8001): rekap order per user

---

### 9. **Frontend Demo**

1. Klik **Create User**: user masuk, event dikirim ke Redis
2. Worker (`consumer.py`) otomatis ambil event, buat order
3. Klik **Create Order**: tambah order manual
4. Klik **Show Summary**: lihat data order yang sudah ada

---

## 📝 **Tips & Catatan**

- Untuk demo, `allow_origins=["*"]` di CORS FastAPI cukup aman.
- Untuk production, sebaiknya restrict domain frontend yang diizinkan.
- Gunakan Docker Compose jika tidak mau ribet setup manual dependency.

---

**Happy coding! 🚀**  
Kalau error, cek log docker, atau jalankan manual per service untuk debug satu-satu.

---
