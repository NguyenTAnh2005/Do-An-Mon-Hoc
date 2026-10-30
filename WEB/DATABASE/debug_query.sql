-- Xóa dữ liệu và reset luôn cả bộ đếm ID về 1
TRUNCATE TABLE 
-- classification_log
-- trash_bin
-- area
account
-- refresh_token
RESTART IDENTITY CASCADE;
--TRUNCATE: Xóa sạch sành sanh dữ liệu nhưng giữ lại cấu trúc bảng.
--RESTART IDENTITY: Đưa bộ đếm ID tự động tăng về lại số 1.
--ASCADE: Tự động xử lý các ràng buộc khóa ngoại (ví dụ xóa Category thì không bị kẹt vì Blog).

-- XÓA dữ liệu và tất cả các bảng 
DROP SCHEMA public CASCADE; CREATE SCHEMA public;


select * from account;
select * from classification_log;
select* from trash_bin;
select*from area;
