import json
from pathlib import Path
import unittest
from cataloglens.core import Catalog, evaluate, tokens

class SearchTests(unittest.TestCase):
    def setUp(self):
        self.products=json.loads((Path(__file__).parents[1]/'examples/products.json').read_text())
        self.c=Catalog(self.products)
    def test_relevance(self): self.assertEqual(self.c.search('dog brush')[0]['product']['id'],'p1')
    def test_filters(self):
        self.assertEqual(self.c.search('coffee',in_stock=True),[])
        self.assertEqual(self.c.search('carrier',max_price_cents=2000),[])
        self.assertEqual(self.c.search('brush',category='kitchen'),[])
    def test_unicode(self): self.assertEqual(self.c.search('فرشاة')[0]['product']['id'],'p4')
    def test_explanation_sums(self):
        hit=self.c.search('dog brush')[0]
        self.assertAlmostEqual(hit['score'],sum(hit['terms'].values()))
    def test_unknown_and_empty(self):
        self.assertEqual(self.c.search('xyz'),[])
        self.assertEqual(len(self.c.search('')),4)
    def test_duplicate_rejected(self):
        with self.assertRaises(ValueError): Catalog(self.products+self.products)
    def test_evaluation(self):
        report=evaluate(self.c,[{'query':'dog','relevant_ids':['p1']}],k=1)
        self.assertEqual(report['mrr'],1); self.assertEqual(report['mean_recall_at_k'],1)
    def test_normalization(self): self.assertEqual(tokens('ＣＡＴ cat'),['cat','cat'])
    def test_returned_record_is_copy(self):
        self.c.search('dog')[0]['product']['title']='changed'
        self.assertEqual(self.c.products['p1']['title'],'Dog grooming brush')
