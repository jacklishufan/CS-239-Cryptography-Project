import re, sys

f = open(sys.argv[1]).read()

preprocess = re.findall(r"Preprocessed query to 1000-document corpus in: ([0-9].+)s", f)
preprocess = [float(preprocess[i]) for i in range(len(preprocess))]

a1 = re.findall(r"Answered query to 1000-document corpus in: ([0-9].+)µs", f)
a2 = re.findall(r"Answered query to 1000-document corpus in: ([0-9].+)ms", f)
a1f = [float(a1[i]) / 1000 for i in range(len(a1))]
a2f = [float(a2[i]) for i in range(len(a2))]
answer = a1f + a2f

upload = re.findall(r"Upload: ([0-9].+) MB", f)
upload = [float(upload[i]) for i in range(len(upload))]

download = re.findall(r"Download: ([0-9].+) MB", f)
download = [float(download[i]) for i in range(len(download))]

print(sum(preprocess) / len(preprocess))
print(sum(answer) / len(answer))
print(sum(upload) / len(upload))
print(sum(download) / len(download))