DELIMITER //
DROP PROCEDURE IF EXISTS createComment// 

CREATE PROCEDURE createComment(IN commentTextIn VARCHAR(500), IN BlogIdIn int, IN UserNameIn VARCHAR(50))
BEGIN
INSERT INTO comment (commentText,BlogID,username) VALUES
   (commentTextIn,BlogIdIn,UserNameIn);
SELECT LAST_INSERT_ID();
END//
DELIMITER ;
