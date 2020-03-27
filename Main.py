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

    # Main Program Loop

    loggedIn = False
    userID = ""

    def login(mycursor): # Can we make this return the userID? We will need it as a variable in other areas
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
                q = "INSERT INTO Users (userID, firstName, lastName, dateJoined, birthDate) VALUES (%s, %s, %s, %s, %s);"
                v = (userID, firstName, lastName, dateJoined, birthDate)
                
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
            action = input("Please choose an action: p = post, r = react, e = exit: ")

            if action.upper() == 'E':
                break
            elif action.upper() == 'P':
                UserID = "pd1" #I made a user in my local DB with this id for testing
                post(UserID, mycursor, mydb) #Can use this to test/experiment with posting
            #elif action.upper() == 'R':

            # TODO: Add all commands, possibly a hierarchy for some
            else:
                break

    mycursor.close()
    mydb.close()
