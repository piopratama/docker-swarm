# 🚀 Docker Swarm Demo Project

Proyek ini dibuat untuk mempelajari dasar penggunaan Docker, Docker Compose, dan Docker Swarm dengan membangun aplikasi sederhana berbasis **backend Flask** dan **frontend statis (HTML/JS)**. Dokumentasi ini memandu dari awal pengujian aplikasi lokal hingga penerapan replikasi service menggunakan Swarm.

---

## 📁 Struktur Folder

```
DOCKERSWARM/
├── backend/
│   ├── app.py
│   ├── Dockerfile
│   └── requirements.txt
├── frontend/
│   ├── index.html
│   └── Dockerfile
├── docker-compose.yml
└── README.md
```

---

## 🧪 Tahap 1: Pengujian Aplikasi Secara Lokal (Tanpa Docker)

### ✅ Backend (Flask)

1. Masuk ke folder:
   ```
   cd backend
   ```
2. Buat virtual environment (opsional tapi disarankan):
   ```
   python -m venv venv
   venv\Scripts\activate
   ```
3. Install dependensi:
   ```
   pip install flask flask-cors
   ```
4. Jalankan aplikasi:
   ```
   python app.py
   ```
5. Akses di browser:
   ```
   http://localhost:5000/api
   ```

### ✅ Frontend (HTML)

1. Masuk ke folder frontend:
   ```
   cd frontend
   ```
2. Jalankan server lokal:
   ```
   python -m http.server 8080
   ```
3. Akses frontend:
   ```
   http://localhost:8080
   ```

> ⚠️ Ubah baris `fetch()` di `index.html` agar mengarah ke backend langsung:
>
> ```js
> fetch("http://localhost:5000/api");
> ```

---

## 🐳 Tahap 2: Pahami dan Uji Dockerfile

### 🔹 Isi `backend/Dockerfile`

```dockerfile
FROM python:3.9-slim
WORKDIR /app
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt
COPY app.py .
CMD ["python", "app.py"]
```

- Menggunakan image ringan Python
- Menginstal dependensi dari `requirements.txt`
- Menjalankan Flask app

### 🔹 Isi `frontend/Dockerfile`

```dockerfile
FROM nginx:alpine
COPY index.html /usr/share/nginx/html/index.html
```

- Menggunakan image NGINX ringan
- Menyalin file HTML ke root web default nginx

---

## 🧪 Tahap 3: Uji Build & Run Docker

### ✅ Build dan Jalankan Backend

```bash
docker build -t backend-test:v1 ./backend
docker run -p 5000:5000 --rm backend-test:v1
```

### ✅ Build dan Jalankan Frontend

```bash
docker build -t frontend-test:v1 ./frontend
docker run -p 8080:80 --rm frontend-test:v1
```

> Gunakan `host.docker.internal` dalam `fetch()` di `index.html` jika backend dijalankan di luar container:
>
> ```js
> fetch("http://host.docker.internal:5000/api");
> ```

---

## ❌ Penanganan Error

Jika container gagal:

- Cek container yang gagal:
  ```
  docker ps -a
  ```
- Lihat log error:
  ```
  docker logs <container_id>
  ```
- Hapus container:
  ```
  docker rm <container_id>
  ```
- Hapus image:
  ```
  docker rmi <image_name>
  ```

---

## 🧠 Penjelasan Teknis

### ✅ Kenapa `--rm`?

- Untuk eksperimen, agar container dihapus otomatis setelah dihentikan
- Tidak menumpuk container "exited" di sistem

### ✅ Kenapa `-p 8080:80`?

- Port 80 adalah port default NGINX di dalam container
- 8080 adalah port yang kita akses dari host (laptop)

### ✅ Kenapa pakai `flask-cors`?

- Karena frontend dan backend diakses dari port berbeda (8080 dan 5000)
- Tanpa CORS, browser akan menolak permintaan dari frontend ke backend

---

## 🏷️ Versioning Image

Gunakan tag saat build image:

```bash
docker build -t backend:v1 ./backend
docker build -t frontend:v1 ./frontend
```

> Ini membantu dalam:
>
> - Traceability
> - Rollback
> - CI/CD

---

## 🧩 Tahap 4: Gunakan Docker Compose (Non-Swarm)

```bash
docker-compose up --build
```

Akses:

- Frontend: `http://localhost:8080`
- Backend: `http://localhost:5000/api`

Stop:

```bash
docker-compose down
```

---

## 🐝 Tahap 5: Pindah ke Docker Swarm

### Inisialisasi:

```bash
docker swarm init
```

### Deploy stack:

```bash
docker stack deploy -c docker-compose.yml swarmdemo
```

### Cek status service:

```bash
docker service ls
```

### Hapus stack:

```bash
docker stack rm swarmdemo
```

---

## 📌 Catatan Akhir

