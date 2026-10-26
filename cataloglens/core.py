"""In-memory BM25 with transparent term contributions and facet filters."""
from collections import Counter
import math
import re
import unicodedata

def tokens(text):
    text = unicodedata.normalize('NFKC',text).casefold()
    return re.findall(r'[^\W_]+',text,flags=re.UNICODE)

class Catalog:
    def __init__(self, products, k1=1.2, b=0.75):
        if not math.isfinite(k1) or k1 <= 0 or not math.isfinite(b) or not 0 <= b <= 1:
            raise ValueError('invalid BM25 parameters')
        self.k1, self.b = k1,b
        self.products, self.terms, self.df = {}, {}, Counter()
        for source in products:
            p = dict(source)
            if not isinstance(p.get('id'),str) or not p['id'] or p['id'] in self.products: raise ValueError('unique string id required')
            for field in ('title','description','category'):
                if not isinstance(p.get(field),str): raise ValueError(f'{field} must be text')
            if type(p.get('price_cents')) is not int or p['price_cents'] < 0: raise ValueError('integer price_cents required')
            if type(p.get('in_stock')) is not bool: raise ValueError('boolean in_stock required')
            terms = Counter(tokens(p['title']+' '+p['description']))
            self.products[p['id']] = p; self.terms[p['id']] = terms
            self.df.update(terms.keys())
        self.avg_length = sum(sum(t.values()) for t in self.terms.values()) / max(len(self.products),1)

    def search(self, query, category=None, max_price_cents=None, in_stock=None, limit=10):
        if type(limit) is not int or limit < 1: raise ValueError('positive limit required')
        if max_price_cents is not None and (type(max_price_cents) is not int or max_price_cents < 0): raise ValueError('invalid price filter')
        if in_stock is not None and type(in_stock) is not bool: raise ValueError('invalid stock filter')
        query_terms = sorted(set(tokens(query)))
        results=[]; n=len(self.products)
        for key,p in self.products.items():
            if category is not None and p['category'] != category: continue
            if max_price_cents is not None and p['price_cents'] > max_price_cents: continue
            if in_stock is not None and p['in_stock'] != in_stock: continue
            terms=self.terms[key]; length=sum(terms.values()); contributions={}
            for term in query_terms:
                tf=terms[term]
                if not tf: continue
                idf=math.log(1+(n-self.df[term]+0.5)/(self.df[term]+0.5))
                denominator=tf+self.k1*(1-self.b+self.b*length/(self.avg_length or 1))
                contributions[term]=idf*tf*(self.k1+1)/denominator
            score=sum(contributions.values())
            if query_terms and score <= 0: continue
            results.append({'product':dict(p),'score':score,'terms':contributions})
        return sorted(results,key=lambda r:(-r['score'],r['product']['id']))[:limit]

def evaluate(catalog, cases, k=5):
    """Macro recall@k and reciprocal rank over judged query cases."""
    if type(k) is not int or k < 1: raise ValueError('positive k required')
    rows=[]
    for case in cases:
        relevant=set(case['relevant_ids'])
        if not relevant: raise ValueError('each query needs relevant judgments')
        if not relevant <= catalog.products.keys(): raise ValueError('unknown relevance id')
        hits=[r['product']['id'] for r in catalog.search(case['query'],limit=k)]
        rank=next((i for i,x in enumerate(hits,1) if x in relevant),None)
        rows.append({'query':case['query'],'recall_at_k':len(set(hits)&relevant)/len(relevant),
                     'reciprocal_rank':1/rank if rank else 0,'ranked_ids':hits})
    return {'queries':rows,'mean_recall_at_k':sum(r['recall_at_k'] for r in rows)/max(len(rows),1),
            'mrr':sum(r['reciprocal_rank'] for r in rows)/max(len(rows),1),'k':k}
