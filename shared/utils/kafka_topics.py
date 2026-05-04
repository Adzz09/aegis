"""
Kafka topic management utility.

Provides functions to create Kafka topics automatically on startup.
"""
import os
from confluent_kafka.admin import AdminClient, NewTopic
from confluent_kafka import KafkaError


# All Kafka topics used in AEGIS
AEGIS_TOPICS = [
    # Sensor topics (produced by sim-engine)
    {"name": "sensor.radar", "partitions": 1, "replication_factor": 1},
    {"name": "sensor.optical", "partitions": 1, "replication_factor": 1},
    {"name": "sensor.rf", "partitions": 1, "replication_factor": 1},
    
    # Fusion output (consumed by classifier, gateway)
    {"name": "fused.tracks", "partitions": 1, "replication_factor": 1},
    
    # Threat scores (consumed by optimizer, gateway)
    {"name": "threat.scores", "partitions": 1, "replication_factor": 1},
    
    # Assignments (consumed by gateway)
    {"name": "assignments", "partitions": 1, "replication_factor": 1},
    
    # System health
    {"name": "system.health", "partitions": 1, "replication_factor": 1},
    
    # Command topic for scenario triggers
    {"name": "sim.commands", "partitions": 1, "replication_factor": 1},
    
    # Dead letter queues
    {"name": "fused.tracks.dlq", "partitions": 1, "replication_factor": 1},
    {"name": "threat.scores.dlq", "partitions": 1, "replication_factor": 1},
    {"name": "assignments.dlq", "partitions": 1, "replication_factor": 1},
]


def get_kafka_brokers() -> str:
    """Get Kafka broker address from environment."""
    return os.getenv("KAFKA_BROKERS", "localhost:19092")


def create_admin_client() -> AdminClient:
    """Create Kafka admin client."""
    return AdminClient({"bootstrap.servers": get_kafka_brokers()})


def create_topics(raise_on_error: bool = False) -> dict:
    """
    Create all AEGIS Kafka topics if they don't exist.
    
    Args:
        raise_on_error: If True, raises exception on error. 
                     If False, logs errors and continues.
    
    Returns:
        Dict of topic_name -> futures.Future objects
    """
    admin = create_admin_client()
    
    # Convert topic configs to NewTopic objects
    new_topics = []
    for topic_config in AEGIS_TOPICS:
        new_topics.append(NewTopic(
            topic_config["name"],
            num_partitions=topic_config["partitions"],
            replication_factor=topic_config["replication_factor"]
        ))
    
    # Create topics
    futures = admin.create_topics(new_topics, raise_on_error=raise_on_error)
    
    return futures


def wait_for_topics(timeout_seconds: float = 30.0) -> bool:
    """
    Wait for all topics to be created.
    
    Args:
        timeout_seconds: How long to wait for topic creation.
    
    Returns:
        True if all topics created, False otherwise.
    """
    import concurrent.futures
    
    futures = create_topics(raise_on_error=False)
    
    try:
        # Wait for results with timeout
        with concurrent.futures.ThreadPoolExecutor(max_workers=1) as executor:
            # Just wait for the first one to complete
            for topic, future in futures.items():
                try:
                    future.result(timeout=timeout_seconds)
                    print(f"Topic '{topic}' created or already exists")
                except Exception as e:
                    # Topic might already exist - that's ok
                    if "already exists" in str(e).lower():
                        print(f"Topic '{topic}' already exists")
                    else:
                        print(f"Warning creating topic '{topic}': {e}")
        
        return True
        
    except Exception as e:
        print(f"Error waiting for topics: {e}")
        return False


def list_topics() -> list:
    """
    List all existing Kafka topics.
    
    Returns:
        List of topic names
    """
    admin = create_admin_client()
    
    # Get cluster metadata
    cluster_metadata = admin.list_topics(timeout=10)
    
    topics = []
    for topic in cluster_metadata.topics.values():
        topics.append(topic.topic)
    
    return topics


def topic_exists(topic_name: str) -> bool:
    """
    Check if a topic exists.
    
    Args:
        topic_name: Name of the topic.
    
    Returns:
        True if topic exists, False otherwise.
    """
    return topic_name in list_topics()


def ensure_topics_exist() -> None:
    """
    Ensure all AEGIS topics exist, creating any that don't.
    
    This is a convenience function for use on service startup.
    """
    print("Ensuring AEGIS Kafka topics exist...")
    
    existing = list_topics()
    topics_created = 0
    
    for topic_config in AEGIS_TOPICS:
        topic_name = topic_config["name"]
        if topic_name not in existing:
            print(f"Creating topic: {topic_name}")
            create_topics()
            topics_created += 1
        else:
            print(f"Topic already exists: {topic_name}")
    
    print(f"Topic setup complete. Created {topics_created} new topics.")


if __name__ == "__main__":
    # Can be run directly to create topics
    ensure_topics_exist()