- Gunakan `docker container prune` untuk bersih-bersih
- Gunakan `docker logs` untuk debugging
- Gunakan tagging (`:v1`, `:dev`, `:latest`) untuk kontrol versi image

---

## 🔗 Referensi

- [Docker CLI](https://docs.docker.com/engine/reference/commandline/docker/)
- [Dockerfile reference](https://docs.docker.com/engine/reference/builder/)
- [Flask documentation](https://flask.palletsprojects.com/)
- [Flask-CORS](https://flask-cors.readthedocs.io/)

---

## 🛠️ Tips Debugging & Modifikasi Image

Kadang kita lupa menambahkan dependensi atau ingin melakukan penyesuaian langsung di dalam container tanpa rebuild penuh. Berikut langkah-langkah praktis:

1. Masuk ke dalam container yang sedang berjalan:

   ```bash
   docker exec -it <container_id> /bin/sh
   ```

   Jika menggunakan image Python non-Alpine:

   ```bash
   docker exec -it <container_id> bash
   ```

2. Install dependensi langsung dari dalam container:

   ```bash
   pip install <nama-dependensi>
   ```

3. Commit perubahan menjadi image baru:

   ```bash
   docker commit <container_id> backend:hotfix
   ```

4. Jalankan image hasil modifikasi:
   ```bash
   docker run -p 5000:5000 backend:hotfix
   ```

> ⚠️ Untuk produksi, selalu update kembali `Dockerfile` dan `requirements.txt` agar image tetap bisa direproduksi dari awal.

---

## 🔍 Kenapa NGINX Alpine Menggunakan Port 80?

- `nginx:alpine` adalah image ringan yang secara default menjalankan server di port **80**
- Kita menggunakan `-p 8080:80` agar port 8080 di host terhubung ke port 80 di dalam container
- Direktori `/usr/share/nginx/html` adalah direktori default tempat NGINX mencari file HTML

Contoh:

```dockerfile
FROM nginx:alpine
COPY index.html /usr/share/nginx/html/index.html
```

Artinya file `index.html` akan langsung diakses pada `http://localhost:8080`

---

## 🌐 Tips Pengecekan Jaringan Antar Container

Dalam beberapa kasus, container mungkin tidak bisa saling terhubung karena masalah jaringan. Berikut adalah langkah-langkah dasar untuk pengecekan dan troubleshooting jaringan antar container:

### 🔎 1. Cek Daftar Network yang Ada

```bash
docker network ls
```

### 🔌 2. Lihat Detail Network Tertentu

```bash
docker network inspect <nama_network>
```

### 🔁 3. Ping Antar Container (Jika pakai custom network)

1. Buat network bridge:

   ```bash
   docker network create mybridge
   ```

2. Jalankan 2 container di network tersebut:

   ```bash
   docker run -dit --name c1 --network mybridge busybox
   docker run -dit --name c2 --network mybridge busybox
   ```

3. Masuk ke salah satu container dan ping:
   ```bash
   docker exec -it c1 sh
   ping c2
   ```

> ⚠️ `busybox` hanya contoh image ringan yang bisa digunakan untuk uji jaringan.

### 🧩 Gunakan Nama Service (bukan IP)

Jika menggunakan Docker Compose atau Swarm, gunakan **nama service** (misal `backend`, `frontend`) untuk komunikasi, karena Docker akan mengelola DNS internal antar service.

Contoh fetch di frontend:

```js
fetch("http://backend:5000/api");
```

---

---

## 🧭 Pemisahan Konfigurasi Compose dan Swarm

Untuk mempermudah pengelolaan, digunakan dua file konfigurasi yang berbeda:

### 📁 `docker-compose.yml` → untuk Pengembangan Lokal

- Menggunakan `build:` untuk membangun image langsung dari Dockerfile
- Cocok untuk pengujian dan debugging lokal
- Jalankan dengan:
  ```bash
  docker-compose up --build
  ```

### 📁 `docker-compose-swarm.yml` → untuk Deploy Docker Swarm

- Menggunakan `image:` karena Swarm **tidak mendukung `build:`**
- Jalankan setelah image dibangun secara manual:
  ```bash
  docker build -t swarmdemo_backend ./backend
  docker build -t swarmdemo_frontend ./frontend
  docker stack deploy -c docker-compose-swarm.yml swarmdemo
  ```

---

## ❗ Penjelasan Penting: Kenapa `fetch('http://localhost')` Tidak Selalu Bekerja?

### 📦 Kasus 1: Lokal (tanpa Docker)

- `localhost` di browser akan mengarah ke backend lokal di host
- Cocok untuk pengujian awal (tanpa container)

### 📦 Kasus 2: Frontend dalam container, backend di host

- Gunakan `host.docker.internal` (khusus Mac/Windows):
  ```js
  fetch("http://host.docker.internal:5000/api");
  ```

### 📦 Kasus 3: Compose / Swarm

- Gunakan nama service Docker (`http://backend:5000`)
- Karena `localhost` dari dalam container akan merujuk ke container itu sendiri, bukan host

### ✅ Solusi Adaptif

Gunakan JavaScript seperti ini di `index.html`:

```js
const isLocal = window.location.hostname === "localhost";
const BASE_URL = isLocal ? "http://localhost:5000" : "http://backend:5000";

fetch(`${BASE_URL}/api`);
```

---

## 🧯 Kenapa `docker stack deploy` Bisa Gagal?

### ⚠️ Error: `image reference must be provided`

Artinya file Compose menggunakan `build:` yang tidak didukung oleh Swarm.

**Solusi:**

- Gunakan `docker-compose build` untuk membangun image terlebih dahulu
- Lalu ubah file Compose ke `image:` dan deploy dengan `docker stack deploy`

---

---

## ⚠️ Pemahaman Tambahan: Masalah Umum Saat Compose dan Swarm

### 🔴 1. Kenapa `docker-compose up --build` Gagal?

Jika kamu menambahkan:

```yaml
deploy:
  replicas: 2
```

...lalu menjalankan `docker-compose up`, maka akan terjadi **konflik port**.

#### 📌 Penyebab:

- `docker-compose` **tidak mendukung `deploy.replicas`**
- Tapi tetap mencoba membuat 2 container **yang mem-bind port yang sama**
- Misalnya:
  - Dua backend mencoba membuka `5000:5000`
  - Hasil: `Only one usage of each socket address is normally permitted`

#### ✅ Solusi:

- Jangan pakai `deploy:` dalam `docker-compose.yml`
- Jalankan:
  ```bash
  docker-compose down
  docker-compose up --build
  ```

---

### 🟡 2. Kenapa `docker stack deploy` Gagal Jika Pakai `build:`?

Swarm **tidak bisa build image langsung**. Saat kamu jalankan:

```bash
docker stack deploy -c docker-compose.yml swarmdemo
```

...dengan file yang berisi:

```yaml
build: ./backend
```

Akan muncul error seperti:

```
failed to create service: image reference must be provided
```

#### ✅ Solusi:

1. **Build dulu imagenya secara manual:**

   ```bash
   docker build -t swarmdemo_backend ./backend
   docker build -t swarmdemo_frontend ./frontend
   ```

2. **Ubah `docker-compose-swarm.yml` menjadi:**

   ```yaml
   image: swarmdemo_backend
   ```

3. **Deploy:**
   ```bash
   docker stack deploy -c docker-compose-swarm.yml swarmdemo
   ```

---

### 🔄 3. Perbedaan `docker-compose` vs `docker stack deploy`

| Fitur                       | `docker-compose`           | `docker stack deploy`       |
| --------------------------- | -------------------------- | --------------------------- |
| Mendukung `build:`          | ✅ Ya                      | ❌ Tidak                    |
| Mendukung `deploy.replicas` | ❌ Tidak (diabaikan)       | ✅ Ya                       |
| Replikasi Container         | ❌ Manual                  | ✅ Otomatis via `replicas`  |
| Port harus unik per host    | ✅ Ya (satu bind per port) | ✅ Ya (hanya 1 yang expose) |
| Cocok untuk                 | Dev / Lokal                | Production / Skala Besar    |

---

---

## 🔎 Mengetahui Nama Service dan Memverifikasi DNS Antar Container

### 🧩 Menentukan Nama Service

#### 🔹 Docker Compose

Nama service diambil dari `docker-compose.yml`:

```yaml
services:
  backend:
  frontend:
```

Maka nama DNS service di dalam jaringan Docker adalah:

- `backend`
- `frontend`

> Ini berarti container `frontend` bisa mengakses `http://backend:5000` tanpa konfigurasi tambahan.

#### 🔹 Docker Swarm

Jika menggunakan:

```bash
docker stack deploy -c docker-compose-swarm.yml swarmdemo
```

Nama service Swarm menjadi:

- `swarmdemo_backend`
- `swarmdemo_frontend`

Namun untuk komunikasi internal antar service, **Docker tetap menyediakan alias DNS seperti `backend`**, jadi `http://backend:5000` tetap valid di dalam jaringan stack.

---

### 🧠 Mengecek DNS Docker Antar Container

#### 🔍 1. Masuk ke salah satu container

```bash
docker exec -it <nama_container> /bin/sh
```

Atau untuk Python image (non-alpine):

```bash
docker exec -it <nama_container> bash
```

#### 🔍 2. Tes DNS menggunakan `ping` atau `nslookup`

```bash
ping backend
```

Jika berhasil, berarti DNS internal Docker bekerja.

> Kamu bisa juga menggunakan:
>
> ```bash
> apt update && apt install -y dnsutils
> nslookup backend
> ```

> Gunakan `alpine` atau `busybox` container jika hanya ingin uji jaringan:
>
> ```bash
> docker run -it --network <network_name> busybox sh
> ping backend
> ```

---
