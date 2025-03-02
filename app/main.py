from flask import Flask, jsonify
import redis
import hashlib
import time
import threading

app = Flask(__name__)


class Cache:
    def __init__(self, ttl=5):  
        self.cache = {}  
        self.ttl = ttl
        self.lock = threading.Lock()

    def get(self, key):
        with self.lock:
            if key in self.cache:
                value, timestamp = self.cache[key]
                if time.time() - timestamp < self.ttl:
                    return value
                else:
                    del self.cache[key]  
        return None

    def set(self, key, value):
        with self.lock:
            self.cache[key] = (value, time.time())


class WriteBatcher:
    def __init__(self, redis_client, flush_interval=30):
        self.buffer = {}  
        self.redis_client = redis_client
        self.flush_interval = flush_interval
        self.lock = threading.Lock()
        self.running = True
        threading.Thread(target=self._flush_loop, daemon=True).start()

    def increment(self, page_id):
        with self.lock:
            self.buffer[page_id] = self.buffer.get(page_id, 0) + 1

    def get_pending(self, page_id):
        with self.lock:
            return self.buffer.get(page_id, 0)

    def flush(self):
        with self.lock:
            if not self.buffer:
                return
            for page_id, count in self.buffer.items():
                self.redis_client.incrby(page_id, count)
            self.buffer.clear()

    def _flush_loop(self):
        while self.running:
            time.sleep(self.flush_interval)
            self.flush()


class ShardedRedis:
    def __init__(self):
        self.shards = {
            "redis_7070": redis.Redis(host='localhost', port=7070, db=0),
            "redis_7071": redis.Redis(host='localhost', port=7071, db=0),
        }

    def _get_shard(self, key):
        hash_value = int(hashlib.md5(key.encode()).hexdigest(), 16)
        shard_index = hash_value % len(self.shards)
        return list(self.shards.keys())[shard_index]

    def incrby(self, key, amount):
        shard = self._get_shard(key)
        self.shards[shard].incrby(key, amount)
        return shard

    def get(self, key):
        shard = self._get_shard(key)
        value = self.shards[shard].get(key)
        return value, shard


redis_client = ShardedRedis()  
app_cache = Cache(ttl=5)       
batcher = WriteBatcher(redis_client, flush_interval=30)  


@app.route('/visits/<page_id>', methods=['POST'])
def increment_visit(page_id):
    
    batcher.increment(page_id)
    return jsonify({"message": f"Visit to {page_id} recorded"})

@app.route('/visits/<page_id>', methods=['GET'])
def get_visits(page_id):
    
    cached_count = app_cache.get(page_id)
    if cached_count is not None:
        return jsonify({"visits": cached_count, "served_via": "in_memory"})

    
    redis_value, shard = redis_client.get(page_id)
    redis_count = int(redis_value or 0)

   
    pending_count = batcher.get_pending(page_id)
    total_count = redis_count + pending_count

    
    app_cache.set(page_id, total_count)

   
    batcher.flush()

    
    return jsonify({"visits": total_count, "served_via": shard})

if __name__ == '__main__':
    app.run(debug=True, port=5000)