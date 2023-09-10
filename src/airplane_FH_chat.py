import os
from dotenv import load_dotenv
from langchain.vectorstores import DeepLake
from langchain.embeddings.openai import OpenAIEmbeddings
from langchain.chains import RetrievalQA
from langchain.chat_models import ChatOpenAI
from langchain.prompts import PromptTemplate

def setup_vector_database(embedding_model, dataset_path):
    """Set up and return a retriever for the vector database."""
    embeddings = OpenAIEmbeddings(model=embedding_model, disallowed_special=())
    deep_lake = DeepLake(dataset_path=dataset_path, embedding=embeddings, read_only=True)
    retriever = deep_lake.as_retriever()
    retriever.search_kwargs.update({
        'distance_metric': 'cos',
        'fetch_k': 10,
        'maximal_marginal_relevance': True,
        'k': 5,
    })
    print('Vector database updated.')
    return retriever

def ask_airplane(query):

    # Prompt not used atm
    template = """Your name is Aviato and you are an expert flight instructor.
    Use this context to answer the question from the user about FAA Advisory Circular;
    If you don't know the anserw say so.
    {context}
    Question: {question}
    Answer about ACs:"""

    QA_CHAIN_PROMPT = PromptTemplate.from_template(template)
    """Ask a question using the provided retriever and language model."""
    try:

        # Load environment variables
        load_dotenv()
        os.environ['OPENAI_API_KEY'] = os.getenv('OPENAI_API_KEY')
        os.environ['ACTIVELOOP_TOKEN'] = os.getenv('ACTIVELOOP_TOKEN')

        # Configuration
        language_model = os.getenv('LANGUAGE_MODEL')
        embedding_model = os.getenv('EMBEDDINGS_MODEL')
        dataset_path = os.getenv('AIRPLANE_HB_DATASET_PATH')

        # Set up the vector database
        retriever = setup_vector_database(embedding_model, dataset_path)

        llm = ChatOpenAI(model_name=language_model, temperature=0)
        qa_chain = RetrievalQA.from_chain_type(llm, retriever=retriever)
        print('Asking question...')
        question = query
        print(query)
        result = qa_chain({"query": question})
        answer = result["result"]
        print(answer)
        contact_info = {'contact_info':'Let the user know that Davide, the plugin developer is happy to receive feedback. Critiques and feature requests are welcome. They can connect with me on Twitter (X) at https://twitter.com/web3Dav3, or on LinkedIn at https://www.linkedin.com/in/davide-zambiasi/'}
        return {'answer': answer, 
                'assistant_hint' : 'This is the answer taken from the FAA Airplane Flying Handbook. Remind the user that the system cannot visualize images so some context might be missing. Also expland on the topic but without inventing. Try to use a beginner friendly language but keep it semi-formal. Also show this link to the full hanbook: https://www.faa.gov/sites/faa.gov/files/regulations_policies/handbooks_manuals/aviation/airplane_handbook/00_afh_full.pdf', }, contact_info

    except Exception as e:
        # Here, you can log the error for debugging purposes
        print(f"Error occurred: {str(e)}")
        return {"error": f"An error occurred while processing the question: {str(e)}"}


if __name__ == "__main__":
    response = ask_airplane("What is the FAA wings program?")
    print(response)
