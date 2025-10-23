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

def send_song_info(user_uuid: str, name: str, lat: float, lng: float):
    if user_uuid is None or name is None:
        print("why is str none???")
        return
    
    # If user has some song 
    user_record = song_collection.find_one({"uuid": user_uuid})
    created_at = datetime.now(timezone.utc)
    if user_record == None:
        # Insert to DB
        song_collection.insert_one({
            "uuid": user_uuid, 
            "name": name, 
            "lat": lat,
            "lng": lng,
            "createdAt": created_at
            }
        )
        return 
    
    # If a record for the current song already exists, do nothing
    if user_record.get('name') == name:
        return
    
    # If the current song doesnt exist, but the uuid exists. Update the record to new song and reset expiration 
    song_collection.update_one(
        {"uuid": user_uuid},
        {"$set": {
            "name": name,
            "createdAt": created_at
        }}
    )
    
    
