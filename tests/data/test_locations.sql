-- SQLite Database Creation Script
-- Save this as test_locations.sql and import into SQLite

CREATE TABLE locations (
  id INTEGER PRIMARY KEY AUTOINCREMENT,
  name TEXT NOT NULL,
  latitude REAL NOT NULL,
  longitude REAL NOT NULL,
  type TEXT,
  city TEXT,
  rating REAL
);

INSERT INTO locations (name, latitude, longitude, type, city, rating) VALUES ('Central Park', 40.7829, -73.9654, 'park', 'New York', 4.8);
INSERT INTO locations (name, latitude, longitude, type, city, rating) VALUES ('Golden Gate Bridge', 37.8199, -122.4783, 'landmark', 'San Francisco', 4.9);
INSERT INTO locations (name, latitude, longitude, type, city, rating) VALUES ('Navy Pier', 41.8919, -87.6051, 'attraction', 'Chicago', 4.5);
INSERT INTO locations (name, latitude, longitude, type, city, rating) VALUES ('Space Needle', 47.6205, -122.3493, 'landmark', 'Seattle', 4.6);
INSERT INTO locations (name, latitude, longitude, type, city, rating) VALUES ('Venice Beach', 33.985, -118.4695, 'beach', 'Los Angeles', 4.4);
INSERT INTO locations (name, latitude, longitude, type, city, rating) VALUES ('Millennium Park', 41.8826, -87.6226, 'park', 'Chicago', 4.7);
INSERT INTO locations (name, latitude, longitude, type, city, rating) VALUES ('Pike Place Market', 47.6097, -122.3425, 'market', 'Seattle', 4.5);
INSERT INTO locations (name, latitude, longitude, type, city, rating) VALUES ('Alcatraz Island', 37.8267, -122.4233, 'historic', 'San Francisco', 4.7);
