from core.models import User
from django.test.client import Client
from django.test.testcases import TestCase
from core.tests import fixtures
import json

PENSOLOGO = 'Penso, logo existo'
PRIMEIRA_LEI = 'Minha primeira lei!'
GRAVITACAO = 'Gravitação is a thing'
INSANIDADE = 'Insanidade is real'


class TestTweetsApi(TestCase):
    @classmethod
    def setUpTestData(cls):
        fixtures.usuarios_cientistas()

    def test_tweets_api(self):
        newton, einstein, descartes, anon = Client(), Client(), Client(), Client()
        newton.force_login(User.objects.get(username='@newton'))
        einstein.force_login(User.objects.get(username='@einstein'))
        descartes.force_login(User.objects.get(username='@descartes'))
        self._follow(newton, '@descartes')
        self._follow(einstein, '@descartes')
        self._follow(einstein, '@newton')
        self._follow(newton, '@einstein')
        self._unfollow(newton, '@einstein')
        self._tweet(descartes, PENSOLOGO)
        self._tweet(newton, PRIMEIRA_LEI)
        self._tweet(newton, GRAVITACAO)
        self._tweet(einstein, 'E = mc2')
        self._tweet(einstein, INSANIDADE)
        self._assert_tweets_home(descartes, [PENSOLOGO])
        self._assert_tweets_home(newton, [GRAVITACAO, PRIMEIRA_LEI, PENSOLOGO])
        self._assert_tweets_home(einstein, [INSANIDADE, 'E = mc2', GRAVITACAO, PRIMEIRA_LEI, PENSOLOGO])
        self._assert_tweets_home(anon, [INSANIDADE, 'E = mc2', GRAVITACAO, PRIMEIRA_LEI, PENSOLOGO])
        self._assert_tweets_user(anon, '@einstein', [INSANIDADE, 'E = mc2'])
        self._assert_tweets_user(newton, '@einstein', [INSANIDADE, 'E = mc2'])

    def _follow(self, client, username):
        r = client.post('/api/follow', {'username': username})
        self.assertEquals(200, r.status_code)
        data = json.loads(r.content.decode('utf-8'))
        self.assertIsNotNone(data)

    def _unfollow(self, client, username):
        r = client.post('/api/unfollow', {'username': username})
        self.assertEquals(200, r.status_code)
        data = json.loads(r.content.decode('utf-8'))
        self.assertIsNotNone(data)

    def _tweet(self, client, text):
        r = client.post('/api/tweet', {'text': text})
        self.assertEquals(200, r.status_code)
        tweet = json.loads(r.content.decode('utf-8'))
        self.assertIsNotNone(tweet)
        self.assertIsNotNone(tweet['id'])
        self.assertEquals(text, tweet['text'])

    def _assert_tweets_home(self, client, expectedtweets):
        r = client.get('/api/list_tweets')
        self.assertEquals(200, r.status_code)
        tweets = json.loads(r.content.decode('utf-8'))
        actualtweets_texts = [t['text'] for t in tweets]
        self.assertEquals(actualtweets_texts, expectedtweets)

    def _assert_tweets_user(self, client, username, expectedtweets):
        r1 = client.get('/api/get_user_details', {'username': username})
        r2 = client.get('/api/list_tweets', {'username': username})
        self.assertEquals(200, r1.status_code)
        self.assertEquals(200, r2.status_code)
        userdetails = json.loads(r1.content.decode('utf-8'))
        tweets = json.loads(r2.content.decode('utf-8'))
        actualtweet_texts = [t['text'] for t in tweets]
        self.assertEquals(actualtweet_texts, expectedtweets)
        for k in ['username', 'avatar', 'last_tweet', 'ifollow']:
            self.assertIsNotNone(userdetails[k])