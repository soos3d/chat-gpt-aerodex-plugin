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
from langchain.document_loaders import PyPDFLoader

load_dotenv()
os.environ['OPENAI_API_KEY'] = os.getenv('OPENAI_API_KEY')
os.environ['ACTIVELOOP_TOKEN'] = os.getenv('ACTIVELOOP_TOKEN')


def download_pdf(url, filename):
    """
    Download a CSV file from a given URL and save it with the specified filename.
    If a file with the same name already exists, it will be overwritten.
    
    Parameters:
    - url (str): The URL of the CSV file to download.
    - filename (str): The name to save the downloaded file as.
    """
    print('Downloading file...')
    urllib.request.urlretrieve(url, filename)
    print(f"Downloaded and saved {filename} from {url}")


HANDBOOK_URL = "https://www.faa.gov/sites/faa.gov/files/regulations_policies/handbooks_manuals/aviation/airplane_handbook/00_afh_full.pdf"
FILE_NAME = "airplane_flying_handbook.pdf"

#download_pdf(HANDBOOK_URL, FILE_NAME)

def load_data():
    print('Loading file...')
    # Use the PyPDFLoader to load and parse the PDF
    loader = PyPDFLoader(f"./{FILE_NAME}")
    pages = loader.load()
    #print(f'Made {len(pages)} chunks')

    print("Splitting files in chunks...")
    text_splitter = RecursiveCharacterTextSplitter(
        chunk_size=2000,
        chunk_overlap=200,
        length_function=len,
        add_start_index=True,
    )

    chunks = text_splitter.split_documents(pages)
    print(f'Split the pages in {len(chunks)} chunks')

    return chunks

def setup_vector_database(chunks):
    
    embedding_model = os.getenv('EMBEDDINGS_MODEL')
    dataset_path = os.getenv('AIRPLANE_HB_DATASET_PATH')
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

language_model = os.getenv('LANGUAGE_MODEL')
text = load_data()
setup_vector_database(text)