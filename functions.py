import mysql.connector
import re
import random
from datetime import date


def post(UserID, mycursor, mydb):
    # Get and check the content for the post
    Content = input("What do you want to post?\n")
    if len(Content) > 1000:
        print("That post was too long! Maximum length is 1000 characters.")

    # ParentPost is null because this function is only used to initiate posts
    ParentPost = None

    # Get TopicID if there is one
    # TopicID = input("What is the topic of your post? (Hit enter for none) TopicID: ")
    # if len(TopicID) == 0:
    #     TopicID = None

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
    q = "INSERT INTO Posts (PostID, UserID, ParentPost, GroupID, Content) VALUES (%s, %s, %s, %s, %s);"
    v = (PostID, UserID, ParentPost, GroupID, Content)
    mycursor.execute(q, v)

    # Now we need to add to the unread table
    # First add it for everyone that follows this userID
    q = "INSERT INTO ReadStatus (UserID, PostID) SELECT UserID, %s FROM (SELECT UserID FROM FollowedUsers WHERE FollowedID = %s) AS Temp;"
    v = (PostID, UserID)
    mycursor.execute(q, v)

    # Then add for everyone in the same groups (minus people that already got it b/c they followed the person)
    q = "INSERT INTO ReadStatus (UserID, PostID) SELECT UserID, %s FROM (SELECT UserID FROM GroupMembers WHERE GroupID = %s AND UserID != %s) AS Temp1 LEFT JOIN (SELECT UserID FROM FollowedUsers WHERE FollowedID = %s) AS Temp2 USING (UserID) WHERE Temp2.UserID IS NULL;"
    v = (PostID, GroupID, UserID, UserID)
    mycursor.execute(q, v)

    mydb.commit()
    return 0


def read(PostID, UserID, mycursor, mydb, commentFlag):  # for reading posts and comments
    q = "SELECT PostID, firstName, lastName, PostTime, GroupName, Content FROM Posts INNER JOIN Users USING(UserID) LEFT JOIN GroupInfo USING(GroupID) WHERE PostID = %s;"
    v = (PostID,)
    mycursor.execute(q, v)
    result = mycursor.fetchall()[0]

    # TODO: add the number of upvotes and downvotes to the information displayed for each post

    if commentFlag == 1:
        print("CommentID: "+result[0]+"| Made by: "+result[1]+" "+result[2]+"| On: "+str(result[3])+"\n"+result[5]+"\n")
    else:
        if result[4] is None:
            print("PostID: "+result[0]+"| Posted by: "+result[1]+" "+result[2]+"| On: "+str(result[3])+"\n"+result[5]+"\n")
        else:
            print("PostID: "+result[0]+"| Posted by: "+result[1]+" "+result[2]+"| On: "+str(result[3])+"| In Group: "+result[4]+"\n"+result[5]+"\n")

    q = "SELECT COUNT(*) FROM Posts WHERE ParentPost = %s"
    mycursor.execute(q, v)
    result = mycursor.fetchall()[0]

    print(result[0]+" people commented on this\n")

    # modify the read status table when the post is displayed to the user
    q = "UPDATE ReadStatus SET HasRead = TRUE WHERE PostID = %s AND UserID = %s;"
    v = (PostID, UserID)
    mycursor.execute(q, v)

    return 0


def listUnreadPosts(UserID, numPosts, mycursor, mydb):
    # select the top numPosts number of posts based on total number of reactions
    q = "SELECT PostID, firstName, lastName, PostTime, GroupName, SUBSTRING_INDEX(Content, " ", 10) FROM Posts INNER JOIN Users USING(UserID) LEFT JOIN GroupInfo USING(GroupID) WHERE PostID IN (SELECT PostID FROM ReadStatus WHERE UserID = %s AND HasRead = FALSE) LIMIT %s;"
    v = (UserID, int(numPosts))
    mycursor.execute(q, v)
    result = mycursor.fetchall()

    # add the number of upvotes and downvotes in the information displayed for each post

    for row in result:
        if result[4] is None:
            print("PostID: "+row[0]+"| Posted by: "+row[1]+" "+row[2]+"| On: "+str(row[3])+"\n"+row[5]+"\n")
        else:
            print("PostID: "+row[0]+"| Posted by: "+row[1]+" "+row[2]+"| On: "+str(row[3])+"| In Group: "+row[4]+"\n"+row[5]+"\n")

    return 0


