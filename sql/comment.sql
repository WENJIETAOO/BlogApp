DROP TABLE IF EXISTS comment;
CREATE TABLE comment (
  CommentID int NOT NULL AUTO_INCREMENT,
  commentText VARCHAR(500),
  BlogID int NOT NULL,
  Username VARCHAR(50),
  Url VARCHAR(90), 
  PRIMARY KEY (CommentID),
  FOREIGN KEY (BlogID)REFERENCES blog(BlogID)
);
