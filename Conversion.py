# https://www.kaggle.com/mchirico/cheltenham-s-facebook-group/version/46

# GROUP INFO:
# Unofficial Cheltenham Township = 25160801076
# Elkins Park Happenings! = 117291968282998
# Free Speech Zone = 1443890352589739
# Cheltenham Lateral Solutions = 1239798932720607
# Cheltenham Township Residents = 335787510131917

import re

memberGroupObjects = []
groups = [
    {'groupName': 'Unofficial Cheltenham Township', 'groupID': '25160801076'},
    {'groupName': 'Elkins Park Happenings!', 'groupID': '117291968282998'},
    {'groupName': 'Free Speech Zone', 'groupID': '1443890352589739'},
    {'groupName': 'Cheltenham Lateral Solutions', 'groupID': '1239798932720607'},
    {'groupName': 'Cheltenham Township Residents', 'groupID': '335787510131917'}
]

linkObjects = []

def SQLCreation(table, CSVFilePath, SQLFilePath, truncate):
    global memberGroupObjects, linkObjects

    CSVFile = open(CSVFilePath, "r")
    records = CSVFile.readlines()[1:]
    CSVFile.close()
    SQLFile = open(SQLFilePath, "a")

    if truncate:
        SQLFile.seek(0, 0)
        SQLFile.truncate()

    IDList = []
    index = 1

    insertPreamble = f"INSERT INTO {table} VALUES "
    insertStatement = insertPreamble

    reactionID = 1
    commentUniqueID = 1
    for record in records:
        attributes = record.split(',')

        if CSVFilePath == 'CSVs/member.csv':
            groupID = attributes[0]
            memberID = attributes[1]
            
            if memberID not in IDList:
                IDList.append(memberID)

                memberFullName = attributes[2]
                memberNameParts = memberFullName.split(' ')
                memberFirstName = memberNameParts[0]
                memberLastName = memberNameParts[len(memberNameParts) - 1]

                insertStatement += f'("{memberID}","{memberFirstName}","{memberLastName}","","")'

                if index % 50 == 0:
                    insertStatement += ";\n\n"
                    SQLFile.write(insertStatement)
                    insertStatement = insertPreamble
                else:
                    insertStatement += ", "

            # For populating the GroupMembers table 
            memberGroupObject = {'groupID': groupID, 'memberID': memberID}
            if memberGroupObject not in memberGroupObjects:
                memberGroupObjects.append(memberGroupObject)

        elif CSVFilePath == 'CSVs/post.csv':
            # Note: Post text has apostrophes replaced with '{APOST}' and commas replaced with '{COMMA}'

            postID = attributes[1]
            if postID not in IDList:
                IDList.append(postID)
                groupID = attributes[0]
                userID = attributes[2]
                timeStamp = attributes[4]
                postText = attributes[7]
                postText = postText.replace('\n', '')

                # Extract Links and create inserts
                links = re.findall('http[s]?://(?:[a-zA-Z]|[0-9]|[$-_@.&+]|[!*\(\),]|(?:%[0-9a-fA-F][0-9a-fA-F]))+', postText)
                for link in links:
                    linkObjects.append({'postID':postID, 'link':link})

                insertStatement += f'("{postID}","{timeStamp}","{userID}","{postID}","","{groupID}","{postText}")'

                if index % 50 == 0:
                    insertStatement += ";\n\n"
                    SQLFile.write(insertStatement)
                    insertStatement = insertPreamble
                else:
                    insertStatement += ", "

        # Any comment without an 'rid' (i.e. it is blank) is a top level comment
        # Any comment with an 'rid' is a comment on a comment, and the rid is the id of the user who is commenting on the comment
        # For all comments on comments, the commentID is the same
        elif CSVFilePath == 'CSVs/comment.csv':
            # Note: Post text has apostrophes replaced with '{APOST}' and commas replaced with '{COMMA}'

            groupID = attributes[0]
            responderID = attributes[6]
            timeStamp = attributes[3]
            commentText = attributes[7]
            commentText = commentText.replace('\n', '')

            commentID=""
            parentPostID=""
            userID=""
            if responderID:
                # This is a comment on a comment
                commentID = commentUniqueID # Since the comment ID is the same for all sub-comments, use a unique one
                commentUniqueID += 1
                parentPostID = attributes[2] # Parent post ID is the top-level comment ID
                userID = responderID # The user ID is the ID of the responder to the top-level comment
            else:
                # This is not a comment on a comment
                commentID = attributes[2] # The comment ID is just the comment ID
                parentPostID = attributes[1] # Parent post ID is the post itself
                userID = attributes[4] # User ID is the original commenter ID

            # Extract Links and create inserts
            links = re.findall('http[s]?://(?:[a-zA-Z]|[0-9]|[$-_@.&+]|[!*\(\),]|(?:%[0-9a-fA-F][0-9a-fA-F]))+', commentText)
            for link in links:
                linkObjects.append({'postID':commentID, 'link':link})

            insertStatement += f'("{commentID}","{timeStamp}","{userID}","{parentPostID}","","{groupID}","{commentText}")'

            if index % 50 == 0:
                insertStatement += ";\n\n"
                SQLFile.write(insertStatement)
                insertStatement = insertPreamble
            else:
                insertStatement += ", "

        elif CSVFilePath == 'CSVs/like.csv':
            # Note: {Like, Love, Wow} = Like, {Angry} = Dislike for posts
            # If cid == x, then the reaction is a top level post, otherwise it's a reaction for that comment

            commentID = attributes[2]
            postID = ""
            if commentID == 'x':
                postID = attributes[1]
            else:
                postID = commentID
            response = attributes[3]
            reaction = True
            if response == 'Angry':
                reaction = False
            userID = attributes[4]

            insertStatement += f'("{postID}", "{userID}", "{reaction}")'

            if index % 100 == 0:
                insertStatement += ";\n\n"
                SQLFile.write(insertStatement)
                insertStatement = insertPreamble
            else:
                insertStatement += ", "

            reactionID += 1

        index += 1
    
    if ('\n' not in insertStatement):
        insertStatement = insertStatement[:-2] # remove last appended comma and space if we did not end on a multiple of 20
        insertStatement += ";\n\n"
    if (insertStatement != insertPreamble):
        SQLFile.write(insertStatement)

    SQLFile.close()

    return 0

