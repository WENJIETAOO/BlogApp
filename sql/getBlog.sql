DELIMITER //
DROP PROCEDURE IF EXISTS getBlog // 

CREATE PROCEDURE getBlog(IN BlogIdIn int)
BEGIN
    SELECT BlogText,Username FROM blog WHERE BlogID = BlogIdIn;

SELECT LAST_INSERT_ID();
END//
DELIMITER ;
