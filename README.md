# meraki-naclitedb
Many Enterprises leverage a combination of off the shelf security tools and homegrown applications to create a source of truth for their endpoints. While Identity Services Engine (ISE) is an option to provide unified access policy in an enterprise another approach would be to leverage information in existing homegrown endpoint databases to trigger policy changes for wired and wireless clients in a Meraki network.

This app is intended to represent the above scenario. A Simple SQL db has been created with several endpoints. A frontend API gateway using flask was added to handle CRUD operations on endpoints in the database. For example via this API we can manually change posture from trusted to untrusted or allow other security tools to drive these changes dynamically.

When an endpoint is updated in the database dynamically via a posture scan or manually as seen in the demo below, that triggers an API call to the meraki cloud dashboard to change client firewall from Trusted to Untrusted or vice versa.

#### Demo
   Update endpoint status in database and trigger relevant Meraki client Group Policy change.
    
   <img src=gifs/naclitemeraki.gif width="100%" height="100%">

### Installation
- git clone https://github.com/msiegy/meraki-naclitedb.git
- pip install -r requirements.txt
- Remove '.sample' from the .env file and enter the relevent API key information.
- Start the app and flask server with: python api.py

- The demo application is now running, you can use postman to hit the flask API and update endpoint information in order to trigger policy changes.

### References
- https://developer.cisco.com/meraki/api-v1/