def listUnreadReplies(ParentPost, numReplies, UserID, mycursor, mydb):

    # Very similar to listUnreadPosts() except with replies, same info should be displayed for each post

    return 0


def reply():

    # similar to post, might be able to incorporate this into post with a couple if statements

    return 0


def react(UserID, PostID, Reaction, commentFlag, mycursor, mydb):
    if Reaction.upper() == 'U':
        ReactValue = True
    elif Reaction.upper() == 'D':
        ReactValue = False
    else:
        print("That is not a reaction option.\n")
        return -1

    q = "INSERT INTO Reactions (UserID, PostID, Reaction) VALUSE (%s, %s, %s);"  # this statement still untested and I am not sure about inputting the true and false values
    v = (UserID, PostID, ReactValue)
    mycursor.execute(q, v)

    if commentFlag > 0:
        if ReactValue:
            print("You have upvoted this comment")
        else:
            print("You have downvoted this comment")
    else:
        if ReactValue:
            print("You have upvoted this post")
        else:
            print("You have downvoted this post")

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


def createGroup(userID, mycursor, mydb):
    groupID = ''
    goodGroupName = False
    while not goodGroupName:
        groupName = input("Please specify a valid group name (3 chars min, 250 chars max) or press 'b' to go back: ")
        if groupName.upper() == 'B':
            return
        elif len(groupName) > 250:
            print('Group name too long.')
        elif len(groupName) < 3:
            print('Group name too short.')
        else:
            q = "SELECT GroupName FROM GroupInfo WHERE GroupName = %s"
            v = (groupName,)
            mycursor.execute(q, v)
            result = mycursor.fetchall()
            if result:
                print('Specified group name is already in use. Please choose another.')
            else:
                print('Specifed group name is free to use. Generating groupID...')
                goodGroupName = True
    freeID = False
    while not freeID:
        groupID = str(random.randint(0, 100000000))
        q = "SELECT GroupID FROM GroupInfo WHERE groupID = %s"
        v = (groupID,)
        mycursor.execute(q, v)
        result = mycursor.fetchall()
        if not result:
            freeID = True

    q = "INSERT INTO GroupInfo (GroupID, GroupName) VALUES (%s, %s);"
    v = (groupID, groupName)
    try:
        mycursor.execute(q, v)
        mydb.commit()
    except mysql.connector.Error as er:
        print("Error while attempting to create group: {}".format(er))
    else:
        print("Group successfully created. Automatically adding you to the group...")
        q = "INSERT INTO GroupMembers (UserID, GroupID) VALUES (%s, %s);"
        v = (userID, groupID)
        try:
            mycursor.execute(q, v)
            mydb.commit()
        except mysql.connector.Error as er:
            print("Error while attempting to add you to the group: {}".format(er))
        else:
            print("Successfully added to group.")


def joinGroup(userID, mycursor, mydb):
    q = "SELECT GroupID, GroupName FROM GroupInfo"
    mycursor.execute(q)
    result = mycursor.fetchall()
    groupIDs = []
    groupNames = []
    for item in result:
        groupIDs.append(item[0])
        groupNames.append(item[1])

    print('Here is a list of available groups, by name: \n')
    for groupName in groupNames:
        print(groupName)

    joinedGroup = False
    while joinedGroup is False:
        groupToJoin = input("Please input the name of the group you would like to join (case-insensitive), or 'b' to go back: ")
        if groupToJoin == 'b':
            return
        elif groupToJoin in groupNames:
            groupIndex = 0
            for group in groupNames:
                if group == groupToJoin:
                    groupID = groupIDs[groupIndex]
                    q = "SELECT * FROM GroupMembers WHERE UserID = %s AND GroupID = %s"
                    v = (userID, groupID,)
                    mycursor.execute(q, v)
                    result = mycursor.fetchall()

                    if result:
                        print('You are already a member of that group.')
                    else:
                        print('Joining group...')
                        q = "INSERT INTO GroupMembers (UserID, GroupID) VALUES (%s, %s);"
                        v = (userID, groupID)
                        try:
                            mycursor.execute(q, v)
                            mydb.commit()
                        except mysql.connector.Error as er:
                            print("Error while attempting to add you to the group: {}".format(er))
                        else:
                            print("Successfully added to group.")
                            joinedGroup = True
                groupIndex += 1
        else:
            print('Speicified name not recognized.')


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
