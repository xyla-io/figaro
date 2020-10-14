import unittest
import code
import pytest
import pandas as pd
from datetime import datetime, timedelta

from ..api import FacebookAPI

@pytest.fixture
def api():
  api = FacebookAPI(
    app_id='APP_ID',
    app_secret='APP_SECRET',
    access_token='ACCESS_TOKEN',
    ad_user_id='AD_USER_ID'
  )
  yield api

def test_ad_user_exists(api):
  """
  Test that the FacebookAPI class can be instanced.
  """
  import pdb; pdb.set_trace()
  assert api.ad_user is not None

def test_account(api):
  """
  Test that the FacebookAPI class can retrieve an ad account.
  """
  account = api.get_account(account_id=1000000)
  assert account is not None
  import pdb; pdb.set_trace()

def test_activity_history(api):
  """
  Test that the FacebookAPI class can retrieve account activity history.
  """
  activity_history = api.get_ad_activity_history(
    start_date=datetime.utcnow() - timedelta(days=7), 
    end_date=datetime.utcnow()
  )
  assert activity_history is not None