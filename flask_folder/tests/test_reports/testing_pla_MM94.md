# Testing Plan — MM-94 (Jacob M.)

These three tests cover the core functionality of hiding card when user is not authorized. when backend reports unauthorized userm and renders now playing with advancing ticks.

## 1. Components Selected for Testing
Frontend user.js (now-playing card renderer) because it controls visibility,  song info, and updates progress.

### Unit Tests (user.js)
1. window.SPOTIFY_AUTH false - hides card when client is not authorized 
2. authorized - false in response hides card when backend reports unauthorized 
3. title, artists, art, progress width increases over time - renders now-playing data and advances progress on tick (title, artists, art, progress width increases over time)

These functions work with MongoDB documents and therefore require mocking.

The unit tests verify:
- card visibility toggles correctly
- song data redner when authorized and song playing 
- progress bar is moving forward 

To run unit testing enter this in terminal
Run: node --test flask_folder/tests/test_user.js
