# 🚀 Docker Swarm Session Sharing Demo

Proyek ini dibuat untuk mempelajari bagaimana membangun aplikasi sederhana menggunakan **Flask** sebagai backend dan **HTML/JavaScript** sebagai frontend dengan tujuan utama **mempelajari session sharing menggunakan Redis** di lingkungan **Docker Compose** dan **Docker Swarm**. Proyek ini dibangun secara bertahap, dimulai dari lokal tanpa Docker, hingga deployment berbasis Swarm.

---

## 🌍 Tujuan & Konsep

Aplikasi ini bertujuan untuk menunjukkan bagaimana **session counter** (menggunakan Flask) dapat disimpan secara **persisten** dan **terdistribusi** melalui Redis.

**Permasalahan utama:** Flask secara default menyimpan session di memori lokal (per container). Jika backend dijalankan di beberapa container, session tidak konsisten.

**Solusi:** Gunakan Redis sebagai session store bersama antar instance backend. Redis hanya bisa dikenali antar-container jika dijalankan di jaringan Docker (bukan saat Flask dijalankan langsung di host).

---

## 📅 Langkah Tahapan Pembangunan

### ✅ 1. Uji Aplikasi Manual (Tanpa Docker)

**Backend (Flask):**
```bash
cd backend
python -m venv venv
venv\Scripts\activate
pip install flask flask-session flask-cors redis
python app.py
```

**Frontend:**
```bash
cd frontend
python -m http.server 8080
```

**Masalah:**
Jika Redis dijalankan di dalam container, Flask (yang berjalan di host) tidak bisa mengenali `host='redis'`. Maka:
- Gunakan `host='localhost'` jika Redis di host
- Gunakan Docker Compose jika Redis dan Flask di container

---

### ✅ 2. Jalankan Redis via Docker

```bash
docker run -d --name redis -p 6379:6379 redis:alpine
```

Ubah koneksi di `app.py`:
```python
redis.StrictRedis(host='localhost', port=6379)
```

Lalu uji Flask kembali.

---

### ✅ 3. Uji Dengan Docker Saja (Tanpa Compose)

Build manual:
```bash
docker build -t backend-test ./backend
docker run -p 5000:5000 backend-test
```

Namun Redis harus dijalankan juga secara manual dan **pastikan keduanya dalam jaringan Docker yang sama**, atau gunakan bridge network khusus.

---

### ✅ 4. Gunakan Docker Compose

Setelah Redis dan backend dijalankan bersama, buat file `docker-compose.yml`:

```yaml
version: "3.8"
services:
  redis:
    image: redis:alpine
    ports:
      - "6379:6379"

  backend:
    build: ./backend
    ports:
      - "5000:5000"
    depends_on:
      - redis

  frontend:
    build: ./frontend
    ports:
      - "8080:80"
    depends_on:
      - backend
```

Jalankan:
```bash
docker-compose up --build
```

---

### ✅ 5. Deploy ke Docker Swarm

Swarm tidak mendukung `build:` sehingga perlu build manual image terlebih dahulu:
```bash
docker build -t swarmdemo_backend ./backend
docker build -t swarmdemo_frontend ./frontend
```

File: `docker-compose-swarm.yml`
```yaml
version: "3.8"
services:
  redis:
    image: redis:alpine
    ports:
      - "6379:6379"

  backend:
    image: swarmdemo_backend
    ports:
      - "5000:5000"
    deploy:
      replicas: 2

  frontend:
    image: swarmdemo_frontend
    ports:
      - "8080:80"
    deploy:
      replicas: 2
```

Deploy:
```bash
docker swarm init

docker stack deploy -c docker-compose-swarm.yml swarmdemo
```

Hapus:
```bash
docker stack rm swarmdemo
```

---

## 🔍 Tujuan Uji Coba Session Sharing

Dengan konfigurasi ini, frontend akan melakukan fetch ke `/api`, dan backend akan menyimpan session counter di Redis. Saat direplikasi di Swarm, session tetap konsisten walaupun request diarahkan ke instance backend berbeda.

Frontend fetch:
```js
fetch("http://backend:5000/api", {
  credentials: "include"
})
```

Backend menggunakan Redis:
```python
app.config['SESSION_TYPE'] = 'redis'
app.config['SESSION_REDIS'] = redis.StrictRedis(host='redis', port=6379)
```

---

## 🌓 Catatan Penting

- `host='redis'` hanya berfungsi jika Redis dan Flask dalam 1 jaringan Docker.
- Saat dijalankan lokal (non-Docker), gunakan `host='localhost'`.
- CORS harus diaktifkan dengan `supports_credentials=True` jika frontend fetch menggunakan `credentials: "include"`.
- Jangan gunakan `deploy:` saat menjalankan `docker-compose up` biasa.

---

## 💡 Tips Debugging

- Cek container:
```bash
docker ps -a
```
- Cek log:
```bash
docker logs <container_id>
```
- Hapus container:
```bash
docker rm -f <container_id>
```
- Hapus stack:
```bash
docker stack rm swarmdemo
```
- Bersih-bersih:
```bash
docker system prune -a --volumes -f
```

---

## 🔗 Referensi

- [Flask-CORS](https://flask-cors.readthedocs.io/)
- [Flask-Session](https://flask-session.readthedocs.io/)
- [Docker CLI](https://docs.docker.com/engine/reference/commandline/docker/)
- [Docker Compose vs Swarm](https://docs.docker.com/compose/)
