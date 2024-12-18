from typing import Optional
from openai import OpenAI, OpenAIError
from pydantic import BaseModel, Field

class LLMConfig(BaseModel):
    """Configuration for LLM client"""
    model: str = Field(default="gpt-4o", description="Model to use for completion")
    temperature: float = Field(default=0.7, description="Temperature for response generation")
    max_tokens: int = Field(default=4000, description="Maximum tokens in response")
    top_p: float = Field(default=0.9, description="Top p for response generation")

class LLMClient:
    """Client for interacting with OpenAI's LLM API"""
    
    def __init__(self, api_key: str, config: Optional[LLMConfig] = None):
        """Initialize LLM client with API key and optional configuration"""
        self._client = OpenAI(api_key=api_key)
        self._config = config or LLMConfig()
    
    def complete(self, prompt: str) -> str:
        """
        Get completion from LLM
        
        Args:
            prompt: The prompt to send to the LLM
            
        Returns:
            The LLM's response as a string
            
        Raises:
            OpenAIError: If there's an error communicating with the API
        """
        try:
            response = self._client.chat.completions.create(
                model=self._config.model,
                messages=[
                    {"role": "system", "content": prompt}
                ],
                temperature=self._config.temperature,
                max_tokens=self._config.max_tokens,
                top_p=self._config.top_p
            )
            return response.choices[0].message.content
        except OpenAIError as e:
            print(f"Error getting completion: {e}")
            raise