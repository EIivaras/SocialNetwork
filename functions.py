import re
from datetime import date
import mysql.connector


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

    # create a PostID
    mycursor.execute("SELECT * FROM Meta;")
    PostID = mycursor.fetchall()[0][0]
    mycursor.execute("UPDATE Meta SET NextPostID = NextPostID + 1;")
    q = "SELECT PostID FROM Posts WHERE PostID = %s;"
    v = (PostID,)
    mycursor.execute(q, v)
    result = mycursor.fetchall()
    while len(result) != 0:
        mycursor.execute("SELECT * FROM Meta;")
        PostID = mycursor.fetchall()[0][0]
        mycursor.execute("UPDATE Meta SET NextPostID = NextPostID + 1;")
        q = "SELECT PostID FROM Posts WHERE PostID = %s;"
        v = (PostID,)
        mycursor.execute(q, v)
        result = mycursor.fetchall()
    print(PostID)  # this print just for testing

    # Post by adding all the information to the database
    q = "INSERT INTO Posts (PostID, UserID, ParentPost, TopicID, GroupID, Content) VALUES (%s, %s, %s, %s, %s, %s);"
    v = (PostID, UserID, ParentPost, TopicID, GroupID, Content)
    mycursor.execute(q, v)

    # Now we need to add to the unread table
    # TODO: First add it for everyone that follows this userID
    q = "INSERT INTO ReadStatus (UserID, PostID) SELECT UserID, %s FROM (SELECT UserID FROM FollowedUsers WHERE FollowedID = %s) AS Temp;"
    v = (PostID, UserID)
    mycursor.execute(q, v)

    # TODO: Then add for everyone in the same groups (minus people that already got it b/c they followed the person)

    mydb.commit()
    return 0


def read(PostID, mycursor):
    # q = "SELECT Content FROM Posts WHERE PostID = %s;"
    q = "SELECT PostID, firstName, lastName, PostTime, GroupName, Content FROM Posts INNER JOIN Users USING(UserID) LEFT JOIN GroupInfo USING(GroupID) WHERE PostID = %s;"
    v = (PostID,)
    mycursor.execute(q, v)
    result = mycursor.fetchall()[0]

    if result[4] is None:
        print("PostID: "+result[0]+"| Posted by: "+result[1]+" "+result[2]+"| On: "+str(result[3])+"\n"+result[5]+"\n")
    else:
        print("PostID: "+result[0]+"| Posted by: "+result[1]+" "+result[2]+"| On: "+str(result[3])+"| In Group: "+result[4]+"\n"+result[5]+"\n")

    q = "SELECT COUNT(*) FROM Posts WHERE ParentPost = %s"
    mycursor.execute(q, v)
    result = mycursor.fetchall()[0]

    print(result[0]+" people replied\n")

    return 0


def listUnreadPosts(UserID, numPosts, mycursor, mydb):
    # still have to sort by most popular in terms of upvotes / downvotes
    q = "SELECT PostID, firstName, lastName, GroupName, SUBSTRING_INDEX(Content, " ", 10) FROM Posts INNER JOIN Users USING(UserID) LEFT JOIN GroupInfo USING(GroupID) WHERE PostID IN (SELECT PostID FROM ReadStatus WHERE UserID = %s AND HasRead = FALSE) LIMIT %s;"
    v = (UserID, numPosts)
    mycursor.execute(q, v)
    result = mycursor.fetchall()
    print(result)
    return 0


def readReplies(ParentPost, numReplies, UserID, mycursor, mydb):

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
            # print(dateJoined)
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


def friend(UserID, mycursor, mydb):
    FriendID = input("Who do you want to become friends with? Their UserID: ")
    if not checkID(FriendID, mycursor):
        print("There is no user with that UserID\n")
        return -1

    if not friendCheck(UserID, FriendID, mycursor):
        q = "INSERT INTO Friends VALUES (%s, %s);"
        v = (UserID, FriendID)
        mycursor.execute(q, v)
        q = "INSERT INTO FollowedUsers VALUES (%s, %s);"
        mycursor.execute(q, v)
        v = (FriendID, UserID)
        q = "INSERT INTO FollowedUsers VALUES (%s, %s);"
        mycursor.execute(q, v)
        mydb.commit()
        print("You and "+FriendID+" are friends now!\n")
        return 0
    else:
        print("You are already friends with this person.\n")
        return -2


def unfollow(UserID, mycursor, mydb):
    FriendID = input("Which friend do you want to unfollow? Their UserID: ")
    if not checkID(FriendID, mycursor):
        print("There is no user with that UserID\n")
        return -1

    if not friendCheck(UserID, FriendID, mycursor):
        print("You must be friends with someone to follow/unfollow them.\n")
        return -2
    else:
        if followCheck(UserID, FriendID, mycursor) == 0:
            print("You have already unfollowed this person.\n")
        else:
            q = "DELETE FROM FollowedUsers WHERE UserID = %s AND FollowedID = %s;"
            v = (UserID, FriendID)
            mycursor.execute(q, v)
            mydb.commit()
            print("You will no longer see content from "+FriendID+"\n")
        return 0


def follow(UserID, mycursor, mydb):
    FriendID = input("Which friend do you want to follow? Their UserID: ")
    if not checkID(FriendID, mycursor):
        print("There is no user with that UserID\n")
        return -1

    if not friendCheck(UserID, FriendID, mycursor):
        print("You must be friends with someone to follow/unfollow them.\n")
        return -2
    else:
        if followCheck(UserID, FriendID, mycursor) == 1:
            print("You have already followed this person.\n")
        else:
            q = "INSERT INTO FollowedUsers VALUES (%s, %s);"
            v = (UserID, FriendID)
            mycursor.execute(q, v)
            mydb.commit()
            print("You will now see content from "+FriendID+"\n")
        return 0


def reply():
    return 0


def react():
    return 0


# Internal Helper Functions Below Here:

# Check if a user ID is valid
def checkID(UserID, mycursor):
    q = "SELECT UserID FROM Users WHERE UserID = %s;"
    v = (UserID,)
    mycursor.execute(q, v)
    result = mycursor.fetchall()
    return len(result)


# Checks if two IDs are friends
def friendCheck(UserID, FriendID, mycursor):
    q = "SELECT UserID FROM Friends WHERE (UserID = %s AND FriendID = %s) OR (UserID = %s AND FriendID = %s);"
    v = (UserID, FriendID, FriendID, UserID)
    mycursor.execute(q, v)
    result = mycursor.fetchall()
    return len(result)


# 0 if not following, 1 if following
def followCheck(UserID, FriendID, mycursor):
    q = "SELECT UserID FROM FollowedUsers WHERE UserID = %s AND FollowedID = %s;"
    v = (UserID, FriendID)
    mycursor.execute(q, v)
    result = mycursor.fetchall()
    return len(result)
