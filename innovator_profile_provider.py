from typing import Dict
from models import GrantQuestion

class InnovatorProfileProvider:
    """Provides relevant innovator profile information for a given question."""
    
    def __init__(self, profile_data: Dict[str, str]):
        """
        Initialize with a dictionary of profile data.
        
        Args:
            profile_data: A dictionary containing various aspects of the innovator's profile.
        """
        self._profile_data = profile_data
    
    def get_profile_info(self, question: GrantQuestion) -> str:
        """
        Get relevant profile information for the given question.
        
        Args:
            question: The grant question for which to provide profile information.
            
        Returns:
            A string containing the relevant profile information.
        """
        # Example logic: Customize this based on your needs
        if question.category == "Innovation":
            return self._profile_data.get("innovation_experience", "No specific innovation experience provided.")
        elif question.category == "Business":
            return self._profile_data.get("business_acumen", "No specific business acumen provided.")
        else:
            return self._profile_data.get("general_background", "No specific background information provided.") 