import pytest
import sys
import os
from datetime import datetime, timezone
from unittest.mock import MagicMock, patch
from flask_folder.spotify.spotify_dao import send_song_info, get_songs_from_db

# Add project root to path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

@pytest.fixture
def mock_song_collection():
    """Mock MongoDB collection for DAO tests."""
    with patch('flask_folder.spotify.spotify_dao.song_collection') as mock:
        mock.find_one.return_value = None
        mock.find.return_value = []
        mock.insert_one.return_value = MagicMock(inserted_id='test_id')
        mock.update_one.return_value = MagicMock(modified_count=1)
        yield mock

@pytest.fixture
def sample_song_data():
    """Sample song data for testing."""
    return {
        'user_uuid': 'test-uuid-123',
        'name': 'Test Song',
        'artist': 'Test Artist',
        'album_art': 'https://example.com/art.jpg',
        'track_ID': 'spotify:track:abc123',
        'lat': 29.9237376,
        'lng': -98.2417408
    }

# Unit tests for Spotify DAO
# TEST 1: Insert New Song with Valid Coordinates
def test_insert_new_song_with_valid_coords(mock_song_collection, sample_song_data):
    
    # Setup: No existing user
    mock_song_collection.find_one.return_value = None
    
    # Execute
    send_song_info(
        user_uuid=sample_song_data['user_uuid'],
        name=sample_song_data['name'],
        artist=sample_song_data['artist'],
        album_art=sample_song_data['album_art'],
        track_ID=sample_song_data['track_ID'],
        lat=sample_song_data['lat'],
        lng=sample_song_data['lng']
    )
    
    # Assert insert_one was called
    assert mock_song_collection.insert_one.called, "insert_one should be called for new user"
    
    # Get the document that was inserted
    call_args = mock_song_collection.insert_one.call_args
    inserted_doc = call_args[0][0]
    
    # Validate document structure
    assert inserted_doc['uuid'] == sample_song_data['user_uuid'], "UUID should match"
    assert inserted_doc['name'] == sample_song_data['name'], "Song name should match"
    assert inserted_doc['artist'] == sample_song_data['artist'], "Artist should match"
    assert inserted_doc['album_art'] == sample_song_data['album_art'], "Album art should match"
    assert inserted_doc['track_ID'] == sample_song_data['track_ID'], "Track ID should match"
    assert inserted_doc['lat'] == sample_song_data['lat'], "Latitude should match"
    assert inserted_doc['lng'] == sample_song_data['lng'], "Longitude should match"
    assert 'createdAt' in inserted_doc, "createdAt timestamp should be present"
    assert isinstance(inserted_doc['createdAt'], datetime), "createdAt should be datetime object"

# TEST 2: Update Existing User's Song
def test_update_existing_user_song(mock_song_collection, sample_song_data):

    # Existing user with old song
    old_timestamp = datetime(2025, 11, 1, 12, 0, 0, tzinfo=timezone.utc)
    existing_user = {
        'uuid': sample_song_data['user_uuid'],
        'name': 'Old Song',
        'artist': 'Old Artist',
        'album_art': 'https://old.com/art.jpg',
        'track_ID': 'spotify:track:old123',
        'lat': sample_song_data['lat'],
        'lng': sample_song_data['lng'],
        'createdAt': old_timestamp
    }
    mock_song_collection.find_one.return_value = existing_user
    
    # Update with new song (no coordinates provided)
    send_song_info(
        user_uuid=sample_song_data['user_uuid'],
        name='New Song',
        artist='New Artist',
        album_art='https://new.com/art.jpg',
        track_ID='spotify:track:new123',
        lat=None,
        lng=None 
    )
    
    # Assert update_one was called
    assert mock_song_collection.update_one.called, "update_one should be called for existing user"
    
    # Get the update document
    call_args = mock_song_collection.update_one.call_args
    filter_doc = call_args[0][0]
    update_doc = call_args[0][1]['$set']
    
    # Validate filter
    assert filter_doc['uuid'] == sample_song_data['user_uuid'], "Filter should match user UUID"
    
    # Validate updated fields
    assert update_doc['name'] == 'New Song', "Song name should be updated"
    assert update_doc['artist'] == 'New Artist', "Artist should be updated"
    assert update_doc['album_art'] == 'https://new.com/art.jpg', "Album art should be updated"
    assert update_doc['track_ID'] == 'spotify:track:new123', "Track ID should be updated"
    
    # Validate coordinates preserved
    assert update_doc['lat'] == sample_song_data['lat'], "Latitude should be preserved"
    assert update_doc['lng'] == sample_song_data['lng'], "Longitude should be preserved"
    
    # Validate timestamp refreshed
    assert 'createdAt' in update_doc, "createdAt should be updated"
    assert isinstance(update_doc['createdAt'], datetime), "createdAt should be datetime"
    assert update_doc['createdAt'] > old_timestamp, "createdAt should be newer (TTL reset)"

# TEST 3: Get Songs Validates Coordinates
def test_get_songs_validates_coordinates(mock_song_collection, caplog):

    # Setup: Mix of valid and invalid data
    mock_documents = [
        # Valid song example
        {
            'uuid': 'user1',
            'name': 'Valid Song',
            'artist': 'Artist 1',
            'album_art': 'https://art1.com',
            'track_ID': 'track1',
            'lat': 29.9237376,
            'lng': -98.2417408
        },
        # Missing lat example
        {
            'uuid': 'user2',
            'name': 'Missing Lat',
            'artist': 'Artist 2',
            'album_art': 'https://art2.com',
            'track_ID': 'track2',
            'lng': -98.0
        },
        # Null coordinates example
        {
            'uuid': 'user3',
            'name': 'Null Coords',
            'artist': 'Artist 3',
            'album_art': 'https://art3.com',
            'track_ID': 'track3',
            'lat': None,
            'lng': None
        },
        # Non-numeric coordinates example
        {
            'uuid': 'user4',
            'name': 'Invalid Coords',
            'artist': 'Artist 4',
            'album_art': 'https://art4.com',
            'track_ID': 'track4',
            'lat': 'not-a-number',
            'lng': 'also-invalid'
        }
    ]
    mock_song_collection.find.return_value = mock_documents
    
    # Execute
    import logging
    with caplog.at_level(logging.WARNING):
        songs = get_songs_from_db()
    
    # Assert only 1 valid song returned
    assert len(songs) == 1, "Should return only 1 valid song"
    
    # Validate the valid song
    assert songs[0]['username'] == 'user1', "Username should match"
    assert songs[0]['song_title'] == 'Valid Song', "Song title should match"
    assert songs[0]['artist_name'] == 'Artist 1', "Artist should match"
    assert songs[0]['lat'] == 29.9237376, "Latitude should match"
    assert songs[0]['lng'] == -98.2417408, "Longitude should match"
    
    # Validate warning logs for invalid data
    assert 'Skipping song with missing coords' in caplog.text, "Should log missing coords"
    assert 'Invalid coord types' in caplog.text, "Should log invalid coord types"
    
    # Count warnings (should be 3: missing, null, invalid)
    warning_count = caplog.text.count('WARNING')
    assert warning_count >= 3, f"Should have at least 3 warnings, got {warning_count}"
