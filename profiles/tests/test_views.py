from django.test import TestCase, RequestFactory
from profiles.views import IndexView


class IndexViewTestCase(TestCase):

    def setUp(self):
        self.factory = RequestFactory()

    def test_index_view_basic(self):
        """Test that index view return a 200 response and uses the correct template"""
        request = self.factory.get('/')
        with self.assertTemplateUsed('index.html'):
            response = IndexView.as_view()(request)
            self.assertEqual(response.status_code, 200)
