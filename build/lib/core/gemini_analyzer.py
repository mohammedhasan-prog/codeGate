import google.generativeai as genai
import json
from .preprocessor import CodePreprocessor
from ..utils.config import config_manager
from ..utils.cache import cache

SECURITY_ANALYSIS_PROMPT = """
You are a security expert analyzing Python code for vulnerabilities. Analyze the provided code and return a structured JSON response.

VULNERABILITY CATEGORIES TO DETECT:
1. **Command Injection** (os.system, subprocess with shell=True, eval, exec)
2. **Path Traversal** (file operations with user input, ../patterns)
3. **SQL Injection** (raw SQL string construction)
4. **Deserialization** (pickle.loads, yaml.load without safe_load)
5. **Cryptographic Issues** (weak algorithms, hardcoded keys, bad randomness)
6. **Information Disclosure** (sensitive data in logs/errors, debug info)
7. **Resource Exhaustion** (infinite loops, fork bombs, unbounded allocations)
8. **Network Security** (unvalidated URLs, insecure connections)
9. **Input Validation** (missing sanitization, buffer overflows)
10. **Dependency Issues** (analyze import statements for known vulnerable packages)

ANALYSIS INSTRUCTIONS:
- Examine each line of code carefully
- Consider data flow and user input paths
- Flag suspicious patterns and functions
- Provide specific line numbers
- Give actionable remediation advice
- Rate severity based on exploitability and impact

RESPONSE FORMAT (JSON only, no markdown):
{
  "analysis_summary": "Brief overview of findings",
  "risk_score": 0-100,
  "vulnerabilities": [
    {
      "type": "command_injection|path_traversal|sql_injection|deserialization|crypto_weakness|info_disclosure|resource_exhaustion|network_security|input_validation|dependency_issue",
      "severity": "critical|high|medium|low",
      "line_number": 123,
      "code_snippet": "vulnerable code here",
      "description": "Detailed explanation of the vulnerability",
      "impact": "What could happen if exploited",
      "remediation": "Specific steps to fix the issue",
      "cwe_id": "CWE-XXX if applicable"
    }
  ],
  "dependencies_analysis": {
    "detected_imports": ["package1", "package2"],
    "security_notes": "Comments about package security"
  },
  "code_quality_notes": "Additional security-related observations"
}

CODE TO ANALYZE:
{code}
"""

class GeminiSecurityAnalyzer:
    def __init__(self):
        self.api_key = config_manager.get("gemini.api_key")
        if not self.api_key:
            raise ValueError("Gemini API key not found. Please set it in ~/.codegate/config.yaml or as an environment variable.")
        genai.configure(api_key=self.api_key)
        self.model = genai.GenerativeModel(config_manager.get("gemini.model"))

    async def analyze(self, code: str):
        cached_result = cache.get(code)
        if cached_result:
            return cached_result

        prompt = SECURITY_ANALYSIS_PROMPT.format(code=code)
        
        try:
            response = await self.model.generate_content_async(
                prompt,
                generation_config=genai.types.GenerationConfig(
                    temperature=config_manager.get("gemini.temperature"),
                    max_output_tokens=config_manager.get("gemini.max_tokens"),
                    response_mime_type="application/json"
                )
            )
            
            # Clean the response text to ensure it's valid JSON
            cleaned_response_text = response.text.strip()
            if cleaned_response_text.startswith("```json"):
                cleaned_response_text = cleaned_response_text[7:]
            if cleaned_response_text.endswith("```"):
                cleaned_response_text = cleaned_response_text[:-3]
            
            result = json.loads(cleaned_response_text)
            cache.set(code, result)
            return result
        except Exception as e:
            # Handle API errors, rate limiting, etc.
            # For now, just re-raising
            raise e
