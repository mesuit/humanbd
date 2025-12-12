from flask import Flask, request, jsonify
from flask_cors import CORS
import nltk
import torch
from transformers import AutoTokenizer, AutoModelForSeq2SeqLM

# Download necessary NLTK data (for sentence splitting)
try:
    nltk.data.find('tokenizers/punkt')
except LookupError:
    nltk.download('punkt')

app = Flask(__name__)
CORS(app)

# --- LOAD THE ADVANCED AI MODEL ---
# We use a T5 model fine-tuned for paraphrasing. 
# This runs locally on your machine.
MODEL_NAME = "Vamsi/T5_Paraphrase_Paws"
print(f"Loading model {MODEL_NAME}...")

device = "cuda" if torch.cuda.is_available() else "cpu"
tokenizer = AutoTokenizer.from_pretrained(MODEL_NAME)
model = AutoModelForSeq2SeqLM.from_pretrained(MODEL_NAME).to(device)

print(f"Model loaded on {device}. Ready to humanise.")

def humanise_text(text):
    """
    Advanced NLP humaniser using T5 Transformer:
    - Splits text into sentences.
    - Uses a neural network to generate natural paraphrases for each sentence.
    """
    # Split text into sentences to process them individually
    sentences = nltk.sent_tokenize(text)
    humanised_sentences = []

    for sentence in sentences:
        # Prepare input for the model
        text_input = "paraphrase: " + sentence + " </s>"
        
        encoding = tokenizer.encode_plus(
            text_input,
            padding="longest",
            return_tensors="pt"
        )
        
        input_ids = encoding["input_ids"].to(device)
        attention_masks = encoding["attention_mask"].to(device)

        # Generate the paraphrase
        # num_beams=5 ensures higher quality outputs by exploring multiple possibilities
        outputs = model.generate(
            input_ids=input_ids, 
            attention_mask=attention_masks,
            max_length=256,
            do_sample=True, # Adds variety (human-like randomness)
            top_k=120,
            top_p=0.95,
            early_stopping=True,
            num_return_sequences=1
        )

        line = tokenizer.decode(outputs[0], skip_special_tokens=True, clean_up_tokenization_spaces=True)
        humanised_sentences.append(line)

    return " ".join(humanised_sentences)

@app.route("/api/humanise", methods=["POST"])
def humanise():
    data = request.get_json()
    text = data.get("text", "")
    
    if not text.strip():
        return jsonify({"humanisedText": ""})

    # Basic error handling
    try:
        humanised = humanise_text(text)
        return jsonify({"humanisedText": humanised})
    except Exception as e:
        print(f"Error: {e}")
        return jsonify({"error": "Failed to process text"}), 500

if __name__ == "__main__":
    app.run(debug=True, port=5000)
