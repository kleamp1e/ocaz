CREATE TABLE synonyms(
    id VARCHAR(64) NOT NULL,
    synonym_ja VARCHAR(128) NULL,
    synonym_en VARCHAR(128) NULL,
    INDEX (synonym_ja),
    INDEX (synonym_en));
