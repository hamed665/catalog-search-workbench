import argparse
import json
from .core import Catalog, evaluate
parser=argparse.ArgumentParser(description='Explainable offline product search')
parser.add_argument('catalog')
parser.add_argument('--query',default='')
parser.add_argument('--evaluate',dest='judgments')
args=parser.parse_args()
with open(args.catalog,encoding='utf-8') as f: catalog=Catalog(json.load(f))
if args.judgments:
    with open(args.judgments,encoding='utf-8') as f: output=evaluate(catalog,json.load(f))
else: output=catalog.search(args.query)
print(json.dumps(output,ensure_ascii=False,indent=2))
