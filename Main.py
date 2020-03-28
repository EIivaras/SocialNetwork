import mysql.connector
import re
from datetime import date
from functions import *
from tables import *

# Intialization

dbHost = input("Please input your host address: ")
dbUser = input("Please input your db user: ")
dbPassword = input("Please input your db password: ")

successfullyConnected = False

try:
    mydb = mysql.connector.connect(
        host=dbHost,
        user=dbUser,
        passwd=dbPassword
    )
except mysql.connector.Error as er:
    print("Error while attempting to connect to server: {}".format(er))
else:
    successfullyConnected = True

if successfullyConnected:

    mycursor = mydb.cursor()
    mycursor.execute("CREATE DATABASE IF NOT EXISTS budgetBook;")
    mycursor.execute("USE budgetBook;")
    createTables(mycursor)

    # Initialize PostID if needed
    mycursor.execute("SELECT * FROM Meta;")
    result = mycursor.fetchall()
    if len(result) == 0:
        mycursor.execute("INSERT INTO Meta VALUE (0)")
        mydb.commit()

    # Main Program Loop

    loggedIn = False
    UserID = ""

    while not loggedIn:
        loginOrRegister = input("Please login (using your userID), register, or exit: l = login, r = register, e = exit: ")
        if loginOrRegister.upper() == 'L':
            userObject = login(mycursor)
            if (userObject["success"]):
                loggedIn = True
                UserID = userObject["userID"]
                break
        elif loginOrRegister.upper() == 'R':
            register(mycursor, mydb)
        elif loginOrRegister.upper() == 'E':
            print("Goodbye.")
            break
        else:
            print("Input not recognized. Closing.")
            break


    if loggedIn:
        while True:
            action = input("Please choose an menu: p = post menu, f = friend menu, g = group menu, e = exit/logout: ")

            if action.upper() == 'E':
                break

            elif action.upper() == 'P':
                while True:
                    print("Post Menu:\np = make a post\nr = reply to a post\nu = read unread posts\nb = back")
                    action = input("What would you like to do? ")
                    if action.upper() == 'P':
                        post(UserID, mycursor, mydb)
                    elif action.upper() == 'R':
                        reply()
                    elif action.upper() == 'U':
                        readUnreadPosts() # will go to the read specific post, reply, read comments, and react options from here
                    elif action.upper() == 'B':
                        break
                    else:
                        print("That is not one of the options.")

            elif action.upper() == 'F':
                while True:
                    print("Friend Menu:\nf = add a friend\nu = unfollow a friend\nr = refollow a friend\nb = back\n")
                    action = input("What would you like to do? ")
                    if action.upper() == 'F':
                        friend(UserID, mycursor, mydb)
                    elif action.upper() == 'U':
                        unfollow(UserID, mycursor, mydb)
                    elif action.upper() == 'R':
                        follow(UserID, mycursor, mydb)
                    elif action.upper() == 'B':
                        break
                    else:
                        print("That is not one of the options.")

            elif action.upper() == 'G':
                while True:
                    print("Group Menu:\nj = join group\nc = create group\nb = back\n")
                    action = input("What would you like to do?")
                    if action.upper() == 'J':
                        joinGroup()
                    elif action.upper() == 'C':
                        createGroup()
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
