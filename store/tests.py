
from datetime import datetime
import unittest
from pytz import UTC
import html5lib

from django.test import TestCase
from django.test import Client
from django.urls import reverse
from rest_framework.test import APITestCase
from caching import invalidation

from .models import Tool
from .models import Edit
from .models import Batch
from .stream import WikidataEditStream

class ToolTest(TestCase):
    def setUp(self):
        invalidation.cache.clear()

    def test_or(self):
        tool = Tool.objects.get(shortid='OR')

        self.assertEquals(('ca7d7cc', 'Pintoch', 'import Charity Navigator'),
            tool.match("Pintoch",
                "/* wbeditentity-update:0| */ import Charity Navigator ([[Wikidata:Edit groups/OR/ca7d7cc|discuss]])"))

    def test_match_without_summary(self):
        tool = Tool.objects.get(shortid='OR')

        self.assertEquals(('ca7d7cc', 'Pintoch', ''),
            tool.match("Pintoch",
                "/* wbeditentity-update:0| */ ([[Wikidata:Edit groups/OR/ca7d7cc|discuss]])"))

    def test_or_setclaim(self):
        tool = Tool.objects.get(shortid='OR')
        self.assertEquals(('3990c0d', 'Pintoch', 'add EIN ids from Charity Navigator'),
             tool.match("Pintoch",
                "/* wbsetclaim-create:2||1 */ [[Property:P1297]]: 88-0302673, add EIN ids from Charity Navigator ([[:toollabs:editgroups/b/OR/3990c0d|details]])"))


    def test_qs(self):
        tool = Tool.objects.get(shortid='QSv2')

        self.assertEquals(('2120', 'Pintoch', '#quickstatements'),
            tool.match("QuickStatementsBot",
                "/* wbcreateclaim-create:1| */ [[Property:P3896]]: Data:Neighbourhoods/New York City.map, #quickstatements; [[:toollabs:quickstatements/#mode=batch&batch=2120|batch #2120]] by [[User:Pintoch|]]"))

    def test_eg(self):
        tool = Tool.objects.get(shortid='EG')

        self.assertEquals(('c367abf', 'Pintoch', ''),
            tool.match("Pintoch", "this was just dumb ([[:toollabs:editgroups/b/EG/c367abf|details]])"))
        self.assertEquals(('c367abf', 'Pintoch', 'this was just dumb'),
            tool.match("Pintoch", "/* undo:0||1234|Rageux */ this was just dumb ([[:toollabs:editgroups/b/EG/c367abf|details]])"))


