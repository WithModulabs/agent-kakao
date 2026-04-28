"""[Optional] Prompt templates tailored to the Convert graph.

Guidelines:
    - Create LangChain `PromptTemplate` or LCEL prompt definitions.
    - Consume these templates from the chain/node modules.

Official document URL:
    - Messages: https://docs.langchain.com/oss/python/langchain/messages
    - OpenAI prompt engineering: https://platform.openai.com/docs/guides/prompt-engineering
"""

EMOTICON_GENERATE_PROMPT = (
    "Transform this photo into a Kakao emoticon style illustration. "
    "Apply a cute cartoon / webtoon art style with bold outlines, soft pastel colors, "
    "and exaggerated, friendly facial expressions typical of Korean emoticons. "
    "Preserve the subject's identity and pose. "
    "The output should look like an official Kakao Friends character sticker "
    "on a transparent or white background."
)
