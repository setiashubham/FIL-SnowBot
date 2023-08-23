import streamlit as st

Tables=[{'QUALIFIED_TABLE_NAME' : "FINANCEDWH.FDWH.FINANCIALS",
'METADATA_QUERY' : "SELECT REPORTING_PERIOD,CLIENT_ID,CHANNEL_ID,REGION_ID,FUND_ID,CURRENCY,SALES,ASSETS,REVENUE,COMMENTS FROM FINANCEDWH.FDWH.FINANCIALS;",
'TABLE_DESCRIPTION' : "This table is about financials."},
{'QUALIFIED_TABLE_NAME' : "FINANCEDWH.FDWH.CHANNEL",
'METADATA_QUERY' : "SELECT CHANNEL_ID,CHANNEL_NAME,COMMENTS FROM FINANCEDWH.FDWH.CHANNEL;",
'TABLE_DESCRIPTION' : "This table is about Channels."}
]


GEN_SQL = """{context}"""

#@st.cache_data(show_spinner=False)
def get_table_context(table_name: str, table_description: str, metadata_query: str = None):
    table = table_name.split(".")
    conn = st.experimental_connection("snowpark")
    columns = conn.query(f"""
        SELECT COLUMN_NAME, DATA_TYPE FROM {table[0].upper()}.INFORMATION_SCHEMA.COLUMNS
        WHERE TABLE_SCHEMA = '{table[1].upper()}' AND TABLE_NAME = '{table[2].upper()}'
        """,
    )
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
        #st.text(len(metadata))
        '''metadata = "\n".join(
            [
                f"- **{metadata['REPORTING_PERIOD'][i]}**: {metadata['COMMENTS'][i]}"
                for i in range(len(metadata["REPORTING_PERIOD"]))
            ]
        )'''
        context = context + f"\n\nAvailable variables by REPORTING_PERIOD:\n\n{metadata}"
    return context

def get_system_prompt():
    st.header("System prompt for FIL SnowBot")
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