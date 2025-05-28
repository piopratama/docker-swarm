import redis

# Connect to Redis running in Docker (bound to localhost:6379)
r = redis.Redis(host='localhost', port=6379)

# Ensure stream and group exist
try:
    r.xgroup_create('mystream', 'mygroup', id='0', mkstream=True)
except redis.exceptions.ResponseError as e:
    if "BUSYGROUP" not in str(e):
        raise

# Add a message to the stream
r.xadd('mystream', {'foo': 'bar'})

# Read a message from the stream using the group
msgs = r.xreadgroup('mygroup', 'consumer1', {'mystream': '>'}, count=1)
print(msgs)
