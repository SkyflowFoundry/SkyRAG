
import openai
from openai import OpenAI
import os
from service.detect_api import skyflow_identify
api_key = os.getenv("OPENAI_API_KEY")
model_name = "gpt-3.5-turbo"

def llm_call(prompt):
    contexts = prompt['results']
    tokenize_query  = prompt['tokenize_query']
    instruction = "you are great QA Engineer answer question please consider all sensitive inforamation such as Name, Location are in form of UUID hence consider those values as sensitive data answer the question, all answer must have at least 100 words based on the context."
    oringinal_prompt = tokenize_query + " " + " ".join(result["Content"] for result in contexts)
    openai.api_key = api_key
    client = OpenAI()
    completion = client.chat.completions.create(
    model=model_name,
    messages=[
        {"role": "system", "content": instruction},
        {"role": "user", "content":oringinal_prompt}
    ]
    )
    original_reply = completion.choices[0].message.content
    detokenize_response = skyflow_identify(original_reply)
    # test_dataset(prompt_text,detokenize_response)
    response_object = {
        "oringinal_prompt" : oringinal_prompt,
        "original_reply": original_reply,
        "detokenize_response": detokenize_response
        }
    return response_object