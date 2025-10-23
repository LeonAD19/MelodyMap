from datetime import datetime, timezone
from dotenv import load_dotenv
from pymongo import MongoClient, ASCENDING
import os
import certifi

# TEMP:
load_dotenv()


# Get MongoDB URI from env, raise error if not set
uri = os.getenv('MONGODB_URI')
if not uri:
    raise ValueError("MONGODB_URI environment variable not set.")

# Create client
client = MongoClient(
    uri, 
    tlsCAFile=certifi.where()   # use a verified HTTPS certificate list
)

db = client.spotify            # database
song_collection = db.songs            # collection

song_collection.create_index(
    [("createdAt", ASCENDING)],
    expireAfterSeconds=30  # 30 seconds
)

def send_song_info(user_uuid: str, name: str = "test"):
    if user_uuid is None or name is None:
        print("why is str none???")
        return
    
    if song_collection.find_one({"uuid": user_uuid, "name": name}) != None:
        return
    
    # Insert to DB
    created_at = datetime.now(timezone.utc)
    song_collection.insert_one(
        {"uuid": user_uuid, "name": name, "createdAt": created_at}
    )
    # print("Inserted:", {"uuid": user_uuid, "name": name, "createdAt": created_at})
    

# send_song_info("124798", "test2")