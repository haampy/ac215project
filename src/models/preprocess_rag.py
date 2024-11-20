import os
import argparse
import pandas as pd
import time
import glob
import hashlib
import chromadb

# Vertex AI
import vertexai
from vertexai.language_models import TextEmbeddingInput, TextEmbeddingModel

import time
if 'GOOGLE_APPLICATION_CREDENTIALS' not in os.environ:
    os.environ['GOOGLE_APPLICATION_CREDENTIALS'] = 'service_account.json'

# Setup
GCP_PROJECT = "ac215-438907"
GCP_LOCATION = "us-central1"
EMBEDDING_MODEL = "text-embedding-004"
EMBEDDING_DIMENSION = 256
GENERATIVE_MODEL = "gemini-1.5-flash-001"
OUTPUT_FOLDER = "outputs"
CHROMADB_HOST = "127.0.0.1"
CHROMADB_PORT = 16990
DATABASE_DIR = 'database'
vertexai.init(project=GCP_PROJECT, location=GCP_LOCATION)
# https://cloud.google.com/vertex-ai/generative-ai/docs/model-reference/text-embeddings-api#python
embedding_model = TextEmbeddingModel.from_pretrained(EMBEDDING_MODEL)

def generate_query_embedding(query):
	query_embedding_inputs = [TextEmbeddingInput(task_type='RETRIEVAL_DOCUMENT', text=query)]
	kwargs = dict(output_dimensionality=EMBEDDING_DIMENSION) if EMBEDDING_DIMENSION else {}
	embeddings = embedding_model.get_embeddings(query_embedding_inputs, **kwargs)
	return embeddings[0].values


def generate_text_embeddings(chunks, dimensionality: int = 256, batch_size=250):
	# Max batch size is 250 for Vertex AI
	all_embeddings = []
	for i in range(0, len(chunks), batch_size):
		batch = chunks[i:i+batch_size]
		inputs = [TextEmbeddingInput(text, "RETRIEVAL_DOCUMENT") for text in batch]
		kwargs = dict(output_dimensionality=dimensionality) if dimensionality else {}
		embeddings = embedding_model.get_embeddings(inputs, **kwargs) 
		all_embeddings.extend([embedding.values for embedding in embeddings])
		time.sleep(1) # change 1 to 20
	return all_embeddings


def load_text_embeddings(df, collection, batch_size=500):

	# Generate ids
	df["id"] = df.index.astype(str)
	hashed_books = df["drugName"].apply(lambda x: hashlib.sha256(x.encode()).hexdigest()[:16])
	df["id"] = hashed_books + "-" + df["id"]
	
	# Process data in batches
	total_inserted = 0
	for i in range(0, df.shape[0], batch_size):
		# Create a copy of the batch and reset the index
		batch = df.iloc[i:i+batch_size].copy().reset_index(drop=True)

		ids = batch["id"].tolist()
		documents = batch["chunk"].tolist() 
		metadatas = [dict(drugName=drugName_tmp) for drugName_tmp in batch["drugName"].tolist()]
		embeddings = batch["embedding"].tolist()

		collection.add(
			ids=ids,
			documents=documents,
			metadatas=metadatas,
			embeddings=embeddings
		)
		total_inserted += len(batch)
		print(f"Inserted {total_inserted} items...")

	print(f"Finished inserting {total_inserted} items into collection '{collection.name}'")

def chunk(database_path,method="char-split"):
	# Make dataset folders
	os.makedirs(OUTPUT_FOLDER, exist_ok=True)
	
	database_dir_path = os.path.join(".",DATABASE_DIR,database_path)
	df = pd.read_csv(database_dir_path,sep='\t')
	df['chunk'] = df.apply(lambda x: f"condition:{x['condition']}, review:\"{x['review']}\", rating:{x['rating']}, date:{x['date']}, usefulCount:{x['usefulCount']}", axis=1)
	df = df[['drugName', 'chunk']]
	df = df.head(500)
	jsonl_filename = os.path.join(OUTPUT_FOLDER, f"chunks-{method}-1.jsonl")
	with open(jsonl_filename, "w") as json_file:
		json_file.write(df.to_json(orient='records', lines=True))

def embed(method="char-split"):
	print("embed()")

	# Get the list of chunk files
	jsonl_files = glob.glob(os.path.join(OUTPUT_FOLDER, f"chunks-{method}-*.jsonl"))
	print("Number of files to process:", len(jsonl_files))

	# Process
	for jsonl_file in jsonl_files:
		print("Processing file:", jsonl_file)

		data_df = pd.read_json(jsonl_file, lines=True)
		print("Shape:", data_df.shape)
		print(data_df.head())

		chunks = data_df["chunk"].values
		if method == "semantic-split":
			embeddings = generate_text_embeddings(chunks,EMBEDDING_DIMENSION, batch_size=15)
		else:
			embeddings = generate_text_embeddings(chunks,EMBEDDING_DIMENSION, batch_size=100)
		data_df["embedding"] = embeddings

		# Save 
		print("Shape:", data_df.shape)
		print(data_df.head())

		jsonl_filename = jsonl_file.replace("chunks-","embeddings-")
		with open(jsonl_filename, "w") as json_file:
			json_file.write(data_df.to_json(orient='records', lines=True))
		
def load(method="char-split"):
	print("load()")

	# Connect to chroma DB
	client = chromadb.HttpClient(host=CHROMADB_HOST, port=CHROMADB_PORT)

	# Get a collection object from an existing collection, by name. If it doesn't exist, create it.
	collection_name = f"{method}-collection"
	print("Creating collection:", collection_name)

	try:
		# Clear out any existing items in the collection
		client.delete_collection(name=collection_name)
		print(f"Deleted existing collection '{collection_name}'")
	except Exception:
		print(f"Collection '{collection_name}' did not exist. Creating new.")

	collection = client.create_collection(name=collection_name, metadata={"hnsw:space": "cosine"})
	print(f"Created new empty collection '{collection_name}'")
	print("Collection:", collection)

	# Get the list of embedding files
	jsonl_files = glob.glob(os.path.join(OUTPUT_FOLDER, f"embeddings-{method}-*.jsonl"))
	print("Number of files to process:", len(jsonl_files))

	# Process
	for jsonl_file in jsonl_files:
		print("Processing file:", jsonl_file)

		data_df = pd.read_json(jsonl_file, lines=True)
		print("Shape:", data_df.shape)
		print(data_df.head())

		# Load data
		load_text_embeddings(data_df, collection)


def main(args=None):
	print("CLI Arguments:", args)

	chunk(database_path=args.database_path,method=args.chunk_type)
	embed(method=args.chunk_type)
	load(method=args.chunk_type)

if __name__ == "__main__":
	# Generate the inputs arguments parser
	# if you type into the terminal '--help', it will provide the description
	parser = argparse.ArgumentParser(description="CLI")
	parser.add_argument(
		"--database_path",
		type=str,
		default="drugsComTrain_raw.tsv",
		help="database path",
	)
	parser.add_argument("--chunk_type", default="char-split", help="char-split | recursive-split | semantic-split")

	args = parser.parse_args()

	main(args)