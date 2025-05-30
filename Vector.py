
import os
import openai
import time
from pinecone import Pinecone, ServerlessSpec
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()

class TextEmbedder:
    def __init__(self, directory, api_key, pinecone_api_key, index_name, chunk_size=1000, overlap=100):
        self.directory = directory
        self.api_key = api_key or os.getenv("API_KEY")
        self.pinecone_api_key = pinecone_api_key or os.getenv("PINECONE_API_KEY")
        self.index_name = index_name or os.getenv("INDEX_NAME")
        self.chunk_size = chunk_size
        self.overlap = overlap
        openai.api_key = self.api_key
        self.client = openai.OpenAI(api_key=self.api_key)
       
        self.pc = Pinecone(api_key=self.pinecone_api_key)
       
        if self.index_name not in self.pc.list_indexes().names():
            print(f"Creating index {self.index_name}...")
            self.pc.create_index(
                name=self.index_name,
                dimension=1536,
                metric='cosine',
                spec=ServerlessSpec(
                    cloud='aws',
                    region='us-east-1'
                )
            )
        else:
            print(f"Index {self.index_name} already exists.")
        self.index = self.pc.Index(self.index_name)
       
    def read_text_files(self):
        texts = []
        try:
            for filename in os.listdir(self.directory):
                if filename.endswith(".txt"):
                    file_path = os.path.join(self.directory, filename)
                    print(f"Reading file: {file_path}")
                    with open(file_path, 'r') as file:
                        text = file.read()
                        if text.strip():
                            texts.append(text)
                            print(f"Successfully read file {filename}")
                        else:
                            print(f"File {filename} is empty or not properly read.")
            if not texts:
                raise FileNotFoundError("No valid text files found in the directory.")
        except Exception as e:
            print(f"Error reading files: {e}")
            raise
        return texts
   
    def split_text_into_chunks(self, text):
        separator = '-- --------------------------------------------'
        chunks = text.split(separator)
        return [chunk.strip() for chunk in chunks if chunk.strip()]
 
    def get_embeddings(self, texts):
        embeddings = []
        for text in texts:
            chunks = self.split_text_into_chunks(text)
            for chunk in chunks:
                response = self.client.embeddings.create(
                    input=chunk,
                    model="text-embedding-3-small"
                )
                embedding_data = response.data[0].embedding
                embeddings.append((chunk, embedding_data))
                print(f"Embedded Data for '{chunk[:50]}...':\n{embedding_data}\n")
        return embeddings
 
    def process_files(self):
        retry_attempts = 3
        for attempt in range(retry_attempts):
            try:
                texts = self.read_text_files()
                embeddings = self.get_embeddings(texts)
                return embeddings
            except FileNotFoundError as e:
                print(f"Attempt {attempt+1}/{retry_attempts} failed: {e}")
                time.sleep(1)  # Wait before retrying
        raise FileNotFoundError("Failed to read text files after multiple attempts.")
   
    def upsert_embeddings_to_pinecone(self, embeddings):
        vectors = []
        for i, (text, embedding) in enumerate(embeddings):
            vector = {
                "id": f'embedding_{i}',
                "values": embedding,
                "metadata": {"text": text}
            }
            vectors.append(vector)
            print(f"Upserting vector ID: embedding_{i}")
        self.index.upsert(vectors=vectors)
        print("Upsert complete")
 
    def query_pinecone(self, user_query):
        print(f"Generating embedding for user query: {user_query}")
        embedding_response = self.client.embeddings.create(input=user_query, model="text-embedding-3-small")
        embedding = embedding_response.data[0].embedding
        print(f"User query embedding: {embedding}")
 
        print("Querying Pinecone index...")
        matching_results = self.index.query(
            vector=embedding,
            top_k=10,
            include_values=True,
            include_metadata=True
        )
 
        print("Query Results:")
        print(matching_results)
        
        return matching_results
 
if __name__ == "__main__":
    directory = "files/"
    api_key = os.environ.get("API_KEY")
    pinecone_api_key = "1ef2ce5e-05fc-4b52-8a02-27fae3251895"
    index_name = 'chat-bot-index'
    embedder = TextEmbedder(directory, api_key, pinecone_api_key, index_name)
    embeddings = embedder.process_files()
    embedder.upsert_embeddings_to_pinecone(embeddings)
    print("Embeddings have been upserted to Pinecone.")
