import os  # Add this line
import redis
import json

class RedisClient:
    def __init__(self):
        # Use 'redis' inside Docker, 'localhost' outside
        host = os.getenv('REDIS_HOST', 'redis') # Default to 'redis' for docker
        self.client = redis.Redis(host=host, port=6379, decode_responses=True)

    def get_client(self):
        return self.client

    def create_consumer_group(self, stream_key, group_name):
        """Creates a consumer group if it doesn't exist."""
        try:
            # '0' means start reading from the beginning of time
            self.client.xgroup_create(stream_key, group_name, id='0', mkstream=True)
            print(f"Consumer Group '{group_name}' created.")
        except redis.exceptions.ResponseError as e:
            if "BUSYGROUP" in str(e):
                print(f"Consumer Group '{group_name}' already exists.")
            else:
                raise e