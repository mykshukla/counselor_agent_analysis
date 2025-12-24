from app.queries.queries import SQL_CAMPAIGN_COUNSELOR, SQL_CAMPAIGN_OVERVIEW
from app.repository.repository import getSqlCampaign, getSqlCampaignCounselor
from app.utils.utils import _query_df, detect_waste, df_to_rows, enrich_rows, paginate


def call_backend(func_name: str, args: dict) -> dict:

    print(func_name)
    print(args)
    
    if func_name == "get_campaign_overview":

        sql, params=getSqlCampaign(SQL_CAMPAIGN_OVERVIEW, {
            "start_date": args["start_date"],
            "end_date": args["end_date"],
            "country": args.get("country"),
        })
        #print(sql)
        rows = _query_df(sql, params)
        df=df_to_rows(rows)
        #print(df)
        rows = enrich_rows(df)
        # sort by weight for “best campaign” feel
        rows.sort(key=lambda x: float(x.get("weight", 0) or 0), reverse=True)
        page = args.get("page", 1)
        page_size = args.get("page_size", 100)
        return paginate(rows, page, page_size)

    if func_name == "get_campaign_counselor_performance":

        sql, params=getSqlCampaignCounselor(SQL_CAMPAIGN_COUNSELOR, {
            "start_date": args["start_date"],
            "end_date": args["end_date"],
            "campaign": args.get("campaign"),
            "country": args.get("country"),
        })
        rows = _query_df(sql, params)
        df=df_to_rows(rows)
        rows = enrich_rows(df)
        rows = enrich_rows(rows)
        rows.sort(key=lambda x: (float(x.get("enrollments", 0) or 0), float(x.get("leads", 0) or 0)), reverse=True)
        return paginate(rows, args.get("page", 1), args.get("page_size",100))

    if func_name == "get_campaign_waste_report":

        sql, params=getSqlCampaign(SQL_CAMPAIGN_OVERVIEW, {
            "start_date": args["start_date"],
            "end_date": args["end_date"],
            "country": None,
        })
        rows = _query_df(sql, params)
        df=df_to_rows(rows)
        rows = enrich_rows(df)
        rows = enrich_rows(rows)
        waste = detect_waste(rows, min_spend=float(args.get("min_spend", 500)))
        return {"total_scanned": len(rows), "waste_top": waste}

    return {"error": f"Unknown tool: {func_name}", "args": args}