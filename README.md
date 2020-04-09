# Introduction #
This project was created as a group of two by Zachary Walford (zwalford - 20679930) and Peter Dye (pjadye - 20678160), and is our take on a social network. We used Facebook as a template as the sample data we used to populate the database was taken from a kaggle dataset [1], which pulled data from five different facebook groups. 

# Running the Code: #
To run the code, python must be installed. Assuming it is, the code be run via a simple: `python Main.py` in the terminal window. The first thing the application will do is prompt the user for a mysql server running somewhere. Simply type the host address, username and password as directed and the application will connect to the MySQL server before creating the database (which we have called `budgetBook`) and populating it with the sample data we pulled from a kaggle dataset [1], albeit converted into a friendly format for insertion into our database. 

**Note that the application will not re-create the database every time the application is run** - instead, the application will check if the database already exists, and if it doesn't, then it will create the database and populate it.

Upon successful MySQL server connection, database creation and data entry, the user will be presented with the command-line client.

# Registration/Login #
The first thing the user will always be asked to do upon consecutive executions of the application is to login or register (using the `L` or `R` keys respectively). This will create a `user` record in the budgetBook database, which will be used whenever the application user joins a group, makes a post, upvotes/downvotes a post, etc. No password is required as this project will not be used by more than the developers and the evaluators. Other than that, the only major piece of information that is required is the userID, which will be used to login on subsequent executions of the application (and is the user's `screen name`). One can specify their first name, last name and birth date but it is not necessary to create a user.

After registering, the user can login by pressing `L` and then typing in their userID.

If during the process of registration the user made a mistake in their inputted data, they are given the opportunity to restart the registration process at the end of the data entry steps.

# CLI #
Upon successful login, the user is presented with the main menu. This includes 4 commands:
* P: Post Menu - Allows the user to create a post, read unread posts or read a post by ID.
* F: Friend Menu - Allows the user to add a friend, unfollow a friend or refollow a friend.
    * When a user adds a friend, that friend is automatically a followed, meaning that user's posts will appear in the user's unread posts list.
    * Unfollowing a friend means the user will not will not see that friend's posts in their unread posts, but they will still be friends.
* G: Group Menu - Allows the user to create or join a group.
    * In facebook, which this database mocks, groups = topics. Whenever a user makes a post, they choose a group that they are in to post to.
* L: Logout
    * Allows the application user to switch budgetBook users.
* E: Exit the Application

# References #
[1] https://www.kaggle.com/mchirico/cheltenham-s-facebook-group/version/46