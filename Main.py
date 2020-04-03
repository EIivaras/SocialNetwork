import mysql.connector
from os import listdir
import functions as api
from tables import createTables

# Intialization

dbHost = input("Please input your host address: ")
dbUser = input("Please input your db user: ")
dbPassword = input("Please input your db password: ")
if dbHost == "" and dbUser == "" and dbPassword == "":
    dbHost = "Localhost"
    dbUser = "remoteuser"
    dbPassword = "password"

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

    # Initialize PostID if needed
    mycursor.execute("SELECT * FROM Meta;")
    result = mycursor.fetchall()
    if len(result) == 0:
        mycursor.execute("INSERT INTO Meta VALUE (44521)")  # this 44521 number is to get past all the inserted data to save time
        mydb.commit()

    # Main Program Loop

    loggedIn = False
    UserID = ""

    while not loggedIn:
        loginOrRegister = input("Please login (using your userID), register, or exit: l = login, r = register, e = exit: ")
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
                    print("Post Menu:\np = make a post\nr = read unread posts\nt = test read\ni = read post by ID\nb = back")
                    action = input("What would you like to do? ")
                    if action.upper() == 'P':
                        api.post(UserID, mycursor, mydb)
                    elif action.upper() == 'R':
                        numPosts = input("How many unread posts would you like to preview? ")
                        api.listUnreadPosts(UserID, numPosts, mycursor, mydb)
                        while True:
                            PostID = input("Which post do you want to read? (b = go back) PostID: ")
                            if PostID.upper() == 'B':
                                break
                            numReplies = input("How many replies do you want to see? Number: ")
                            api.read(PostID, mycursor)
                    elif action.upper() == 'T':  # this whole case should be deleted, it is just for testing
                        PostID = input("Which post do you want to read? (b = go back) PostID: ")
                        api.read(PostID, mycursor)
                    elif action.upper() == 'I':
                        continue
                    elif action.upper() == 'B':
                        break
                    else:
                        print("That is not one of the options.")

            elif action.upper() == 'F':
                while True:
                    print("Friend Menu:\nf = add a friend\nu = unfollow a friend\nr = refollow a friend\nb = back\n")
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
                    print("Group Menu:\nj = join group\nc = create group\nb = back\n")
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
