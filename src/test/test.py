from events import *
import json
import time
pairs = json.load(open('files/main_pairs.json'))
start = time.time()
r = get_reserves(pairs)
end = time.time()
print(r)
print('cost:', end - start)
