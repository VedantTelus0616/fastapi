DB_PATH = './DB/'
COLLECTION_NAME = 'prompt_embeddings'
COLLECTION_METADATA = {'hnsw:space': 'cosine'}
EMBEDDING_MODEL_NAME = 'sentence-transformers/all-mpnet-base-v2'

SIM_P_1 = 'similar_prompt_1'
SIM_S_1 = 'similar_prompt_score_1'
SIM_P_2 = 'similar_prompt_2'
SIM_S_2 = 'similar_prompt_score_2'

QS = 'Questions'
DIST = 'distances'
DOC = 'documents'
SIM_SCORE = 'similarity_score'
SIM_QS = 'similar_qs'