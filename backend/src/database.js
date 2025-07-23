const sqlite3 = require('sqlite3').verbose();
const path = require('path');

const dbPath = path.join(__dirname, '..', 'database.db');

// Create database connection
const db = new sqlite3.Database(dbPath, (err) => {
  if (err) {
    console.error('Error opening database:', err.message);
  } else {
    console.log('Connected to SQLite database.');
  }
});

// Initialize database tables
const initializeDatabase = () => {
  db.serialize(() => {
    // Cities table
    db.run(`
      CREATE TABLE IF NOT EXISTS cities (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        name TEXT NOT NULL,
        latitude REAL NOT NULL,
        longitude REAL NOT NULL,
        country TEXT,
        created_at DATETIME DEFAULT CURRENT_TIMESTAMP
      )
    `);

    // Routes table to store optimal routes
    db.run(`
      CREATE TABLE IF NOT EXISTS routes (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        city_ids TEXT NOT NULL,
        total_distance REAL NOT NULL,
        route_order TEXT NOT NULL,
        algorithm TEXT DEFAULT 'held-karp',
        created_at DATETIME DEFAULT CURRENT_TIMESTAMP
      )
    `);

    // Distance cache table
    db.run(`
      CREATE TABLE IF NOT EXISTS distance_cache (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        from_city_id INTEGER NOT NULL,
        to_city_id INTEGER NOT NULL,
        distance REAL NOT NULL,
        duration INTEGER,
        created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
        FOREIGN KEY (from_city_id) REFERENCES cities (id),
        FOREIGN KEY (to_city_id) REFERENCES cities (id),
        UNIQUE(from_city_id, to_city_id)
      )
    `);
  });
};

// Initialize database when module is loaded
initializeDatabase();

module.exports = { db };
