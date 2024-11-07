from langchain_core.messages import AIMessage, HumanMessage, trim_messages

def chat_to_memory(list_chat_history, n_used_memory=10):
    
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
    list_chat_history = chat_history
    text_history = "Chat History: "
    
    for i in range(0, len(list_chat_history)):
        if i % 2 == 0:
            text_history = text_history + "\n" + "Human: " + list_chat_history[i]['input']
        elif i % 2 == 1:
            text_history = text_history + "\n" + "AI: " + list_chat_history[i]['output']
    
    with open("./database/chat_history.txt", "w") as file:
        file.write(text_history)
