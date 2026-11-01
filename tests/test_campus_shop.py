import json
import tempfile
import unittest
from pathlib import Path
from academy import ProfileStore
from campus_shop import CATALOGUE, DEFAULT_EQUIPMENT, normalize_cosmetics
from server import BrowserGame

class CampusShopTests(unittest.TestCase):
    def setUp(self):
        self.tmp=tempfile.TemporaryDirectory();self.path=Path(self.tmp.name)/'profiles.json'
        self.store=ProfileStore(self.path);self.pid=self.store.active_id
    def tearDown(self):self.tmp.cleanup()
    def test_old_save_migrates_without_losing_card_surfaces(self):
        p=self.store.active;p['coins']=90;p['owned'].append('Midnight slate');p['theme']='Midnight slate'
        del p['cosmetics'];self.store.save();restored=ProfileStore(self.path).active
        self.assertEqual(restored['coins'],90);self.assertEqual(restored['theme'],'Midnight slate')
        self.assertIn('Midnight slate',restored['owned'])
        self.assertEqual(restored['cosmetics']['equipped'],DEFAULT_EQUIPMENT)
    def test_purchase_equip_once_and_persist_every_category(self):
        self.store.active['coins']=500
        for item in ('jacaranda','midnight-coder','petals','gothic'):
            self.store.purchase_cosmetic(self.pid,item)
            balance=self.store.active['coins'];self.store.purchase_cosmetic(self.pid,item)
            self.assertEqual(self.store.active['coins'],balance)
        p=ProfileStore(self.path).active
        self.assertEqual(p['coins'],320)
        self.assertEqual(p['cosmetics']['equipped'],dict(background='jacaranda',title='midnight-coder',effect='petals',ornament='gothic'))
    def test_insufficient_funds_and_invalid_items(self):
        before=self.store.active['cosmetics'].copy()
        for item in ('rainy','unknown',[],None):
            with self.assertRaises(ValueError):self.store.purchase_cosmetic(self.pid,item)
        self.assertEqual(self.store.active['coins'],0);self.assertEqual(self.store.active['cosmetics'],before)
    def test_inventory_repair_and_separate_profiles(self):
        p={'cosmetics':{'owned':['petals','petals','bad',[]],'equipped':{'title':'petals','effect':'sparkles'}}}
        normalize_cosmetics(p)
        self.assertEqual(p['cosmetics']['equipped'],DEFAULT_EQUIPMENT)
        self.assertEqual(p['cosmetics']['owned'].count('petals'),1)
        self.store.active['coins']=100;self.store.purchase_cosmetic(self.pid,'petals')
        second=self.store.create('Second')
        self.assertNotIn('petals',self.store.profiles[second]['cosmetics']['owned'])
    def test_browser_purchase_and_catalogue(self):
        self.store.active['coins']=100;g=BrowserGame(self.store)
        state=g.action({'action':'purchase_cosmetic','item':'python-scholar'})
        self.assertEqual(state['profile']['coins'],55)
        self.assertEqual(state['active_cosmetics']['title'],'python-scholar')
        self.assertEqual(set(state['shop_categories']),{'background','title','effect','ornament'})
        self.assertEqual(len(state['shop']),16)
    def test_background_files_exist(self):
        root=Path(__file__).parents[1]/'static/assets'
        for item in CATALOGUE.values():
            if item.get('image'):self.assertTrue((root/item['image']).is_file())

if __name__=='__main__':unittest.main()
