# Tsoha-Project--ks
"# Tsoha-Project-Äks"

Äks™ is a state of the art, social media platform to make a fool of yourself for anyone to see.

Main feature is to be able to publish short messages (100 word) for anyone to see and comment on messages sent by other people.

Comments on existing posts can be done as anonymous to keep thing spicy.

Other features include:

User control: Register, login and post as a user under your own Äks™ alias.

Following other users: Follow other users to get quick access to their posts.

Äks-club™: Tired of the rubble rousers giving you hard time? Then you shoud subscribe to Äks-club™! Äks-club™ gives you access to private lounge where only other Äks-club™ members can see your messages! This only for cheap 30€/month subscribtion. Want to try out Äks-club™? Use our 1hour trial access code: Äks4Life


Done:
- User registering and login functions
- Showing of posted messages
- Ability to post a new message
- Ability to comment a message
- Message search
- Ability to follow users (Works only trough user page)
- Ability to filter only followed users messages
- Removing the non essential files from repository
- Registering as a subscriber
- Limited access, subscribers only message space. (Members messages also shown in other areas if member)
- Admin users with ability to moderate messages (Can be accessed only by going to address 'http://127.0.0.1:5000/admin'. Admin account must be enabled manually trough psql console by changing users 'is_staff' row to 'True'.)
- Making the frontend more user-friendly

To be done:
Done everything i planned from the start. :)


How to test:

1. Create a new virtual enviroment with command 'python3 -m venv venv'

2. Activate the virtual inviroment with command 'source venv/bin/activate' (Path may change depending on python version and operating system)

3. Install dependicies from requirements.txt with command 'pip install -r requirements.txt'

4. Create file named '.env' to main folder of the app.

5. Enter your preferred database to '.env' file as follows 'DATABASE_URL = postgresql:///*database_name*'. Replace '*database_name*' with your preferred database.

6. Enter secret key to '.env' file as follows 'SECRET_KEY = *secretkey*'. Replace *secretkey* with you own secret key. You can create one with following chain of command: python3-->import secrets-->secrets.token_hex(16)

7. Check that you chosen database don't have any tables on it to begin with.

8. Import tables from schema.sql to current database with command 'psql < schqma.sql'. Tables can also be added manually by copying the create table commands from schqma.sql to you preferred psql interface.

9. Now you should be able to start up the flask app with command 'flask run'.

10. The website is accessible in address 'http://127.0.0.1:5000'


psql database can be accessed trough console with following:

Give console command 'psql' to activate the database interface.

Command '\dt;' shows all the tables.

To show content of specific table use command 'SELECT * FROM table_name;'

Tables included currently: messages, users, comments, following