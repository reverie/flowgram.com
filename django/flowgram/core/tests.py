"""
Flowgram core backend unit tests
Filename: tests.py
Author: Christian Yang

Unit tests for Flowgram core application. When creating new tests, can inherit
from FlowgramAPITestCase, which provides some common test functionality across
API methods, such as auto-adding the CSRF middleware token to POST requests

When running tests, the test runner will look for all methods with prototype
in form of test*(). Run the test runner from the /flowgram/ directory using
<python manage.py test [app_name]>, where [app_name] should usually be 'core'
(leaving out [app_name] will cause the test runner to run tests for all
module applications, as well as some default Django tests, which don't seem
to be compatible with the current Flowgram/Django setup.

Basic test flow:
- Test runner loads test fixtures specified by class 'fixtures' member
- Within test, craft response from self.client.post() or self.client.get()
  members
- Validate response
*Note that client is recreated after each test, so need to
do setup on test-by-test basis.

Useful client members to be aware of:
client.login(username,password)
- When test requires logged in user

client.post(self, path, data={}, content_type=MULTIPART_CONTENT, **extra)
- Generate a POST request

client.get(self, path, data={}, **extra)
- Generates a GET request
"""
from django.test import TestCase
from django.test.client import *
from django.contrib.csrf.middleware import _make_token

class FlowgramAPITestClient(Client):
    add_csrf_tokens_to_posts = True
    """
    Test client providing additional functionality for Flowgram testing
    """
    def post(self, path, data={}, content_type=MULTIPART_CONTENT, **extra):
        """
        Overridden method to add csrf token to the **extra dictionary if
        desired. 
        """
        if self.add_csrf_tokens_to_posts and hasattr(self.session, 'session_key'):
            data['csrfmiddlewaretoken'] = _make_token(self.session.session_key)
        return Client.post(self, path, data, content_type, **extra)

    def request(self, **request):
        """
        Overridden method to add 'REMOTE_ADDR' meta tag required for middleware.
        Uses bogus external IP address 11.22.33.44.
        """
        if not request.has_key('REMOTE_ADDR'):
            request['REMOTE_ADDR'] = '11.22.33.44'
        return Client.request(self, **request)

class FlowgramAPITestCase(TestCase):
    def __call__(self, result=None):
        """
        Overridden to create a FlowgramAPITestClient instead of normal,
        and setting it up to add csrf tokens or not
        """
        self.client = FlowgramAPITestClient()
        self._pre_setup()
        super(TestCase, self).__call__(result)

class DelpageTest(FlowgramAPITestCase):
    fixtures = ['delpage_test.xml']
    
    def test_bad_id(self):
        # Try dummy ID
        response = self.client.post('/api/delpage/', {'page_id':'xxxxxxxxxxxxxx'})
        self.assertContains(response,"<response><version>1.0</version><code>5"
        "</code><succeeded>0</succeeded><description>Input invalid.</description>"
        "<body>page_id xxxxxxxxxxxxxx could not be converted to Page object"
        "</body></response>", 1, status_code=200)

    def test_no_log_in(self):
        # Try legit ID without logging in
        response = self.client.post('/api/delpage/', {'page_id':'B56B96JBC64Q4M'})
        self.assertContains(response, "<response><version>1.0</version><code>3"
        "</code><succeeded>0</succeeded><description>User does not have permission "
        "to edit that resource.</description><body>AnonymousUser does not have "
        "permission to edit that page_id</body></response>", 1, status_code=200)

    def test_delete_success(self):
        # Login and try, should succeed
        response = self.client.login(username='testuser',password='testuserpassword')
        response = self.client.post('/api/delpage/', {'page_id':'B56B96JBC64Q4M'})
        self.assertContains(response, "<response><version>1.0</version><code>0"
        "</code><succeeded>1</succeeded><description>OK</description><body></body>"
        "</response>",1, status_code=200)

    def test_delete_twice(self):
        # Login and try, should succeed
        response = self.client.login(username='testuser',password='testuserpassword')
        response = self.client.post('/api/delpage/', {'page_id':'B56B96JBC64Q4M'})
        self.assertContains(response, "<response><version>1.0</version><code>0"
        "</code><succeeded>1</succeeded><description>OK</description><body></body>"
        "</response>",1, status_code=200)
        
        # Try to delete again, should result in 'can't convert'
        response = self.client.post('/api/delpage/', {'page_id':'B56B96JBC64Q4M'})
        self.assertContains(response, "<response><version>1.0</version><code>5"
        "</code><succeeded>0</succeeded><description>Input invalid.</description>"
        "<body>Page already deleted</body></response>", 1, status_code=200)

    # TODO(andrew): add test for deleting someone else's page
    # TODO(andrew): add test for deleting a page and then trying to get it
