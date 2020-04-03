DELIMITER //
DROP PROCEDURE IF EXISTS delComment // 

CREATE PROCEDURE delComment(IN CommentIdIn int,IN usernameIn VARCHAR(50))
BEGIN
    DELETE FROM comment WHERE CommentID = CommentIdIn And Username = usernameIn;

SELECT LAST_INSERT_ID();
END//
DELIMITER ;
