def post(UserID, mycursor, mydb):
    # Get and check the content for the post
    Content = input("What do you want to post?\n")
    if len(Content) > 1000:
        print("That post was too long! Maximum length is 1000 characters.")

    # ParentPost is null because this function is only used to initiate posts
    ParentPost = None

    # Get TopicID if there is one
    TopicID = input("What is the topic of your post? (Hit enter for none) TopicID: ")
    if len(TopicID) == 0:
        TopicID = None

    # Get the GroupID if there is one
    GroupID = input("What group do you want to post in? (Hit enter for none) GroupID: ")
    if len(GroupID) == 0:
        GroupID = None

    # Post by adding all the information to the database
    q = "INSERT INTO Posts (UserID, ParentPost, TopicID, GroupID, Content) VALUES (%s, %s, %s, %s, %s);"
    v = (UserID, ParentPost, TopicID, GroupID, Content)
    mycursor.execute(q, v)
    mydb.commit()

    # Now we need to add to the unread table
    PostID = mycursor.lastrowid
    # TODO: First add it for everyone that follows this userID

    # TODO: Then add for everyone in the same groups

    return 0


def read(PostID, mycursor): #Working!
    q = "SELECT Content FROM Posts WHERE PostID = %s;"
    v = (str(PostID),)
    mycursor.execute(q, v)
    Content = mycursor.fetchall()
    print(Content[0][0])

    return 0


def readUnreadPosts(): # this is unRED not
    return 0


def readComments():
    return 0

def login(mycursor):
    userID = input("Please input your userID: ")
    q = "SELECT UserID FROM Users WHERE userID = %s"
    v = (str(userID),)
    mycursor.execute(q, v)
    result = mycursor.fetchall()
    if result:
        print(f"Welcome back, {userID}.\n")
        return {"userID": userID, "success": True}
    else:
        print("UserID does not exist. Please register at the prompt.")
        return {"userID": userID, "success": False}


def register(mycursor, mydb):
    registered = False
    while not registered:
        userID = input("Please input your wanted userID or type 'e' to exit: ")

        if userID.upper() == 'E':
            break

        q = "SELECT UserID FROM Users WHERE userID = %s"
        v = (str(userID),)
        mycursor.execute(q, v)
        result = mycursor.fetchall()
        if not result:
            print("Requested UserID is free to use.")
            firstName = input("Please input your first name (leave blank if you prefer not to): ")
            lastName = input("Please input your last name (leave blank if you prefer not to): ")
            dateOkay = False
            birthDate = ""
            while not dateOkay:
                birthDate = input("Please input your date of birth in the format YYYY-MM-DD (leave blank if you prefer not to): ")
                if birthDate == "":
                    break
                if re.match("(19[0-9][0-9]|20[01][0-9]|2020)-(0[1-9]|1[12])-([0-2][0-9]|3[01])", birthDate):
                    dateOkay = True
                else:
                    print("Not a valid date.")
            dateJoined = str(date.today())
            print(dateJoined)
            q = "INSERT INTO Users (userID, firstName, lastName, birthDate, dateJoined) VALUES (%s, %s, %s, %s, %s);"
            v = (userID, firstName, lastName, birthDate, dateJoined)

            try:
                mycursor.execute(q, v)
                mydb.commit()
            except mysql.connector.Error as er:
                print("Error while attempting to register: {}".format(er))
            else:
                print("Successfully registered. Please login at the prompt.")
                registered = True
        else:
            print("UserID already in use.")
    return 0


def friend(UserID, FriendID, mycursor, mydb):
    q = "INSERT INTO Friends (UserID, FriendID) VALUES (%s, %s);"
    v = (UserID, FriendID)
    mycursor.execute(q, v)
    q = "INSERT INTO FollowedUsers (UserID, FollowedID) VALUES (%s, %s);"
    mycursor.execute(q, v)
    q = "INSERT INTO FollowedUsers (FriendID, UserID) VALUES (%s, %s);"
    mycursor.execute(q, v)
    mydb.commit()

    print("You and "+FriendID+" are friends now!")

    return 0


def unfollow():
    return 0


def reply():
    return 0

def react():
    return 0
