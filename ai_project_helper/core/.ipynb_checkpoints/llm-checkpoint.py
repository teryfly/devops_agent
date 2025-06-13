# core/llm.py

import requests
from ai_project_helper.core.prompt import build_prompt
import logging

logger = logging.getLogger("ai_project_helper.llm")

class LLMClient:
    def __init__(self, config):
        self.api_url = config['llm']['api_url']
        self.api_key = config['llm']['api_key']
        self.model = config['llm']['model']

    def build_prompt(self, plan_text):
        return build_prompt(plan_text)

    def plan_to_actions(self, plan_text: str):
        prompt = self.build_prompt(plan_text)
        logger.info(f"LLMClient 提交的 PROMPT:\n{'='*24}\n{prompt}\n{'='*24}")
        response = requests.post(
            self.api_url,
            json={
                "model": self.model,
                "messages": [{"role": "system", "content": prompt}],
                "max_tokens": 2048000,
                "temperature": 0,
            },
            headers={"Authorization": f"Bearer {self.api_key}"}
        )
        response.raise_for_status()
        return response.json()["choices"][0]["message"]["content"]

    def generate_bash_script(self, steps_text: str):
        prompt = f"""Generate a batch/bash script that converts each step of the following plan into executable commands. Return only the script content without any additional information or explanations.
{steps_text}
"""
        logger.info(f"LLMClient CreateProject PROMPT:\n{'='*24}\n{prompt}\n{'='*24}")
        response = requests.post(
            self.api_url,
            json={
                "model": self.model,
                "messages": [{"role": "system", "content": prompt}],
                "max_tokens": 2048,
                "temperature": 0,
            },
            headers={"Authorization": f"Bearer {self.api_key}"}
        )
        response.raise_for_status()
        content = response.json()["choices"][0]["message"]["content"]
        return content.strip()