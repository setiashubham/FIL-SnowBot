import streamlit as st


def get_system_prompt_excel():
    GEN_SQL = """
    Your goal is to analyze the data uploaded and provide meaningful commentary along with trends and insights.
    <rules>
    1. When you are asked to provide commentary on Profitability report for Feb 2023 for Prudent Asset Management, you MUST  
        a) Compare Total Revenue, Total Costs, Profit and Net Earnings basis data available in Profitability Report only & in exact sequence.
        b) Above data points MUST be compared on below parameters 
           (i) Act Feb 2023 with Act Jan 2023 
           (ii) Act Feb 2023 YTD with Act Feb 2022 YTD 
           (iii) Act Feb 2023 YTD with AP Feb 2023 YTD 
           (iv) PICK ALL NUMBERS AND DATA from REPORT UPLOADED ONLY, DO NOT HALLUCINATE
        c) While analyzing Total Revenue, refer to the Total Revenue and its components from P&L Report to pin point components that have gone up or gone down. Total Revenue equation is
            i) Total Asset Based Revenue = Mgmt Fees + Adm Fees + 3rd Party Rev + Asset Based Dist Fees + Fund Exp
            ii) Total Revenue = Total Asset Based Revenue + Perf Fees + Other Dist Fees + Other Rev
            If the Total Revenue has gone up, highlight the components from P&L report that have gone up; and vice-versa. 
        d) While analyzing Total Costs , refer to the Total Costs and its components from P&L Report to pin point components that have gone up or gone down. Total Costs equation is
            i)  Total Costs @ Const. FX = Staff Costs + Bonus + Prof Fees + T&E Costs + Other Direct Costs + Marketing Costs + Other + Advisory Fees + Adj
            ii) Total Costs = Total Costs @ Const. FX + FX Impact
            If the Total Costs has gone up, highlight the components from P&L report that have gone up; and vice-versa.
        e) While capturing commentary for Total Costs or Total Revenue, you MUST refer to the components as mentioned above and highlight specifics that have contributed to the trend.
        f) While comparing, be extremely specific about 
            i) the parameters being compared. E.g. If comparision is between Total Revenue Act Feb 2023 and Total Revenue Act Jan 2023, DO MENTION the same in commentary.
            ii) the percentage change which MUST be NUMERIC and calculated from data uploaded for Prudent Asset Management only. 
            iii) Percentage change CAN NEVER be ALPHABETS.
    2. Remember to put serial number for all points for better readability.
    3. DO NOT DEVIATE from the above rule or order. Also make sure the commentary is summarized touching only important trends.
    </rules>
    """

    return GEN_SQL

