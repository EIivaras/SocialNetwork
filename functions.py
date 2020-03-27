def post(UserID, mycursor, mydb): #Working!
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

    # Post by adding all the information to the database
    q = "INSERT INTO Posts (UserID, ParentPost, TopicID, GroupID, Content) VALUES (%s, %s, %s, %s, %s);"
    v = (UserID, ParentPost, TopicID, GroupID, Content)
    mycursor.execute(q, v)
    mydb.commit()

    return 0


def read(PostID, mycursor): #Working!
    q = "SELECT Content FROM Posts WHERE PostID = %s;"
    v = (str(PostID),)
    mycursor.execute(q, v)
    Content = mycursor.fetchall()
    print(Content[0][0])
    
    return 0
