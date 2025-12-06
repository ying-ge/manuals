"""
GLM (BigModel GLM4.6) API Client
Implements interaction with the GLM API for LLM-based extraction.
"""
import os
import json
import re
import time
import logging
from typing import Dict, Any, Optional

import requests

logger = logging.getLogger(__name__)


class GLMClient:
    """Client for interacting with BigModel GLM API."""
    
    def __init__(
        self,
        api_key: Optional[str] = None,
        base_url: Optional[str] = None,
        model_name: Optional[str] = None,
        timeout: int = 30
    ):
        """
        Initialize GLM client.
        
        Args:
            api_key: GLM API key (defaults to GLM_API_KEY env var)
            base_url: GLM API base URL (defaults to https://open.bigmodel.cn/api/paas/v4)
            model_name: Model name (defaults to GLM_MODEL_NAME env var or 'glm-4.6')
            timeout: Request timeout in seconds
        """
        self.api_key = api_key or os.getenv('GLM_API_KEY')
        self.base_url = base_url or os.getenv('GLM_BASE_URL', 'https://open.bigmodel.cn/api/paas/v4')
        self.model_name = model_name or os.getenv('GLM_MODEL_NAME', 'glm-4.6')
        self.timeout = timeout
        
        if not self.api_key:
            raise ValueError("GLM_API_KEY must be provided or set in environment")
    
    def _make_request(
        self,
        messages: list,
        temperature: float = 0.0,
        max_retries: int = 5,
        initial_delay: float = 1.0
    ) -> Dict[str, Any]:
        """
        Make a request to the GLM API with exponential backoff retry.
        
        Args:
            messages: List of message dicts with 'role' and 'content'
            temperature: Sampling temperature (0 for deterministic)
            max_retries: Maximum number of retry attempts
            initial_delay: Initial delay in seconds before first retry
            
        Returns:
            API response as dict
            
        Raises:
            Exception: If all retries fail
        """
        url = f"{self.base_url}/chat/completions"
        headers = {
            'Authorization': f'Bearer {self.api_key}',
            'Content-Type': 'application/json'
        }
        
        payload = {
            'model': self.model_name,
            'messages': messages,
            'temperature': temperature,
            'max_tokens': 3000,  # 增加token限制以支持更详细的中文内容
        }
        
        delay = initial_delay
        last_exception = None
        
        for attempt in range(max_retries):
            try:
                logger.debug(f"GLM API request attempt {attempt + 1}/{max_retries}")
                response = requests.post(
                    url,
                    headers=headers,
                    json=payload,
                    timeout=self.timeout
                )
                
                if response.status_code == 200:
                    return response.json()
                
                # Handle rate limiting and server errors with retry
                if response.status_code in [429, 500, 502, 503, 504]:
                    logger.warning(
                        f"GLM API returned {response.status_code}, retrying after {delay}s"
                    )
                    if attempt < max_retries - 1:
                        time.sleep(delay)
                        delay = min(delay * 2, 32)  # Exponential backoff, max 32s
                        continue
                
                # For other errors, raise immediately
                response.raise_for_status()
                
            except requests.exceptions.RequestException as e:
                last_exception = e
                logger.warning(f"GLM API request failed: {e}")
                if attempt < max_retries - 1:
                    time.sleep(delay)
                    delay = min(delay * 2, 32)
                else:
                    raise Exception(f"GLM API request failed after {max_retries} attempts") from e
        
        raise Exception(f"GLM API request failed after {max_retries} attempts") from last_exception
    
    def extract_structured_info(
        self,
        abstract: str,
        system_prompt: Optional[str] = None
    ) -> Dict[str, str]:
        """
        Extract structured information from abstract using GLM.
        
        Args:
            abstract: The abstract text to analyze
            system_prompt: Optional custom system prompt
            
        Returns:
            Dictionary with extracted fields: what_done, ai_role, models, data_sources, metrics
            
        Raises:
            Exception: If extraction fails
        """
        if system_prompt is None:
            system_prompt = (
                "你是一个科学文献分析助手。请从摘要中提取以下信息，并输出严格的一个JSON对象，包含以下键：\n"
                "- what_done: 这篇论文做了什么（详细描述研究内容、研究方法、研究目标、实验设计、主要发现等，要求详细且完整，尽量包含研究的关键步骤和主要结果，字数控制在300-500字）\n"
                "- ai_role: 用AI做了什么（AI在研究中扮演的角色、具体应用场景、如何使用AI解决问题等，要求详细说明AI的具体作用和应用方式，字数控制在200-300字）\n"
                "- models: 用了哪个模型（模型名称、算法类型、架构等，用英文原名称）\n"
                "- data_sources: 数据资源（数据集来源、数据规模、数据类型等，详细描述）\n"
                "- metrics: 评估指标（可选，如果有的话）\n"
                "重要要求：\n"
                "1. what_done 和 ai_role 必须用中文回答，内容要详细和完整\n"
                "2. models 和 data_sources 可以用英文（如果是专有名词），也可以中英结合\n"
                "3. 所有内容要准确反映摘要中的信息，不要编造\n"
                "4. 如果某个字段找不到，设置为空字符串"
            )
        
        user_prompt = f'摘要：\n"""\n{abstract}\n"""\n\n请从上述摘要中提取信息，用中文详细描述研究内容和AI应用。只返回JSON对象，不要其他文字。'
        
        messages = [
            {'role': 'system', 'content': system_prompt},
            {'role': 'user', 'content': user_prompt}
        ]
        
        try:
            response = self._make_request(messages, temperature=0.0)
            
            # Extract content from response
            if 'choices' in response and len(response['choices']) > 0:
                content = response['choices'][0].get('message', {}).get('content', '')
            else:
                raise ValueError("Invalid response format from GLM API")
            
            # Try to parse JSON
            result = self._parse_json_response(content)
            
            # Validate and truncate fields
            validated_result = self._validate_extraction_result(result)
            
            return validated_result
            
        except Exception as e:
            logger.error(f"GLM extraction failed: {e}")
            raise
    
    def _parse_json_response(self, content: str) -> Dict[str, str]:
        """
        Parse JSON from response content, attempting to extract JSON block if needed.
        
        Args:
            content: Response content that should contain JSON
            
        Returns:
            Parsed JSON as dict
        """
        # Try direct parse first
        try:
            return json.loads(content.strip())
        except json.JSONDecodeError:
            pass
        
        # Try to find JSON block in markdown code fence
        json_match = re.search(r'```(?:json)?\s*(\{.*?\})\s*```', content, re.DOTALL)
        if json_match:
            try:
                return json.loads(json_match.group(1))
            except json.JSONDecodeError:
                pass
        
        # Try to find any JSON object
        json_match = re.search(r'\{[^{}]*(?:\{[^{}]*\}[^{}]*)*\}', content, re.DOTALL)
        if json_match:
            try:
                return json.loads(json_match.group(0))
            except json.JSONDecodeError:
                pass
        
        raise ValueError(f"Could not parse JSON from response: {content[:200]}")
    
    def _validate_extraction_result(self, result: Dict[str, Any]) -> Dict[str, str]:
        """
        Validate and clean extraction result.
        
        Args:
            result: Raw extraction result
            
        Returns:
            Validated result with all required fields
        """
        required_fields = ['what_done', 'ai_role', 'models', 'data_sources', 'metrics']
        validated = {}
        
        for field in required_fields:
            value = result.get(field, '')
            if not isinstance(value, str):
                value = str(value) if value is not None else ''
            # Allow longer content for what_done and ai_role (up to 2000 chars)
            if field in ['what_done', 'ai_role']:
                validated[field] = value[:2000]
            else:
                # Other fields can be shorter
                validated[field] = value[:500]
        
        return validated