def GroupsSQLCreation():
    global groups

    SQLFile = open("SQLInserts/groupsInserts.sql", 'a')
    SQLFile.seek(0, 0)
    SQLFile.truncate()

    insertPreamble = "INSERT INTO GroupInfo VALUES "
    insertStatement = insertPreamble

    for group in groups:
        insertStatement += f"('{group['groupID']}', '{group['groupName']}'), "

    insertStatement = insertStatement[:-2] # remove last appended comma and space if we did not end on a multiple of 20 
    insertStatement += ';\n\n'
    SQLFile.write(insertStatement)
    SQLFile.close()

    return 0

def GroupMembersSQLCreation():
    global memberGroupObjects

    SQLFile = open("SQLInserts/groupMembersInserts.sql", 'a')
    SQLFile.seek(0, 0)
    SQLFile.truncate()

    insertPreamble = "INSERT INTO GroupMembers VALUES "
    insertStatement = insertPreamble

    index = 1
    for memberGroupObject in memberGroupObjects:
        insertStatement += f"('{memberGroupObject['groupID']}', '{memberGroupObject['memberID']}')"

        if index % 100 == 0:
            insertStatement += ";\n\n"
            SQLFile.write(insertStatement)
            insertStatement = insertPreamble
        else:
            insertStatement += ", "

        index += 1

    if ('\n' not in insertStatement):
        insertStatement = insertStatement[:-2] # remove last appended comma and space if we did not end on a multiple of 20
        insertStatement += ";\n\n"
    if (insertStatement != insertPreamble):
        SQLFile.write(insertStatement)

    SQLFile.close()

    return 0

def LinksSQLCreation():
    global linkObjects

    SQLFile = open("SQLInserts/linksInserts.sql", 'a')
    SQLFile.seek(0, 0)
    SQLFile.truncate()

    insertPreamble = "INSERT INTO Links VALUES "
    insertStatement = insertPreamble
    
    index = 1
    for linkObject in linkObjects:
        postID = linkObject['postID']
        link = linkObject['link']

        insertStatement += f'("{postID}", "{link}")'

        if index % 100 == 0:
            insertStatement += ";\n\n"
            SQLFile.write(insertStatement)
            insertStatement = insertPreamble
        else:
            insertStatement += ", "
        
        index += 1

    if ('\n' not in insertStatement):
        insertStatement = insertStatement[:-2] # remove last appended comma and space if we did not end on a multiple of 20
        insertStatement += ";\n\n"
    if (insertStatement != insertPreamble):
        SQLFile.write(insertStatement) 

    SQLFile.close()
    
    return 0

while True:
    conversion = input("A = all, U = users, P = posts, R = reactions, E = exit: ")

    if conversion.upper() == 'E':
        break
    elif conversion.upper() == 'A':
        SQLCreation('Users', "CSVs/member.csv", "SQLInserts/usersInserts.sql", True)
        GroupsSQLCreation()
        GroupMembersSQLCreation()
        SQLCreation('Posts', "CSVs/post.csv", "SQLInserts/postsInserts.sql", True)
        SQLCreation('Posts', "CSVs/comment.csv", "SQLInserts/postsInserts.sql", False)
        LinksSQLCreation()
        SQLCreation('Reactions', "CSVs/like.csv", "SQLInserts/reactionsInserts.sql", True)
    elif conversion.upper() == 'U':
        SQLCreation('Users', "CSVs/member.csv", "SQLInserts/usersInserts.sql", True)
        GroupsSQLCreation()
        GroupMembersSQLCreation()
    elif conversion.upper() == 'P':
        SQLCreation('Posts', "CSVs/post.csv", "SQLInserts/postsInserts.sql", True)
        SQLCreation('Posts', "CSVs/comment.csv", "SQLInserts/postsInserts.sql", False)
        LinksSQLCreation()
    elif conversion.upper() == 'R':
        SQLCreation("CSVs/like.csv", "SQLInserts/reactionsInserts.sql", True)
    else:
        print('Unrecognized input.')


