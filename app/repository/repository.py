
from typing import Any, List

from app.utils.utils import normalize_country, normalize_param, sanitize_params


def getSqlCampaign(sql: str,  args: dict):
    params: List[Any] = [args.get("start_date"), args.get("end_date")]  

    country=normalize_param(args.get("country"))
    if country:
        sql += " AND C.NAME = %s"
        params.append(normalize_country(country))

    sql+="""
        GROUP BY L.UTM_CAMPAIGN
        ORDER BY enrollments DESC, leads DESC   
        """ 
    #params = sanitize_params(sql, params)
    return sql, params 

def getSqlCampaignCounselor(sql: str,  args: dict):
    params: List[Any] = [args.get("start_date"), args.get("end_date")]  
    
    country=normalize_param(args.get("country"))
    if country:
        sql += " AND C.NAME = %s"
        params.append(normalize_country(country))

    campaign=normalize_param(args.get("campaign"))
    if campaign:
        sql += " AND L.UTM_CAMPAIGN LIKE %s"
        params.append(f"%{campaign.strip()}%")    

    sql+="""
        GROUP BY L.UTM_CAMPAIGN, U.USER_FULL_NAME
        ORDER BY enrollments DESC, demos DESC, leads DESC     
        """ 
    
    #params = sanitize_params(sql, params)

    return sql, params  


def getSqlCampaignMatrix(sql: str,  args: dict):
    params: List[Any] = [args.get("start_date"), args.get("end_date")]    

    country=normalize_param(args.get("country"))
    if country:
        sql += " AND C.NAME = %s"
        params.append(normalize_country(country))

    sql+="""
        GROUP BY L.UTM_CAMPAIGN, C.NAME 
        ORDER BY enrollments DESC, leads DESC
        """ 
    #params = sanitize_params(sql, params)
    return sql, params 


def getSqlCounselorMatrix(sql: str,  args: dict):
    params: List[Any] = [args.get("start_date"), args.get("end_date")]  

    country=normalize_param(args.get("country"))
    if country:
        sql += " AND C.NAME = %s"
        params.append(normalize_country(country))

    sql+="""
       GROUP BY U.ID, U.USER_FULL_NAME, C.NAME 
       ORDER BY enrollments DESC, leads DESC  
        """ 

    #params = sanitize_params(sql, params)
    return sql, params 

def getSqlCampaignCounselorMetrics(sql: str,  args: dict):
    params: List[Any] = [args.get("start_date"), args.get("end_date")]  
    
    country=normalize_param(args.get("country"))
    country=normalize_country(country)
    if country:
        sql += " AND C.NAME = %s"
        params.append(country)

    campaign=normalize_param(args.get("campaign"))
    if campaign:
        sql += " AND L.UTM_CAMPAIGN LIKE %s"
        params.append(f"%{campaign.strip()}%")    

    sql+="""
        GROUP BY L.UTM_CAMPAIGN, U.ID, U.USER_FULL_NAME, C.NAME
        ORDER BY campaign_name, enrollments DESC, leads DESC    
        """ 

    #params = sanitize_params(sql, params)
    return sql, params 


