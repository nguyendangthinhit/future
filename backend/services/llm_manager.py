import os
import json
import requests
import google.generativeai as genai

class LLMResponse:
    def __init__(self, text):
        self.text = text

class LLMManager:
    def __init__(self):
        self.gemini_keys = []
        self.current_gemini_index = 0
        self.provider = os.getenv("LLM_PROVIDER", "gemini").lower()
        self.fpt_api_key = os.getenv("FPT_API_KEY", "")
        self.fpt_model_name = os.getenv("FPT_MODEL_NAME", "GLM-4.7")
        self._load_gemini_keys()

    def _load_gemini_keys(self):
        keys_str = os.getenv("GEMINI_API_KEY", "")
        if keys_str:
            # Split by comma and strip whitespace
            self.gemini_keys = [k.strip() for k in keys_str.split(",") if k.strip() and k.strip() != "your_gemini_api_key_here"]
        
    def get_gemini_api_key(self):
        """Returns the current Gemini API key, or None if no valid keys exist."""
        if not self.gemini_keys:
            return None
        return self.gemini_keys[self.current_gemini_index]

    def rotate_gemini_key(self):
        """Rotates to the next Gemini key. Returns the new key or None."""
        if not self.gemini_keys:
            return None
        self.current_gemini_index = (self.current_gemini_index + 1) % len(self.gemini_keys)
        print(f"[LLMManager] Rotated to Gemini key index {self.current_gemini_index}")
        return self.get_gemini_api_key()

    def get_gemini_model(self, model_name="gemini-2.5-flash"):
        """Configures genai with the current key and returns the model."""
        key = self.get_gemini_api_key()
        if not key:
            print("Warning: GEMINI_API_KEY is not set or empty.")
            return None
        genai.configure(api_key=key)
        return genai.GenerativeModel(model_name)
    
    def generate_content_with_retry(self, prompt, model_name="gemini-2.5-flash", max_retries=None):
        """Attempts to generate content using the configured provider. Falls back to FPT if Gemini fails."""
        if self.provider == "fpt":
            return self._generate_with_fpt(prompt)
        else:
            try:
                return self._generate_with_gemini(prompt, model_name, max_retries)
            except Exception as e:
                # If Gemini is exhausted and we have an FPT key, use FPT as fallback
                if "exhausted" in str(e).lower() and self.fpt_api_key:
                    print(f"[LLMManager] Gemini exhausted. Falling back to FPT Cloud ({self.fpt_model_name})...")
                    return self._generate_with_fpt(prompt)
                raise e

    def _generate_with_fpt(self, prompt):
        if not self.fpt_api_key:
            raise Exception("FPT_API_KEY is not set or empty, but LLM_PROVIDER is 'fpt'.")
        
        url = "https://mkp-api.fptcloud.com/chat/completions"
        headers = {
            "Content-Type": "application/json",
            "Authorization": f"Bearer {self.fpt_api_key}"
        }
        data = {
            "model": self.fpt_model_name,
            "messages": [
                {
                    "role": "user",
                    "content": prompt
                }
            ],
            "stream": False
        }
        
        response = requests.post(url, headers=headers, data=json.dumps(data))
        if response.status_code != 200:
            raise Exception(f"FPT API Error {response.status_code}: {response.text}")
            
        json_resp = response.json()
        try:
            content = json_resp["choices"][0]["message"]["content"]
            return LLMResponse(content)
        except (KeyError, IndexError) as e:
            raise Exception(f"Unexpected response format from FPT API: {json_resp}")

    def _generate_with_gemini(self, prompt, model_name="gemini-2.5-flash", max_retries=None):
        if not self.gemini_keys:
             raise Exception("GEMINI_API_KEY is not set or empty.")
             
        if max_retries is None:
            max_retries = len(self.gemini_keys)
            
        attempts = 0
        last_error = None
        while attempts < max_retries:
            try:
                model = self.get_gemini_model(model_name)
                if not model:
                    raise Exception("Failed to initialize Gemini model")
                response = model.generate_content(prompt)
                return response
            except Exception as e:
                last_error = e
                error_msg = str(e).lower()
                # Check for rate limit (429) or invalid key (400/401/403)
                if "429" in error_msg or "resource exhausted" in error_msg or "quota" in error_msg or "400" in error_msg or "401" in error_msg or "403" in error_msg or "api key" in error_msg:
                    print(f"[LLMManager] Error with Gemini key index {self.current_gemini_index}: {e}. Rotating key...")
                    self.rotate_gemini_key()
                    attempts += 1
                else:
                    # Reraise other errors (e.g. network issues not related to key)
                    raise e
        
        print(f"[LLMManager] All {max_retries} attempts failed. Exhausted available Gemini keys.")
        raise Exception(f"All Gemini API keys exhausted or invalid. Last error: {last_error}")

# Singleton instance for global use
llm_manager = LLMManager()
