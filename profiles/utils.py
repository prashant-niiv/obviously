import json
import os

from django.conf import settings

import faiss
import numpy as np
from sentence_transformers import SentenceTransformer

# Load model globally once
EMBEDDING_MODEL = SentenceTransformer("all-MiniLM-L6-v2")


def get_embedding_model():
    """Returns the globally loaded model instance."""
    return EMBEDDING_MODEL


def load_faiss_index(embeddings):
    """
    Loads FAISS index if available, otherwise creates and saves a new index.
    """
    os.makedirs(settings.MEDIA_ROOT, exist_ok=True)  # Ensure MEDIA_ROOT exists
    FAISS_INDEX_PATH = os.path.join(settings.MEDIA_ROOT, "faiss_index.idx")  # FAISS index path

    if os.path.exists(FAISS_INDEX_PATH):
        index = faiss.read_index(FAISS_INDEX_PATH)
    else:
        index = faiss.IndexFlatL2(embeddings.shape[1])  # L2 distance index
        index.add(embeddings)
        faiss.write_index(index, FAISS_INDEX_PATH)

    return index


def find_similar_persons(name, top_k=5, threshold=0.5):
    from profiles.models import Person  # Delayed import to prevent circular import issue

    """
    Finds similar persons based on first_name + last_name embeddings using FAISS.
    """
    try:
        # Generate an embedding vector for the given name using the embedding model.
        embedding_model = get_embedding_model()
        embedding_vector = (np.array(embedding_model.encode(name), dtype="float32")).reshape(1, -1)
    except Exception:
        return []  # If the embedding model fails to load or encoding fails, return an empty list.

    # Fetch persons and their embeddings
    persons = Person.objects.exclude(embedding__isnull=True).exclude(embedding="").values_list("id", "embedding")
    if not persons:
        return []  # If no persons with embeddings are found, return an empty list.

    # Convert stored JSON embeddings to numpy array
    person_ids, embeddings = zip(*persons)
    embeddings = np.array([json.loads(e) for e in embeddings], dtype="float32")

    # Load FAISS index
    index = load_faiss_index(embeddings)

    # Perform similarity search
    distances, indices = index.search(embedding_vector, k=min(top_k, len(person_ids)))

    # Apply threshold filter and extract valid person IDs
    person_ids = [person_ids[i] for d, i in zip(distances[0], indices[0]) if d <= threshold and i >= 0]

    return Person.objects.filter(id__in=person_ids)
