"""LangChain model, LLMChain, message and streaming helpers."""

from typing import Dict, Generator, Any

from langchain.chains import LLMChain
from langchain_core.messages import SystemMessage, HumanMessage, AIMessage
from langchain_openai import ChatOpenAI

from .config import OPENAI_API_KEY, OPENAI_MODEL, OPENAI_TEMPERATURE
from .prompts import (
    ASSESSMENT_CHAT_TEMPLATE,
    ASSESSMENT_PROMPT,
    MESSAGE_DEMO_SYSTEM,
    NARRATIVE_CHAT_TEMPLATE,
)


def build_llm() -> ChatOpenAI:
    """Create the OpenAI chat model from environment configuration."""
    if not OPENAI_API_KEY:
        raise ValueError(
            "OPENAI_API_KEY is missing. Create a .env file from .env.example "
            "and add your OpenAI API key."
        )

    return ChatOpenAI(
        model=OPENAI_MODEL,
        temperature=OPENAI_TEMPERATURE,
        api_key=OPENAI_API_KEY,
    )


def build_assessment_chain(llm: ChatOpenAI) -> LLMChain:
    """
    Build the reusable LLMChain required by the assignment.

    The assignment also requires a reusable single-string PromptTemplate.
    We use that PromptTemplate here with an explicit system safety prefix.
    """
    from langchain_core.prompts import PromptTemplate

    chain_prompt = PromptTemplate(
        input_variables=ASSESSMENT_PROMPT.input_variables,
        template=(
            f"SYSTEM SAFETY INSTRUCTIONS:\n"
            f"{__import__('src.prompts', fromlist=['SYSTEM_PROMPT']).SYSTEM_PROMPT}\n\n"
            f"{ASSESSMENT_PROMPT.template}"
        ),
    )
    return LLMChain(llm=llm, prompt=chain_prompt)


def run_assessment(chain: LLMChain, inputs: Dict[str, Any]) -> str:
    """Run the reusable LLMChain and return its raw text."""
    result = chain.invoke(inputs)
    if isinstance(result, dict):
        return str(result.get("text", ""))
    return str(result)


def message_demo(llm: ChatOpenAI, user_text: str) -> list:
    """
    Demonstrate SystemMessage -> HumanMessage -> AIMessage.

    The returned list can be inspected in the Streamlit UI. The actual AIMessage
    is obtained from the model so the example reflects a real chat conversation.
    """
    messages = [
        SystemMessage(content=MESSAGE_DEMO_SYSTEM),
        HumanMessage(content=user_text),
    ]
    response = llm.invoke(messages)
    if isinstance(response, AIMessage):
        messages.append(response)
    return messages


def stream_narrative(
    llm: ChatOpenAI, assessment_json: str, language: str
) -> Generator[str, None, None]:
    """Yield narrative chunks from llm.stream() for st.write_stream()."""
    messages = NARRATIVE_CHAT_TEMPLATE.format_messages(
        assessment_json=assessment_json,
        language=language,
    )
    for chunk in llm.stream(messages):
        content = getattr(chunk, "content", "")
        if content:
            yield content


def build_chat_assessment_messages(inputs: Dict[str, Any]):
    """Build the System + Human messages used by the chat prompt."""
    return ASSESSMENT_CHAT_TEMPLATE.format_messages(**inputs)
