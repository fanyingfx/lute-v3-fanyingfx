create table main.sentencenote
(
     SeNtID   INTEGER not null
        primary key autoincrement,
    BookID INTEGER,
    PageID   INTEGER,
    SeText   VARCHAR(500),
    SeNtText VARCHAR(500)
);

create table main.sentencenotetags
(
    SeNtTgID INTEGER,
    SeNtID   INTEGER
);

