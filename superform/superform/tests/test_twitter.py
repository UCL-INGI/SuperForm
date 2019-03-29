import json
import pytest
import random
import string
from superform import Publishing
from superform.models import StatusCode
from superform.plugins import twitter
from twitter import twitter_utils

CONFIG_FIELDS = ["consumer_key", "consumer_secret", "access_token_key", "access_token_secret"]


def test_tweet_too_big():
    # Test for is_valid_tweet function
    tweet = 'Simple message respecting Twitter\'s status conditions'
    assert twitter.tweet_too_big(tweet) is False
    for i in range(0, 281):
        tweet += str(i)
    assert twitter.tweet_too_big(tweet) is True  # A tweet cannot be longer than 280 characters


# case where the tweet has no description.
def test_run_with_empty_tweet():
    pub = Publishing()
    pub.date_from = '13.02.02'
    pub.title = 'test-Title'
    pub.link_url = 'blablablablablablablajdsfvjdbvjdnfvqebdnbqdfnvsdùnvbmqknkfnbùsfvdf'
    pub.description = ''
    pub.image_url = 'imague url'
    pub.date_until = '14.02.16'
    pub.state = 1
    pub.channel_id = 'Twitter'

    configdata = {"consumer_key": ["kTB8ji6trOpAXoQQBMgRwOUoz"],
                  "consumer_secret": ["oJpKcyObcM6sakaStGsIJ0XnQceebPOrC5CcpJeD54jou1XAEm"],
                  "access_token_key": ["1052553285343858688-2KPjU0CKB5Y6HxR3G5FVUnC8bxZDTJ"],
                  "access_token_secret": ["Sd8Se0oRuffyBwyRBmkgyJlaFVeE8HqQPcQm5rx08S9dx"]}
    config = json.dumps(configdata)
    code = twitter.run(pub, config)
    assert code[0].value == StatusCode.ERROR.value
    assert code[1] == "Empty tweet"


# case where the value of the credentials are now false ( ex : Twitter has blocked the account)
def test_run_false_credentials():
    pub = Publishing()
    pub.date_from = '13.02.02'
    pub.title = 'test-Title'
    pub.link_url = 'blablablablablablablajdsfvjdbvjdnfvqebdnbqdfnvsdùnvbmqknkfnbùsfvdf'
    pub.description = 'something something'
    pub.image_url = 'imague url'
    pub.date_until = '14.02.16'
    pub.state = 1
    pub.channel_id = 'Twitter'

    configdata = {"consumer_key": ["coucou"],
                  "consumer_secret": ["thisisfalse"],
                  "access_token_key": ["blabla"],
                  "access_token_secret": ["beuh"]}
    config = json.dumps(configdata)
    code = twitter.run(pub, config)
    assert code[0].value == StatusCode.ERROR.value
    assert code[1] == "Uncorrect credentials, please review your configuration"


# case where the wrong JSON is send as channel config
def test_run_uncorrect_credentials_JSON():
    pub = Publishing()
    pub.date_from = '13.02.02'
    pub.title = 'test-Title'
    pub.link_url = 'blablablablablablablajdsfvjdbvjdnfvqebdnbqdfnvsdùnvbmqknkfnbùsfvdf'
    pub.description = 'something something'
    pub.image_url = 'imague url'
    pub.date_until = '14.02.16'
    pub.state = 1
    pub.channel_id = 'Twitter'

    configdata = {"csumer_key": ["coucou"],
                  "consumer_seet": ["thisisfalse"],
                  "accesken_key": ["blabla"],
                  "acc_token_secret": ["beuh"]}
    config = json.dumps(configdata)
    code = twitter.run(pub, config)
    assert code[0].value == StatusCode.ERROR.value
    assert code[1] == "Uncorrect credentials, please review your configuration"


def test_send_tweet_correct_tweet():
    pub = Publishing()
    pub.date_from = '13.02.02'
    pub.link_url = ' : test string'
    rabdomStr = randomword(12)
    pub.description = "<tweet-separator>" + rabdomStr + "</tweet-separator> "
    pub.image_url = ""
    pub.date_until = '14.02.16'
    pub.state = 1
    pub.channel_id = 'Twitter'

    configdata = {'consumer_key': 'kTB8ji6trOpAXoQQBMgRwOUoz',
                  'consumer_secret': 'oJpKcyObcM6sakaStGsIJ0XnQceebPOrC5CcpJeD54jou1XAEm',
                  'access_token_key': '1052553285343858688-2KPjU0CKB5Y6HxR3G5FVUnC8bxZDTJ',
                  'access_token_secret': 'Sd8Se0oRuffyBwyRBmkgyJlaFVeE8HqQPcQm5rx08S9dx'}
    config = json.dumps(configdata)

    code = twitter.run(pub, config)
    assert code[0].value == StatusCode.OK.value


def randomword(length):
    letters = string.ascii_lowercase
    return "".join(random.choice(letters) for i in range(length))
