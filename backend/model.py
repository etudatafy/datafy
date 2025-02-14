import logging
from transformers import AutoTokenizer, AutoModelForCausalLM, BitsAndBytesConfig
import torch
import chromadb
from sentence_transformers import SentenceTransformer
from PyPDF2 import PdfReader
from langchain.text_splitter import RecursiveCharacterTextSplitter
# Suppress specific warning messages from ChromaDB and other modules
import warnings
warnings.filterwarnings("ignore", category=UserWarning, module="chromadb")
warnings.filterwarnings("ignore", category=UserWarning, module="transformers")
warnings.filterwarnings("ignore", category=UserWarning, module="torch")
warnings.filterwarnings("ignore", category=DeprecationWarning)
warnings.filterwarnings("ignore", category=FutureWarning)

# Configure logging to completely suppress unnecessary output
logging.basicConfig(level=logging.ERROR) 
logger = logging.getLogger(__name__)
logger.setLevel(logging.ERROR) 

# Suppress TensorFlow warnings
import tensorflow as tf
tf.get_logger().setLevel('ERROR')

# Model and database configurations
MODEL_NAME = "EleutherAI/gpt-neo-1.3B"
EMBEDDING_MODEL = "all-MiniLM-L6-v2"
DB_PATH = "./chroma_db"

class RAGModel:
    def __init__(self):
        """Initializes the language model and ChromaDB vector database."""
        self.tokenizer = AutoTokenizer.from_pretrained(MODEL_NAME)
        self.tokenizer.pad_token = self.tokenizer.eos_token
        self.model = AutoModelForCausalLM.from_pretrained(
            MODEL_NAME,
            device_map="auto",
            quantization_config=BitsAndBytesConfig(load_in_8bit=True),
        )
        
        self.embedding_model = SentenceTransformer(EMBEDDING_MODEL)
        
        self.chroma_client = chromadb.PersistentClient(path=DB_PATH)
        self.collection = self.chroma_client.get_or_create_collection("pdf_chunks")

    def generate_response(self, query, top_k=3, max_new_tokens=300):
        """Generates a response to the given query."""
        relevant_chunks = self.retrieve_relevant_chunks(query, top_k)
        context = "\n".join(relevant_chunks)
        full_prompt = f"Context: {context}\n\nQuestion: {query}\nAnswer:"
        
        inputs = self.tokenizer(full_prompt, return_tensors="pt", padding=True, truncation=True).to("cuda")
        outputs = self.model.generate(
            inputs.input_ids,
            max_new_tokens=max_new_tokens,
            num_return_sequences=1,
            do_sample=True,
            temperature=0.7,
            pad_token_id=self.tokenizer.eos_token_id,
        )
        
        generated_text = self.tokenizer.decode(outputs[0], skip_special_tokens=True)

        if "Answer:" in generated_text:
            generated_text = generated_text.split("Answer:")[-1].strip()
        
        return generated_text

    def retrieve_relevant_chunks(self, query, top_k=3):
        """Retrieves the most relevant text chunks based on the given query."""
        query_embedding = self.embedding_model.encode(query).tolist()
        results = self.collection.query(query_embeddings=[query_embedding], n_results=top_k)
        return [doc["text"] for doc in results["metadatas"][0]]

    def ingest_pdf(self, pdf_path):
        """Processes a PDF file and stores its contents in ChromaDB."""
        text = self.load_pdf_text(pdf_path)
        chunks = self.split_text(text)
        
        for i, chunk in enumerate(chunks):
            embedding = self.embedding_model.encode(chunk).tolist()
            self.collection.add(ids=[str(i)], embeddings=[embedding], metadatas=[{"text": chunk}])
    
    def load_pdf_text(self, pdf_path):
        """Extracts text from a PDF file."""
        reader = PdfReader(pdf_path)
        text = ""
        for page in reader.pages:
            text += page.extract_text() + "\n"
        return text

    def split_text(self, text, chunk_size=500, chunk_overlap=100):
        """Splits text into smaller chunks for efficient processing."""
        splitter = RecursiveCharacterTextSplitter(chunk_size=chunk_size, chunk_overlap=chunk_overlap)
        return splitter.split_text(text)

# Initialize the model globally
rag_model = RAGModel()

if __name__ == "__main__":
    # PDF Processing (only needed once)
    rag_model.ingest_pdf("./assets/pdf/yks_document.pdf")
    
    # Query processing
    query = "Nasil basarili olurum?"
    response = rag_model.generate_response(query)
    print("Model Response:", response)
