DELIMITER //
DROP PROCEDURE IF EXISTS getComment // 

CREATE PROCEDURE getComment(IN commentidIn int)
BEGIN
	SELECT commentText,CommentID,Username FROM comment WHERE CommentID =commentidIn;

SELECT LAST_INSERT_ID();
END//
DELIMITER ;
