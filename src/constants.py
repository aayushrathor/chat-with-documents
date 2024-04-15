import os

from chromadb.config import Settings

from langchain.document_loaders import CSVLoader, PDFMinerLoader, TextLoader, UnstructuredExcelLoader, Docx2txtLoader
from langchain.document_loaders import UnstructuredFileLoader, UnstructuredMarkdownLoader
from langchain.document_loaders import UnstructuredHTMLLoader

ROOT_DIRECTORY = os.path.dirname(os.path.realpath(__file__))
SOURCE_DIRECTORY = f"{ROOT_DIRECTORY}/data"
PERSIST_DIRECTORY = f"{ROOT_DIRECTORY}/vectorstores/db"

MODELS_PATH = "./models"
INGEST_THREADS = os.cpu_count() or 8

CHROMA_SETTINGS = Settings(
    anonymized_telemetry=False,
    is_persistent=True,
)
CONTEXT_WINDOW_SIZE = 4096
MAX_NEW_TOKENS = CONTEXT_WINDOW_SIZE  # int(CONTEXT_WINDOW_SIZE/4)

# https://python.langchain.com/en/latest/_modules/langchain/document_loaders/excel.html#UnstructuredExcelLoader
DOCUMENT_MAP = {
    ".html": UnstructuredHTMLLoader,
    ".txt": TextLoader,
    ".md": UnstructuredMarkdownLoader,
    ".py": TextLoader,
    # ".pdf": PDFMinerLoader,
    ".pdf": UnstructuredFileLoader,
    ".csv": CSVLoader,
    ".xls": UnstructuredExcelLoader,
    ".xlsx": UnstructuredExcelLoader,
    ".docx": Docx2txtLoader,
    ".doc": Docx2txtLoader,
}

# EMBEDDING_MODEL_NAME = "hkunlp/instructor-large"  # Uses 1.5 GB of VRAM (High Accuracy with lower VRAM usage)
# EMBEDDING_MODEL_NAME = "hkunlp/instructor-xl" # Uses 5 GB of VRAM (Most Accurate of all models)
# EMBEDDING_MODEL_NAME = "intfloat/e5-large-v2" # Uses 1.5 GB of VRAM (A little less accurate than instructor-large)
# EMBEDDING_MODEL_NAME = "intfloat/e5-base-v2" # Uses 0.5 GB of VRAM (A good model for lower VRAM GPUs)
EMBEDDING_MODEL_NAME = "all-MiniLM-L6-v2" # Uses 0.2 GB of VRAM (Less accurate but fastest - only requires 150mb of vram)

####
#### MULTILINGUAL EMBEDDING MODELS
####

# EMBEDDING_MODEL_NAME = "intfloat/multilingual-e5-large" # Uses 2.5 GB of VRAM
# EMBEDDING_MODEL_NAME = "intfloat/multilingual-e5-base" # Uses 1.2 GB of VRAM
