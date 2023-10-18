CREATE TABLE terms(
    id VARCHAR(64) NOT NULL PRIMARY KEY,
    parent_id VARCHAR(64) NULL,
    created_at INT NOT NULL,
    updated_at INT NOT NULL,
    representative_ja VARCHAR(128) NULL,
    representative_en VARCHAR(128) NULL,
    INDEX (parent_id),
    INDEX (representative_ja),
    INDEX (representative_en));
