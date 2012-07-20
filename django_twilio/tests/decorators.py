from hmac import new
from hashlib import sha1
from base64 import encodestring

from django.conf import settings
from django.http import HttpResponse
from django.test import Client, RequestFactory
from django.utils.unittest import TestCase

from twilio.twiml import Response, Verb

from django_twilio import settings as django_twilio_settings
from django_twilio.exceptions import InvalidMethodError
from django_twilio.decorators import twilio_view
from django_twilio.models import Caller
#from django_twilio.tests.views import response_view, str_view, verb_view


#class TwilioViewTest(TestCase):
#    urls = 'django_twilio.tests.urls'
#
#    def setUp(self):
#        self.client = Client(enforce_csrf_checks=True)
#        self.factory = RequestFactory(enforce_csrf_checks=True)
#
#        # Test URIs.
#        self.uri = 'http://testserver/tests/decorators'
#        self.str_uri = '/tests/decorators/str_view/'
#        self.verb_uri = '/tests/decorators/verb_view/'
#        self.response_uri = '/tests/decorators/response_view/'
#
#        # Guarantee a value for the required configuration settings after each
#        # test case.
#        django_twilio_settings.TWILIO_ACCOUNT_SID = 'xxx'
#        django_twilio_settings.TWILIO_AUTH_TOKEN = 'xxx'
#
#        # Pre-calculate Twilio signatures for our test views.
#        self.response_signature = encodestring(new(django_twilio_settings.TWILIO_AUTH_TOKEN,
#                '%s/response_view/' % self.uri, sha1).digest()).strip()
#        self.str_signature = encodestring(new(django_twilio_settings.TWILIO_AUTH_TOKEN,
#                '%s/str_view/' % self.uri, sha1).digest()).strip()
#        self.str_signature_with_from_field_normal_caller = encodestring(new(
#                django_twilio_settings.TWILIO_AUTH_TOKEN,
#                '%s/str_view/From+12222222222' % self.uri,
#                sha1).digest()).strip()
#        self.str_signature_with_from_field_blacklisted_caller = encodestring(
#                new(django_twilio_settings.TWILIO_AUTH_TOKEN,
#                '%s/str_view/From+13333333333' % self.uri,
#                sha1).digest()).strip()
#        self.verb_signature = encodestring(new(django_twilio_settings.TWILIO_AUTH_TOKEN,
#                '%s/verb_view/' % self.uri, sha1).digest()).strip()
#
#    def test_is_csrf_exempt(self):
#        self.assertTrue(self.client.post(self.str_uri).csrf_exempt)
#
#    def test_requires_post(self):
#        debug_orig = settings.DEBUG
#        settings.DEBUG = False
#        self.assertEquals(self.client.get(self.str_uri).status_code, 405)
#        self.assertEquals(self.client.head(self.str_uri).status_code, 405)
#        self.assertEquals(self.client.options(self.str_uri).status_code, 405)
#        self.assertEquals(self.client.put(self.str_uri).status_code, 405)
#        self.assertEquals(self.client.delete(self.str_uri).status_code, 405)
#        settings.DEBUG = True
#        self.assertEquals(self.client.get(self.str_uri).status_code, 200)
#        self.assertEquals(self.client.head(self.str_uri).status_code, 200)
#        self.assertEquals(self.client.options(self.str_uri).status_code, 200)
#        self.assertEquals(self.client.put(self.str_uri).status_code, 200)
#        self.assertEquals(self.client.delete(self.str_uri).status_code, 200)
#        settings.DEBUG = debug_orig
#
#    def test_allows_post(self):
#        request = self.factory.post(self.str_uri, HTTP_X_TWILIO_SIGNATURE=self.str_signature)
#        self.assertEquals(str_view(request).status_code, 200)
#
#    def test_decorator_preserves_metadata(self):
#        self.assertEqual(str_view.__name__, 'str_view')
#
#    def test_missing_settings_return_forbidden(self):
#        del django_twilio_settings.TWILIO_ACCOUNT_SID
#        del django_twilio_settings.TWILIO_AUTH_TOKEN
#        debug_orig = settings.DEBUG
#        settings.DEBUG = False
#        self.assertEquals(self.client.post(self.str_uri).status_code, 403)
#        settings.DEBUG = True
#        self.assertEquals(self.client.post(self.str_uri).status_code, 200)
#        settings.DEBUG = debug_orig
#
#    def test_missing_signature_returns_forbidden(self):
#        debug_orig = settings.DEBUG
#        settings.DEBUG = False
#        self.assertEquals(self.client.post(self.str_uri).status_code, 403)
#        settings.DEBUG = True
#        self.assertEquals(self.client.post(self.str_uri).status_code, 200)
#        settings.DEBUG = debug_orig
#
#    def test_incorrect_signature_returns_forbidden(self):
#        debug_orig = settings.DEBUG
#        settings.DEBUG = False
#        request = self.factory.post(self.str_uri, HTTP_X_TWILIO_SIGNATURE='fakesignature')
#        self.assertEquals(str_view(request).status_code, 403)
#        settings.DEBUG = True
#        self.assertEquals(str_view(request).status_code, 200)
#        settings.DEBUG = debug_orig
#
#    def test_no_from_field(self):
#        request = self.factory.post(self.str_uri,
#                HTTP_X_TWILIO_SIGNATURE=self.str_signature)
#        self.assertEquals(str_view(request).status_code, 200)
#
#    def test_from_field_no_caller(self):
#        request = self.factory.post(self.str_uri, {'From': '+12222222222'},
#                HTTP_X_TWILIO_SIGNATURE=self.str_signature_with_from_field_normal_caller)
#        self.assertEquals(str_view(request).status_code, 200)
#
#    def test_blacklist_works(self):
#        debug_orig = settings.DEBUG
#        settings.DEBUG = False
#        request = self.factory.post(self.str_uri, {'From': '+13333333333'},
#                HTTP_X_TWILIO_SIGNATURE=self.str_signature_with_from_field_blacklisted_caller)
#        response = str_view(request)
#        r = Response()
#        r.reject()
#        self.assertEquals(response.content, str(r))
#        settings.DEBUG = True
#        request = self.factory.post(self.str_uri, {'From': '+13333333333'},
#                HTTP_X_TWILIO_SIGNATURE=self.str_signature_with_from_field_blacklisted_caller)
#        response = str_view(request)
#        r = Response()
#        r.reject()
#        self.assertEquals(response.content, str(r))
#        settings.DEBUG = debug_orig
#
#    def test_decorator_modifies_str(self):
#        request = self.factory.post(self.str_uri,
#                HTTP_X_TWILIO_SIGNATURE=self.str_signature)
#        self.assertTrue(isinstance(str_view(request), HttpResponse))
#
#    def test_decorator_modifies_verb(self):
#        request = self.factory.post(self.verb_uri, HTTP_X_TWILIO_SIGNATURE=self.verb_signature)
#        self.assertTrue(isinstance(verb_view(request), HttpResponse))
#
#    def test_decorator_preserves_httpresponse(self):
#        request = self.factory.post(self.response_uri, HTTP_X_TWILIO_SIGNATURE=self.response_signature)
#        self.assertTrue(isinstance(response_view(request), HttpResponse))


