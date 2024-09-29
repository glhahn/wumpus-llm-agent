import logging
import sqlite3
from dataclasses import dataclass
from datetime import datetime

logger = logging.getLogger(__name__)


@dataclass
class GameMetrics:
    """Represents metrics from a single game run."""

    timestamp: datetime
    num_turns: int
    rooms_explored: int
    death_by_pit: bool
    death_by_wumpus: bool
    death_by_arrows: bool
    game_won: bool
    arrows_remaining: int
    action_generation_errors: int
    average_response_time: float
    total_response_time: float


class WumpusDB:
    def __init__(self, db_path: str = "wumpus_metrics.db") -> None:
        """
        Initialize database connection and ensure schema exists.

        Args:
            db_path: Path to the SQLite database file
        """
        self.db_path = db_path
        self.conn = None
        # initialize schema on creation
        self._connect()
        self._init_schema()

    def _connect(self) -> None:
        """Establish database connection with proper configuration."""
        self.conn = sqlite3.connect(self.db_path, detect_types=sqlite3.PARSE_DECLTYPES)
        # enable foreign key constraints
        self.conn.execute("PRAGMA foreign_keys = ON")

    def _init_schema(self) -> None:
        """Initialize database schema if it doesn't exist."""
        logger.info("* Initializing database at: %s", self.db_path)

        cursor = self.conn.cursor()

        # create game metrics table with indexed columns
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS game_metrics (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                timestamp DATETIME DEFAULT CURRENT_TIMESTAMP,
                num_turns INTEGER NOT NULL,
                rooms_explored INTEGER NOT NULL,
                death_by_pit BOOLEAN NOT NULL,
                death_by_wumpus BOOLEAN NOT NULL,
                death_by_arrows BOOLEAN NOT NULL,
                game_won BOOLEAN NOT NULL,
                arrows_remaining INTEGER NOT NULL,
                action_generation_errors INTEGER DEFAULT 0,
                average_response_time FLOAT,
                total_response_time FLOAT
            )
        """)

        # create index for commonly queried columns
        cursor.execute("""
            CREATE INDEX IF NOT EXISTS idx_game_metrics_timestamp 
            ON game_metrics(timestamp)
        """)

        self.conn.commit()

    def __enter__(self):
        """Context manager entry."""
        if self.conn is None:
            self._connect()
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        """Context manager exit."""
        if self.conn:
            if exc_type is None:
                self.conn.commit()
            else:
                self.conn.rollback()
            self.conn.close()
            self.conn = None

    def close(self):
        """Close the database connection."""
        if self.conn:
            self.conn.close()
            self.conn = None

    def add_game_metrics(self, metrics: GameMetrics) -> None:
        """
        Record metrics for a completed game.

        Args:
            metrics: GameMetrics object containing the game results

        Raises:
            sqlite3.Error: If the database operation fails
        """
        try:
            cursor = self.conn.cursor()
            cursor.execute(
                """
                INSERT INTO game_metrics (
                    timestamp, num_turns, rooms_explored,
                    death_by_pit, death_by_wumpus, death_by_arrows,
                    game_won, arrows_remaining, action_generation_errors, 
                    average_response_time, total_response_time
                ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            """,
                (
                    metrics.timestamp,
                    metrics.num_turns,
                    metrics.rooms_explored,
                    metrics.death_by_pit,
                    metrics.death_by_wumpus,
                    metrics.death_by_arrows,
                    metrics.game_won,
                    metrics.arrows_remaining,
                    metrics.action_generation_errors,
                    metrics.average_response_time,
                    metrics.total_response_time,
                ),
            )
            self.conn.commit()
        except sqlite3.Error:
            self.conn.rollback()
            raise
