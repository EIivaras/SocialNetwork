import mysql.connector
import re
from os import listdir
# from datetime import date
import functions as api
from tables import createTables

# Intialization

dataOkay = False

while not dataOkay:
    dbHost = input("Please input your host address: ")
    dbUser = input("Please input your db user: ")
    dbPassword = input("Please input your db password: ")

    print('\nIs all of the following data that you entered okay?')
    print(f'dbHost: {dbHost}; dbUser: {dbUser}; dbPassword: {dbPassword};')
    dataOkay = input("\nIf the above is what you wanted, type 'Y'. Otherwise, hit any other key and the process will be restarted: ")

    if dataOkay.upper() == 'Y':
        dataOkay = True

if dbHost == "" and dbUser == "" and dbPassword == "":  # This if case was for ease of testing can be deleted after
    dbHost = "Localhost"
    dbUser = "remoteuser"
    dbPassword = "password"

successfullyConnected = False

try:
    mydb = mysql.connector.connect(
        host=dbHost,
        user=dbUser,
        passwd=dbPassword,
        autocommit=True
    )
except mysql.connector.Error as er:
    print("Error while attempting to connect to server: {}".format(er))
else:
    successfullyConnected = True

if successfullyConnected:

    mycursor = mydb.cursor()
    mycursor.execute("SHOW DATABASES LIKE 'budgetBook';")
    dbExists = mycursor.fetchall()

    if not dbExists:
        print("Creating database...")
        mycursor.execute("CREATE DATABASE budgetBook;")
        mycursor.execute("USE budgetBook;")
        createTables(mycursor)
        mycursor.execute('SET FOREIGN_KEY_CHECKS=0')
        SQLInsertFilePaths = listdir('./SQLInserts')
        for filePath in SQLInsertFilePaths:
            print(f"Inserting data for {filePath}...")
            file = open(f'./SQLInserts/{filePath}', 'r')
            statements = file.readlines()
            try:
                for statement in statements:
                    mycursor.execute(statement)
            except mysql.connector.Error as er:
                pass
            mydb.commit()
            file.close()
        mycursor.execute('SET FOREIGN_KEY_CHECKS=1')
        print("Finished.")

    else:
        mycursor.execute("USE budgetBook")

    # Initialize PostID if needed
    mycursor.execute("SELECT * FROM Meta;")
    result = mycursor.fetchall()
    if len(result) == 0:
        mycursor.execute("INSERT INTO Meta VALUE (44521)")  # this 44521 number is to get past all the inserted data to save time
        mydb.commit()

    # Main Program Loop

    executing = True

    while executing:

        loggedIn = False
        UserID = ""

        while not loggedIn:
            loginOrRegister = input("Please login (using your userID), register, or exit: L = Login, R = Register, E = Exit: ")
            if loginOrRegister.upper() == 'L':
                userObject = api.login(mycursor)
                if (userObject["success"]):
                    loggedIn = True
                    UserID = userObject["userID"]
                    break
            elif loginOrRegister.upper() == 'R':
                api.register(mycursor, mydb)
            elif loginOrRegister.upper() == 'E':
                print("Goodbye.")
                executing = False
                break
            else:
                print("That was not one of the options.")

        if loggedIn:
            while True:
                action = input("Main Menu:\nP = Post Menu\nF = Friend Menu\nG = Group Menu\nL = Logout\nE = Exit the Application\nWhich menu do you want? ")

                if action.upper() == 'E':
                    executing = False
                    break

                elif action.upper() == 'L':
                    break

                elif action.upper() == 'P':
                    while True:
                        action = input("Post Menu:\nP = Create a Post\nR = Read Unread Posts\nI = Read Post by ID\nG = Browse Posts by Group\nB = Back\nWhat would you like to do? ")
                        if action.upper() == 'P':
                            api.post(UserID, None, mycursor, mydb)
                        elif action.upper() == 'R' or action.upper() == 'I':
                            if action.upper() == 'R':
                                numPosts = input("How many unread posts would you like to preview? Number: ")
                                if not re.match("[0-9]+", numPosts):
                                    print("You must specify a number.")
                                    continue
                                print("")
                                listReturn = api.listUnreadPosts(UserID, numPosts, None, mycursor, mydb)
                                if listReturn < 0:
                                    continue
                            while True:
                                PostID = input("Which post do you want to read? (B = Go Back) PostID: ")
                                print("")
                                if PostID.upper() == 'B':
                                    break
                                readResult = api.read(PostID, UserID, mycursor, mydb, 0)
                                if readResult < 0:
                                    continue
                                PostIDStack = []
                                while True:
                                    if len(PostIDStack) == 0:
                                        print("Menu for PostID "+PostID+": V = Upvote/Downvote, C = Comment, P = Preview comments, B = Go Back")
                                    else:
                                        print("Menu for CommentID "+PostID+": V = Upvote/Downvote, C = Comment, P = Preview Comments, B = Go Back")
                                    postaction = input("What do you want to do? ")

                                    if postaction.upper() == 'V':
                                        Reaction = input("U = Upvote, D = Downvote: ")
                                        api.react(UserID, PostID, Reaction, len(PostIDStack), mycursor, mydb)
                                    elif postaction.upper() == 'C':
                                        api.post(UserID, PostID, mycursor, mydb)
                                    elif postaction.upper() == 'P':
                                        numReplies = input("How many comments do you want to preview? Number: ")
                                        if not re.match("[0-9]+", numReplies):
                                            print("You must specify a number.")
                                            continue
                                        print("")
                                        if action.upper() == 'I':
                                            listReturn = api.listComments(UserID, numReplies, PostID, mycursor, mydb)
                                        else:
                                            listReturn = api.listUnreadPosts(UserID, numReplies, PostID, mycursor, mydb)
                                        if listReturn < 0:
                                            continue

                                        PostIDStack.append(PostID)
                                        PostID = input("Which comment do you want to read? (B = Go Back) CommentID: ")
                                        if PostID.upper() == 'B':
                                            PostID = PostIDStack.pop()
                                        else:
                                            api.read(PostID, UserID, mycursor, mydb, 1)

                                    elif postaction.upper() == 'B':
                                        if len(PostIDStack) == 0:
                                            break
                                        else:
                                            PostID = PostIDStack.pop()

                        elif action.upper() == 'G':
                            api.browsePostsInGroup(UserID, mycursor, mydb)
                        elif action.upper() == 'B':
                            break
                        else:
                            print("That is not one of the options.")

                elif action.upper() == 'F':
                    while True:
                        print("Friend Menu:\nF = Add a Friend\nU = Unfollow a Friend\nR = Refollow a Friend\nB = Back\n")
                        action = input("What would you like to do? ")
                        if action.upper() == 'F':
                            api.friend(UserID, mycursor, mydb)
                        elif action.upper() == 'U':
                            api.unfollow(UserID, mycursor, mydb)
                        elif action.upper() == 'R':
                            api.follow(UserID, mycursor, mydb)
                        elif action.upper() == 'B':
                            break
                        else:
                            print("That is not one of the options.")

                elif action.upper() == 'G':
                    while True:
                        print("Group Menu:\nJ = Join Group\nC = Create Group\nB = Back\n")
                        action = input("What would you like to do? ")
                        if action.upper() == 'J':
                            api.joinGroup(UserID, mycursor, mydb)
                        elif action.upper() == 'C':
                            api.createGroup(UserID, mycursor, mydb)
                        elif action.upper() == 'B':
                            break
                        else:
                            print("That is not one of the options.")

                # TODO: Add all commands, possibly a hierarchy for some
                else:
                    print("That is not one of the options.")

            print("Goodbye!")

    mycursor.close()
    mydb.close()
