# Broadlink RM REST Server

## Purpose
This Python based web server provides REST interactivity with any local [Broadlink RM*](http://www.ibroadlink.com/rm/) type IR/RF blasters.

NOTE: To connect your RM devices to your network without downloading the Broadlink mobile app, refer to the [python-broadlink Example Use](https://github.com/mjg59/python-broadlink#example-use) instructions.

Please read the [Notes](#notes) section before using. Refer to the [API](#api) section to learn how this server can be used.

## Setup

### Local Setup
1. Clone ```app/``` to the folder of your choice. 
2. Create ```app/data``` folder.
3. Install dependencies via pip: ```pip install falcon peewee broadlink psycopg2-binary```
4. Install the WSGI implementation of your choice (these instructions assume you are using gunicorn): ```pip install gunicorn```
5. Navigate to the app folder
6. Run ```gunicorn -b 0.0.0.0:8000 broadlink_rm_rest_app:app```

Your databases will be available in the app/data folder.

### Docker Instructions

To create and start container:
```docker run -d --name broadlink_rm_rest_app --restart unless-stopped -p 8000:8000 -v </local/path/to/data>:/app/data raman325/broadlink-rm-rest-server```

#### Optional Environment Variables
These can be added to the above command with ```-e <NAME>=<VALUE>```

Parameter Name | Description
-------------- | -----------
HOST | Specifies the HOST that will be used to access the REST server. Defaults to ```0.0.0.0``` which exposes the server to the entire network. To provide local access only, use ```127.0.0.1``` or ```localhost``` instead.
PORT | Specifies the port that the container will listen on. Note that if this is changed, the ```create``` command should be updated accordingly (e.g. ```-p <Public Port>:<PORT>```)

#### Persist DB files
In the ```docker run``` command listed above, the DB files (commands.db and blasters.db) will be persisted in /local/path/to/data on your host server.

## API
NOTE: All return values are in JSON format

Endpoint | HTTP Method | Description | Returns
-------- | ----------- | ----------- | -------
```/discoverblasters``` | ```GET``` | Discovers all new Broadlink RM blasters and adds them to the database (Note: blasters must be in the database before they can be used by the application). Blasters will be added to the database unnamed, so it's recommended to use ```PUT /blasters/<attr>/<value>?new_name=<new_name>``` to set a friendly name for each blaster.<br><br>NOTE: Discovery will also update blaster IP addresses when applicable. | ```num_devices``` - # of newly discovered devices
```/blasters``` | ```GET``` | Gets all blasters (only returns blasters that have already been discovered once). | 
```/blasters?target_name=<target_name>&command_name=<command_name>``` | ```POST``` | Sends command ```<command_name>``` for target ```<target_name>``` to all blasters. | 
```/blasters/<attr>/<value>``` | ```GET``` | Gets specified blaster. ```<attr>``` should be either ```ip```, ```mac```, or ```name```, and ```<value>``` should be the corresponding value. | 
```/blasters/<attr>/<value>``` | ```DELETE``` | Deletes specified blaster. ```<attr>``` should be either ```ip```, ```mac```, or ```name```, and ```<value>``` should be the corresponding value. | 
```/blasters/<attr>/<value>?new_name=<new_name>``` | ```PUT``` | Sets blasters name to ```<new_name>```, replacing an existing name if it already exists. ```<attr>``` should be either ```ip```, ```mac```, or ```name```, and ```<value>``` should be the corresponding value.<br><br>NOTE: If blaster lookup via IP isn't working, try to rediscover blasters using /discoverblasters which will update IP addresses to their latest. | 
```/blasters/<attr>/<value>?target_name=<target_name>&command_name=<command_name>``` | ```POST``` | Sends command ```<command_name>``` for target ```<target_name>``` via specified blaster. ```<attr>``` should be either ```ip```, ```mac```, or ```name```, and ```<value>``` should be the corresponding value.<br><br>NOTE: If blaster lookup via IP isn't working, try to rediscover blasters using /discoverblasters which will update IP addresses to their latest. | 
```/commands``` | ```GET``` | Gets all commands. | 
```/targets``` | ```GET``` | Gets all targets. | 
```/targets/<target_name>``` | ```PUT``` | Creates target ```<target_name>```. | 
```/targets/<target_name>``` | ```DELETE``` | Deletes target ```<target_name>``` and all of its associated commands. | 
```/targets/<target_name>?new_name=<new_name>``` | ```PATCH``` | Updates the name of ```<target_name>``` to ```<new_name>```. | 
```/targets/<target_name>/commands``` | ```GET``` | Gets all commands for target ```<target_name>```. | 
```/targets/<target_name>/commands/<command_name>``` | ```GET``` | Gets command ```<command_name>``` for target ```<target_name>```. | 
```/targets/<target_name>/commands/<command_name>``` | ```DELETE``` | Deletes command ```<command_name>``` for target ```<target_name>```. | 
```/targets/<target_name>/commands/<command_name>?new_name=<new_name>``` | ```PATCH``` | Updates command name of  ```<command_name>``` for target ```<target_name>``` to ```<new_name>```. | 
```/targets/<target_name>/commands/<command_name>?blaster_attr=<blaster_attr>&blaster_value=<blaster_value>``` | ```PUT``` | Learns command ```<command_name>``` for target ```<target_name>``` using specified blaster. ```<blaster_attr>``` should be either ```ip```, ```mac```, or ```name``` and ```<blaster_value>``` should be the corresponding value. If ```<command_name>``` already exists, it will be replaced with the new value. The app will wait for ~10 seconds to detect an input signal from the blaster specified before timing out.<br><br>NOTE: If blaster lookup via IP isn't working, try to rediscover blasters using /discoverblasters which will update IP addresses to their latest. | 
```/targets/<target_name>/commands/<command_name>?value=<value>``` | ```PUT``` | Sets the value command ```<command_name>``` for target ```<target_name>``` to ```<value>```. If ```<command_name>``` already exists, it will be replaced with the new value. If you plan to use this method, you should look at the code to see how values are encoded, or use existing command values in the database. | 

## Notes
1. Parameters are case sensitive so it's recommended to use lowercase for everything.
2. The blasters and target/commands databases, blasters.db and commands.db, are independent files because  they are completely unrelated. As long as you are using Broadlink RM* blasters, you can use the same commands.db for every instance of the application.
3. The database files are in SQLite3 format and can be hand edited if needed. I use [SQLiteStudio](https://sqlitestudio.pl/index.rvt).
4. To start from scratch, simply stop the container/app, delete the two .db files, and restart.
5. This was tested on an RM3 Mini but should theoretically support any RM device that [python-broadlink](https://github.com/mjg59/python-broadlink) does.

## Shout outs
1. @mjg59 for [python-broadlink](https://github.com/mjg59/python-broadlink)
2. @falconry for [falcon](https://github.com/falconry/falcon). This is my first REST app and [falcon](https://github.com/falconry/falcon) made it a breeze.
3. @coleifer for [peewee](https://github.com/coleifer/peewee) which made persisting the data simple.
4. My wife for putting up with my late night/weekend experimentation.


## TODO
1. Docker support
2. Test cases
3. Authentication
3. Case insensitivity
4. Mechanism to export/import commands
5. Mechanism to share commands
