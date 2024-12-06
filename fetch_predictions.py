import requests
import zipfile
import os
import json

def fetch_predictions_from_github():
    owner = "RecepU"
    repo = "PredictionCyrpto"
    headers = {"Authorization": f"Bearer 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"}  # Replace with your token

# Get the list of artifacts
    url = f"https://api.github.com/repos/{owner}/{repo}/actions/artifacts"
    response = requests.get(url, headers=headers)

    print("Response Status Code:", response.status_code)
    if response.status_code != 200:
        print("Failed to fetch artifacts.")
        return False

    artifacts = response.json().get("artifacts", [])
    for artifact in artifacts:
        print(f"Found Artifact: {artifact['name']}")
        if artifact["name"] == "predictions":
            # Download the artifact
            download_url = artifact["archive_download_url"]
            download_response = requests.get(download_url, headers=headers)
            if download_response.status_code == 200:
                with open("predictions.json.zip", "wb") as f:
                    f.write(download_response.content)
                print("Predictions artifact downloaded successfully.")
                return True
            else:
                print(f"Failed to download artifact. Status Code: {download_response.status_code}")
    print("No predictions artifact found.")
    return False

def extract_and_validate_predictions():
    # Unzip the artifact
    if not os.path.exists("predictions.json.zip"):
        raise FileNotFoundError("The file predictions.json.zip does not exist.")
    
    with zipfile.ZipFile("predictions.json.zip", "r") as zip_ref:
        zip_ref.extractall(".")
    
    # Load and validate the predictions JSON
    try:
        with open("predictions.json", "r") as f:
            data = f.read().strip()
            print("Raw predictions.json content:", data)  # Debugging step
            if not data:
                raise ValueError("The predictions.json file is empty.")
            
            predictions = json.loads(data)  # Validate JSON format
            
            # Re-save the JSON file to ensure a clean format
            with open("predictions.json", "w") as clean_file:
                json.dump(predictions, clean_file, indent=4)
            
            print("Predictions JSON validated and cleaned.")
            return predictions
    except json.JSONDecodeError as e:
        raise ValueError(f"Invalid JSON format in predictions.json: {e}") from e

def format_predictions(predictions):
    if not predictions:
        return "No predictions available."
    result = "Top Predicted Gainers for the Next 24 Hours:\n"
    for pred in predictions:
        result += (
            f"Symbol: {pred['symbol']}\n"
            f"Price: ${pred['price']:.2f}\n"
            f"Change (24h): {pred['percent_change_24h']:.2f}%\n"
            f"Volume: ${pred['volume_24h']:.2f}\n"
            f"Galaxy Score: {pred['galaxy_score']:.2f}\n"
            f"Reason: {pred['reason']}\n\n"
        )
    return result

# Main function to handle everything
if __name__ == "__main__":
    if fetch_predictions_from_github():
        try:
            predictions = extract_and_validate_predictions()
            print(format_predictions(predictions))
        except Exception as e:
            print(f"Error: {e}")
    else:
        print("Failed to fetch predictions.")