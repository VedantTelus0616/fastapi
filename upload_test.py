import json
import requests

def send_json_file(url, filename):
  """
  Sends a JSON file to the specified FastAPI endpoint.

  Args:
      url: The URL of the FastAPI endpoint.
      filename: The path to the JSON file.
  """
  # Open the JSON file
  with open(filename, 'rb') as f:
      file_data = f.read()

  # Set headers indicating multipart form data upload
  headers = {'Content-Type': 'multipart/form-data'}

  # Prepare the data payload
  files = {'file': (filename, file_data, 'application/json')}

  try:
      response = requests.post(url, files=files, headers=headers)
      response.raise_for_status()  # Raise an exception for non-2xx status codes
      print(response.json())  # Print the response data (usually a success message)
  except requests.exceptions.RequestException as e:
      print(f"Error sending JSON file: {e}")

# Example usage
url = "http://0.0.0.0:8000"  # Replace with your actual URL
filename = "/home/shared/sri/nlp/code_gen/notebooks/Batch2_023_Dedup_qwen72b.json"  # Replace with your JSON file path
res = send_json_file(url, filename)
print(len(res))
print(res[0])
