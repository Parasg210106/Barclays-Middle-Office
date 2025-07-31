import logging
from psycopg2.extras import RealDictCursor
from psycopg2.pool import SimpleConnectionPool
from contextlib import contextmanager
import os

logger = logging.getLogger(__name__)

class DatabaseClient:
    def __init__(self):
        self.connection_pool = None
        self._setup_connection_pool()
    
    def _setup_connection_pool(self):
        """Initialize connection pool to PostgreSQL"""
        try:
            self.connection_pool = SimpleConnectionPool(
                minconn=1,
                maxconn=10,
                host=os.getenv("DB_HOST", "postgres"),
                port=os.getenv("DB_PORT", "5432"),
                database=os.getenv("DB_NAME", "tradesim"),
                user=os.getenv("DB_USER", "tradesim"),
                password=os.getenv("DB_PASSWORD", "tradesim")
            )
            logger.info("Database connection pool initialized successfully")
        except Exception as e:
            logger.error(f"Failed to initialize database connection pool: {e}")
            raise
    
    @contextmanager
    def get_connection(self):
        """Get a database connection from the pool"""
        conn = None
        try:
            if self.connection_pool is None:
                logger.error("Database connection pool is not initialized.")
                raise Exception("Database connection pool is not initialized.")
            conn = self.connection_pool.getconn()
            yield conn
        except Exception as e:
            if conn:
                conn.rollback()
            logger.error(f"Database operation failed: {e}")
            raise
        finally:
            if conn and self.connection_pool is not None:
                self.connection_pool.putconn(conn)
    
    def execute_query(self, query: str, params: tuple = ()):
        """Execute a query and return results"""
        if not isinstance(params, tuple):
            params = tuple(params)
        with self.get_connection() as conn:
            with conn.cursor(cursor_factory=RealDictCursor) as cursor:
                cursor.execute(query, params)
                if query.strip().upper().startswith('SELECT'):
                    return cursor.fetchall()
                else:
                    conn.commit()
                    return cursor.rowcount
    
    def execute_many(self, query: str, params_list: list):
        """Execute multiple queries with different parameters"""
        with self.get_connection() as conn:
            with conn.cursor() as cursor:
                cursor.executemany(query, params_list)
                conn.commit()
                return cursor.rowcount
    
    def close(self):
        """Close the connection pool"""
        if self.connection_pool:
            self.connection_pool.closeall()
            logger.info("Database connection pool closed")

# Database initialization functions
def init_trade_tables(db_client: DatabaseClient):
    """Initialize trade-related database tables"""
    create_trades_table = """
    CREATE TABLE IF NOT EXISTS trades (
        trade_id VARCHAR(255) PRIMARY KEY,
        trade_date TIMESTAMP NOT NULL,
        settlement_date TIMESTAMP NOT NULL,
        instrument_id VARCHAR(255) NOT NULL,
        instrument_type VARCHAR(100) NOT NULL,
        quantity DECIMAL(20,8) NOT NULL,
        price DECIMAL(20,8) NOT NULL,
        currency VARCHAR(3) NOT NULL,
        counterparty_id VARCHAR(255) NOT NULL,
        trader_id VARCHAR(255) NOT NULL,
        portfolio_id VARCHAR(255) NOT NULL,
        side VARCHAR(10) NOT NULL,
        status VARCHAR(50) DEFAULT 'BOOKED',
        stp BOOLEAN DEFAULT FALSE,
        recap_doc TEXT,
        termsheet_doc TEXT,
        validation_status VARCHAR(50) DEFAULT 'PENDING',
        isin VARCHAR(12),
        cusip VARCHAR(9),
        lei VARCHAR(20),
        settlement_instructions JSONB,
        custodian VARCHAR(255),
        accrued_interest DECIMAL(20,8),
        fees DECIMAL(20,8),
        is_block_trade BOOLEAN DEFAULT FALSE,
        parent_trade_id VARCHAR(255),
        allocation_percentage DECIMAL(5,2),
        risk_checks JSONB DEFAULT '{}',
        risk_violations JSONB DEFAULT '[]',
        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
        updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
    );
    """
    
    create_trade_events_table = """
    CREATE TABLE IF NOT EXISTS trade_events (
        event_id VARCHAR(255) PRIMARY KEY,
        event_type VARCHAR(100) NOT NULL,
        trade_id VARCHAR(255) NOT NULL,
        timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
        data JSONB NOT NULL,
        source_service VARCHAR(100) NOT NULL
    );
    """
    
    create_exceptions_table = """
    CREATE TABLE IF NOT EXISTS exceptions (
        exception_id VARCHAR(255) PRIMARY KEY,
        trade_id VARCHAR(255) NOT NULL,
        exception_type VARCHAR(50) NOT NULL,
        description TEXT NOT NULL,
        status VARCHAR(20) DEFAULT 'OPEN',
        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
        resolved_at TIMESTAMP,
        resolution_notes TEXT
    );
    """
    
    create_allocation_rules_table = """
    CREATE TABLE IF NOT EXISTS allocation_rules (
        rule_id VARCHAR(255) PRIMARY KEY,
        portfolio_id VARCHAR(255) NOT NULL,
        allocation_type VARCHAR(50) NOT NULL,
        percentage DECIMAL(5,2) NOT NULL,
        priority INTEGER DEFAULT 1,
        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
    );
    """
    
    create_lifecycle_events_table = """
    CREATE TABLE IF NOT EXISTS lifecycle_events (
        event_id VARCHAR(255) PRIMARY KEY,
        trade_id VARCHAR(255) NOT NULL,
        from_status VARCHAR(50) NOT NULL,
        to_status VARCHAR(50) NOT NULL,
        timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
        reason TEXT,
        metadata JSONB DEFAULT '{}'
    );
    """
    
    try:
        db_client.execute_query(create_trades_table)
        db_client.execute_query(create_trade_events_table)
        db_client.execute_query(create_exceptions_table)
        db_client.execute_query(create_allocation_rules_table)
        db_client.execute_query(create_lifecycle_events_table)
        logger.info("Database tables initialized successfully")
    except Exception as e:
        logger.error(f"Failed to initialize database tables: {e}")
        raise 