def str_view(request):
    """A simple view with no decorator."""
    return '<Response><Sms>hi</Sms></Response>'


def verb_view(request):
    """A simple view that returns a Twilio verb."""
    r = Response()
    r.say('hello')
    return r


class TwilioViewTest(TestCase):

    def setUp(self):
        self.client = Client(enforce_csrf_checks=True)
        self.factory = RequestFactory(enforce_csrf_checks=True)
        settings.DEBUG = True

        # Guarantee a value for the required configuration settings after each
        # test case.
        django_twilio_settings.TWILIO_ACCOUNT_SID = 'xxx'
        django_twilio_settings.TWILIO_AUTH_TOKEN = 'xxx'

    def test_invalid_http_methods_raise_exception(self):
        self.assertRaises(InvalidMethodError, twilio_view, method='put')
        self.assertRaises(InvalidMethodError, twilio_view, method='delete')
        self.assertRaises(InvalidMethodError, twilio_view, method='patch')

    def test_valid_http_methods_dont_raise_exception(self):
        twilio_view(method='get')(str_view)
        twilio_view(method='post')(str_view)

    def test_using_invalid_http_methods_raises_405(self):
        test_view = twilio_view(method='GET')(str_view)

        request = self.factory.post('/test/')
        response = test_view(request)
        self.assertEqual(response.status_code, 405)

        test_view = twilio_view(method='POST')(str_view)

        request = self.factory.get('/test/')
        response = test_view(request)
        self.assertEqual(response.status_code, 405)

    def test_is_csrf_exempt_when_method_is_post(self):
        test_view = twilio_view(method='POST')(str_view)
        self.assertTrue(hasattr(test_view, 'csrf_exempt') and test_view.csrf_exempt)

    def test_is_not_csrf_exempt_when_method_is_get(self):
        test_view = twilio_view(method='GET')(str_view)
        self.assertFalse(hasattr(test_view, 'csrf_exempt'))

    def test_blacklist_works(self):
        test_view = twilio_view(method='GET', blacklist=True)(str_view)

        # Create a blacklisted caller:
        Caller.objects.create(phone_number='+18182223333', blacklisted=True)

        # Generate a fake request from this caller:
        request = self.factory.get('/test/', {'From': '+18182223333'})
        response = test_view(request)

        # Make sure the caller got rejected:
        expected = Response()
        expected.reject()
        self.assertEqual(response.content, str(expected))

    def test_return_xml(self):
        test_view = twilio_view(method='GET', blacklist=True)(str_view)
        request = self.factory.get('/test/')
        response = test_view(request)
        self.assertEqual(response.content, str_view('test'))

    def test_return_verb(self):
        test_view = twilio_view(method='GET', blacklist=True)(verb_view)
        request = self.factory.get('/test/')
        response = test_view(request)
        self.assertEqual(response.content, '<?xml version="1.0" encoding="UTF-8"?><Response><Say>hello</Say></Response>')

