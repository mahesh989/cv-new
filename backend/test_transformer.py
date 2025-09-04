# test_transformer.py
from sentence_transformers import SentenceTransformer

def main():
    print("Loading model...")
    model = SentenceTransformer('all-MiniLM-L6-v2', device='cpu')
    print("Model loaded successfully!")

    # Test the model
    sentences = ['This is a test sentence.', 'Another test sentence.']
    embeddings = model.encode(sentences)
    print(f"Generated embeddings with shape: {embeddings.shape}")

if __name__ == "__main__":
    main()