from datetime import datetime, timezone
from pymongo import MongoClient, ASCENDING
import os
import certifi
from flask_folder import logger

# Get MongoDB URI from env, raise error if not set
uri = os.getenv('MONGODB_URI')
if not uri:
    logger.error("MONGODB_URI environment variable not set.")
    client = None
    db = None
    song_collection = None
else:
    # Create client
    client = MongoClient(
        uri,
        tlsCAFile=certifi.where(),   # use a verified HTTPS certificate list
        serverSelectionTimeoutMS=3000,  # prevents hanging requests / timeouts.
        socketTimeoutMS=3000    # prevents hanging requests / timeouts.
    )

    SONG_RECORD_TTL_SECONDS = 30

    db = client.spotify            # database
    song_collection = db.songs            # collection

    song_collection.create_index(
        [("createdAt", ASCENDING)],
        expireAfterSeconds=SONG_RECORD_TTL_SECONDS
    )

def send_song_info(user_uuid: str, name: str, artist: str, album_art: str, lat: float = None, lng: float = None):
    if song_collection is None:
        logger.error("Cannot send song info: MongoDB connection not available.")
        return

    if user_uuid is None or name is None:
        logger.error(f"send_song_info called with invalid params: uuid={user_uuid}, name={name}")
        return

    # If user has some song
    user_record = song_collection.find_one({"uuid": user_uuid})
    created_at = datetime.now(timezone.utc)
    
    # Build the update document with required fields
    update_doc = {
        "name": name,
        "artist": artist,
        "album_art": album_art,
        "createdAt": created_at
    }

    # Only update lat/lng if both are provided
    # Else we pull the old lat and lng
    if lat is not None and lng is not None:
        update_doc["lat"] = lat
        update_doc["lng"] = lng
    else:
        if user_record is not None:
            update_doc['lat'] = user_record.get('lat')
            update_doc['lng'] = user_record.get('lng')

    if user_record is None:
        # New user: require coordinates
        if lat is None or lng is None:
            logger.warning(f"Cannot create new record for {user_uuid}: lat/lng required for new users")
            return

        # Insert to DB
        song_collection.insert_one({
            "uuid": user_uuid,
            **update_doc
        })
        return

    # If a record for the current song already exists for the current user, do nothing
    if user_record.get('name') == name:
        return
    
    # If the current song doesn't exist, but the uuid exists. Update the record to new song and reset expiration
    song_collection.update_one(
        {"uuid": user_uuid},
        {"$set": update_doc}
    )

# Retrieve all songs from the database
def get_songs_from_db():
    if song_collection is None:
        return []
    
    songs = []
    for song in song_collection.find():
        # Extract coordinates
        lat = song.get("lat")
        lng = song.get("lng")
        
        # Skip documents with missing/invalid coordinates
        # (Prevents "null" pins at 0.0, 0.0)
        if lat is None or lng is None:
            logger.warning(f"Skipping song with missing coords: {song.get('uuid')}")
            continue
        try:
            lat_float = float(lat)
            lng_float = float(lng)
        except (ValueError, TypeError):
            logger.warning(f"Invalid coord types for {song.get('uuid')}: lat={lat}, lng={lng}")
            continue
        
        songs.append({
            "username": song.get("uuid", "Anonymous"),
            "song_title": song.get("name", "Unknown"),
            "artist_name": song.get("artist", "Unknown"),
            "album_art": song.get("album_art"),
            "lat": lat_float,
            "lng": lng_float,
        })
    return songs