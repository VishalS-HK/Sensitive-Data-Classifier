from crewai import Agent, Task, Crew, Process
from langchain_openai.chat_models import ChatOpenAI
from dotenv import load_dotenv
import os

load_dotenv()
api_key = os.getenv('OPENAI_API_KEY')
Model = 'gpt-4o'
llm = ChatOpenAI(api_key=api_key, model=Model)

def CrewAIAgentFlow(document):
    classifier_agent = Agent(
        role="data classifier",
        goal=(
            "accurately classify all the data in the document uploaded. "
            "classify each of the data into one of the classes: "
            "PII (Personally Identifiable Information), PHI (Protected Health Information), "
            "or PCI (Payment Card Information). "
            "the output should be grouped by class, with each class followed by a list of corresponding data. "
            "for example:\n"
            "PII:\n- Item 1\n- Item 2\n"
            "PHI:\n- Item 1\n- Item 2\n"
            "PCI:\n- Item 1\n- Item 2"
        ),
        backstory="you are an AI assistant whose only job is to classify and format data in the documents accurately and honestly.",
        verbose=True,
        allow_delegation=False,
        llm=llm
    )

    context_agent = Agent(
        role= "sensitive data context provider",
        goal= "accurately provide context on what sensitive information was found in the document, if any. List them.",
        backstory= "you are an AI assistant tasked to provide context for fields data you deem are sensitive in nature, that are there in the document, if any.",
        verbose= True,
        allow_delegation= False,
        llm=llm
    )

    classify_task = Task(
        description=f"classify the following document:\n{document}",
        agent=classifier_agent,
        expected_output=(
            "the output should be grouped by class and formatted as:\n"
            "PII:\n- Item 1\n- Item 2\n"
            "PHI:\n- Item 1\n- Item 2\n"
            "PCI:\n- Item 1\n- Item 2"
        )
    )

    context_task = Task (
        description = f"provide additional context on the sensistive fields found in the document: \n {document}",
        agent= context_agent,
        expected_output=( 
            "A list of potential sensitive fields and the risks it might have, if exposed or leaked or breached. Keep it short and concise"
            "For example:\n"
            "Sensitive field: - Item\n "
            "Risk involved:"
            "Let the risk involved be just a few ones."
        )
    )

    crew = Crew(
        agents=[classifier_agent, context_agent],
        tasks=[classify_task, context_task],
        verbose=True,
        process=Process.sequential
    )

    result = crew.kickoff()
    response = {
        'classification-res': result.tasks_output[0],
        'sensitive_fields_res': result.tasks_output[1]
    }

    return response


# document = """
# Patient Name: John Doe
# MRN: 123456
# Date: 2024-01-01
# Dr. Smith noted that patient's blood pressure was 120/80.
# Payment Method: Visa ending in 4532
# Contact: (555) 123-4567
# """
# CrewAIAgentFlow(document)