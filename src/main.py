from langchain.vectorstores import Chroma
from langchain.callbacks.manager import CallbackManager
from langchain.callbacks.streaming_stdout import StreamingStdOutCallbackHandler
import chainlit as cl
from langchain_openai import ChatOpenAI
from langchain.chains import RetrievalQA, ConversationalRetrievalChain
from langchain.prompts import (
    SystemMessagePromptTemplate,
    HumanMessagePromptTemplate,
    ChatPromptTemplate,
)
from langchain.memory import ConversationBufferMemory, ChatMessageHistory
from langchain.text_splitter import RecursiveCharacterTextSplitter
from langchain.embeddings import HuggingFaceEmbeddings

from constants import (
    CHROMA_SETTINGS,
    DOCUMENT_MAP,
    EMBEDDING_MODEL_NAME,
    PERSIST_DIRECTORY,
)


# load the LLM
def load_llm():
    # llm = Ollama(
    #     model="mistral",
    #     verbose=True,
    #     # base_url="https://periods-veterans-redeem-compression.trycloudflare.com",
    #     callback_manager=CallbackManager([StreamingStdOutCallbackHandler()]),
    # )
    llm = ChatOpenAI(
        model="lmstudio-community/Meta-Llama-3-8B-Instruct-GGUF",
        api_key=None,
        base_url="http://localhost:1234/v1",
        temperature=0.3,
        streaming=True,
        callback_manager=CallbackManager([StreamingStdOutCallbackHandler()]),
    )
    return llm


general_system_template = r"""<s> [INST] You are an Intelligent AI Assistant named chatty. [/INST] </s>
[INST] Context: {context} [/INST]
"""
general_user_template = "User Query: {question}"
messages = [
    SystemMessagePromptTemplate.from_template(general_system_template),
    HumanMessagePromptTemplate.from_template(general_user_template),
]
QA_PROMPT = ChatPromptTemplate.from_messages(messages)


def retrieval_qa_chain(llm, vectorstore):
    qa_chain = RetrievalQA.from_chain_type(
        llm,
        chain_type="stuff",
        retriever=vectorstore.as_retriever(),
        chain_type_kwargs={"prompt": QA_PROMPT},
        return_source_documents=True,
        callbacks=CallbackManager([StreamingStdOutCallbackHandler()]),
    )
    return qa_chain


def qa_bot():
    llm = load_llm()
    vectorstore = Chroma(
        persist_directory=PERSIST_DIRECTORY,
        embedding_function=HuggingFaceEmbeddings(
            model_name=EMBEDDING_MODEL_NAME,
            model_kwargs={"device": "cpu"},
        ),
        client_settings=CHROMA_SETTINGS,
    )

    qa = retrieval_qa_chain(llm, vectorstore)
    return qa


# @cl.on_chat_start
# async def start():
#     chain = qa_bot()
#     msg = cl.Message(content="Firing up the research info bot...")
#     await msg.send()
#     msg.content = "Hi, welcome to research info bot. What is your query?"
#     await msg.update()
#     cl.user_session.set("chain", chain)


@cl.on_chat_start
async def on_chat_start():
    files = None
    files = await cl.AskFileMessage(
        content="Please Upload a file to begin!!",
        accept=[
            "text/plain",
            "text/csv",
            "application/pdf",
            "text/markdown",
            "text/html",
            "application/vnd.sealed.xls",
            "application/vnd.sealed.doc",
        ],
        max_files=1,
        max_size_mb=25,
        timeout=180,
    ).send()

    file = files[0]  # type: ignore
    msg = cl.Message(content=f"Processing `{file.name}`!!", disable_feedback=True)
    await msg.send()

    file_extension = file.name.split(".")[-1]

    text = ""
    loader_class = DOCUMENT_MAP.get("." + file_extension)
    if loader_class:
        loader = loader_class(file.path)
        text = loader.load()

    texts = RecursiveCharacterTextSplitter(
        chunk_size=1000, chunk_overlap=100
    ).split_text(text[0].page_content)
    metadatas = [{"source": f"{i}-pl"} for i in range(len(texts))]

    msg.content = "Hold on while embeddings are generated!!"
    await msg.send()

    embeddings = HuggingFaceEmbeddings(
        model_name=EMBEDDING_MODEL_NAME,
        model_kwargs={"device": "cpu"},
    )
    docsearch = await cl.make_async(Chroma.from_texts)(
        texts, embeddings, metadatas=metadatas
    )

    message_history = ChatMessageHistory()

    memory = ConversationBufferMemory(
        memory_key="chat_history",
        output_key="answer",
        chat_memory=message_history,
        return_messages=True,
    )

    # Create a chain that uses the Chroma vector store
    chain = ConversationalRetrievalChain.from_llm(
        ChatOpenAI(
            model="lmstudio-community/Meta-Llama-3-8B-Instruct-GGUF",
            api_key="chat-with-documents",  # type: ignore
            base_url="http://localhost:1234/v1",
            temperature=0.3,
            streaming=True,
            callback_manager=CallbackManager([StreamingStdOutCallbackHandler()]),
        ),
        chain_type="stuff",
        retriever=docsearch.as_retriever(),
        memory=memory,
        return_source_documents=True,
    )
    chain.combine_docs_chain.llm_chain.prompt.messages[0] = (
        SystemMessagePromptTemplate.from_template(general_system_template)
    )

    # Let the user know that the system is ready
    msg.content = f"Processing `{file.name}` done. You can now ask questions!"
    await msg.update()

    cl.user_session.set("chain", chain)


@cl.on_message
async def main(message: cl.Message):
    chain = cl.user_session.get("chain")
    cb = cl.AsyncLangchainCallbackHandler(stream_final_answer=True)

    res = await chain.ainvoke(message.content, callbacks=[cb])  # type: ignore
    answer = res["answer"]
    source_documents = res["source_documents"]

    text_elements = []

    if source_documents:
        print(f"source_documents: {source_documents}")
        for source_idx, source_doc in enumerate(source_documents):
            source_name = f"source_{source_idx}"
            text_elements.append(
                cl.Text(content=source_doc.page_content, name=source_name)
            )
        source_names = [text_el.name for text_el in text_elements]

        if source_names:
            answer += f"\nSources: {', '.join(source_names)}"
        else:
            answer += "\nNo sources found"

    await cl.Message(content=answer, elements=text_elements).send()
