import json

# Load predictions from predictions.json
def load_predictions(file_path="predictions.json"):
    try:
        with open(file_path, "r") as f:
            predictions = json.load(f)
        return predictions
    except Exception as e:
        return {"error": f"Failed to load predictions: {e}"}

# Format predictions for user queries
def format_predictions(predictions):
    if "error" in predictions:
        return predictions["error"]

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

# Query GPT for specific predictions
def query_gpt(user_query):
    predictions = load_predictions()

    if "which coins" in user_query.lower():
        # List all top gainers
        return format_predictions(predictions)
    
    elif "btc" in user_query.lower():
        # Specific query for BTC
        for pred in predictions:
            if pred["symbol"].lower() == "btc":
                return (
                    f"BTC Prediction:\n"
                    f"Price: ${pred['price']:.2f}\n"
                    f"Change (24h): {pred['percent_change_24h']:.2f}%\n"
                    f"Volume: ${pred['volume_24h']:.2f}\n"
                    f"Galaxy Score: {pred['galaxy_score']:.2f}\n"
                    f"Reason: {pred['reason']}"
                )
        return "BTC data is not available in the predictions."

    return "I'm not sure about that. Try asking about the top coins or a specific coin like BTC."

# Example Usage
if __name__ == "__main__":
    print("Example GPT Query Responses:")
    print(query_gpt("Which coins will gain the most in the next 24 hours?"))
    print(query_gpt("What about BTC?"))
    print(query_gpt("Tell me about ETH."))
