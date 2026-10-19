from langchain_groq import ChatGroq
from langchain_chroma import Chroma
from langchain_core.prompts import ChatPromptTemplate
from langchain_huggingface import HuggingFaceEmbeddings
from dotenv import load_dotenv

load_dotenv()


from src.state import AgentState
from src.tools import get_img_of_day

llm=ChatGroq(model="openai/gpt-oss-20b",temperature=0)

embeddings=HuggingFaceEmbeddings(model_name="sentence-transformers/all-MiniLM-L6-v2")
vector_store=Chroma(persist_directory='./chroma_db',embedding_function=embeddings)
print("Vector count : ",vector_store._collection.count())
classify_prompt=ChatPromptTemplate.from_template(
    """
        Classify this question into exactly one category:
        - retrieve: specific conceptual or factual astronomy questions
        - call_api: asks for today's or the current astronomy picture, or what is happening now
        - clarify: too broad or vague to answer well (no specific topic)

        Examples:
        "why do stars twinkle" -> retrieve
        "how far is the moon" -> retrieve
        "what's today's astronomy picture" -> call_api
        "tell me about space" -> clarify
        "explain astronomy" -> clarify
        "tell me something cool" -> clarify

        Question: {question}
        Respond with only one word: retrieve, call_api, or clarify.
""")


answer_prompt=ChatPromptTemplate.from_template(""" 
    Answer the astronomy question using only the context provided below.
    If the context doesn't contain information, say so honestly

    Context:{context}

    Question:{question}

    Answer:

""")


def classify_node(state:AgentState):
    chain=classify_prompt| llm
    result=chain.invoke({'question':state['question']})
    return {'route':result.content.strip().lower()}

def call_api_node(state:AgentState):
    result=get_img_of_day.invoke({})
    return {'answer':result}

def retrieve_node(state: AgentState):
    results = vector_store.similarity_search(state["question"], k=3)
    context = "\n\n".join([r.page_content for r in results])

    chain = answer_prompt | llm
    formatted = answer_prompt.format(context=context, question=state["question"])
    print("FORMATTED PROMPT:\n", formatted)

    response = chain.invoke({"context": context, "question": state["question"]})
    return {"answer": response.content}


def clarify_node(state:AgentState):
    return {'answer':'Could be you be more specific? For example,are you asking about a general astronomy concept or something currently visible in the sky?'}

