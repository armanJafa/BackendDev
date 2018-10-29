# Forums Application

## Purpose: 
We are creating a forums application exploring how to scale an application.

### Basic Forums App 
We utilizing one database for everything. Started adding forum, thread, and post information all into one centralized database.

### Basic Forums App v2
Began to explore potential scalability issues for our application. 
We created a sharded database using multiple shards for posts.
Created a Shard key of a mod 3 on the thread id.

Web Service API
Your Flask application should expose the following RESTful URL endpoints. All data sent to and from the API should be in JSON format with the Content-Type header field set to application/json.

## API
|                          |   |
|--------------------------|---|
| Method                   |GET |
| URL                      |/forums|
| Action                   |List available discussion forums|
| Request Payload          |N/A|
| Successful Response      |HTTP 200 OK </br>[</br>{ "id": 1, name: "redis", creator: "alice" },</br> { "id": 2, name: "mongodb", creator:"bob" }</br>]|
| Error Response           |None. Returns an empty array if no forums have been created.|
| Requires Authentication? |No|
| Notes                    |N/A|


|                          |   |
|--------------------------|---|
| Method                   |POST|
| URL                      |/forums|
| Action                   |Create a new discussion forum|
| Request Payload          |{ </br>"name": "cassandra"</br>}|
| Successful Response      |HTTP 201 Created </br> Location header field set to /forums/<forum_id> for new forum|
| Error Response           |HTTP 409 Conflict if forum already exists|
| Requires Authentication? |Yes|
| Notes                    |N/A|

|                          |   |
|--------------------------|---|
| Method                   |GET|
| URL                      |/forums/<forum_id>|
| Action                   |List threads in the specified forum|
| Request Payload          |N/A|
| Successful Response      |HTTP 200 OK </br>[</br>{</br>"id": 1,</br>"title": "Does anyone know how to start Redis?",</br>"creator": "bob",</br>"timestamp": "Wed, 05 Sep 2018 16:22:29 GMT"</br>},</br>{</br>"id": 2,</br>"title": "Has anyone heard of Edis?",</br>"creator": "charlie",</br>"timestamp": "Tue, 04 Sep 2018 13:18:43 GMT"</br>}</br>]|
| Error Response           |HTTP 404 Not Found|
| Requires Authentication? |No|
| Notes                    |The timestamp for a thread is the timestamp for the most recent post to that thread.</br>The creator for a thread is the author of its first post.</br>Threads are listed in reverse chronological order.|

|                          |   |
|--------------------------|---|
| Method                   |   |
| URL                      |   |
| Action                   |   |
| Request Payload          |   |
| Successful Response      |   |
| Error Response           |   |
| Requires Authentication? |   |
| Notes                    |   |
