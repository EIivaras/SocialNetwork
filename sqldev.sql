CREATE VIEW Popularity AS SELECT PostID, NumReactions, numUpvotes, numDownvotes FROM
(SELECT PostID, COUNT(Reaction) AS numReactions FROM Reactions GROUP BY PostID) Total
LEFT JOIN
(SELECT PostID, COUNT(Reaction) AS numUpvotes FROM Reactions WHERE Reaction = TRUE GROUP BY PostID) Up
USING(PostID)
LEFT JOIN
(SELECT PostID, COUNT(Reaction) AS numDownvotes FROM Reactions WHERE Reaction = FALSE GROUP BY PostID) Down
USING(PostID);
