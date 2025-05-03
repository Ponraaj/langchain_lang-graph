from dotenv import load_dotenv
from langchain_google_genai import ChatGoogleGenerativeAI
from langchain_core.prompts import ChatPromptTemplate
from langchain_core.runnables import RunnableLambda, RunnableParallel
from langchain_core.output_parsers import StrOutputParser


load_dotenv()

model = ChatGoogleGenerativeAI(model="gemini-2.0-flash")


def analyze_plot(plot):
    template = ChatPromptTemplate.from_messages([
        ("system", "You are a movie critic with a deep knowledge on all the movies."),
        ("human",
         "Analyze the plot: {plot}. What are the strenghts and weakness of the plot? Keep your result within 1 paragraph")
    ])

    return template.format_prompt(plot=plot)


def analyze_character(plot):
    template = ChatPromptTemplate.from_messages([
        ("system", "You are a movie critic with a deep knowledge on all the movies."),
        ("human",
         "Analyze the characters: {plot}. What are the strenghts and weakness of the characters and how are the portrayed? Keep your result within 1 paragraph")
    ])

    return template.format_prompt(plot=plot)


def provide_ratings(plot_analysis, characters_analysis):
    template = ChatPromptTemplate.from_messages([
        ("system", "You are a movie critic with a deep knowledge on all the movies."),
        ("human",
         "I want you to provide your ratings based on how interesting the story and the characters was. Here is the plot analysis:\n{plot_analysis}\nHere is the character analysis:\n{characters_analysis}\n Give me your ratings out of 10 and give its strenghts and weakness.")
    ])

    return template.format_prompt(plot_analysis=plot_analysis, characters_analysis=characters_analysis)


summary_template = ChatPromptTemplate.from_messages([
    ("system", "You are a movie critic with a deep knowledge on all movies"),
    ("human",
     "Give me a brief summary of the movie {movie}, including its plot with its characters")
])

plot_chain = (
    RunnableLambda(lambda x: analyze_plot(x)) | model | StrOutputParser()
)

character_chain = (
    RunnableLambda(lambda x: analyze_character(x)) | model | StrOutputParser()
)

chain = (
    summary_template
    | model
    | StrOutputParser()
    | RunnableParallel(branches={"plot": plot_chain, "characters": character_chain})
    | RunnableLambda(lambda x: provide_ratings(x["branches"]["plot"], x["branches"]["characters"]))
    | model
    | StrOutputParser()
)

movie = input("Enter a movie to provide ratings: ")
result = chain.invoke({"movie": movie})
print(result)
