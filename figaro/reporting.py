import pandas as pd

from .base import rate_limit
from . import FacebookAPI
from typing import Optional, List, Dict
from datetime import datetime
from facebook_business.adobjects.campaign import Campaign

class FacebookReporter:
  api: FacebookAPI

  def __init__(self, api: FacebookAPI):
    self.api = api
  
  def get_campaign_insights_report(self, start_date: datetime, end_date: datetime, campaigns: Optional[List[any]] = None, columns: List[str] = []) -> pd.DataFrame:
    params = {
      'time_increment': 1,
      'time_range': {
        'since' : start_date.strftime('%Y-%m-%d'),
        'until' : end_date.strftime('%Y-%m-%d'),
      },
    }

    data_frame = pd.DataFrame([])

    if campaigns is None:
      campaigns = self.api.get_campaigns()

    for campaign in campaigns:
      insights_data_frame = self.get_campaign_insights(campaign=campaign, fields=columns, params=params)        
      data_frame = data_frame.append(insights_data_frame)

    data_frame.reset_index(drop=True, inplace=True)
    return data_frame

  def get_ad_set_insights_report(self, start_date: datetime, end_date: datetime, ad_sets: Optional[List[any]], columns: List[str]=[]) -> pd. DataFrame:
    params = {
      'time_increment': 1,
      'time_range': {
        'since' : start_date.strftime('%Y-%m-%d'),
        'until' : end_date.strftime('%Y-%m-%d'),
      },
    }

    data_frame = pd.DataFrame([])

    if ad_sets is None:
      campaigns = self.api.get_campaigns()
      ad_sets = self.api.get_ad_sets(campaigns=campaigns)

    for ad_set in ad_sets:
      insights_data_frame = self.get_ad_set_insights(ad_set=ad_set, fields=columns, params=params)
      data_frame = data_frame.append(insights_data_frame)
    
    data_frame.reset_index(drop=True, inplace=True)
    return data_frame

  def get_ad_insights_report(self, start_date: datetime, end_date: datetime, ads: Optional[List[any]], columns: List[str]=[]) -> pd. DataFrame:
    params = {
      'time_increment': 1,
      'time_range': {
        'since' : start_date.strftime('%Y-%m-%d'),
        'until' : end_date.strftime('%Y-%m-%d'),
      },
    }

    data_frame = pd.DataFrame([])

    if ads is None:
      campaigns = self.api.get_campaigns()
      ad_sets = self.api.get_ad_sets(campaigns=campaigns)
      ads = ad_sets

    for ad in ads:
      insights_data_frame = self.get_ad_insights(ad=ad, fields=columns, params=params)
      data_frame = data_frame.append(insights_data_frame)
    
    data_frame.reset_index(drop=True, inplace=True)
    return data_frame

  @rate_limit
  def get_campaign_insights(self, campaign: any, fields: List[str], params: Dict[str, any]) -> pd.DataFrame:
    insights = campaign.get_insights(fields=fields, params=params)    
    df = pd.DataFrame.from_records(insights)
    return self.df_without_unexpected_cols(df, fields)

  @rate_limit
  def get_ad_set_insights(self, ad_set: any, fields: List[str], params: Dict[str, any]) -> pd.DataFrame:
    insights = ad_set.get_insights(fields=fields, params=params)
    df = pd.DataFrame.from_records(insights)
    return self.df_without_unexpected_cols(df, fields)
  
  @rate_limit
  def get_ad_insights(self, ad: any, fields: List[str], params: Dict[str, any]) -> pd.DataFrame:
    insights = ad.get_insights(fields=fields, params=params)
    df = pd.DataFrame.from_records(insights)
    return self.df_without_unexpected_cols(df, fields)
  
  def df_without_unexpected_cols(self, data_frame: pd.DataFrame, expected_cols: List[str]) -> pd.DataFrame:
    return pd.DataFrame(data_frame, columns=expected_cols)