#    def test_requires_post(self):
#        debug_orig = settings.DEBUG
#        settings.DEBUG = False
#        self.assertEquals(self.client.get(self.str_uri).status_code, 405)
#        self.assertEquals(self.client.head(self.str_uri).status_code, 405)
#        self.assertEquals(self.client.options(self.str_uri).status_code, 405)
#        self.assertEquals(self.client.put(self.str_uri).status_code, 405)
#        self.assertEquals(self.client.delete(self.str_uri).status_code, 405)
#        settings.DEBUG = True
#        self.assertEquals(self.client.get(self.str_uri).status_code, 200)
#        self.assertEquals(self.client.head(self.str_uri).status_code, 200)
#        self.assertEquals(self.client.options(self.str_uri).status_code, 200)
#        self.assertEquals(self.client.put(self.str_uri).status_code, 200)
#        self.assertEquals(self.client.delete(self.str_uri).status_code, 200)
#        settings.DEBUG = debug_orig
#
#    def test_allows_post(self):
#        request = self.factory.post(self.str_uri, HTTP_X_TWILIO_SIGNATURE=self.str_signature)
#        self.assertEquals(str_view(request).status_code, 200)
#
#    def test_decorator_preserves_metadata(self):
#        self.assertEqual(str_view.__name__, 'str_view')
#
#    def test_missing_settings_return_forbidden(self):
#        del django_twilio_settings.TWILIO_ACCOUNT_SID
#        del django_twilio_settings.TWILIO_AUTH_TOKEN
#        debug_orig = settings.DEBUG
#        settings.DEBUG = False
#        self.assertEquals(self.client.post(self.str_uri).status_code, 403)
#        settings.DEBUG = True
#        self.assertEquals(self.client.post(self.str_uri).status_code, 200)
#        settings.DEBUG = debug_orig
#
#    def test_missing_signature_returns_forbidden(self):
#        debug_orig = settings.DEBUG
#        settings.DEBUG = False
#        self.assertEquals(self.client.post(self.str_uri).status_code, 403)
#        settings.DEBUG = True
#        self.assertEquals(self.client.post(self.str_uri).status_code, 200)
#        settings.DEBUG = debug_orig
#
#    def test_incorrect_signature_returns_forbidden(self):
#        debug_orig = settings.DEBUG
#        settings.DEBUG = False
#        request = self.factory.post(self.str_uri, HTTP_X_TWILIO_SIGNATURE='fakesignature')
#        self.assertEquals(str_view(request).status_code, 403)
#        settings.DEBUG = True
#        self.assertEquals(str_view(request).status_code, 200)
#        settings.DEBUG = debug_orig
#
#    def test_no_from_field(self):
#        request = self.factory.post(self.str_uri,
#                HTTP_X_TWILIO_SIGNATURE=self.str_signature)
#        self.assertEquals(str_view(request).status_code, 200)
#
#    def test_from_field_no_caller(self):
#        request = self.factory.post(self.str_uri, {'From': '+12222222222'},
#                HTTP_X_TWILIO_SIGNATURE=self.str_signature_with_from_field_normal_caller)
#        self.assertEquals(str_view(request).status_code, 200)
#
#    def test_blacklist_works(self):
#        debug_orig = settings.DEBUG
#        settings.DEBUG = False
#        request = self.factory.post(self.str_uri, {'From': '+13333333333'},
#                HTTP_X_TWILIO_SIGNATURE=self.str_signature_with_from_field_blacklisted_caller)
#        response = str_view(request)
#        r = Response()
#        r.reject()
#        self.assertEquals(response.content, str(r))
#        settings.DEBUG = True
#        request = self.factory.post(self.str_uri, {'From': '+13333333333'},
#                HTTP_X_TWILIO_SIGNATURE=self.str_signature_with_from_field_blacklisted_caller)
#        response = str_view(request)
#        r = Response()
#        r.reject()
#        self.assertEquals(response.content, str(r))
#        settings.DEBUG = debug_orig
#
#    def test_decorator_modifies_str(self):
#        request = self.factory.post(self.str_uri,
#                HTTP_X_TWILIO_SIGNATURE=self.str_signature)
#        self.assertTrue(isinstance(str_view(request), HttpResponse))
#
#    def test_decorator_modifies_verb(self):
#        request = self.factory.post(self.verb_uri, HTTP_X_TWILIO_SIGNATURE=self.verb_signature)
#        self.assertTrue(isinstance(verb_view(request), HttpResponse))
#
#    def test_decorator_preserves_httpresponse(self):
#        request = self.factory.post(self.response_uri, HTTP_X_TWILIO_SIGNATURE=self.response_signature)
#        self.assertTrue(isinstance(response_view(request), HttpResponse))
