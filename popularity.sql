SELECT PostID, numReactions, numUpvotes, numDownvotes FROM
(SELECT PostID, COUNT(Reaction) AS numReactions FROM Reactions GROUP BY PostID) AS T1,
(SELECT COUNT(Reaction) AS numUpvotes FROM Reactions WHERE Reaction = TRUE GROUP BY PostID) AS T2,
(SELECT COUNT(Reaction) AS numDownvotes FROM Reactions WHERE Reaction = FALSE GROUP BY PostID) AS T3;
