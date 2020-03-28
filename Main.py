import mysql.connector
import re
from os import listdir
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

    # Main Program Loop

    loggedIn = False
    userID = ""

    while not loggedIn:
        loginOrRegister = input("Please login (using your userID), register, or exit: l = login, r = register, e = exit: ")
        if loginOrRegister.upper() == 'L':
            userObject = login(mycursor)
            if (userObject["success"]):
                loggedIn = True
                userID = userObject["userID"]
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
            action = input("Please choose an menu: p = post menu, f = friend menu, g = group menu, e = exit: ")

            if action.upper() == 'E':
                break

            elif action.upper() == 'P':
                while True:
                    print("Post Menu:\np = make a post\nr = reply to a post\nu = read unread posts\nb = back")
                    action = input("What would you like to do? ")
                    if action.upper() == 'P':
                        post(userID, mycursor, mydb)
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
                    print("Friend Menu:\nf = add a friend\nu = unfollow a friend\nb = back\n")
                    action = input("What would you like to do?")
                    if action.upper() == 'F':
                        friend()
                    elif action.upper() == 'U':
                        unfollow()
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
