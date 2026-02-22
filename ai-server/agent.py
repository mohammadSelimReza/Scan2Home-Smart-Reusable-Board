import os
from typing import List, Dict, Any
from dotenv import load_dotenv
from langchain_openai import ChatOpenAI
from langchain_core.messages import SystemMessage, HumanMessage, AIMessage, BaseMessage

# Load environment variables
load_dotenv()

# Initialize ChatOpenAI
# You can pin a model version if needed, e.g., model="gpt-4o"
llm = ChatOpenAI(model="gpt-4o", temperature=0)

def _convert_history_to_messages(chat_history: List[Dict[str, str]]) -> List[BaseMessage]:
    """Converts a list of dicts to LangChain message objects."""
    messages = []
    for msg in chat_history:
        role = msg.get("role")
        content = msg.get("content", "")
        if role == "user":
            messages.append(HumanMessage(content=content))
        elif role == "assistant":
            messages.append(AIMessage(content=content))
        elif role == "system":
            messages.append(SystemMessage(content=content))
    return messages

def user_chatbot(FAQ_context: str, chat_history: List[Dict[str, str]], message: str = "") -> str:
    """
    Constructs the prompt and executes the chat using LangChain OpenAI.
    
    Args:
        FAQ_context: A string containing the FAQ.
        chat_history: A list of dictionaries representing the chat history.
        message: The latest user message.
        
    Returns:
        The content of the assistant's response.
    """
    system_prompt = f"""You are a helpful customer support assistant.
Use the following FAQ to answer the user's questions.
If the answer is not in the FAQ, politely say you don't know and offer to connect them to a human agent.

{FAQ_context}
"""
    
    messages = [SystemMessage(content=system_prompt)]
    
    # Add chat history
    messages.extend(_convert_history_to_messages(chat_history))
    
    # Add the latest message if provided
    if message:
        messages.append(HumanMessage(content=message))
        
    # Execute the LLM call
    response = llm.invoke(messages)
    return response.content

def agent_chatbot(full_profile: str, chat_history: List[Dict[str, str]], FAQ_context: str, message: str = "") -> str:
    """
    Constructs the prompt and executes the chat using LangChain OpenAI with a custom profile.
    
    Args:
        full_profile: A string containing the agent's persona/instructions.
        chat_history: A list of dictionaries representing the chat history.
        FAQ_context: A string containing the FAQ.
        message: The latest user message.
        
    Returns:
        The content of the assistant's response.
    """
    system_prompt = f"""{full_profile}

Use the following FAQ to answer the user's questions where relevant.

{FAQ_context}
"""
    
    messages = [SystemMessage(content=system_prompt)]
    
    messages.extend(_convert_history_to_messages(chat_history))
    
    if message:
        messages.append(HumanMessage(content=message))
        
    # Execute the LLM call
    response = llm.invoke(messages)
    return response.content
