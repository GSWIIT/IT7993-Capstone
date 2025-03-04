from datasketch import MinHash
import numpy as np

def create_lsh_embedding_hash(embedding):
    m = MinHash(num_perm=128)
    for value in embedding:
        m.update(str(value).encode('utf8'))
    return m

# Generate LSH for two similar face embeddings
embedding1 = np.random.rand(128)  # Simulated face embedding
embedding2 = embedding1 + (np.random.rand(128) * 0.01)  # Slightly modified embedding

hash1 = create_lsh_embedding_hash(embedding1)
hash2 = create_lsh_embedding_hash(embedding2)

similarity = hash1.jaccard(hash2)
print("Similarity:", similarity)  # Should be high for the same person