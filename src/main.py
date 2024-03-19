from langchain.embeddings import GPT4AllEmbeddings
from langchain.vectorstores import Chroma
from langchain.llms import Ollama
from langchain.callbacks.manager import CallbackManager
from langchain.callbacks.streaming_stdout import StreamingStdOutCallbackHandler
import chainlit as cl
from langchain_openai import ChatOpenAI
from langchain.chains import RetrievalQA, RetrievalQAWithSourcesChain
from langchain.prompts import (
    SystemMessagePromptTemplate,
    HumanMessagePromptTemplate,
    ChatPromptTemplate,
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
        model="mistral",
        api_key=None,
        base_url="http://localhost:1234/v1",
        temperature=0,
        # streaming=True,
        callback_manager=CallbackManager([StreamingStdOutCallbackHandler()]),
    )
    return llm


general_system_template = r"""<s> [INST] You are an Intelligent AI Assistant. Your response should be clear and concise. [/INST] </s> [INST] Context: {context} [/INST]"""
general_user_template = "Question: {question}"
messages = [
    SystemMessagePromptTemplate.from_template(general_system_template),
    HumanMessagePromptTemplate.from_template(general_user_template),
]
QA_PROMPT = ChatPromptTemplate.from_messages(messages)


def retrieval_qa_chain(llm, vectorstore):
    qa_chain = RetrievalQA.from_chain_type(
        llm,
        retriever=vectorstore.as_retriever(),
        chain_type_kwargs={"prompt": QA_PROMPT},
        return_source_documents=True,
    )
    return qa_chain


def qa_bot():
    llm = load_llm()
    DB_PATH = "vectorstores/db/"
    vectorstore = Chroma(
        persist_directory=DB_PATH, embedding_function=GPT4AllEmbeddings()
    )

    qa = retrieval_qa_chain(llm, vectorstore)
    return qa


@cl.on_chat_start
async def start():
    chain = qa_bot()
    msg = cl.Message(content="Firing up the research info bot...")
    await msg.send()
    msg.content = "Hi, welcome to research info bot. What is your query?"
    await msg.update()
    cl.user_session.set("chain", chain)


@cl.on_message
async def main(message):
    chain = cl.user_session.get("chain")
    cb = cl.AsyncLangchainCallbackHandler(
        stream_final_answer=True, answer_prefix_tokens=["FINAL", "ANSWER"]
    )
    cb.answer_reached = True
    # res=await chain.acall(message, callbacks=[cb])
    res = await chain.acall(message.content, callbacks=[cb])
    print(f"response: {res}")
    answer = res["result"]
    answer = answer.replace(".", ".\n")
    sources = res["source_documents"]

    if sources:
        answer += f"\nSources: " + str(str(sources))
    else:
        answer += f"\nNo Sources found"

    await cl.Message(content=answer).send()
