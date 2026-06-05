import os
import random
import google.generativeai as genai

class GeminiKeyManager:
    def __init__(self):
        self.keys = []
        self._load_keys()
        self.current_index = 0

    def _load_keys(self):
        keys_str = os.getenv("GEMINI_API_KEY", "")
        if keys_str:
            # Split by comma and strip whitespace
            self.keys = [k.strip() for k in keys_str.split(",") if k.strip() and k.strip() != "your_gemini_api_key_here"]
        
    def get_api_key(self):
        """Returns the current API key, or None if no valid keys exist."""
        if not self.keys:
            return None
        return self.keys[self.current_index]

    def rotate_key(self):
        """Rotates to the next key. Returns the new key or None."""
        if not self.keys:
            return None
        self.current_index = (self.current_index + 1) % len(self.keys)
        print(f"[KeyManager] Rotated to key index {self.current_index}")
        return self.get_api_key()

    def get_model(self, model_name="gemini-2.5-flash"):
        """Configures genai with the current key and returns the model."""
        key = self.get_api_key()
        if not key:
            print("Warning: GEMINI_API_KEY is not set or empty. Using mock model.")
            return None
        genai.configure(api_key=key)
        return genai.GenerativeModel(model_name)
    
    def generate_content_with_retry(self, prompt, model_name="gemini-2.5-flash", max_retries=None):
        """Attempts to generate content, rotating keys if a ResourceExhausted or authentication error occurs."""
        if not self.keys:
             raise Exception("GEMINI_API_KEY is not set or empty.")
             
        if max_retries is None:
            max_retries = len(self.keys)
            
        attempts = 0
        last_error = None
        while attempts < max_retries:
            try:
                model = self.get_model(model_name)
                if not model:
                    raise Exception("Failed to initialize Gemini model")
                response = model.generate_content(prompt)
                return response
            except Exception as e:
                last_error = e
                error_msg = str(e).lower()
                # Check for rate limit (429) or invalid key (400/401/403)
                if "429" in error_msg or "resource exhausted" in error_msg or "quota" in error_msg or "400" in error_msg or "401" in error_msg or "403" in error_msg or "api key" in error_msg:
                    print(f"[KeyManager] Error with key index {self.current_index}: {e}. Rotating key...")
                    self.rotate_key()
                    attempts += 1
                else:
                    # Reraise other errors (e.g. network issues not related to key)
                    raise e
        
        print(f"[KeyManager] All {max_retries} attempts failed. Exhausted available keys.")
        raise Exception(f"All API keys exhausted or invalid. Last error: {last_error}")

# Singleton instance for global use
gemini_key_manager = GeminiKeyManager()
