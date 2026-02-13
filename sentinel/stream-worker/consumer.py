import json
import time
from redis_writer import RedisClient
from features import calculate_rolling_stats

# CONFIG
STREAM_KEY = "game_events"
GROUP_NAME = "sentinel_processors"
CONSUMER_NAME = "worker_1"
HISTORY_LEN = 20  # Look at last 20 clicks

# Connect
r_client = RedisClient()
r = r_client.get_client()
r_client.create_consumer_group(STREAM_KEY, GROUP_NAME)

print("👀 Sentinel Stream Worker Listening...")

while True:
    try:
        # 1. READ from Stream (Blocking for 1 sec to save CPU)
        # '>' means "give me new messages I haven't seen yet"
        entries = r.xreadgroup(GROUP_NAME, CONSUMER_NAME, {STREAM_KEY: '>'}, count=1, block=1000)

        if not entries:
            continue

        for stream, messages in entries:
            for message_id, content in messages:
                
                # 2. PARSE Data
                try:
                    payload = json.loads(content['payload'])
                    user_id = content['user_id']
                    click_data = payload['click_data']
                except (KeyError, json.JSONDecodeError):
                    print(f"⚠️ Corrupt data: {content}")
                    r.xack(STREAM_KEY, GROUP_NAME, message_id)
                    continue

                # 3. UPDATE Sliding Window History (The "State")
                # We use a Redis List to store the last 20 clicks for this specific user
                history_key = f"history:{user_id}"
                
                # Push new click to the left (Head)
                r.lpush(history_key, json.dumps(click_data))
                
                # Trim list to keep only last 20 (Tail)
                r.ltrim(history_key, 0, HISTORY_LEN - 1)

                # 4. FETCH History & CALCULATE Features
                # Get all items in the list
                raw_history = r.lrange(history_key, 0, -1)
                # Convert strings back to JSON
                history_objs = [json.loads(x) for x in raw_history]

                features = calculate_rolling_stats(history_objs)

                # 5. SAVE Features to Feature Store (Redis Hash)
                if features:
                    feature_key = f"features:{user_id}"
                    r.hset(feature_key, mapping=features)
                    
                    print(f"🧠 Updated {user_id}: Var={features['reaction_time_variance']:.2f} | Acc={features['accuracy_mean']:.2f}")

                # 6. ACKNOWLEDGE Message (Tell Redis we are done)
                r.xack(STREAM_KEY, GROUP_NAME, message_id)

    except Exception as e:
        print(f"❌ Error: {e}")
        time.sleep(1)