"""
LLM Extractor with GLM -> OpenAI -> Heuristic fallback logic.
"""
import os
import re
import json
import logging
from typing import Dict, Optional, Tuple

try:
    from src.glm_client import GLMClient
except ImportError:
    from glm_client import GLMClient

# Optional OpenAI import
try:
    import openai
    OPENAI_AVAILABLE = True
except ImportError:
    OPENAI_AVAILABLE = False

logger = logging.getLogger(__name__)


class LLMExtractor:
    """Extracts structured information from abstracts using LLM with fallback."""
    
    def __init__(self):
        """Initialize extractor with GLM and OpenAI clients."""
        self.glm_client = None
        self.openai_client = None
        
        # Try to initialize GLM
        if os.getenv('GLM_API_KEY'):
            try:
                self.glm_client = GLMClient()
                logger.info("GLM client initialized successfully")
            except Exception as e:
                logger.warning(f"Failed to initialize GLM client: {e}")
        
        # Try to initialize OpenAI
        if OPENAI_AVAILABLE and os.getenv('OPENAI_API_KEY'):
            try:
                self.openai_client = openai.OpenAI(api_key=os.getenv('OPENAI_API_KEY'))
                logger.info("OpenAI client initialized successfully")
            except Exception as e:
                logger.warning(f"Failed to initialize OpenAI client: {e}")
    
    def extract(self, abstract: str) -> Tuple[Dict[str, str], bool, Optional[str]]:
        """
        Extract structured information from abstract with fallback logic.
        
        Args:
            abstract: The abstract text to analyze
            
        Returns:
            Tuple of (extracted_data, needs_manual_review, raw_llm_output)
            - extracted_data: Dict with keys: what_done, ai_role, models, data_sources, metrics
            - needs_manual_review: Boolean indicating if manual review is needed
            - raw_llm_output: Raw LLM output if there was a parsing issue
        """
        # Try GLM first
        if self.glm_client:
            try:
                result = self.glm_client.extract_structured_info(abstract)
                logger.info("Successfully extracted using GLM")
                return result, False, None
            except Exception as e:
                logger.warning(f"GLM extraction failed: {e}, falling back to OpenAI")
        
        # Try OpenAI as fallback
        if self.openai_client:
            try:
                result, raw_output = self._extract_with_openai(abstract)
                if result:
                    logger.info("Successfully extracted using OpenAI")
                    return result, False, None
                else:
                    logger.warning("OpenAI extraction failed, falling back to heuristic")
            except Exception as e:
                logger.warning(f"OpenAI extraction failed: {e}, falling back to heuristic")
        
        # Final fallback to heuristic
        logger.info("Using heuristic extraction")
        result = self._heuristic_extract(abstract)
        return result, True, None
    
    def _extract_with_openai(self, abstract: str) -> Tuple[Optional[Dict[str, str]], Optional[str]]:
        """
        Extract using OpenAI ChatCompletion.
        
        Args:
            abstract: The abstract text to analyze
            
        Returns:
            Tuple of (extracted_data or None, raw_output)
        """
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
        
        try:
            response = self.openai_client.chat.completions.create(
                model="gpt-3.5-turbo",
                messages=[
                    {"role": "system", "content": system_prompt},
                    {"role": "user", "content": user_prompt}
                ],
                temperature=0.0,
                max_tokens=2000  # 增加token限制以支持更详细的中文内容
            )
            
            content = response.choices[0].message.content
            
            # Try to parse JSON
            import json
            result = self._parse_json_response(content)
            
            # Validate
            validated = self._validate_extraction_result(result)
            
            return validated, content
            
        except Exception as e:
            logger.error(f"OpenAI extraction error: {e}")
            return None, None
    
    def _parse_json_response(self, content: str) -> Dict[str, str]:
        """Parse JSON from response content."""
        # Try direct parse
        try:
            return json.loads(content.strip())
        except json.JSONDecodeError:
            pass
        
        # Try to find JSON block
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
        
        raise ValueError(f"Could not parse JSON from response")
    
    def _validate_extraction_result(self, result: Dict) -> Dict[str, str]:
        """Validate and clean extraction result."""
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
    
    def _heuristic_extract(self, abstract: str) -> Dict[str, str]:
        """
        Heuristic extraction based on keywords and patterns.
        
        Args:
            abstract: The abstract text to analyze
            
        Returns:
            Dictionary with extracted fields (may have empty strings)
        """
        abstract_lower = abstract.lower()
        
        # Extract what_done - look for objective/purpose/study sentences
        what_done = self._extract_what_done(abstract)
        
        # Extract ai_role - look for AI/ML related sentences
        ai_role = self._extract_ai_role(abstract)
        
        # Extract models - look for model names
        models = self._extract_models(abstract)
        
        # Extract data sources
        data_sources = self._extract_data_sources(abstract)
        
        # Extract metrics
        metrics = self._extract_metrics(abstract)
        
        return {
            'what_done': what_done[:2000],  # 允许更长的内容
            'ai_role': ai_role[:2000],      # 允许更长的内容
            'models': models[:500],
            'data_sources': data_sources[:500],
            'metrics': metrics[:500]
        }
    
    def _extract_what_done(self, abstract: str) -> str:
        """Extract what was done from abstract."""
        # Look for sentences with key phrases
        patterns = [
            r'(?:we|this study|this work|the study)\s+([^.!?]+(?:investigated|analyzed|evaluated|examined|studied|assessed|compared|proposed|designed|implemented)[^.!?]+)',
            r'(?:objective|aim|purpose|goal)[^.!?]*?:\s*([^.!?]+)',
            r'(?:background|introduction)[^.!?]*?:\s*([^.!?]+)',
        ]
        
        for pattern in patterns:
            match = re.search(pattern, abstract, re.IGNORECASE)
            if match:
                return match.group(1).strip()
        
        # Fallback: return first sentence
        sentences = re.split(r'[.!?]+', abstract)
        if sentences:
            return sentences[0].strip()
        
        return ""
    
    def _extract_ai_role(self, abstract: str) -> str:
        """Extract AI role from abstract."""
        ai_keywords = [
            'artificial intelligence', 'machine learning', 'deep learning',
            'neural network', 'ai', 'ml', 'algorithm', 'model', 'prediction',
            'classification', 'detection', 'diagnosis', 'automated'
        ]
        
        sentences = re.split(r'[.!?]+', abstract)
        for sentence in sentences:
            sentence_lower = sentence.lower()
            if any(keyword in sentence_lower for keyword in ai_keywords):
                return sentence.strip()
        
        return ""
    
    def _extract_models(self, abstract: str) -> str:
        """Extract model names from abstract."""
        model_patterns = [
            r'\b(?:CNN|RNN|LSTM|GRU|BERT|GPT|ResNet|VGG|AlexNet|Inception|MobileNet|EfficientNet)\b',
            r'\b(?:random forest|decision tree|support vector machine|SVM|logistic regression|linear regression)\b',
            r'\b(?:gradient boosting|XGBoost|LightGBM|CatBoost)\b',
            r'\b(?:k-means|clustering|PCA)\b',
        ]
        
        models = []
        for pattern in model_patterns:
            matches = re.findall(pattern, abstract, re.IGNORECASE)
            models.extend(matches)
        
        if models:
            return ', '.join(set(models))
        return ""
    
    def _extract_data_sources(self, abstract: str) -> str:
        """Extract data sources from abstract."""
        # Look for dataset mentions
        patterns = [
            r'(?:dataset|data set|database|cohort|registry)[^.!?]*?(?:of|from|with)\s+([^.!?]{10,80})',
            r'(?:using|from)\s+(?:the\s+)?([A-Z][A-Za-z\s]+(?:dataset|database|registry|cohort))',
        ]
        
        for pattern in patterns:
            match = re.search(pattern, abstract, re.IGNORECASE)
            if match:
                return match.group(1).strip()
        
        return ""
    
    def _extract_metrics(self, abstract: str) -> str:
        """Extract evaluation metrics from abstract."""
        metric_keywords = [
            'accuracy', 'precision', 'recall', 'F1', 'AUC', 'ROC',
            'sensitivity', 'specificity', 'AUROC', 'RMSE', 'MAE',
            'R-squared', 'confusion matrix', 'performance'
        ]
        
        metrics = []
        abstract_lower = abstract.lower()
        for keyword in metric_keywords:
            if keyword.lower() in abstract_lower:
                metrics.append(keyword)
        
        if metrics:
            return ', '.join(metrics[:5])  # Limit to 5 metrics
        
        return ""
