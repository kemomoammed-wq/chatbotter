# llm_integration.py: Advanced LLM Integration (OpenAI, HuggingFace, Local Models)
import os
import logging
import json
from typing import Dict, List, Optional, Any, Iterator
from dataclasses import dataclass
import requests
from openai import OpenAI
import time

logger = logging.getLogger(__name__)

@dataclass
class LLMConfig:
    """Configuration for LLM models"""
    provider: str  # 'openai', 'huggingface', 'local', 'ollama'
    model_name: str
    api_key: Optional[str] = None
    base_url: Optional[str] = None
    temperature: float = 0.7
    max_tokens: int = 1000
    top_p: float = 0.9
    frequency_penalty: float = 0.1
    presence_penalty: float = 0.1

class LLMProvider:
    """Base class for LLM providers"""
    
    def __init__(self, config: LLMConfig):
        self.config = config
        self.client = None
        
    def generate(self, messages: List[Dict], stream: bool = False) -> Any:
        """Generate response from messages"""
        raise NotImplementedError
        
    def stream_generate(self, messages: List[Dict]) -> Iterator[str]:
        """Stream response tokens"""
        raise NotImplementedError

class OpenAIProvider(LLMProvider):
    """OpenAI API Provider (GPT-3.5, GPT-4, etc.)"""
    
    def __init__(self, config: LLMConfig):
        super().__init__(config)
        api_key = config.api_key or os.getenv('OPENAI_API_KEY', '')
        if not api_key:
            logger.warning("OpenAI API key not found. Using default.")
            api_key = "sk-placeholder"
        
        self.client = OpenAI(
            api_key=api_key,
            base_url=config.base_url or "https://api.openai.com/v1"
        )
    
    def generate(self, messages: List[Dict], stream: bool = False) -> Dict[str, Any]:
        """Generate response using OpenAI API"""
        try:
            response = self.client.chat.completions.create(
                model=self.config.model_name,
                messages=messages,
                temperature=self.config.temperature,
                max_tokens=self.config.max_tokens,
                top_p=self.config.top_p,
                frequency_penalty=self.config.frequency_penalty,
                presence_penalty=self.config.presence_penalty,
                stream=stream
            )
            
            if stream:
                return response  # Return stream object
            else:
                return {
                    'content': response.choices[0].message.content,
                    'usage': {
                        'prompt_tokens': response.usage.prompt_tokens,
                        'completion_tokens': response.usage.completion_tokens,
                        'total_tokens': response.usage.total_tokens
                    },
                    'model': response.model,
                    'finish_reason': response.choices[0].finish_reason
                }
        except Exception as e:
            logger.error(f"OpenAI API error: {e}")
            return {'content': 'Sorry, I encountered an error. Please try again.', 'error': str(e)}
    
    def stream_generate(self, messages: List[Dict]) -> Iterator[str]:
        """Stream response tokens"""
        try:
            stream = self.client.chat.completions.create(
                model=self.config.model_name,
                messages=messages,
                temperature=self.config.temperature,
                max_tokens=self.config.max_tokens,
                stream=True
            )
            
            for chunk in stream:
                if chunk.choices[0].delta.content is not None:
                    yield chunk.choices[0].delta.content
        except Exception as e:
            logger.error(f"OpenAI streaming error: {e}")
            yield f"Error: {str(e)}"

class HuggingFaceProvider(LLMProvider):
    """HuggingFace API Provider"""
    
    def __init__(self, config: LLMConfig):
        super().__init__(config)
        self.api_key = config.api_key or os.getenv('HUGGINGFACE_API_KEY', '')
        self.api_url = f"https://api-inference.huggingface.co/models/{config.model_name}"
        
    def generate(self, messages: List[Dict], stream: bool = False) -> Dict[str, Any]:
        """Generate response using HuggingFace API"""
        try:
            # Combine messages into prompt
            prompt = self._format_messages(messages)
            
            headers = {"Authorization": f"Bearer {self.api_key}"} if self.api_key else {}
            payload = {
                "inputs": prompt,
                "parameters": {
                    "temperature": self.config.temperature,
                    "max_new_tokens": self.config.max_tokens,
                    "top_p": self.config.top_p,
                    "return_full_text": False
                }
            }
            
            response = requests.post(self.api_url, headers=headers, json=payload, timeout=30)
            response.raise_for_status()
            result = response.json()
            
            # Extract generated text
            if isinstance(result, list) and len(result) > 0:
                generated_text = result[0].get('generated_text', '')
            elif isinstance(result, dict):
                generated_text = result.get('generated_text', '')
            else:
                generated_text = str(result)
            
            return {
                'content': generated_text.strip(),
                'model': self.config.model_name,
                'provider': 'huggingface'
            }
        except Exception as e:
            logger.error(f"HuggingFace API error: {e}")
            return {'content': 'Sorry, I encountered an error. Please try again.', 'error': str(e)}
    
    def _format_messages(self, messages: List[Dict]) -> str:
        """Format messages for HuggingFace models"""
        formatted = []
        for msg in messages:
            role = msg.get('role', 'user')
            content = msg.get('content', '')
            if role == 'system':
                formatted.append(f"System: {content}")
            elif role == 'user':
                formatted.append(f"Human: {content}")
            elif role == 'assistant':
                formatted.append(f"Assistant: {content}")
        return "\n".join(formatted)
    
    def stream_generate(self, messages: List[Dict]) -> Iterator[str]:
        """Stream response tokens (not fully supported by HF API)"""
        result = self.generate(messages)
        # Simulate streaming by yielding chunks
        content = result.get('content', '')
        words = content.split(' ')
        for word in words:
            yield word + ' '
            time.sleep(0.05)  # Small delay for streaming effect

