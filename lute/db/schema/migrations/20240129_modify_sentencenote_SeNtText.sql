create table sentencenote_dg_tmp
(
    SeNtID   INTEGER not null
        primary key autoincrement,
    BookID   INTEGER,
    PageID   INTEGER,
    SeText   VARCHAR(500),
    SeNtText TEXT
);

insert into sentencenote_dg_tmp(SeNtID, BookID, PageID, SeText, SeNtText)
select SeNtID, BookID, PageID, SeText, SeNtText
from sentencenote;

drop table sentencenote;

alter table sentencenote_dg_tmp
    rename to sentencenote;

create unique index sentencenote_SeNtID_BookID_PageID_SeText_uindex
    on sentencenote (SeNtID, BookID, PageID, SeText);

