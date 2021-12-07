# meraki-naclitedb
Many Enteprrise leverage a combination of off the shelf security tools and homegrown applications to create a source of truth for their endpoints. While Identity Services Engine (ISE) is an option to provide unified access policy in an enterprise another approach would be to leverage information in existing homegrown endpoint databases to trigger policy changes for wired and wireless clients in a Meraki network.

This app is intended to represent the above scenario. A Simple SQL db has been created with several endpoints. To handle CRUD operations on endpoints in the databsae, a frontend API gateway using flask was created.

When an endpoint is updated in the database dynamically via a posture scan or manually as seen in the demo below, that triggers an API call to the meraki cloud dashboard to change client firewall from Trusted to Untrusted or vice versa.

#### Demo
   Update endpoint status in database and trigger relevant Meraki client Group Policy change.
    
   <img src=gifs/naclitemeraki.gif width="100%" height="100%">
