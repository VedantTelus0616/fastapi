import re
import chromadb

from uuid import uuid4
from chromadb.utils import embedding_functions
from sentence_transformers import SentenceTransformer

class VectorDB:
    IDS = 'ids'
    DIST = 'distances'
    META = 'metadatas'
    EMB = 'embeddings'
    DOC = 'documents'
    URIS = 'uris'
    DATA = 'data'
    
    def __init__(self, db_path, collection_name, collection_metadata, embedding_model_name):
        '''
        Setup the vector DB
        
        db_path: str: Path on disk to where the DB is stored
        collection_name: str: Name of collection
        collection_metadata: Dict: 
        embedding_model_name: str: Name of model used to compute embeddings
        '''
        
        self.client = chromadb.PersistentClient(path=db_path)
        # self.client = chromadb.Client()
        self.emb_function = embedding_functions.SentenceTransformerEmbeddingFunction(model_name=embedding_model_name)
        self.metadata = collection_metadata
        self.collection_name = collection_name
        self.model = SentenceTransformer(embedding_model_name)
        
        # if no collection, create it
        try:
            self.collection = self.client.get_collection(collection_name, embedding_function=self.emb_function)
        except ValueError as err:
            print(f'Collection {collection_name} not availble. Creating it instead')
            self.collection = self.client.create_collection(
                name=collection_name,
                metadata=collection_metadata,
                embedding_function=self.emb_function
            )
    
    def normalise_results(self, results):
        normalised_distances = []
        distances = results[self.DIST]
        for distance in distances:
            normalised_dist = 1 - (distance / 2)
            normalised_distances.append(normalised_dist)
        results[self.DIST] = normalised_distances
        return results
        
    
    def compare_all(self, all_documents, n_results=2):
        '''
        Compares the given set of documents with all documents in the db
        
        all_documents: List[str]: List of documents where each document is a str
        n_results: int: number of results to query for
        normalise: bool: if True, return distances in 0-1 range
        '''
        if n_results <= 0:
            n_results = 2

        embeddings = self.model.encode(all_documents)
        
        results = self.collection.query(
            query_embeddings=embeddings.tolist(),
            n_results=n_results,
            include=[self.EMB, self.DIST, self.DOC]
        )

        for emb in results['embeddings']:
            if emb is not None:
                print(len(emb[0]))
        
        return results
    
    def compare_within(self, all_documents, n_results=3):
        '''
        Compares the given set of documents with each other
        
        all_documents: List[str]: List of documents where each document is a str
        n_results: int: number of results to query for
        normalise: bool: if True, return distances in 0-1 range
        '''
        if n_results <= 0:
            n_results = 2 + 1
        
        new_collection_name = str(uuid4())
        collection = self.client.get_or_create_collection(
            name=new_collection_name,
            metadata=self.metadata,
            embedding_function=self.emb_function
        )

        embeddings = self.model.encode(all_documents)
        
        collection.add(
            documents=all_documents,
            embeddings=embeddings.tolist(),
            ids=[str(uuid4()) for x in all_documents]
        )

        results = collection.query(
            query_embeddings=embeddings.tolist(),
            n_results=n_results
        )
        
        self.client.delete_collection(name=new_collection_name)
        
        return results
    
    def update(self, new_documents):
        '''
        Add new documents to the DB
        
        new_documents: List[str]: Each document is a string
        '''
        self.collection.add(
            ids=[str(uuid4()) for doc in new_documents],
            documents=new_documents)
    
    def purge_collection(self):
        '''
        Purge the DB of all documents
        '''
        self.client.delete_collection(name=self.collection_name)
        self.collection = self.client.create_collection(
            name=self.collection_name,
            metadata=self.metadata,
            embedding_function=self.emb_function
        )

    def update_h5(self, documents, embeddings):
        '''
        Update the vector store with documents and embeddings

        documents : np.array[str]
        embeddings: np.array: Size [num_docs X 768]
        '''
        self.collection.add(
            documents=documents,
            embeddings=embeddings.tolist(),
            ids=[str(uuid4()) for x in documents]
        )

    def count(self):
        '''
        Get count of embeddings
        '''
        return self.collection.count()