import os
import urllib.request
from dotenv import load_dotenv
from langchain.document_loaders.csv_loader import CSVLoader
from langchain.text_splitter import RecursiveCharacterTextSplitter
from langchain.vectorstores import DeepLake
from langchain.embeddings.openai import OpenAIEmbeddings
from langchain.chains import RetrievalQA
from langchain.chat_models import ChatOpenAI
import time

def download_csv(url, filename):
    """
    Download a CSV file from a given URL and save it with the specified filename.
    If a file with the same name already exists, it will be overwritten.
    
    Parameters:
    - url (str): The URL of the CSV file to download.
    - filename (str): The name to save the downloaded file as.
    """
    urllib.request.urlretrieve(url, filename)
    print(f"Downloaded and saved {filename} from {url}")

def load_data(file_path):
    loader = CSVLoader(file_path=file_path)
    print("loading CSV file...")
    data = loader.load()

    print("Splitting files in chunks...")
    text_splitter = RecursiveCharacterTextSplitter(
        chunk_size=500,
        chunk_overlap=50,
        length_function=len,
        add_start_index=True,
    )
    chunks = text_splitter.split_documents(data)
    print(f'Split the pages in {len(chunks)} chunks')
    return chunks

def setup_vector_database(chunks, embedding_model, dataset_path):
    embeddings = OpenAIEmbeddings(model=embedding_model, disallowed_special=())
    deep_lake = DeepLake(dataset_path=dataset_path, embedding=embeddings, overwrite=True)
    deep_lake.add_documents(chunks)
    print('Vector database updated.')
    retriever = deep_lake.as_retriever()
    retriever.search_kwargs.update({
        'distance_metric': 'cos',
        'fetch_k': 10,
        'maximal_marginal_relevance': True,
        'k': 5,
    })
    return retriever

def ask_question(retriever, language_model):

    llm = ChatOpenAI(model_name=language_model, temperature=0)
    qa_chain = RetrievalQA.from_chain_type(llm, retriever=retriever)
    test_question = 'Is there an advisory circular about icing?'
    print('Asking test question...')
    result = qa_chain({"query": test_question})
    return result["result"]

def index_data():
    load_dotenv()
    os.environ['OPENAI_API_KEY'] = os.getenv('OPENAI_API_KEY')
    os.environ['ACTIVELOOP_TOKEN'] = os.getenv('ACTIVELOOP_TOKEN')
    language_model = os.getenv('LANGUAGE_MODEL')
    embedding_model = os.getenv('EMBEDDINGS_MODEL')
    dataset_path = os.getenv('DATASET_PATH')

    CSV_URL = "https://www.faa.gov/regulations_policies/advisory_circulars/index.cfm/go/document.exportAll/statusID/2"
    FILE_NAME = "advisory_circulars_list.csv"
    download_csv(CSV_URL, FILE_NAME)

    chunks = load_data(FILE_NAME)
    retriever = setup_vector_database(chunks, embedding_model, dataset_path)
    result = ask_question(retriever, language_model)
    print(result)

def run_indexing_periodically():
    while True:
        index_data()  # This is the function that runs your indexing script
        print('Done indexing. Will index again in 24 hours.') 
        time.sleep(86400)  # Sleep for 24 hours

#run_indexing_periodically()

if __name__ == "__main__":
    index_data()
