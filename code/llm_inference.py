from openai import OpenAI
from dotenv import load_dotenv, find_dotenv, get_key

def inference(user_prompt):
    client = OpenAI(
        base_url = "https://integrate.api.nvidia.com/v1",
        api_key = get_key(find_dotenv(), "NVIDIA_API_KEY")
    )

    completion = client.chat.completions.create(
        model="qwen/qwen3-next-80b-a3b-instruct",
        messages=[{"role":"user","content":user_prompt}],
        temperature=0.2,
        top_p=0.7,
        max_tokens=8192,
        stream=False
    )

    # for chunk in completion:
    #     reasoning = getattr(chunk.choices[0].delta, "reasoning_content", None)
    #     if reasoning:
    #         print(reasoning, end="")
    #     if chunk.choices[0].delta.content is not None:
    #         print(chunk.choices[0].delta.content, end="")

    return completion.choices[0].message.content.strip('\n')