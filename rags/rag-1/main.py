import os
from dotenv import load_dotenv
from langchain_google_genai import ChatGoogleGenerativeAI, GoogleGenerativeAIEmbeddings
from langchain_community.document_loaders import PyPDFLoader
from langchain_core.prompts import ChatPromptTemplate
from langchain_chroma import Chroma
from langchain.text_splitter import RecursiveCharacterTextSplitter

load_dotenv()

curr_dir = os.path.dirname(os.path.abspath(__file__))
file_path = os.path.join(curr_dir, "documents", "cp_guide.pdf")
vdb_path = os.path.join(curr_dir, "db")

embeddings = GoogleGenerativeAIEmbeddings(
    model="models/text-embedding-004"
)

llm = ChatGoogleGenerativeAI(model="gemini-2.0-flash")

if not os.path.exists(vdb_path):
    print("Initializing DB.......")

    if not os.path.exists(file_path):
        raise FileNotFoundError(f"The file {file_path} does not exists")

    loader = PyPDFLoader(file_path)
    documents = loader.load()

    text_splitter = RecursiveCharacterTextSplitter(
        chunk_size=1000, chunk_overlap=100)

    chunks = text_splitter.split_documents(documents)

    db = Chroma.from_documents(
        chunks, embeddings, persist_directory=vdb_path)
else:
    print("Vector DB already exists")

db = Chroma(persist_directory=vdb_path, embedding_function=embeddings)

query = input("Enter your query: ")
retriever = db.as_retriever(
    search_type="similarity_score_threshold",
    search_kwargs={"k": 10, "score_threshold": 0.5}
)

chunks = retriever.invoke(query)
context_str = "\n\n".join([chunk.page_content for chunk in chunks])

template = ChatPromptTemplate.from_messages([
    ("system", '''
You are a highly knowledgeable and experienced assistant with deep expertise in Competitive Programming and Data Structures & Algorithms (DSA). You are expected to help users understand complex problems, optimize their solutions, analyze time and space complexities, and suggest best practices and strategies commonly used in competitive programming environments such as Codeforces, Leetcode, AtCoder, etc.

Your responses should be accurate, concise, and structured in a way that helps users quickly grasp the solution or concept. When explaining, use relevant examples, pseudocode, or step-by-step breakdowns as needed. If the problem can be improved or clarified, guide the user accordingly.

Assume the user has a working knowledge of basic programming (e.g., C++, Python, Java) and common algorithmic concepts, but may need help applying or optimizing them.

     '''),
    ("human", '''
User Query:
{query}

Relevant Context:
Here are some refred context from the books which might help you to answer the user's query

{context}

''')
])

prompt = template.format_prompt(query=query, context=context_str)
res = llm.invoke(prompt)

print(res.content)
