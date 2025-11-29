"""
LLM API Provider - Support for OpenAI, Anthropic, and other API services
"""
import os
from typing import Optional
from app.core.config import settings
import logging

logger = logging.getLogger(__name__)

# Try to import API clients
try:
    import openai
    OPENAI_AVAILABLE = True
except ImportError:
    OPENAI_AVAILABLE = False
    openai = None

try:
    import anthropic
    ANTHROPIC_AVAILABLE = True
except ImportError:
    ANTHROPIC_AVAILABLE = False
    anthropic = None

try:
    from groq import Groq
    GROQ_AVAILABLE = True
except ImportError:
    GROQ_AVAILABLE = False
    Groq = None

try:
    import requests
    REQUESTS_AVAILABLE = True
except ImportError:
    REQUESTS_AVAILABLE = False
    requests = None


class LLMAPIClient:
    """LLM client using external API services (OpenAI, Anthropic, etc.)"""
    
    def __init__(self, provider: str = None, api_key: str = None, model: str = None):
        """
        Initialize API client
        
        Args:
            provider: API provider ('openai', 'anthropic', etc.)
            api_key: API key (or from env)
            model: Model name to use
        """
        self.provider = (provider or settings.LLM_API_PROVIDER or "").strip()
        self.api_key = (api_key or settings.LLM_API_KEY or "").strip()
        self.model = model or settings.LLM_API_MODEL
        
        if not self.provider:
            raise ValueError("LLM_API_PROVIDER must be set in config (e.g., 'openai' or 'anthropic')")
        if not self.api_key:
            raise ValueError("LLM_API_KEY must be set in config")
        
        self._client = None
        self._initialize_client()
    
    def _initialize_client(self):
        """Initialize the API client based on provider"""
        if self.provider.lower() == 'openai':
            if not OPENAI_AVAILABLE:
                raise ImportError("openai package not installed. Run: pip install openai")
            self._client = openai.OpenAI(api_key=self.api_key)
            logger.info(f"Initialized OpenAI client with model: {self.model}")
        
        elif self.provider.lower() == 'anthropic':
            if not ANTHROPIC_AVAILABLE:
                raise ImportError("anthropic package not installed. Run: pip install anthropic")
            self._client = anthropic.Anthropic(api_key=self.api_key)
            logger.info(f"Initialized Anthropic client with model: {self.model}")
        
        elif self.provider.lower() == 'groq':
            if not GROQ_AVAILABLE:
                raise ImportError("groq package not installed. Run: pip install groq")
            self._client = Groq(api_key=self.api_key)
            logger.info(f"Initialized Groq client with model: {self.model}")
        
        elif self.provider.lower() == 'huggingface' or self.provider.lower() == 'hf':
            if not REQUESTS_AVAILABLE:
                raise ImportError("requests package not installed. Run: pip install requests")
            # Hugging Face Inference API
            self._client = None  # We'll use requests directly
            logger.info(f"Initialized Hugging Face Inference API with model: {self.model}")
        
        else:
            raise ValueError(f"Unsupported provider: {self.provider}. Supported: 'openai', 'anthropic', 'groq', 'huggingface'")
    
    def generate_text(
        self,
        system_message: str,
        user_message: str,
        max_tokens: int = None,
        temperature: float = None,
        top_p: float = None
    ) -> str:
        """
        Generate text using API
        
        Args:
            system_message: System prompt
            user_message: User message
            max_tokens: Max tokens to generate
            temperature: Sampling temperature
            top_p: Nucleus sampling threshold
            
        Returns:
            Generated text
        """
        max_tokens = max_tokens or settings.MAX_NEW_TOKENS
        temperature = temperature if temperature is not None else settings.TEMPERATURE
        top_p = top_p if top_p is not None else settings.TOP_P
        
        try:
            if self.provider.lower() == 'openai':
                response = self._client.chat.completions.create(
                    model=self.model,
                    messages=[
                        {"role": "system", "content": system_message},
                        {"role": "user", "content": user_message}
                    ],
                    max_tokens=max_tokens,
                    temperature=temperature,
                    top_p=top_p
                )
                return response.choices[0].message.content.strip()
            
            elif self.provider.lower() == 'anthropic':
                response = self._client.messages.create(
                    model=self.model,
                    max_tokens=max_tokens,
                    temperature=temperature,
                    top_p=top_p,
                    system=system_message,
                    messages=[
                        {"role": "user", "content": user_message}
                    ]
                )
                return response.content[0].text.strip()
            
            elif self.provider.lower() == 'groq':
                # Groq uses OpenAI-compatible API
                response = self._client.chat.completions.create(
                    model=self.model,
                    messages=[
                        {"role": "system", "content": system_message},
                        {"role": "user", "content": user_message}
                    ],
                    max_tokens=max_tokens,
                    temperature=temperature,
                    top_p=top_p
                )
                return response.choices[0].message.content.strip()
            
            elif self.provider.lower() in ['huggingface', 'hf']:
                # Hugging Face Inference API
                api_url = f"https://api-inference.huggingface.co/models/{self.model}"
                headers = {}
                if self.api_key:
                    headers["Authorization"] = f"Bearer {self.api_key}"
                
                payload = {
                    "inputs": f"<|system|>\n{system_message}\n<|user|>\n{user_message}\n<|assistant|>\n",
                    "parameters": {
                        "max_new_tokens": max_tokens,
                        "temperature": temperature,
                        "top_p": top_p,
                        "return_full_text": False
                    }
                }
                
                response = requests.post(api_url, headers=headers, json=payload, timeout=30)
                response.raise_for_status()
                result = response.json()
                
                # Handle different response formats
                if isinstance(result, list) and len(result) > 0:
                    return result[0].get('generated_text', '').strip()
                elif isinstance(result, dict):
                    return result.get('generated_text', '').strip()
                else:
                    return str(result).strip()
        
        except Exception as e:
            logger.error(f"API generation failed: {e}")
            raise


# Global API client instance
_api_client_instance = None


def get_api_client() -> Optional[LLMAPIClient]:
    """Get global API client instance if configured"""
    global _api_client_instance
    
    # Check if API is configured
    provider = (settings.LLM_API_PROVIDER or "").strip()
    api_key = (settings.LLM_API_KEY or "").strip()
    
    if not provider or not api_key:
        return None  # API not configured, use local models
    
    if _api_client_instance is None:
        try:
            _api_client_instance = LLMAPIClient()
        except (ValueError, ImportError) as e:
            logger.warning(f"API client not available: {e}")
            return None
    return _api_client_instance

