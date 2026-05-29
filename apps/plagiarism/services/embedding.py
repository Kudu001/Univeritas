"""
Embedding service.

Text chunks  → all-MiniLM-L6-v2 (sentence-transformers) → 384-dim vectors
Code chunks  → microsoft/codebert-base (transformers)    → 768-dim vectors

Models are loaded lazily and cached at module level.
"""

_text_model = None
_code_tokenizer = None
_code_model = None


def load_text_model():
    global _text_model
    if _text_model is None:
        from sentence_transformers import SentenceTransformer
        _text_model = SentenceTransformer('all-MiniLM-L6-v2')
    return _text_model


def load_code_model():
    global _code_tokenizer, _code_model
    if _code_model is None:
        from transformers import AutoTokenizer, AutoModel
        _code_tokenizer = AutoTokenizer.from_pretrained('microsoft/codebert-base')
        _code_model = AutoModel.from_pretrained('microsoft/codebert-base')
        _code_model.eval()
    return _code_tokenizer, _code_model


def generate_text_embedding(text):
    """Generate 384-dim embedding using all-MiniLM-L6-v2. For text chunks only."""
    model = load_text_model()
    vector = model.encode(text, convert_to_numpy=True)
    return vector.tolist()


def generate_code_embedding(code):
    """Generate 768-dim embedding using CodeBERT. For code chunks only."""
    import torch
    tokenizer, model = load_code_model()
    inputs = tokenizer(
        code,
        return_tensors='pt',
        truncation=True,
        max_length=512,
        padding=True,
    )
    with torch.no_grad():
        outputs = model(**inputs)
    # Use mean pooling over token embeddings
    vector = outputs.last_hidden_state.mean(dim=1).squeeze().numpy()
    return vector.tolist()
