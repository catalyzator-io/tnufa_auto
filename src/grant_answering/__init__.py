from src.utils.configs import AppConfig
from src.utils.models import GrantResponse
from src.grant_answering.grant_answering import GrantAnswering
from src.grant_answering.container import Container as GrantAnsweringContainer

def process_grant(
    config: AppConfig,
    entity_id: str,
) -> GrantResponse:
    """Convenience function for processing a grant application
    
    Args:
        config: Application configuration
        entity_id: ID of the entity to answer about
        grant: Grant application to process
    Returns:
        Generated responses to grant questions
    """
    container = GrantAnsweringContainer(config)
    pipeline = container.create_grant_answering()
    return pipeline.process_grant_application(
        entity_id,
        config.grant_value
    )

__all__ = ["process_grant", "GrantAnswering", "GrantAnsweringContainer"]
