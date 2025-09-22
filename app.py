from flask import Flask, request, jsonify
from flask_cors import CORS
import nltk
from nltk.corpus import wordnet
import random

# Download necessary NLTK data
nltk.download('punkt')
nltk.download('wordnet')
nltk.download('omw-1.4')

app = Flask(__name__)
CORS(app)

def humanise_text(text):
    """
    Simple NLP humaniser:
    - Splits into sentences
    - Replaces some words with synonyms
    - Adds minor variations for natural flow
    """
    sentences = nltk.sent_tokenize(text)
    humanised_sentences = []

    for sentence in sentences:
        words = sentence.split()
        new_words = []
        for word in words:
            # Replace some words with synonyms randomly
            if random.random() < 0.3:
                synonyms = wordnet.synsets(word)
                if synonyms:
                    lemmas = [lemma.name() for syn in synonyms for lemma in syn.lemmas()]
                    lemmas = [l.replace('_', ' ') for l in lemmas if l.lower() != word.lower()]
                    if lemmas:
                        word = random.choice(lemmas)
            new_words.append(word)
        humanised_sentences.append(" ".join(new_words))

    return " ".join(humanised_sentences)

@app.route("/api/humanise", methods=["POST"])
def humanise():
    data = request.get_json()
    text = data.get("text", "")
    if not text.strip():
        return jsonify({"humanisedText": ""})

    humanised = humanise_text(text)
    return jsonify({"humanisedText": humanised})

if __name__ == "__main__":
    app.run(debug=True)
