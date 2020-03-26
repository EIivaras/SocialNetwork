import mysql.connector
from functions import *
from tables import *

# Intialization

mydb = mysql.connector.connect(
  host="localhost",
  user="remoteuser",
  passwd="password"
)
mycursor = mydb.cursor()
mycursor.execute("CREATE DATABASE IF NOT EXISTS budgetBook;")
mycursor.execute("USE budgetBook;")
createTables(mycursor)

# Main Program Loop

loggedIn = False

def login():
    return 0

def register():
    return 0

loginOrRegister = input("Please login (using your userID and password) or register: l = login, r = register: ")
if loginOrRegister.upper() == 'L':
    login()
elif loginOrRegister.upper() == 'R':
    register()
    login()
else:
    print("Input not recognized. Closing.")


if loggedIn:
    while True:
        action = input("Please choose an action: p = post, r = react, e = exit")

        if action.upper() == 'E':
            break
        # elif action.upper() == 'P':
            # TODO
        # elif action.upper() == 'R':
            # TODO
        # TODO: Add all commands, possibly a hierarchy for some
