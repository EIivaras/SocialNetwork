# https://www.kaggle.com/mchirico/cheltenham-s-facebook-group/version/46

# GROUP INFO:
# Unofficial Cheltenham Township = 25160801076
# Elkins Park Happenings! = 117291968282998
# Free Speech Zone = 1443890352589739
# Cheltenham Lateral Solutions = 1239798932720607
# Cheltenham Township Residents = 335787510131917

membersCSV = open("member.csv", 'r')
postsCSV = open("post.csv", 'r')
commentsCSV = open("comment.csv", 'r')
likesCSV = open("like.csv", 'r')

usersSQL = open("usersSQLInserts.sql", "a+")
groupsSQL = open("groupsSQLInserts.sql", "a+")
groupMembersSQL = open("groupMembersSQLInserts.sql", "a+")
postsSQL = open("postsSQLInserts.sql", "a+") # Includes posts and comments
reactionsSQL = open("reactionsSQLInserts.sql", "a+")

def SQLCreation(table, CSVFile, SQLFile):
    SQLFile.truncate()
    records = CSVFile.readlines()[1:]
    IDList = []
    index = 1

    insertPreamble = f"INSERT INTO {table} VALUES "
    insertStatement = insertPreamble
    for record in records:
        attributes = record.split(',')

        if table == 'Users':
            memberID = attributes[1]
            if (memberID not in IDList):
                IDList.append(memberID)
                memberFullName = attributes[2]
                memberNameParts = memberFullName.split(' ')
                memberFirstName = memberNameParts[0]
                memberLastName = memberNameParts[len(memberNameParts) - 1]

                insertStatement += f'("{memberID}","{memberFirstName}","{memberLastName}","","")'

                if index % 20 == 0:
                    insertStatement += ";\n\n"
                    SQLFile.write(insertStatement)
                    insertStatement = insertPreamble
                else:
                    insertStatement += ", "

        # elif table == 'Posts':

        # elif table == "Reactions":
            
        index += 1
    
    if ('\n' not in insertStatement):
        insertStatement = insertStatement[:-2] # remove last appended comma and space if we did not end on a multiple of 20
        insertStatement += ";\n\n"
    if (insertStatement != insertPreamble):
        SQLFile.write(insertStatement)

    SQLFile.close()

while True:
    conversion = input("A = all, U = users, P = posts, R = reactions, E = exit: ")

    if conversion.upper() == 'E':
        break
    elif conversion.upper() == 'A':
        SQLCreation('Users', membersCSV, usersSQL)
        SQLCreation('Posts', postsCSV, postsSQL)
        SQLCreation('Reactions', likesCSV, reactionsSQL)
    elif conversion.upper() == 'U':
        SQLCreation('Users', membersCSV, usersSQL)
    elif conversion.upper() == 'P':
        SQLCreation('Posts', postsCSV, postsSQL)
    elif conversion.upper() == 'R':
        SQLCreation('Reactions', likesCSV, reactionsSQL)
    else:
        print('Unrecognized input.')

