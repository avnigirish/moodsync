# from transformers import pipeline

# # Load the Hugging Face sentiment-analysis model
# sentiment_analyzer = pipeline("sentiment-analysis")

# def analyze_mood(text):
#     result = sentiment_analyzer(text)
#     return result

# # Example usage
# text = "I am feeling great today!"
# mood = analyze_mood(text)
# print(mood)

from transformers import pipeline

sentiment_analyzer = pipeline("sentiment-analysis", model="distilbert-base-uncased-finetuned-sst-2-english", framework="pt")
result = sentiment_analyzer("I am very happy!")
print(result)


