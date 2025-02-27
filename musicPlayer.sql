-- database: :memory:

CREATE DATABASE musicPLayer

CREATE TABLE IF NOT EXISTS playlists 
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    name TEXT,
    description TEXT,
    image_path TEXT