class OllamaProvider(LLMProvider):
    """Ollama Local Models Provider"""
    
    def __init__(self, config: LLMConfig):
        super().__init__(config)
        self.base_url = config.base_url or "http://localhost:11434"
        
    def generate(self, messages: List[Dict], stream: bool = False) -> Dict[str, Any]:
        """Generate response using Ollama"""
        try:
            prompt = self._format_messages(messages)
            
            payload = {
                "model": self.config.model_name,
                "prompt": prompt,
                "stream": stream,
                "options": {
                    "temperature": self.config.temperature,
                    "num_predict": self.config.max_tokens
                }
            }
            
            response = requests.post(
                f"{self.base_url}/api/generate",
                json=payload,
                timeout=60,
                stream=stream
            )
            response.raise_for_status()
            
            if stream:
                return response  # Return stream
            else:
                result = response.json()
                return {
                    'content': result.get('response', ''),
                    'model': self.config.model_name,
                    'provider': 'ollama'
                }
        except Exception as e:
            logger.error(f"Ollama error: {e}")
            return {'content': 'Sorry, I encountered an error. Please try again.', 'error': str(e)}
    
    def _format_messages(self, messages: List[Dict]) -> str:
        """Format messages for Ollama"""
        formatted = []
        for msg in messages:
            role = msg.get('role', 'user')
            content = msg.get('content', '')
            formatted.append(f"{role.capitalize()}: {content}")
        return "\n".join(formatted)
    
    def stream_generate(self, messages: List[Dict]) -> Iterator[str]:
        """Stream response tokens from Ollama"""
        try:
            prompt = self._format_messages(messages)
            payload = {
                "model": self.config.model_name,
                "prompt": prompt,
                "stream": True,
                "options": {
                    "temperature": self.config.temperature
                }
            }
            
            response = requests.post(
                f"{self.base_url}/api/generate",
                json=payload,
                stream=True,
                timeout=60
            )
            
            for line in response.iter_lines():
                if line:
                    data = json.loads(line)
                    if 'response' in data:
                        yield data['response']
        except Exception as e:
            logger.error(f"Ollama streaming error: {e}")
            yield f"Error: {str(e)}"

class LLMManager:
    """Manager for multiple LLM providers"""
    
    def __init__(self):
        self.providers = {}
        self.default_provider = None
        self._load_configs()
    
    def _load_configs(self):
        """Load LLM configurations"""
        # OpenAI configuration
        openai_config = LLMConfig(
            provider='openai',
            model_name=os.getenv('OPENAI_MODEL', 'gpt-3.5-turbo'),
            api_key=os.getenv('OPENAI_API_KEY', ''),
            temperature=0.7,
            max_tokens=1000
        )
        
        # HuggingFace configuration
        hf_config = LLMConfig(
            provider='huggingface',
            model_name=os.getenv('HF_MODEL', 'mistralai/Mistral-7B-Instruct-v0.2'),
            api_key=os.getenv('HUGGINGFACE_API_KEY', ''),
            temperature=0.7,
            max_tokens=1000
        )
        
        # Ollama configuration
        ollama_config = LLMConfig(
            provider='ollama',
            model_name=os.getenv('OLLAMA_MODEL', 'llama2'),
            base_url=os.getenv('OLLAMA_BASE_URL', 'http://localhost:11434'),
            temperature=0.7,
            max_tokens=1000
        )
        
        # Initialize providers
        try:
            self.providers['openai'] = OpenAIProvider(openai_config)
            self.default_provider = 'openai'
        except Exception as e:
            logger.warning(f"Could not initialize OpenAI: {e}")
        
        try:
            self.providers['huggingface'] = HuggingFaceProvider(hf_config)
            if not self.default_provider:
                self.default_provider = 'huggingface'
        except Exception as e:
            logger.warning(f"Could not initialize HuggingFace: {e}")
        
        try:
            self.providers['ollama'] = OllamaProvider(ollama_config)
            if not self.default_provider:
                self.default_provider = 'ollama'
        except Exception as e:
            logger.warning(f"Could not initialize Ollama: {e}")
        
        # Fallback to first available provider
        if not self.default_provider and self.providers:
            self.default_provider = list(self.providers.keys())[0]
    
    def get_provider(self, provider_name: Optional[str] = None) -> Optional[LLMProvider]:
        """Get LLM provider by name"""
        name = provider_name or self.default_provider
        return self.providers.get(name)
    
    def generate(self, messages: List[Dict], provider_name: Optional[str] = None, stream: bool = False) -> Dict[str, Any]:
        """Generate response using specified provider"""
        provider = self.get_provider(provider_name)
        if not provider:
            return {'content': 'No LLM provider available. Please configure your API keys.', 'error': 'No provider'}
        
        return provider.generate(messages, stream=stream)
    
    def stream_generate(self, messages: List[Dict], provider_name: Optional[str] = None) -> Iterator[str]:
        """Stream response tokens"""
        provider = self.get_provider(provider_name)
        if not provider:
            yield 'No LLM provider available.'
            return
        
        yield from provider.stream_generate(messages)

# Global instance
_llm_manager = None

def get_llm_manager() -> LLMManager:
    """Get global LLM manager instance"""
    global _llm_manager
    if _llm_manager is None:
        _llm_manager = LLMManager()
    return _llm_manager

