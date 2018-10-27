# Forums Application

## Purpose: 
We are creating a forums application exploring how to scale an application.

### Basic Forums App 
We utilizing one database for everything. Started adding forum, thread, and post information all into one centralized database.

### Basic Forums App v2
Began to explore potential scalability issues for our application. 
We created a sharded database using multiple shards for posts.
Created a Shard key of a mod 3 on the thread id.
