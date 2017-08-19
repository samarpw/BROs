from django.test import TestCase
from django.core.urlresolvers import resolve
from profiles.views import IndexView

class ProfilesURLsTestCase(TestCase):

    def test_root_url_uses_index_view(self):
        """Test that the root of the site resolves to the correct view"""
        root = resolve('/')
        self.assertEqual(root.func.view_class, IndexView)