class EditTest(TestCase):
    def setUp(self):
        invalidation.cache.clear()

    def test_ingest_jsonlines_or(self):
        Edit.ingest_jsonlines('store/testdata/one_or_batch.json')

        self.assertEquals(1, Batch.objects.count())
        batch = Batch.objects.get()
        self.assertEquals('OR', batch.tool.shortid)
        self.assertEquals('Pintoch', batch.user)
        self.assertEquals('ca7d7cc', batch.uid)
        self.assertEquals(datetime(2018, 3, 6, 16, 39, 37, tzinfo=UTC), batch.started)
        self.assertEquals(datetime(2018, 3, 6, 16, 41, 10, tzinfo=UTC), batch.ended)
        self.assertEquals(51, batch.nb_edits)
        self.assertEquals('32.9', batch.editing_speed)

    def test_ingest_eg(self):
        Edit.ingest_jsonlines('store/testdata/eg_revert.json')
        self.assertEquals(1, Batch.objects.count())
        batch = Batch.objects.get()
        self.assertEquals('EG', batch.tool.shortid)

    def test_ingest_twice(self):
        Edit.ingest_jsonlines('store/testdata/one_or_batch.json')
        Edit.ingest_jsonlines('store/testdata/one_or_batch.json')

        self.assertEquals(1, Batch.objects.count())
        batch = Batch.objects.get()
        self.assertEquals(51, batch.nb_edits)

    def test_ingest_new_items(self):
        Edit.ingest_jsonlines('store/testdata/qs_batch_with_new_items.json')
        self.assertEquals(1, Batch.objects.count())
        batch = Batch.objects.get()
        self.assertEquals(82, batch.nb_edits)
        self.assertEquals(9, batch.nb_new_pages)
        self.assertEquals(9, batch.nb_pages)
        self.assertEquals(0, batch.nb_existing_pages)

    def test_hijack(self):
        """
        Someone trying to reuse the token to artificially attribute
        edits to a batch
        """
        Edit.ingest_jsonlines('store/testdata/one_or_batch.json')
        Edit.ingest_jsonlines('store/testdata/hijack.json')

        self.assertEquals(1, Batch.objects.count())
        batch = Batch.objects.get()
        self.assertEquals(51, batch.nb_edits)

    def test_ingest_jsonlines_qs(self):
        Edit.ingest_jsonlines('store/testdata/one_qs_batch.json')

        self.assertEquals(1, Batch.objects.count())
        batch = Batch.objects.get()
        self.assertEquals('QSv2', batch.tool.shortid)
        self.assertEquals('Pintoch', batch.user)
        self.assertEquals('2120', batch.uid)
        self.assertEquals(datetime(2018, 3, 7, 16, 20, 12, tzinfo=UTC), batch.started)
        self.assertEquals(datetime(2018, 3, 7, 16, 20, 14, tzinfo=UTC), batch.ended)
        self.assertEquals(4, batch.nb_edits)

    def test_reverts(self):
        Edit.ingest_jsonlines('store/testdata/qs_batch_with_reverts.json')

        self.assertEquals(1, Batch.objects.count())
        batch = Batch.objects.get()
        self.assertEquals(5, batch.nb_edits)
        self.assertEquals(2, batch.nb_reverted)

    def test_str(self):
        Edit.ingest_jsonlines('store/testdata/one_or_batch.json')

        edit = Edit.objects.all().order_by('timestamp')[0]
        self.assertEquals('https://www.wikidata.org/wiki/index.php?diff=644512815&oldid=376870215', edit.url)
        self.assertEquals('<Edit https://www.wikidata.org/wiki/index.php?diff=644512815&oldid=376870215 >', str(edit))

class BatchEditsViewTest(APITestCase):
    @classmethod
    def setUpClass(cls):
        Edit.ingest_jsonlines('store/testdata/one_or_batch.json')
        cls.batch = Batch.objects.get()

    def test_nbpages(self):
        self.assertEquals(51, self.batch.nb_pages)

    def test_avg_diffsize(self):
        self.assertTrue(2500 < self.batch.avg_diffsize)
        self.assertTrue(self.batch.avg_diffsize < 3000)

    def pagination(self):
        response = self.client.get(reverse('batch-edits', args=[self.batch.id]))
        self.assertEqual(response.status_code, 200)
        self.assertEqual(self.batch.edit_set.count(), response.data['count'])

    @classmethod
    def tearDownClass(cls):
        Batch.objects.all().delete()

class WikidataEditStreamTest(unittest.TestCase):
    def test_stream(self):
        s = WikidataEditStream()
        for idx, edit in enumerate(s.stream()):
            if idx > 10:
                break
            self.assertEquals('wikidatawiki', edit['wiki'])


class PagesTest(TestCase):

    @classmethod
    def setUpClass(cls):
        cls.client = Client()
        cls.parser = html5lib.HTMLParser(strict=True)
        Edit.ingest_jsonlines('store/testdata/one_or_batch.json')
        cls.batch = Batch.objects.get()
        Edit.ingest_jsonlines('store/testdata/one_qs_batch.json')

    def get_page(self, url_name, **kwargs):
        return self.client.get(reverse(url_name, kwargs or None))

    def check_html(self, response):
        self.assertEqual(200, response.status_code)
        self.parser.parse(response.content)

    def test_batches_list(self):
        response = self.get_page('list-batches')
        self.check_html(response)

    def test_batches_list_filtered(self):
        response = self.client.get(reverse('list-batches')+'?tool=OR')
        self.check_html(response)
        tag = self.batch.tags.all()[0]
        response = self.client.get(reverse('list-batches')+'?tool=OR&tags='+tag.id)
        self.check_html(response)

    def test_batch(self):
        response = self.client.get(self.batch.url)
        self.check_html(response)

    def test_batch_404(self):
        response = self.client.get('/b/ST/3849384/')
        self.assertEqual(404, response.status_code)

    @classmethod
    def tearDownClass(cls):
        Batch.objects.all().delete()
