
create table if not exists words_dg_tmp
(
    WoID            INTEGER                            not null
        primary key,
    WoLgID          INTEGER                            not null
        references languages
            on delete cascade,
    WoText          VARCHAR(250)                       not null,
    WoTextLC        VARCHAR(250)                       not null,
    WoStatus        INTEGER                                 not null,
    WoTranslation   VARCHAR(500),
    WoRomanization  VARCHAR(100),
    WoTokenCount    TINYINT  default '0'               not null,
    WoLemma         VARCHAR(250),
    WoCreated       DATETIME default CURRENT_TIMESTAMP not null,
    WoStatusChanged DATETIME default CURRENT_TIMESTAMP not null,
    WoUpdated DATETIME default CURRENT_TIMESTAMP not null,
    WoSyncStatus    INTEGER  default 0                 not null
);

insert into words_dg_tmp(WoID, WoLgID, WoText, WoTextLC, WoStatus, WoTranslation, WoRomanization, WoTokenCount, WoLemma,
                         WoCreated, WoStatusChanged, WoSyncStatus)
select WoID,
       WoLgID,
       WoText,
       WoTextLC,
       WoStatus,
       WoTranslation,
       WoRomanization,
       WoTokenCount,
       WoLemma,
       WoCreated,
       WoStatusChanged,
       WoSyncStatus
from words;
drop trigger trig_words_after_update_WoStatus_if_following_parent;
drop trigger trig_words_update_WoStatusChanged;
drop trigger trig_wordparents_after_delete_change_WoSyncStatus;

drop trigger trig_wordparents_after_insert_update_parent_WoStatus_if_following;


drop table words;

alter table words_dg_tmp
    rename to words;

create index WoLgID
    on words (WoLgID);

create index WoStatus
    on words (WoStatus);

create index WoStatusChanged
    on words (WoStatusChanged);

create index WoTextLC
    on words (WoTextLC);

create unique index WoTextLCLgID
    on words (WoTextLC, WoLgID);

create index WoTokenCount
    on words (WoTokenCount);



