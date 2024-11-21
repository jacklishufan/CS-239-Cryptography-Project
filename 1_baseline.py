encoding_width = 2**13 # restricted by ckks size
database_size = 100
import time

# Client Setup

import numpy as np
from Pyfhel import Pyfhel, PyCtxt

print(f"[Client] Initializing Pyfhel session and data...")
HE_client = Pyfhel()           # Creating empty Pyfhel object
ckks_params = {
    'scheme': 'CKKS',   # can also be 'ckks'
    'n': 2**14,         # Polynomial modulus degree. For CKKS, n/2 values can be
                        #  encoded in a single ciphertext. 
                        #  Typ. 2^D for D in [10, 15]
    'scale': 2**30,     # All the encodings will use it for float->fixed point
                        #  conversion: x_fix = round(x_float * scale)
                        #  You can use this as default scale or use a different
                        #  scale on each operation (set in HE.encryptFrac)
    'qi_sizes': [60, 30, 30, 30, 60] # Number of bits of each prime in the chain. 
                        # Intermediate values should be  close to log2(scale)
                        # for each operation, to have small rounding errors.
}
HE_client.contextGen(**ckks_params)  # Generate context for bfv scheme
HE_client.keyGen() # Generates both a public and a private key
HE_client.relinKeyGen()
HE_client.rotateKeyGen()

# Generate and encrypt query vector
x = np.random.rand(encoding_width)
cx = HE_client.encrypt(x)

# Serializing data and public context information

start = time.time()
s_context    = HE_client.to_bytes_context()
s_public_key = HE_client.to_bytes_public_key()
s_relin_key  = HE_client.to_bytes_relin_key()
s_rotate_key = HE_client.to_bytes_rotate_key()
#s_cx         = [cx[j].to_bytes() for j in range(len(cx))]
s_cx         = cx.to_bytes()
end = time.time()

print(f"[Client] Sending HE_client={HE_client} and cx={cx}")
print(f"[Client] Sent {(len(s_context) + len(s_public_key) + len(s_relin_key) + len(s_rotate_key) + len(s_cx)) / (10**6)} MB")
print(f"[Client] Setup took {end - start}s")
print("="*40)

# Server Mock

def hyperbolic_distance_parts(u, v): # returns only the numerator and denominator of the hyperbolic distance formula
    diff = u - v
    du = -(1 - u @ u) # for some reason we need to negate this
    dv = -(1 - v @ v) # for some reason we need to negate this
    return diff @ diff, du * dv # returns the numerator and denominator

# document matrix containing rows of document encoding vectors
D = np.random.rand(database_size, encoding_width)

HE_server = Pyfhel()
HE_server.from_bytes_context(s_context)
HE_server.from_bytes_public_key(s_public_key)
HE_server.from_bytes_relin_key(s_relin_key)
HE_server.from_bytes_rotate_key(s_rotate_key)
cx = PyCtxt(pyfhel=HE_server, bytestring=s_cx)
print(f"[Server] Received HE_server={HE_server} and cx={cx}")

# Encode each document weights in plaintext
res = []
start = time.time()
for i in range(len(D)):
    cd = HE_server.encrypt(D[i])
    res.append(hyperbolic_distance_parts(cx, cd))
end = time.time()

s_res = [(res[j][0].to_bytes(), res[j][1].to_bytes()) for j in range(len(res))]

print(f"[Server] Distances computed! Responding: res={res[0]}...")
print(f"[Server] Sent {(np.sum([len(s_res[i]) for i in range(len(s_res))])) / (10**6)} MB")

print(f"[Server] Compute took {end - start}s with bandwidth {len(D) / (end-start)} documents/s")
print("="*40)

# Note that the time is mostly restricted by database size and not encoding size

# Client Parse Response

def hyperbolic_distance(u, v):
    num = ((u - v) @ (u - v))
    den = (1 - (u @ u)) * (1 - (v @ v))
    return np.arccosh(1 + 2 * (num / den))

start = time.time()
c_res = []
for i in range(len(s_res)):
    c_num = PyCtxt(pyfhel=HE_server, bytestring=s_res[i][0])
    c_den = PyCtxt(pyfhel=HE_server, bytestring=s_res[i][1])
    p_num = HE_client.decrypt(c_num)[0]
    p_den = HE_client.decrypt(c_den)[0]
    dist = np.arccosh(1 + 2 * (p_num / p_den))
    c_res.append(dist)
end = time.time()

print(f"[Server] Compute took {end - start}s with bandwidth {len(s_res) / (end-start)} documents/s")
print("="*40)

# Checking result
expected_res = [hyperbolic_distance(x, np.array(w)) for w in D]
for i in range(len(c_res)):
    result = c_res[i]
    expected = expected_res[i]
    if np.abs(result - expected) < 1e-3:
        pass
    else:
        print(f"got: {result}, expected: {expected}")
        assert False