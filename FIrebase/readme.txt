In this project we will be using firebase to deploy our website. 
This readme is documentation on how to deploy our webapp.
We will be using firebase, as it allows development on mobile and desktop applciations

To get the system functional, use the following command
'''
gcloud run deploy melody-map   --source .   --region us-central1   --allow-unauthenticated
'''

Step 1: 
    Add firebase token and project name as variables
    By defining the two variables
    1. FIREBASE_TOKEN - Firebase CLI token. Use a secured variable for this so that it is masked and encrypted in our logs.
    2.FIREBASE_PROJECT - Firebase project name. If we dont have have we need to create one in firebase console.

Step 2:
    Assuming Firebase CLI is installed
    Our project contains a firebase.json (firebase_json_example.json file has been created as an example)
    once file is locally ran, firebase init will be generated.

Step 3: 
    Using a pipe to deploy to firebase
    Firebase will add deployment configuration in our bitbucket-pipeline.yml file. (bitbucket-pipeline-example.yml has been made to show how it would look)
    bitbucket deployments will be able to track development 
    Once committed, it will be reported if successful or not. 
    Once successful application will be running on firebase 

