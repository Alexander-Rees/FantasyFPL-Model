"""
LLM Model - Llama 3.1 8B with MLX (optimized for M1 Max) or PyTorch (Docker)
"""

try:
    import os
    from mlx_lm import load, generate
    import mlx.core as mx
    MLX_AVAILABLE = True
except ImportError:
    load = None
    generate = None
    mx = None
    MLX_AVAILABLE = False

# PyTorch fallback for Docker
try:
    from transformers import AutoModelForCausalLM, AutoTokenizer
    import torch
    TORCH_AVAILABLE = True
except ImportError:
    AutoModelForCausalLM = None
    AutoTokenizer = None
    torch = None
    TORCH_AVAILABLE = False

# llama-cpp-python fallback
try:
    from llama_cpp import Llama
    LLAMA_CPP_AVAILABLE = True
except ImportError as e:
    print(f"DEBUG: llama_cpp import failed: {e}")
    Llama = None
    LLAMA_CPP_AVAILABLE = False

from app.core.config import settings
from app.models.llm_api import get_api_client
import logging

logger = logging.getLogger(__name__)


class LLMModel:
    """Llama 3.1 8B Instruct using MLX for Apple Silicon"""
    
    def __init__(self, model_name: str = None):
        """
        Initialize LLM model with MLX
        
        Args:
            model_name: Model identifier (default from settings)
        """
        self.model_name = model_name or settings.LLM_MODEL_NAME
        self.model = None
        self.tokenizer = None
        self._loaded = False
    
    def load_model(self):
        """Load model and tokenizer (lazy loading)"""
        if self._loaded:
            return
        
        # Check if API is configured - if so, skip local model loading
        api_client = get_api_client()
        if api_client:
            logger.info(f"API client configured ({settings.LLM_API_PROVIDER}). Skipping local model load.")
            self._loaded = True
            self.use_api = True
            return
        
        # Try llama-cpp-python (GGUF)
        if LLAMA_CPP_AVAILABLE and os.path.exists(settings.LLM_MODEL_PATH):
            logger.info(f"Loading GGUF model from {settings.LLM_MODEL_PATH}...")
            try:
                # n_gpu_layers=-1 means use all available layers on GPU (Metal)
                # n_ctx=4096 or 8192 for Llama 3.1
                self.model = Llama(
                    model_path=settings.LLM_MODEL_PATH,
                    n_gpu_layers=-1, 
                    n_ctx=8192,
                    verbose=True
                )
                self._loaded = True
                self.use_llama_cpp = True
                logger.info("✅ Model loaded successfully with llama-cpp-python")
                return
            except Exception as e:
                logger.error(f"llama-cpp load failed: {e}")

        # Try MLX first (Apple Silicon), fallback to PyTorch (Docker)
        if MLX_AVAILABLE:
            logger.info(f"Loading {self.model_name} with MLX (Apple Silicon)...")
            logger.info("This may take a few minutes on first run (downloading ~4.5GB)")
            try:
                self.model, self.tokenizer = load(self.model_name)
                self._loaded = True
                self.use_mlx = True
                logger.info("✅ Model loaded successfully with MLX")
                return
            except Exception as e:
                logger.warning(f"MLX load failed: {e}, trying PyTorch fallback...")
        
        # PyTorch fallback for Docker/Standard Env
        if TORCH_AVAILABLE:
            # Use configured HF model (default: Qwen/Qwen2.5-1.5B-Instruct)
            hf_model = settings.LLM_HF_MODEL_NAME
            logger.info(f"Loading {hf_model} with PyTorch...")
            try:
                self.tokenizer = AutoTokenizer.from_pretrained(hf_model)
                if self.tokenizer.pad_token is None:
                    self.tokenizer.pad_token = self.tokenizer.eos_token
                    
                self.model = AutoModelForCausalLM.from_pretrained(
                    hf_model,
                    torch_dtype=torch.float16 if torch.cuda.is_available() else torch.float32,
                    device_map="auto" if torch.cuda.is_available() else None,
                    trust_remote_code=True
                )
                if not torch.cuda.is_available():
                    self.model = self.model.to("cpu")
                self._loaded = True
                self.use_mlx = False
                logger.info("✅ Model loaded successfully with PyTorch")
                return
            except Exception as e:
                logger.error(f"PyTorch load failed: {e}")
                logger.warning("LLM generation will be disabled. Retrieval-only mode available.")
        
        logger.warning("Neither MLX nor PyTorch available. LLM will return placeholder responses.")
        self._loaded = True
        self.use_mlx = False
    
    def generate_text(
        self,
        prompt: str,
        max_tokens: int = None,
        temperature: float = None,
        top_p: float = None,
        verbose: bool = False,
        system_message: str = None,
        user_message: str = None
    ) -> str:
        """
        Generate text from prompt using MLX, PyTorch, or API
        
        Args:
            prompt: Input prompt (legacy format, used if system/user not provided)
            max_tokens: Maximum tokens to generate (default from settings)
            temperature: Sampling temperature (default from settings)
            top_p: Nucleus sampling threshold (default from settings)
            verbose: Print generation progress
            system_message: System prompt (for API calls)
            user_message: User message (for API calls)
            
        Returns:
            Generated text (without prompt)
        """
        # Use settings defaults if not specified
        max_tokens = max_tokens or settings.MAX_NEW_TOKENS
        temperature = temperature if temperature is not None else settings.TEMPERATURE
        top_p = top_p if top_p is not None else settings.TOP_P

        # Try API first if configured
        api_client = get_api_client()
        if api_client:
            try:
                # Use system/user messages if provided, otherwise parse prompt
                if system_message and user_message:
                    response = api_client.generate_text(
                        system_message=system_message,
                        user_message=user_message,
                        max_tokens=max_tokens,
                        temperature=temperature,
                        top_p=top_p
                    )
                    return response
                else:
                    # Fallback: try to extract from prompt format
                    if "<|start_header_id|>system" in prompt:
                        # Llama format - extract system and user
                        parts = prompt.split("<|start_header_id|>user<|end_header_id|>")
                        if len(parts) == 2:
                            system_part = parts[0].split("<|start_header_id|>system<|end_header_id|>")
                            if len(system_part) == 2:
                                system_msg = system_part[1].split("<|eot_id|>")[0].strip()
                                user_msg = parts[1].split("<|eot_id|>")[0].strip()
                                response = api_client.generate_text(
                                    system_message=system_msg,
                                    user_message=user_msg,
                                    max_tokens=max_tokens,
                                    temperature=temperature,
                                    top_p=top_p
                                )
                                return response
                    # If we can't parse, use prompt as user message
                    response = api_client.generate_text(
                        system_message="You are a helpful assistant.",
                        user_message=prompt,
                        max_tokens=max_tokens,
                        temperature=temperature,
                        top_p=top_p
                    )
                    return response
            except Exception as e:
                logger.warning(f"API generation failed: {e}. Falling back to local model.")
        
        # Fallback to local models
        # Ensure model is loaded (or fallback)
        if not self._loaded:
            self.load_model()

        try:
            if hasattr(self, 'use_llama_cpp') and self.use_llama_cpp:
                # llama-cpp-python generation
                messages = []
                if system_message:
                    messages.append({"role": "system", "content": system_message})
                if user_message:
                    messages.append({"role": "user", "content": user_message})
                else:
                    # Fallback if only prompt provided
                    messages.append({"role": "user", "content": prompt})
                
                response = self.model.create_chat_completion(
                    messages=messages,
                    max_tokens=max_tokens,
                    temperature=temperature,
                    top_p=top_p
                )
                return response['choices'][0]['message']['content'].strip()

            if hasattr(self, 'use_mlx') and self.use_mlx and MLX_AVAILABLE:
                # MLX generation (Apple Silicon)
                response = generate(
                    self.model,
                    self.tokenizer,
                    prompt=prompt,
                    max_tokens=max_tokens,
                    temp=temperature,
                    top_p=top_p,
                    verbose=verbose,
                )
            elif hasattr(self, 'use_mlx') and not self.use_mlx and TORCH_AVAILABLE and self.model is not None:
                # PyTorch generation (Docker/Standard Env)
                device = next(self.model.parameters()).device
                
                # Build prompt from system/user messages if prompt is empty
                if not prompt and (system_message or user_message):
                    prompt = self.format_prompt(
                        system_message or "You are a helpful assistant.",
                        user_message or ""
                    )
                
                inputs = self.tokenizer(prompt, return_tensors="pt").to(device)
                
                if inputs.input_ids.nelement() == 0:
                    logger.warning("Empty input for generation")
                    return ""
                
                with torch.no_grad():
                    outputs = self.model.generate(
                        inputs.input_ids,
                        attention_mask=inputs.attention_mask,
                        max_new_tokens=max_tokens,
                        temperature=temperature,
                        top_p=top_p,
                        do_sample=True,
                        pad_token_id=self.tokenizer.eos_token_id
                    )
                response = self.tokenizer.decode(outputs[0], skip_special_tokens=True)
            else:
                # Fallback placeholder
                logger.warning("LLM generation unavailable; returning placeholder response.")
                return "[Placeholder answer: LLM model not available. Please configure an API service (OpenAI/Anthropic) or ensure MLX (Apple Silicon) or PyTorch is installed.]"
            
            # Strip prompt if present
            if response.startswith(prompt):
                response = response[len(prompt):].strip()
            return response
        except Exception as e:
            logger.error(f"Generation failed: {e}")
            raise
    
    def format_prompt(self, system_message: str, user_message: str) -> str:
        """
        Format prompt for Llama 3.1 Instruct
        
        Args:
            system_message: System instruction
            user_message: User query
            
        Returns:
            Formatted prompt string
        """
        # Llama 3.1 Instruct format
        prompt = f"""<|begin_of_text|><|start_header_id|>system<|end_header_id|>

{system_message}<|eot_id|><|start_header_id|>user<|end_header_id|>

{user_message}<|eot_id|><|start_header_id|>assistant<|end_header_id|>

"""
        return prompt
    
    def __del__(self):
        """Cleanup on deletion"""
        if self._loaded:
            logger.info("Unloading LLM model")


# Global model instance (singleton)
_llm_instance = None


def get_llm() -> LLMModel:
    """Get global LLM instance (singleton pattern)"""
    global _llm_instance
    if _llm_instance is None:
        _llm_instance = LLMModel()
    return _llm_instance
