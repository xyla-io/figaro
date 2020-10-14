import unittest
import pdb

from ..api import FacebookAPI
from ..reporting import FacebookReporter
from datetime import datetime, timedelta

class Test_FacebookReporter(unittest.TestCase):
  def setUp(self):
    api = FacebookAPI(
      app_id='APP_ID',
      app_secret='APP_SECRET',
      access_token='ACCESS_TOKEN',
      ad_user_id='AD_USER_ID'
    )
    api.account_id = 1000000
    self.reporter = FacebookReporter(api=api)

  def test_campaign_insights(self):
    """
    Test that the FacebookAPI class can be instanced.
    """
    end = datetime.utcnow()
    start = datetime.utcnow() - timedelta(days=2)
    fields = [
      'account_id',
      'account_name',
      'campaign_id',
      'campaign_name',
      'impressions',
      'clicks',
      'spend',
      'unique_clicks',
      'actions',
      'date_start',
      'date_stop',
    ]
    report = self.reporter.get_campaign_insights_report(
      start_date=start,
      end_date=end,
      columns=fields
    )
    self.assertIsNotNone(report)

  def test_ad_set_insights(self):
    start = datetime.utcnow() - timedelta(days=2)
    end = datetime.utcnow()
    campaigns = self.reporter.api.get_campaigns()
    ad_sets = self.reporter.api.get_ad_sets(campaigns=campaigns)
    fields = [
      'account_id',
      'account_name',
      'account_currency',
      'campaign_id',
      'campaign_name',
      'adset_id',
      'adset_name',
      'impressions',
      'clicks',
      'spend',
      'unique_clicks',
      'actions',
      'date_start',
      'date_stop',
      'frequency',
    ]
    report = self.reporter.get_ad_set_insights_report(
      start_date=start, 
      end_date=end, 
      ad_sets=ad_sets, 
      columns=fields
    )
    self.assertIsNotNone(report)
  
  def test_ad_insights(self):
    start = datetime.utcnow() - timedelta(days=1)
    end = datetime.utcnow()
    campaigns = self.reporter.api.get_campaigns()
    ad_sets = self.reporter.api.get_ad_sets(campaigns=campaigns)
    ads = self.reporter.api.get_ads(ad_sets=ad_sets)

    columns = [
      'ad_id',
      'ad_name',
      'adset_id',
      'adset_name',
      'campaign_id',
      'campaign_name',
      'frequency',
      'impressions',
      'outbound_clicks',
      'reach',
      'relevance_score',
      'impressions',
      'social_spend',
      'clicks',
      'unique_clicks',
      # 'video_10_sec_watched_actions',
      # 'video_30_sec_watched_actions',
      # 'video_avg_percent_watched_actions',
      # 'video_avg_time_watched_actions',
      # 'video_p100_watched_actions',
      # 'video_p25_watched_actions',
      # 'video_p50_watched_actions',
      # 'video_p75_watched_actions',
      # 'video_p95_watched_actions',
    ]

    report = self.reporter.get_ad_insights_report(start_date=start, end_date=end, ads=ads, columns=columns)
    import pdb; pdb.set_trace()
    self.assertIsNotNone(report)