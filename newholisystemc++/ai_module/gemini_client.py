import os
from google import genai
from dotenv import load_dotenv

class GeminiClient:
    def __init__(self):
        load_dotenv()
        self.api_key = os.getenv("GEMINI_API_KEY")
        if not self.api_key:
            print("Warning: GEMINI_API_KEY not found in environment.")
        
        try:
            self.client = genai.Client(api_key=self.api_key)
            self.chat_session = self.client.chats.create(model='gemini-2.5-flash')
        except Exception as e:
            print(f"Error starting AI chat session: {e}")
            self.chat_session = None
            
    def analyze_system(self, cpu_history, ram_history, top_processes):
        cpu_avg = sum(cpu_history[-10:]) / len(cpu_history[-10:]) if cpu_history else 0
        ram_avg = sum(ram_history[-10:]) / len(ram_history[-10:]) if ram_history else 0
        
        process_str = ", ".join([f"{p['name']} ({p.get('cpu', 0):.1f}%)" for p in top_processes[:5]])
        
        prompt = (f"System Diagnostics: Avg CPU {cpu_avg:.1f}%, Avg RAM: {ram_avg:.1f}%. "
                  f"Top consumers: {process_str}. "
                  f"Provide a brief analysis of the system condition and 1-2 practical optimization tips. "
                  f"CRITICAL INSTRUCTION: Output strictly in pure plain text. Do NOT use markdown formatting, asterisks (* or **), or bullet points. Use standard paragraph spacing and clean structure.")
        try:
            response = self.client.models.generate_content(
                model='gemini-2.5-flash',
                contents=prompt
            )
            return response.text.replace("*", "")
        except Exception as e:
            return f"Error contacting AI: {e}"

    def ask_query(self, query, context=""):
        if not self.chat_session:
            return "AI Chat session is not initialized."
        try:
            formatted_query = query
            if context:
                formatted_query = f"[Hidden Context - Real-time System State: {context}]\n\n" \
                                  f"[System Instruction: Provide answers in a clear, structured, and properly organized format. " \
                                  f"Do NOT use any markdown symbols like asterisks (* or **) or hashtags (#). Ensure everything is clean, consistent, and easy to read using normal spacing.]\n\n" \
                                  f"User Query: {query}"
            
            response = self.chat_session.send_message(formatted_query)
            return response.text.replace("*", "").replace("#", "")
        except Exception as e:
            return f"Error with AI Chat: {e}"
