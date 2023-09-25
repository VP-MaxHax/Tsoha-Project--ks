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

To be done:
- Message search
- Ability to follow users
- Ability to filter only followed users messages
- Registering as a subscriber
- Limited access, subscribers only message space.
- Admin users with ability to moderate messages
- Making the frontend user-friendly
- Removing the non essential files from repository


How to test:

1. Activate virtual enviroment with command '/venv/scripts/activate'

2. Activate flask with command 'flask run'

3. Website is usable in address 'http://127.0.0.1:5000/'


psql database can be accessed trought console with following:

Give console command 'psql' to activate the database interface.

Command '\dt;' shows all the tables.

To show content of specific table use command 'SELECT * FROM table_name;'

Tables included currently:

messages (Has some test messages to demo the features)

users (Has 3 test account to try out the user features. username///pass as follows
       test///123     test2///456     test3///789)
       
comments (Has some test comments from registered and anonymous users.)
