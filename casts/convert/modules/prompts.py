"""[Optional] Prompt templates tailored to the Convert graph.

Guidelines:
    - Create LangChain `PromptTemplate` or LCEL prompt definitions.
    - Consume these templates from the chain/node modules.

Official document URL:
    - Messages: https://docs.langchain.com/oss/python/langchain/messages
    - OpenAI prompt engineering: https://platform.openai.com/docs/guides/prompt-engineering
"""

EMOTICON_GENERATE_PROMPT = """Use the attached reference image as the exact character reference.

Create a KakaoTalk-style emoticon sticker sheet in a 4x4 grid, total 16 panels.
Theme: love

Important:
- Keep the exact same character identity in every panel
- Preserve the same face, hairstyle, proportions, species, age impression, outfit vibe, and overall charm
- Do not redesign or reinterpret the character
- Strong character consistency is critical

Style:
- cute Korean messenger emoticon style
- very expressive facial expressions
- playful, sweet, affectionate, charming
- lively, bouncy, adorable energy like popular KakaoTalk stickers
- soft pastel colors
- clean white background
- sticker-like cutout feeling
- bold readable silhouette
- simple and clean composition in each panel
- polished commercial emoticon sheet
- each panel should work as an independent sticker
- emotional clarity at small size

Scene directions:
1. shy blush with tiny heart gesture
2. heart eyes looking at someone lovingly
3. making a big hand heart
4. warm cuddle or hug
5. pouty jealous expression
6. shy confession with a small letter
7. pounding heart, excited love reaction
8. missing you expression, reaching forward
9. happy together mood with floating hearts
10. thankful smile holding a heart
11. sleepy good night pose with cozy feeling
12. kiss face expression
13. embarrassed cute smile hiding face
14. playful possessive love expression
15. cheering with love and sparkles
16. peaceful happy smile leaning on a big heart

Korean text, short and natural, placed across selected panels only:
- 사랑해
- 좋아해
- 심쿵
- 안아줘
- 두근두근
- 보고싶어
- 고마워
- 잘자
- 쪽
- 내꺼야

Text styling:
- Korean text only
- short, bold, cute, highly readable
- use at most 1 short text per panel
- natural placement like real KakaoTalk emoticons
- do not overload the sheet with text
- playful and emotionally clear

Composition:
- 16-panel sticker sheet
- evenly spaced grid
- clean white canvas
- each panel clearly separated
- consistent line quality and color harmony
- expressive pose variety
- no unnecessary props or background elements

Output:
sticker sheet format, 16 panels, consistent characters"""
