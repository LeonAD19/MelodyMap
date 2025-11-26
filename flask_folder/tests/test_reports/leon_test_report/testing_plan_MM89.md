# Testing Plan — MM-89 (Leon A.)

These three tests cover the core functionality of storing, updating, and retrieving user music data, which is the main responsibility of spotify_dao

## 1. Components Selected for Testing
I chose to test the spotify_dao module because it is core to storing and retrieving user music pin data

### Unit Tests (spotify_dao)
1. send_song_info() — inserting new song data
2. send_song_info() — updating existing song data
3. get_songs_from_db() — validating coordinates before returning

These functions work with MongoDB documents and therefore require mocking.

The unit tests verify:
- correct fields stored
- correct refresh behavior
- coordinates preserved
- invalid data skipped
- warning logs emitted

To run unit testing enter this in terminal
Run: pytest flask_folder/tests/test_spotify_dao.py -v
