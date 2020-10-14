from .base import rate_limit
from typing import Optional, List, Dict
from itertools import chain
from datetime import datetime
from facebook_business import FacebookSession
from facebook_business import FacebookAdsApi
from facebook_business.adobjects.adaccount import AdAccount
from facebook_business.adobjects.adaccountuser import AdAccountUser as AdUser
from facebook_business.adobjects.campaign import Campaign
from facebook_business.adobjects.adset import AdSet
from facebook_business.adobjects.ad import Ad
from facebook_business.adobjects.adcreative import AdCreative
from facebook_business.adobjects.objectparser import ObjectParser
from facebook_business.adobjects.adactivity import AdActivity

class FacebookAPI:
  ad_user: AdUser
  account: Optional[AdAccount]
  api: FacebookAdsApi

  def __init__(self, app_id: str, app_secret: str, access_token: str, ad_user_id: str, api_version: str):
    session = FacebookSession(app_id, app_secret, access_token)
    self.api = FacebookAdsApi(session, api_version=api_version)
    FacebookAdsApi.set_default_api(self.api)
    self.ad_user = AdUser(fbid=ad_user_id)

  @property
  def account_id(self) -> Optional[int]:
    return None if self.account is None else int(self.account['id'].split('_')[-1])

  @account_id.setter
  def account_id(self, id: Optional[int]):
    if id is None:
      self.account = None
      return 

    self.account = AdAccount('act_{}'.format(id))

  @rate_limit
  def limit(self):
    pass

  @rate_limit
  def get_account(self, account_id: int) -> AdAccount:
    account = AdAccount('act_{}'.format(account_id))
    account.api_get(fields=[
      'account_id',
      'currency',
      'timezone_name',
    ])
    return account

  @rate_limit
  def get_campaigns(self) -> List[Campaign]:
    return list(self.account.get_campaigns(fields=[
      Campaign.Field.id,
      Campaign.Field.name,
      Campaign.Field.status,
      Campaign.Field.updated_time,
      Campaign.Field.objective
    ]))

  def get_ad_sets(self, campaigns: List[Campaign]) -> List[AdSet]:
    def chunks(l, n):
      for i in range(0, len(l), n):
        yield l[i:i + n]

    campaign_batches = list(chunks(campaigns, 50))
    ad_sets = list(chain.from_iterable([self.get_ad_sets_batch(campaigns=batch) for batch in campaign_batches]))
    return ad_sets
  
  def get_ads(self, ad_sets: List[AdSet]) -> List[Ad]:
    def chunks(l, n):
      for i in range(0, len(l), n):
        yield l[i:i + n]

    ad_sets_batches = list(chunks(ad_sets, 50))
    ads = list(chain.from_iterable([self.get_ads_batch(ad_sets=batch) for batch in ad_sets_batches]))
    return ads

  def get_ad_creatives(self, object_ids: List[str]) -> List[AdCreative]:
    def chunks(l, n):
      for i in range(0, len(l), n):
        yield l[i:i + n]

    ad_creatives_batches = list(chunks(object_ids, 50))
    ad_creatives = list(chain.from_iterable([self.get_ad_creatives_batch(object_ids=batch) for batch in ad_creatives_batches]))
    return ad_creatives

  @rate_limit
  def get_ad_sets_batch(self, campaigns: List[Campaign]) -> List[AdSet]:
    ad_sets = []
    parser = ObjectParser(api=self.api, target_class=AdSet)

    def success(response):
      nonlocal ad_sets
      nonlocal parser
      nonlocal self
      ad_sets += self.get_all_pages(first_page=response.json(), parser=parser)

    def failure(response):
      print('ad set failure response', response.error())
      raise response.error()

    batch = self.api.new_batch()
    for campaign in campaigns:
      request = campaign.get_ad_sets(
        fields=[
          AdSet.Field.id,
          AdSet.Field.name,
          AdSet.Field.status,
          AdSet.Field.updated_time,
          AdSet.Field.campaign_id,
          AdSet.Field.targeting,
          AdSet.Field.promoted_object
        ],
        pending=True
      )
      request.add_to_batch(batch=batch, success=success, failure=failure)

    batch.execute()
    return ad_sets

  @rate_limit
  def get_ads_batch(self, ad_sets: List[AdSet]) -> List[Ad]:
    ads = []
    parser = ObjectParser(api=self.api, target_class=Ad)

    def success(response):
      nonlocal ads
      nonlocal parser
      nonlocal self
      ads += self.get_all_pages(first_page=response.json(), parser=parser)

    def failure(response):
      print('ad failure response', response.error())
      raise response.error()

    batch = self.api.new_batch()
    for ad_set in ad_sets:
      request = ad_set.get_ads(
        fields=[
          Ad.Field.id,
          Ad.Field.name,
          Ad.Field.status,
          Ad.Field.updated_time,
          Ad.Field.campaign_id,
          Ad.Field.adset,
          Ad.Field.adset_id,
          Ad.Field.tracking_specs,
          Ad.Field.source_ad,
          Ad.Field.source_ad_id,
          Ad.Field.creative,
        ],
        pending=True
      )
      request.add_to_batch(batch=batch, success=success, failure=failure)

    batch.execute()
    return ads

  @rate_limit
  def get_ad_creatives_batch(self, object_ids: List[str]) -> List[AdCreative]:
    ad_creatives = []
    parser = ObjectParser(api=self.api, target_class=AdCreative)
    params = {
      'thumbnail_height': 256,
      'thumbnail_width': 256,
    }

    def success(response):
      nonlocal ad_creatives
      nonlocal parser
      nonlocal params
      nonlocal self
      ad_creatives += self.get_all_pages(first_page=response.json(), parser=parser, params=params)

    def failure(response):
      print('ad creative failure response', response.error())
      raise response.error()

    batch = self.api.new_batch()
    for id in object_ids:
      creative = AdCreative(id)
      creative.api_get(
        batch=batch, 
        params=params,
        fields=[
          AdCreative.Field.name,
          AdCreative.Field.title,
          AdCreative.Field.body,
          AdCreative.Field.image_url,
          AdCreative.Field.thumbnail_url,
        ],
        success=success,
        failure=failure
      )

    batch.execute()
    return ad_creatives

  def get_ad_activity_history(self, start_date: datetime, end_date: datetime, object_ids: List[str]=[]) -> List[AdActivity]:
    parameters = {
      'category': AdActivity.Category.ad,
      'since': start_date,
      'until': end_date,
    }
    if object_ids:
      parameters['extra_oids'] = object_ids

    fields = [
      AdActivity.Field.event_time,
      AdActivity.Field.event_type,
      AdActivity.Field.extra_data,
      AdActivity.Field.object_id,
      AdActivity.Field.object_name,
    ]
    return list(self.account.get_activities(fields=fields, params=parameters))

  def get_all_pages(self, first_page: any, parser: ObjectParser, params: Optional[Dict[any, any]]=None):
    json = first_page
    objects = parser.parse_multiple(json)
    while 'paging' in json and 'next' in json['paging']:
      self.limit()
      json = self.api.call('GET', json['paging']['next'], params=params).json()
      objects += parser.parse_multiple(json)
    return objects
