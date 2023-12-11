# API to dedup prompts
Accepts csv files with prompts to be deduplicated against itself as well as against the existing corpus

Steps to build docker image

`docker build -t <image_name> .` 

Steps to run docker image

`docker run -d -p 80:80 <image_name>`

## Endpoints to use

**ALL INPUT IS VIA FORM FIELDS**

### Points to note:
- When starting the image for the first time, update the DB. A local DB is being used, hence it needs to be populated before being used.
- Use `/purge` to clear the DB of all existing data
- Always update the db after a purge

### /update

Adds new prompts to the DB. Always use this to add new deduped prompts to the DB. 

Form Data Inputs:
```
csv_file: bytes 
col_name: str : Name of the column to consider for deduplication
```

cURL
```
curl --location '0.0.0.0/update' \
--form 'csv_file=@"path_to_file"' \
--form 'col_name="name_of_column"'
```

### /dedup
Given a csv_file with a column of prompts, this API identifies the closest set of prompts in the DB.

Form Data Inputs:
```
csv_file: bytes 
col_name: str : Name of the column to consider for deduplication
```

cURL
```
curl --location '0.0.0.0/dedup' \
--form 'csv_file=@"path_to_file"' \
--form 'col_name="name_of_column"'
```

Returns the same CSV file with 4 added columns
```
similar_prompt_1 : str: Text of the closest prompt
similar_prompt_score_1 : float: A value between 0 and 1. The closer the score is to 1, the more similar the prompts are
similar_prompt_2 : str: Text of the closest prompt
similar_prompt_score_2 : float: A value between 0 and 1. The closer the score is to 1, the more similar the prompts are
```

### /dedup_within
Compares all the prompts in the csv_file with itself to identify duplicates

Form Data Inputs:
```
csv_file: bytes 
col_name: str : Name of the column to consider for deduplication
```

cURL
```
curl --location '0.0.0.0/dedup_within' \
--form 'csv_file=@"path_to_file"' \
--form 'col_name="name_of_column"'
```

Returns the same CSV file with 4 added columns
```
similar_prompt_1 : str: Text of the closest prompt
similar_prompt_score_1 : float: A value between 0 and 1. The closer the score is to 1, the more similar the prompts are
similar_prompt_2 : str: Text of the closest prompt
similar_prompt_score_2 : float: A value between 0 and 1. The closer the score is to 1, the more similar the prompts are
```

### /purge 
Purges the DB collection of all existing prompts and their embeddings

cURL
```
curl --location '0.0.0.0/purge'
```

### /upsert
Same as `/update`
Utilise `/update` instead

cURL
```
curl --location '0.0.0.0/upsert' \
--form 'csv_file=@"path_to_csv_file"' \
--form 'col_name="name_of_column"'
```

### /upsert_h5
For developer use

Upload a H5 file containing prompts and their embeddings. 

H5 file structure
```
{
    'strings': numpy.array[prompts],
    'strings': numpy.array[embeddings]
}
```

cURL
```
curl --location '0.0.0.0/upsert_h5' \
--form 'h5_bytes=@"name_of_h5_file"'
```

Form Data Inputs:
```
h5_bytes: bytes 
```

