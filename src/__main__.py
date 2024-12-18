from src.ingestion import ingest
from src.utils.configs import AppConfig

if __name__ == "__main__":
    ingest(
        config=AppConfig.from_env(),
        entity_id="28bcc163-f7d0-41e9-b602-d28500c86dea",
        form_id="innovator_introduction"
    )
