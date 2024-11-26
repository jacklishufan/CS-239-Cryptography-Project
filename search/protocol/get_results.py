import re, sys

f = open(sys.argv[1]).read()

preprocess = re.findall(r"Preprocessed query to 100-document corpus in: ([0-9].+)s", f)
preprocess = [float(preprocess[i]) for i in range(len(preprocess))]

answer = re.findall(r"Answered query to 100-document corpus in: ([0-9].+)µs", f)
answer = [float(answer[i]) for i in range(len(answer))]

upload = re.findall(r"Upload: ([0-9].+) MB", f)
upload = [float(upload[i]) for i in range(len(upload))]

download = re.findall(r"Download: ([0-9].+) MB", f)
download = [float(download[i]) for i in range(len(download))]

print(sum(preprocess) / len(preprocess))
print(sum(answer) / len(answer))
print(sum(upload) / len(upload))
print(sum(download) / len(download))