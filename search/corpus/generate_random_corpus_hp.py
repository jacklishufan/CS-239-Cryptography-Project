import argparse
import numpy as np
import csv
import math

parser = argparse.ArgumentParser(description='Corpus parameters.')
parser.add_argument('-f', '--file', action='store', type=str,
                    help='Name of CSV file', default="medcorpus_hp.csv")
parser.add_argument('-n', '--num', action='store', type=int,
                    help='Num docs in corpus', default=40960)
parser.add_argument('-s', '--slots', action='store', type=int,
                    help='Num slots in embedding', default=192)
parser.add_argument('-b', '--bits', action='store', type=int,
                    help='Precision (in bits) of embedding slots', default=5)
args = parser.parse_args()

def sample_from_unit_sphere(dim, num_samples=1):
    # Generate random points
    samples = np.random.normal(0, 1, (num_samples, dim))
    # Scale them to be within the unit sphere
    radii = np.random.uniform(0, 1, num_samples) #** (1 / dim)
    # Normalize the samples to the surface of the sphere and scale by radius
    samples = samples / np.linalg.norm(samples, axis=1, keepdims=True) * radii[:, np.newaxis]
    return samples

def write_csv(args):
    with open(args.file, "w") as csv_file:
        writer = csv.writer(csv_file, delimiter=",")
        num_commas = args.slots + 2

        # Write the number of docs
        writer.writerow([str(args.num)]+(['']*num_commas))

        # Write the number of slots
        writer.writerow([str(args.slots)]+(['']*num_commas))

        # Write the slot precision
        writer.writerow([str(args.bits)]+(['']*num_commas))

        # Write doc contents
        for i in range(args.num):
            emb = sample_from_unit_sphere(args.slots) # D X L
            emb_norm = np.linalg.norm(emb,axis=-1) # D X L
            emb_scaled = emb / (1-emb_norm+1e-4) 
            
            emb_scaled = (emb_scaled * 1000).astype(int) # round to fixed point int
            emb_norm_scaled = emb_norm /  (1-emb_norm+1e-4) 
            emb_norm_scaled = (emb_norm_scaled * 1000).astype(int) # ro
            emb_scaled = emb_scaled[0].tolist()
            emb_norm_scaled = emb_norm_scaled.tolist()[0]
            row = emb_scaled
            # breakpoint()
            # emb = list(np.random.randint(low=0, high=math.pow(2, args.bits),
            #                              size=args.slots, dtype=int))
            row.append('file-'+str(i)+"-url")
            row.append("file-"+str(i) + "-title")
            row.append(emb_norm_scaled)
            writer.writerow(row)

def main(args):
    write_csv(args)

if __name__ == "__main__":
    main(args)
