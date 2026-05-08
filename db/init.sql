CREATE TABLE IF NOT EXISTS games (
    id                INTEGER PRIMARY KEY,
    title             VARCHAR(255) NOT NULL,
    thumbnail         TEXT,
    short_description TEXT,
    game_url          TEXT,
    genre             VARCHAR(150),
    platform          VARCHAR(100),
    publisher         VARCHAR(150),
    developer         VARCHAR(150),
    release_date      DATE,
    price             VARCHAR(50),
    created_at        TIMESTAMP DEFAULT NOW()
);

CREATE TABLE IF NOT EXISTS tags (
    id   SERIAL PRIMARY KEY,
    name VARCHAR(100) UNIQUE NOT NULL
);

CREATE TABLE IF NOT EXISTS game_tags (
    game_id INTEGER REFERENCES games(id) ON DELETE CASCADE,
    tag_id  INTEGER REFERENCES tags(id)  ON DELETE CASCADE,
    PRIMARY KEY (game_id, tag_id)
);

CREATE INDEX IF NOT EXISTS idx_games_title    ON games(title);
CREATE INDEX IF NOT EXISTS idx_games_genre    ON games(genre);
CREATE INDEX IF NOT EXISTS idx_games_platform ON games(platform);
CREATE INDEX IF NOT EXISTS idx_tags_name      ON tags(name);