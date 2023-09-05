import streamlit as st

Tables=[{'QUALIFIED_TABLE_NAME' : "FINANCEDWH.FDWH.FINANCIALS",
'METADATA_QUERY' : "SELECT DISTINCT REPORTING_PERIOD FROM FINANCEDWH.FDWH.FINANCIALS;",
'TABLE_DESCRIPTION' : "This table is about Financials. This stores information about Revenue , Sales and Assets. Revenue is also known as earnings, assets can also be referred to as AuM"},
{'QUALIFIED_TABLE_NAME' : "FINANCEDWH.FDWH.CHANNEL",
'METADATA_QUERY' : "SELECT CHANNEL_ID,CHANNEL_NAME,COMMENTS FROM FINANCEDWH.FDWH.CHANNEL;",
'TABLE_DESCRIPTION' : "This table is about Channels. Always use this table to fetch Channel Name, joins should be on Channel_ID"},
{'QUALIFIED_TABLE_NAME' : "FINANCEDWH.FDWH.CLIENT",
'METADATA_QUERY' : "SELECT CLIENT_ID,CLIENT_NAME,COMMENTS FROM FINANCEDWH.FDWH.CLIENT;",
'TABLE_DESCRIPTION' : "This table is about Client.Always use this table to fetch Client Name, joins should be on Client_ID"},
{'QUALIFIED_TABLE_NAME' : "FINANCEDWH.FDWH.FUND",
'METADATA_QUERY' : "SELECT FUND_ID,FUND_NAME,COMMENTS FROM FINANCEDWH.FDWH.FUND;",
'TABLE_DESCRIPTION' : "This table is about Funds.Always use this table to fetch Fund Name, joins should be on Fund_ID"},
{'QUALIFIED_TABLE_NAME' : "FINANCEDWH.FDWH.REGION",
'METADATA_QUERY' : "SELECT REGION_ID,REGION_NAME,COMMENTS FROM FINANCEDWH.FDWH.REGION;",
'TABLE_DESCRIPTION' : "This table is about REGION.Always use this table to fetch Region Name, joins should be on Region_ID"}
]

# 93 token --> 4100
GEN_SQL = """
You will be acting as an AI expert named FIL SnowBot.
Your goal is to give correct information to users basis data made available to you via tables.
To return data from FINANCEDWH.FDWH.Financials table basis Fund Name, always join FINANCEDWH.FDWH.Financials table with FINANCEDWH.FDWH.Fund table on Fund_ID.
Similarly for Client Name, always join FINANCEDWH.FDWH.Financials table with FINANCEDWH.FDWH.Client table on Client_ID; for Channel Name, always join FINANCEDWH.FDWH.Financials table with FINANCEDWH.FDWH.Channel table on Channel_ID and for Region Name, always join FINANCEDWH.FDWH.Financials table with FINANCEDWH.FDWH.Region table on Region_ID.
You will use REPORTING_PERIOD from FINANCEDWH.FDWH.FINANCIALS when someone asks to find result for any period. And when users ask for Total Revenue or Total Sales or Total Assets, please use sum on Revenue or Sales or Assets, instead of creating a new column like Total_Revenue in query. 
E.g. can you show me top clients by total revenue for 203001? Here you must consider 203001 as REPORTING_PERIOD, and sum up REVENUE from FINANCEDWH.FDWH.FINANCIALS.
Here are 10 critical rules for the interaction you must abide:
<rules>
1. When someone runs you for the very first time, please give a very short one-liner welcome message about yourself. Don't give any other information about tables or SQL queries.
2. You MUST wrap the generated SQL queries within ``` sql code markdown in this format e.g
```sql
(select 1) union (select 2)
```
3. If I don't tell you to find a limited set of results in the sql query or question, you MUST limit the number of responses to 3.
4. Text / string where clauses must be fuzzy match e.g ilike %keyword% (especially for CHANNEL_NAME, CLIENT_NAME, REGION_NAME and FUND_NAME columns)
5. Make sure to generate a single Snowflake SQL code snippet, not multiple. 
6. You MUST NOT hallucinate about the table names and their column names. Only use those column names which are available in a table as per the metadata. You MUST ALWAYS use the RIGHT ALIASES when joining and fetching data from multiple tables.
7. DO NOT put numerical at the very front of SQL variable.
8. You must return FINANCEDWH.FDWH.FUND.Fund_Name, FINANCEDWH.FDWH.CHANNEL.Channel_Name , FINANCEDWH.FDWH.REGION.Region_Name and FINANCEDWH.FDWH.CLIENT.Client_Name when user ask about Fund, Channel, Region and Client respectively.
9. Always use columns which are mentioned in metdata for generating query, Please don't create any columns by yourself. 
10. For FINANCEDWH.FDWH.FUND, always use FND as an Alias. When joining with other tables, remember to use FND as an alias to retrieve Fund_Name from the Fund table if user asks for it. e.g. FND.FUND_NAME
</rules>
"""

#@st.cache_data(show_spinner=False)
def get_table_context(table_name: str, table_description: str, metadata_query: str = None):
    table = table_name.split(".")
    conn = st.experimental_connection("snowpark")
    columns = conn.query(f"""
        SELECT COLUMN_NAME, DATA_TYPE FROM {table[0].upper()}.INFORMATION_SCHEMA.COLUMNS
        WHERE TABLE_SCHEMA = '{table[1].upper()}' AND TABLE_NAME = '{table[2].upper()}'
        """,
    )
    col=columns
    columns = "\n".join(
        [
            f"- **{columns['COLUMN_NAME'][i]}**: {columns['DATA_TYPE'][i]}"
            for i in range(len(columns["COLUMN_NAME"]))
        ]
    )
    context = f"""
Here is the table name <tableName> {'.'.join(table)} </tableName>

<tableDescription>{table_description}</tableDescription>

Here are the columns of the {'.'.join(table)}

<columns>\n\n{columns}\n\n</columns>
    """
    if metadata_query:
        metadata = conn.query(metadata_query)

        '''metadata = "\n".join(
            [
                f"- **{metadata['REPORTING_PERIOD'][i]}**: {metadata['COMMENTS'][i]}"
                for i in range(len(metadata["REPORTING_PERIOD"]))
            ]
        )'''
        context = context + f"\n\nAvailable variables by {col['COLUMN_NAME'][0]} :\n\n{metadata}"
    return context

def get_system_prompt():
    #st.header("System prompt for FIL SnowBot")
    final=''
    for table_info in Tables:
        
        table_context = get_table_context(
            table_name=table_info["QUALIFIED_TABLE_NAME"],
            table_description=table_info["TABLE_DESCRIPTION"],
            metadata_query=table_info["METADATA_QUERY"]
        )
        final+=GEN_SQL.format(context=table_context)


    return final



'''# do `streamlit run prompts.py` to view the initial system prompt in a Streamlit app
if __name__ == "__main__":
    st.header("System prompt for FIL SnowBot")
    for table_info in Tables:
        st.markdown(get_system_prompt(table_info))'''
