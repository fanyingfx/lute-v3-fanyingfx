DROP TRIGGER IF EXISTS trig_sn_update_SnUpdated;
CREATE TRIGGER  trig_sn_update_SnUpdated
-- created by db/schema/migrations_repeatable/trig_words.sql
    AFTER UPDATE OF SeNtText
    ON sentencenote
    FOR EACH ROW
    WHEN old.SeNtText<> new.SeNtText

BEGIN
    UPDATE sentencenote
    SET SnUpdated= CURRENT_TIMESTAMP
    WHERE SeNtID = NEW.SeNtID;
END