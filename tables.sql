CREATE TABLE IF NOT EXISTS Users
(
  UserID VARCHAR(50) NOT NULL,
  FirstName VARCHAR(50) NOT NULL,
  LastName VARCHAR(50) NOT NULL,
  BirthDate DATE,
  DateJoined DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP, -- Format of "YYYY-MM-DD"
  PRIMARY KEY (UserID)
);

CREATE TABLE IF NOT EXISTS GroupInfo
(
  GroupID VARCHAR(50) NOT NULL,
  GroupName VARCHAR(250) NOT NULL,
  PRIMARY KEY (GroupID)
);

CREATE TABLE IF NOT EXISTS GroupMembers
(
  UserID VARCHAR(50) NOT NULL,
  GroupID VARCHAR(50) NOT NULL,
  PRIMARY KEY (UserID, GroupID),
  FOREIGN KEY (UserID) REFERENCES Users(UserID),
  FOREIGN KEY (GroupID) REFERENCES GroupInfo(GroupID)
);

CREATE TABLE IF NOT EXISTS Friends
(
  UserID VARCHAR(50) NOT NULL,
  FriendID VARCHAR(50) NOT NULL,
  PRIMARY KEY (UserID, FriendID),
  FOREIGN KEY (UserID) REFERENCES Users(UserID),
  FOREIGN KEY (FriendID) REFERENCES Users(UserID)
);

CREATE TABLE IF NOT EXISTS FollowedUsers
(
  UserID VARCHAR(50) NOT NULL,
  FollowedID VARCHAR(50) NOT NULL,
  PRIMARY KEY (UserID, FollowedID),
  FOREIGN KEY (UserID) REFERENCES Users(UserID),
  FOREIGN KEY (FollowedID) REFERENCES Users(UserID)
);

CREATE TABLE IF NOT EXISTS Posts
(
  PostID VARCHAR(50) NOT NULL,
  PostTime DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP,
  Content VARCHAR(2000) NOT NULL,
  UserID VARCHAR(50) NOT NULL,
  GroupID VARCHAR(50),
  ParentPost VARCHAR(50),
  PRIMARY KEY (PostID),
  FOREIGN KEY (UserID) REFERENCES Users(UserID),
  FOREIGN KEY (GroupID) REFERENCES GroupInfo(GroupID),
  FOREIGN KEY (ParentPost) REFERENCES Posts(PostID)
);

CREATE TABLE IF NOT EXISTS Links
(
  PathID INT NOT NULL AUTO_INCREMENT,
  PostID VARCHAR(50) NOT NULL,
  Path VARCHAR(1000) NOT NULL,
  PRIMARY KEY (PathID),
  FOREIGN KEY (PostID) REFERENCES Posts(PostID)
);

CREATE TABLE IF NOT EXISTS Reactions
(
  PostID VARCHAR(50) NOT NULL,
  UserID VARCHAR(50) NOT NULL,
  Reaction BOOLEAN NOT NULL,
  PRIMARY KEY (PostID, UserID),
  FOREIGN KEY (UserID) REFERENCES Users(UserID),
  FOREIGN KEY (PostID) REFERENCES Posts(PostID)
);

CREATE TABLE IF NOT EXISTS ReadStatus
(
  PostID VARCHAR(50) NOT NULL,
  UserID VARCHAR(50) NOT NULL,
  HasRead BOOLEAN NOT NULL,
  PRIMARY KEY (PostID, UserID),
  FOREIGN KEY (UserID) REFERENCES Users(UserID),
  FOREIGN KEY (PostID) REFERENCES Posts(PostID)
);

CREATE TABLE IF NOT EXISTS Meta
(
    NextPostID INT NOT NULL,
    PRIMARY KEY (NextPostID)
);
