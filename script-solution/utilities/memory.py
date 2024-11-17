from langchain_core.messages import AIMessage, HumanMessage, trim_messages

def chat_to_memory(list_chat_history, n_used_memory=10):
    """
    Converts a chat history list into memory format for AI models, keeping only the latest entries 
    up to a specified limit.

    Args:
        list_chat_history (list): List of chat messages with 'input' (human) and 'output' (AI) text.
        n_used_memory (int): Max number of messages to retain in memory (default is 10).

    Returns:
        selected_memory (list): List of memory of `HumanMessage` and `AIMessage` objects.
    """
    
    memory = []
    
    for i in range(0, len(list_chat_history)):
        if i % 2 == 0:
            memory.append(HumanMessage(content=list_chat_history[i]['input']))
        elif i % 2 == 1:
            memory.append(AIMessage(content=list_chat_history[i]['output']))

    if len(memory) % 2 == 1:
        memory.append(AIMessage(content=""))
            
    selected_memory = trim_messages(
        memory,
        token_counter=len,
        max_tokens=n_used_memory,
        strategy="last",
        start_on="human",
        allow_partial=False,
    )
    
    return selected_memory


def write_chat_history(chat_history):
    """
    Saves chat history to a text file with labeled human and AI messages.

    Args:
        chat_history (list): List of chat messages with 'input' (human) and 'output' (AI) text.

    Returns:
        None
    """

    list_chat_history = chat_history
    text_history = "Chat History: "
    
    for i in range(0, len(list_chat_history)):
        if i % 2 == 0:
            text_history = text_history + "\n" + "Human: " + list_chat_history[i]['input']
        elif i % 2 == 1:
            text_history = text_history + "\n" + "AI: " + list_chat_history[i]['output']
    
    with open("./database/chat_history.txt", "w") as file:
        file.write(text_history)