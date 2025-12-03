# Melody Map

## 📌 Project Name
**Melody Map**

---

## 🎯 Description

**Who you’re working with**  
Team Members:  
- Mateo Salinas  
- Leon Altamirano  
- Devin Schupbach  
- Caden Sprague  
- Jacob Mora  

**What you’re creating**  
We are building a website where people around you can see what music you are listening to in real time. Beyond simply showing the current track, we aim to add unique features such as displaying which portion of a song someone is on. The website will integrate with both **Spotify** and **Apple Music**, and depending on how our sprints progress, we may also expand to a mobile app version.  

**Who you’re doing it for (your audience)**  
Our audience includes students, music enthusiasts, and everyday listeners who want to share and discover music with people nearby.  

**Why you’re doing this (the impact/change you hope to make)**  
We want to:  
- Help people discover new music.  
- Provide a platform to share music in a fun, interactive way.  
- Encourage social connection through music discovery while maintaining user privacy.  

---

## ![Project Logo](./Documentation/MelodyMapLogo.png)

---

## 🛠️ Technologies

We plan to use the following technologies:  
- **Frontend Engine** for loading the website  
- **Mapping Engine** for map/pins functionality  
- [Spotify API](https://developer.spotify.com/) and [Apple Music API](https://developer.apple.com/apple-music/) for track integration  
- **AI Tools**: [ChatGPT](https://chat.openai.com/), [Gemini](https://deepmind.google/technologies/gemini/), and [GitHub Copilot](https://github.com/features/copilot) to assist with debugging, formatting, and ideation.  

---

## 🚀 Features

### Initial Sprint Features

1. **Map Creation**  
   - Displays a world map on the site.  
   - Used by all users as the base interactive layer.  

2. **User Location Tracking**  
   - Automatically detects the user’s location when the app loads.  
   - Centers the map view on the user’s current location.  

3. **Pin Creation**  
   - Users can place “pins” on the map at specific locations.  
   - Optional feature: customize pin images (not required for MVP).  

4. **Music Integration – Apple Music**  
   - Pulls the current track name from Apple Music.  
   - Displays this info on the user’s pin/location.  

5. **Music Integration – Spotify**  
   - Pulls the current track name from Spotify.  
   - Displays this info on the user’s pin/location.  

6. **Nearby Listening Visibility**  
   - Allows users to see what others within a one-mile radius are listening to in real time.  
##
## Sprint 1 Review

### Review and Retrospective

For this sprint our main focus was to create the website, communicate with spotify api, and create a map.

* [__Retrospective__](./Documentation/Sprint1/Sprint1-Retrospective.md)

* __Burnup Report:__ ![Sprint1-Burnup](./Documentation/Sprint1/Sprint1-Burnup.png)

* __Contributions__
   * [Jira Task Documentation](./Documentation/Sprint1/Sprint1-Jira.md)

   * __Caden__ : Established a route that communicates with Spotify API, and implemented spotify token refresh (so end user needs to manually verify as little as possible).
   * __Devin__ : Created and designed the inital homepage/website, implemented a feature to display the current song's  metadata on map pin, and display which account type has been linked.
   * __Jacob__ : Created a barebones flask website to run locally, implemented a feature that shows error codes coming from spotify's api, and researched on how to deploy to firebase. 
   * __Leon__ : I implemented the OAuth login and handled the OAuth callback process. I also worked with Caden to store the access token securely. In addition, I developed the OAuth request and redirect endpoints and integrated the login display into the home.html page.
   * __Mateo__ : Researched and implemented the map API. Ensured map displayed current user location, can scroll, and zoom in and out of map. Also made sure user can add pins to map and the pin(s) are displayed. 

* __Future Implementation__

   * Deploy to firebase

   * Create better UI/UX

   * Show other users' songs on map

   * Refine pin functionality


# Sprint 2 Review

### Demo
We demoed the develop branch

### Review and Retrospective

For this sprint our main focus was to host the website, create and use a database, and overhaul the UI.

* [__Retrospective__](./Documentation/Sprint2/Sprint2-Retrospective.md)

* __Burnup Report:__ ![Sprint2-Burnup](./Documentation/Sprint2/Sprint2-Burnup.png)

* __Contributions__
   * [Jira Task Documentation](./Documentation/Sprint2/Sprint2-Jira.md)

   * __Caden__ : I set up the host environment in Google Cloud, created the database, and implemented functionality to send song information to the database.
   * __Devin__ : I merged all the different webpages we had into one homepage, fixed the visuals for the pin song information that was displayed, and redesigned the UI for the homepage for a polished look.
   * __Jacob__ : I implemented logout button, and created a user card that displays the current song from user, which handles when no song is playing and tracks song progress. 
   * __Leon__ : Implemented handling song info on map pins including the location as well as having a mock account setup. Displayed the user profile info on the top bar showing the users profile pic as well as the username.
   * __Mateo__ : I researched the lifetime of our pins in our map. I determined why/when they expired and how to ensure that their lifetime did not expire.  I created a document that contained my research and attached it to the given task. I also created/started working on our unit and integration tests.

* __Future Implementation__

   * Uniform pin displays (not a different view for MY pin vs YOUR pin)

   * Pin lifetime should have certain lifetime after the song ends, and should not be removed until the song is over.

   * Get our spotify app public (so others can use the app too)

   * Update location for pins (instead of just timing it out and replacing the song info at the old location)

   * link/redirect function so user can click on another person's song and see it on spotify/maybe hear a preview?

# Sprint 3 Review

### Demo
We demoed the develop branch

### Review and Retrospective

For this sprint our main focus was to finalize aspects of the user expierence, now the use can preview other people's songs and queue them into their own spotfy accounts. There is also some user customization for the expiereience of the user. 

* [__Retrospective__](./Documentation/Sprint2/Sprint3-Retrospective.md)

* __Burnup Report:__ ![Sprint3-Burnup](./Documentation/Sprint3/Sprint3-Burnup.png)

* __Contributions__
   * [Jira Task Documentation](./Documentation/Sprint3/Sprint3-Jira.md)

   * __Caden__ : I changed how pins are dropped and adds a side panel that allows the user to preview someone else's song. I also added a test for the spotify_tokens and song preview.
   * __Devin__ : I created my tests for the front end, added a settings popup, created the customized pins, and the ability to shift between light and dark mode on the map.
   * __Jacob__ : 
   * __Leon__ : I created user profile and player card selections for UI. Created backend routes for the user to select those options. I also created spotify_dao test files to test spotify send song info and get song info. This data also generated a hmtl report that I converted to a pdf.
   * __Mateo__ : I fixed some errors I had with the Spotify login flow unit and integration tests that were implemented last sprint. This sprint I added new unit tests that ensured that our application was compatible with the Spotify login flow. I also made integration tests that made sure our application tested how our application handles different scenarios that involve the Spotify login flow such as API errors, login errors, etc.

* __Future Implementation__

   * Getting permission from spotify for a public app 
   * Generate more UX for the user such as adding a liked songs or favorite playlist 
   * Optimize the codebase to support high volume users
   * 