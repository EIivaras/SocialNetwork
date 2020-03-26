def post(userID, mycursor):
    # Get and check the content for the post
    Content = input("What do you want to post?\n")
    print(len(Content))
    if len(Content) > 1000:
        print("That post was too long! Maximum length is 1000 characters.")

    GroupID = input("What group do you want to post in? (Hit enter for none) GroupID: ")
    if len(groupID) == 0:
        groupID = "NULL"

    TopicID = input("What is the topic of your post? (Hit enter for none) TopicID: ")
    if len(TopicID) == 0:
        TopicID = "NULL"

    ParentPost = "NULL"

    mycursor.execute("INSERT INTO Posts (UserID, ParentPost, TopicID, GroupID, Content) VALUES ({}, {}, {}, {}, {});".format(UserID, ParentPost, TopicID, GroupID, Content))

    return 0
