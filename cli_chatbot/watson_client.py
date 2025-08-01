import os
from dotenv import load_dotenv
from ibm_watsonx_ai.foundation_models import ModelInference
from ibm_watsonx_ai import Credentials


load_dotenv()

API_KEY = os.getenv("WATSONX_API_KEY")
PROJECT_ID = os.getenv("WATSONX_PROJECT_ID")

creds = Credentials(
    url="https://us-south.ml.cloud.ibm.com",  # Dallas Region
    api_key=API_KEY
)

model = ModelInference(
    model_id="ibm/granite-3-3-8b-instruct",
    credentials=creds,
    project_id=PROJECT_ID
)

def ask_watson(pergunta):
    system_prompt = open("../prompts/base_prompt.txt").read()
    full_prompt = f"{system_prompt}\n\nUsuário: {pergunta}\nAssistente:"

    response = model.generate(
        prompt=full_prompt,
        params={
            "decoding_method": "greedy",
            "max_new_tokens": 800,
            "stop_sequences": ["Usuário:"],
            "temperature": 0.2,
            "repetition_penalty": 1.1,
        }
    )
    return response['results'][0]['generated_text']

