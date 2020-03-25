def post(userID):
    # Get and check the content for the post
    content = input("What do you want to post?\n")
    print(len(content))
    if len(content) > 1000:
        print("That post was too long! Maximum length is 1000 characters.")



    return 0
