import os
from dotenv import load_dotenv

# Load environment variables from a .env file
load_dotenv()

class Config:
    """Configuration class for the application. Dynamically fetches settings from environment variables."""

    # General Config
    @staticmethod
    def get_log_level():
        """Returns the log level."""
        return os.getenv("LOG_LEVEL", "INFO")

    # Database Config
    @staticmethod
    def get_singlestore_db_url():
        """Returns the SingleStore database URL."""
        return os.getenv("SINGLESTORE_DB_URL")

    @staticmethod
    def get_db_pool_size():
        """Returns the database connection pool size."""
        return int(os.getenv("DB_POOL_SIZE", "10"))

    # S3 & Polymarket Config
    @staticmethod
    def get_aws_access_key_id():
        """Returns the AWS access key ID."""
        return os.getenv("AWS_ACCESS_KEY_ID", "19639457-c11c-4a74-ae5e-57ccf926e015")

    @staticmethod
    def get_aws_secret_access_key():
        """Returns the AWS secret access key."""
        return os.getenv("AWS_SECRET_ACCESS_KEY", "HRsLUdAuK6su1hpnKRpSOrZdWnyuYltm")

    @staticmethod
    def get_s3_bucket():
        """Returns the S3 bucket name."""
        return os.getenv("S3_BUCKET", "flatfiles")

    @staticmethod
    def get_s3_prefix():
        """Returns the S3 prefix."""
        return os.getenv("S3_PREFIX", "us_stocks_sip/trades_v1/2024/")

    @staticmethod
    def get_s3_endpoint_url():
        """Returns the S3 endpoint URL."""
        return os.getenv("S3_ENDPOINT_URL", "https://files.polygon.io")

    @staticmethod
    def get_s3_region():
        """Returns the S3 region."""
        return os.getenv("S3_REGION", "us-east-1")

    # Simulation Config
    @staticmethod
    def get_throughput():
        """Returns the simulation throughput (number of inserts/messages per second)."""
        return int(os.getenv("THROUGHPUT", "1000"))

    @staticmethod
    def get_mode():
        """Returns the simulation mode ('db' or 'kafka')."""
        return os.getenv("MODE", "db")

    @staticmethod
    def get_num_threads():
        """Returns the number of threads to use for sending trades."""
        return int(os.getenv("NUM_THREADS", "8"))

    # Kafka Config
    @staticmethod
    def get_kafka_broker():
        """Returns the Kafka broker URL."""
        return os.getenv("KAFKA_BROKER", "localhost:9092")

    @staticmethod
    def get_kafka_topic():
        """Returns the Kafka topic name."""
        return os.getenv("KAFKA_TOPIC", "trades")

    # CSV Config
    @staticmethod
    def get_local_csv_path():
        """Returns the local path for saving the downloaded CSV."""
        return os.getenv("LOCAL_CSV_PATH", "./trades_data.csv")

    # Logging Config
    @staticmethod
    def get_log_interval():
        """Returns the interval (in seconds) for logging updates."""
        return int(os.getenv("LOG_INTERVAL", "5"))

    # Database Batch Config
    @staticmethod
    def get_batch_size():
        """Returns the batch size for database inserts."""
        return int(os.getenv("BATCH_SIZE", "1000"))
