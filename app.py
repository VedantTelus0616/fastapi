import h5py
import base64
import uvicorn
import constants
import pandas as pd
import vector_db as vdb

from pydantic import BaseModel
from io import StringIO, BytesIO
from typing_extensions import Annotated
from fastapi import FastAPI, File, Form, UploadFile
from fastapi.responses import StreamingResponse

class Item(BaseModel):
    name: str

vector_db = vdb.VectorDB(
    constants.DB_PATH,
    constants.COLLECTION_NAME,
    constants.COLLECTION_METADATA,
    constants.EMBEDDING_MODEL_NAME,
)
app = FastAPI()

def parse_raw_data(raw_data):
    '''
    Parse raw data into csv format

    raw_data: Annotated[str, Form()]
    '''
    data = base64.b64decode(raw_data) # .decode("utf-8")
    data = BytesIO(data)
    df = pd.read_csv(data)
    return df

def stream_dataframe(dataframe):
    '''
    Return a dataframe as a stream
    '''
    stream = StringIO()
    dataframe.to_csv(stream, index=False)
    response = StreamingResponse(iter([stream.getvalue()]), media_type="text/csv")
    response.headers["content-Disposition"] = "attachment; filename=result.csv"
    return response

def get_csv_documents(csv_file: bytes, col_name: str):
    '''
    Parse the csv_file for the required column

    csv_file: File
    col_name: str
    '''
    data = BytesIO(csv_file)
    df = pd.read_csv(data)
    col_values = df[col_name].values
    return df, col_values

def add_results_to_df(dataframe, db_results, compare_within=False):
    '''
    Add the results to the dataframe
    '''
    sim_p_1 = []
    sim_s_1 = []
    sim_p_2 = []
    sim_s_2 = []
    for prompts, scores in zip(db_results['documents'], db_results['distances']):
        if not compare_within:
            p_1, p_2 = prompts
            s_1, s_2 = scores
        else:
            # we are skipping the 0th item when "comparing within" because
            # the first returned item will always be itself, when the entire collection
            # is made of only the given prompts
            p_1, p_2 = prompts[1:]
            s_1, s_2 = scores[1:]
        
        s_1 = 1 - s_1 / 2
        s_2 = 1 - s_2 / 2
        sim_p_1.append(p_1)
        sim_p_2.append(p_2)
        sim_s_1.append(s_1)
        sim_s_2.append(s_2)
    dataframe[constants.SIM_P_1] = sim_p_1
    dataframe[constants.SIM_S_1] = sim_s_1
    dataframe[constants.SIM_P_2] = sim_p_2
    dataframe[constants.SIM_S_2] = sim_s_2
    return dataframe

@app.get("/")
async def root():
    return {"message": "Hello World"}

@app.post("/dedup")
async def dedup(csv_file: Annotated[bytes, File()], col_name: Annotated[str, Form()]):
    df, documents = get_csv_documents(csv_file, col_name)
    # result = vector_db.compare_all(documents)
    results = vector_db.compare_all(documents.tolist())
    df = add_results_to_df(df, results)
    return stream_dataframe(df)

@app.post("/dedup_within")
async def dedup_within(csv_file: Annotated[bytes, File()], col_name: Annotated[str, Form()]):
    df, documents = get_csv_documents(csv_file, col_name)
    results = vector_db.compare_within(documents.tolist())
    df = add_results_to_df(df, results, compare_within=True)
    return stream_dataframe(df)

@app.get("/purge")
async def purge():
    vector_db.purge_collection()
    return "Purged Collection"

@app.post("/update")
async def update(csv_file: Annotated[bytes, File()], col_name: Annotated[str, Form()]):
    df, documents = get_csv_documents(csv_file, col_name)
    cur_count = vector_db.count()
    vector_db.update(documents.tolist())
    new_count = vector_db.count()
    return f"Embedding count increased from {cur_count} to {new_count}"

@app.post("/upsert")
async def upsert(csv_file: Annotated[bytes, File()], col_name: Annotated[str, Form()]):
    print('Upserting')
    df, documents = get_csv_documents(csv_file, col_name)
    vector_db.update(documents.tolist())
    return f"Inserted {len(df)} Documents"

@app.post("/upsert_h5")
async def upsert_h5(h5_bytes: Annotated[bytes, File()]):
    h5_file = BytesIO(h5_bytes)
    h5_file = h5py.File(h5_file, 'r')
    documents = [doc.decode('utf-8') for doc in h5_file['strings']]
    embeddings = h5_file['embeddings'][:]
    print(len(documents))
    vector_db.update_h5(documents, embeddings)
    return "Updated DB"


if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8000)