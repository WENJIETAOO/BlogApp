DELIMITER //
DROP PROCEDURE IF EXISTS DeleteBlog // 

CREATE PROCEDURE DeleteBlog(IN BlogIdIn int,IN usernameIn VARCHAR(50))
BEGIN
DELETE FROM comment WHERE BlogID = BlogIdIn And Username = usernameIn;
DELETE FROM blog WHERE BlogID = BlogIdIn And Username = usernameIn;
END//
DELIMITER ;
