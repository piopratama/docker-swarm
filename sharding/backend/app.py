from flask import Flask, jsonify, request
from flask_cors import CORS
import psycopg2, time, threading, os, requests

app = Flask(__name__)
CORS(app)

USE_LOCAL = os.environ.get("RUN_ENV", "").lower() == "local"

# Host dan port DB
def get_db_host(db_key):
    docker_hosts = {
        "shard1": ("shard1-db", 5432),
        "shard2": ("shard2-db", 5432),
        "replica1": ("replica1-db", 5432),
        "replica2": ("replica2-db", 5432),
    }
    local_hosts = {
        "shard1": ("localhost", 5433),
        "shard2": ("localhost", 5434),
        "replica1": ("localhost", 5436),
        "replica2": ("localhost", 5437),
    }
    return local_hosts[db_key] if USE_LOCAL else docker_hosts[db_key]

def try_connect(dbname, dbkey):
    host, port = get_db_host(dbkey)
    try:
        return psycopg2.connect(
            dbname=dbname,
            user="user",
            password="pass",
            host=host,
            port=port
        )
    except Exception as e:
        print(f"[ERROR] Cannot connect to {dbname} at {host}:{port} → {e}")
        return None

# Elasticsearch config
ES_URL = "http://elasticsearch:9200/demo/_doc"

def index_to_elasticsearch(doc, retries=3):
    for attempt in range(1, retries + 1):
        try:
            res = requests.post(ES_URL, json=doc)
            if res.status_code in [200, 201]:
                print(f"[INFO] Indexed to ES → ID: {doc.get('id')}, Data: {doc.get('data')}")
                return
            else:
                print(f"[WARN] Attempt {attempt}: Failed to index → {res.status_code} → {res.text}")
        except Exception as e:
            print(f"[WARN] Attempt {attempt}: Exception during ES indexing → {e}")
        time.sleep(1)
    print("[ERROR] Giving up on indexing to ES.")

# Hitung isi shard1
def get_shard1_count():
    conn = try_connect("shard1", "shard1")
    if not conn:
        return 0
    cur = conn.cursor()
    cur.execute("SELECT COUNT(*) FROM demo")
    count = cur.fetchone()[0]
    conn.close()
    return count

@app.route("/write")
def write_data():
    count = get_shard1_count()
    data = f"data-{count + 1}"
    db_target = "shard1" if count < 5 else "shard2"

    conn = try_connect(db_target, db_target)
    if not conn:
        db_target = "shard2" if db_target == "shard1" else "shard1"
        conn = try_connect(db_target, db_target)
        if not conn:
            return jsonify({"error": "Both shards unavailable"}), 500

    cur = conn.cursor()
    cur.execute("INSERT INTO demo (data, source) VALUES (%s, %s)", (data, db_target))
    conn.commit()
    cur.execute("SELECT currval(pg_get_serial_sequence('demo','id'))")
    new_id = cur.fetchone()[0]
    conn.close()

    # Index ke Elasticsearch
    index_to_elasticsearch({
        "id": new_id,
        "data": data,
        "source": db_target
    })

    return jsonify({"written_to": db_target, "data": data})

@app.route("/read")
def read_data():
    results = []
    for replica_name in ["replica1", "replica2"]:
        conn = try_connect(replica_name, replica_name)
        if not conn:
            continue
        cur = conn.cursor()
        cur.execute("SELECT * FROM demo")
        rows = cur.fetchall()
        for row in rows:
            results.append({
                "id": row[0],
                "data": row[1],
                "source": row[2],
                "replica": replica_name
            })
        conn.close()
    results.sort(key=lambda x: x['id'])
    return jsonify(results)

@app.route("/search")
def search_data():
    keyword = request.args.get("q", "").strip()
    if not keyword:
        return jsonify({"error": "Parameter 'q' harus diisi"}), 400

    es_query = {
        "query": {
            "match_phrase": {
                "data": keyword
            }
        }
    }

    try:
        res = requests.get("http://elasticsearch:9200/demo/_search", json=es_query)
        es_data = res.json()
        hits = es_data.get("hits", {}).get("hits", [])
        results = [hit["_source"] for hit in hits]
        return jsonify(results)
    except Exception as e:
        return jsonify({"error": f"Elasticsearch search failed: {e}"}), 500


# Replikasi dari shard → replica
def replicate_data():
    while True:
        time.sleep(10)
        for source_db, replica_db in [("shard1", "replica1"), ("shard2", "replica2")]:
            source_conn = try_connect(source_db, source_db)
            replica_conn = try_connect(replica_db, replica_db)
            if not source_conn or not replica_conn:
                continue

            source_cur = source_conn.cursor()
            source_cur.execute("SELECT * FROM demo")
            data = source_cur.fetchall()
            source_conn.close()

            replica_cur = replica_conn.cursor()
            replica_cur.execute("SELECT id FROM demo")
            existing_ids = set(row[0] for row in replica_cur.fetchall())

            for row in data:
                if row[0] not in existing_ids:
                    replica_cur.execute(
                        "INSERT INTO demo (id, data, source) VALUES (%s, %s, %s)",
                        (row[0], row[1], row[2])
                    )
            replica_conn.commit()
            replica_conn.close()

# Jalankan replikasi background
threading.Thread(target=replicate_data, daemon=True).start()

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000)
