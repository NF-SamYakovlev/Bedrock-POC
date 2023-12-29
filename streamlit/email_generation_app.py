import json, boto3
import streamlit as st
from bedrock_payloads import build_payload

st.set_page_config(page_title="C2FO Copilot", page_icon=":love_letter:", layout="wide")

# TARGET USE CASE: Post-call wrapup email
# TODO: Ingest data from voice call transcripts stored in an S3 bucket

boto3.setup_default_session(profile_name='neuraflash_dev_sso')
# Bedrock Runtime client used to invoke and question the models
bedrock_runtime = boto3.client(
    service_name='bedrock-runtime', 
    region_name='us-east-1'
)

# Form parameters
sales_stages = ['Prospecting', 'Discovery', 'Present Solution', 'Consideration', 'Participation', 'Repeat Use']
bedrock_response = "Your bedrock response will appear here!"
full_prompt = 'this is the model input'

st.title("SRM Copilot Demo")

with st.sidebar:
    st.header("Configuration")
    st.subheader("Sales")
    col1, col2, col3 = st.columns([1,1,1])
    with col1:
        sales_stage = st.radio("Sales Process Stage", sales_stages, key="sales_stage")
    with col2:
        customer_segment = st.radio("Segmentation", ["Sun Spot", "Sweet Spot", "Low Spot"], key="customer_segment")
    with col3: 
        model_selection = st.radio("Model selection", ['Claude v2', 'Titan Embeddings'], horizontal=True, key="model_selection")
    "---"
    st.subheader("Technical")
    #model_selection = st.radio("Model selection", ['Claude v2', 'Titan Embeddings'], horizontal=True, key="model_selection")
    output_format = st.text_area("Bedrock output format", height = 110, value="Transcript summary, up to two paragraphs long. Highlight key positive and negative points from the customer's side, and any products that were discussed during the call (Early Payment, Cash Flow Plus, or Capitol Finance)", help="what format you'd like the bot responses to take")
    input_prefix = st.text_area("Bedrock prompt prefix", height = 220, value="Given the transcript enclosed in brackets, provide a brief summary and up to three sets of recommendations for next steps.")
    input_suffix = st.text_area("Bedrock prompt suffix", height = 220, value="The customer is not necessarily as familiar with the product as the agent is.")

col1, col2 = st.columns([3,3])

def get_bedrock_response():
    prefix = input_prefix
    body = input_transcript
    suffix = input_suffix
    
    print("boto3 version: " + boto3.__version__)
    
    full_prompt = 'Human: ' + prefix + '\n\nThe customer is in the ' + sales_stage + ' stage of the sales process.\n' + st.session_state[sales_stage] + '\n\n  \n\n[' + body + ']\n\n ' + suffix + '\n\nGenerate these in the form of ' + output_format + '\nAssistant:'
    
    # The payload to be provided to Bedrock 
    #payload = {
    #        "modelId": "anthropic.claude-v2",
    #        "contentType": "application/json",
    #        "accept": "*/*",
    #        "body": {
    #            "prompt": full_prompt,
    #            "max_tokens_to_sample": 500,
    #            "temperature": 0.5,
    #            "top_k": 300,
    #            "top_p": 1,
    #            "stop_sequences": [],
    #            "anthropic_version": "bedrock-2023-05-31"
    #        }
    #    }
    payload = build_payload(model_selection, full_prompt)
    
    
    # The actual call to retrieve an answer from the model
    response = bedrock_runtime.invoke_model(
        modelId = payload["modelId"],
        body = json.dumps(payload["body"])
    )

    print(response)

    response_body = json.loads(response.get('body').read())
    answer = response_body.get('completion') #[0].get('data').get('text')

    bedrock_response = answer                       # Update contents of bedrock response text area
    st.session_state.bedrock_result = answer        # Redundancy for above, may not be necessary?
    st.session_state.bedrock_prompt = full_prompt
    
    return {
        'statusCode': 200,
        'headers': {
            'Access-Control-Allow-Headers': '*',
            'Access-Control-Allow-Origin': '*',
            'Access-Control-Allow-Methods': 'OPTIONS,POST,GET'
        },
        'body': json.dumps({ "Answer": answer })
    }

with st.container():
    with col1:
        tab1, tab2, tab3 = st.tabs(['Input Transcript', 'Sales Process Stage Prompts', 'Segment Descriptions'])
        with tab1:
            input_transcript = st.text_area('Input Transcript',height = 415)
            interest_level = st.select_slider('How interested in the product would you say the customer felt during this call?', 
                            options = ['Very Cold', 'Cold', 'Neutral', 'Hot', 'Very Hot'],
                            value=('Neutral'))
            sentiment_level = st.select_slider('How would you describe the tone of this call?',
                            options = ['Very Unfriendly', 'Mildly Unfriendly', 'Neutral', 'Mildly Friendly', 'Very Friendly'],
                            value=('Neutral'))
            urgency_level = st.select_slider('How urgent are the topics on this call?',
                            options = ['Not Urgent at All', 'Not Very Urgent', 'Neutral', 'Mildly Urgent', 'Very Urgent'],
                            value=('Neutral'))
            extra_smalltalk = st.text_area('Additional context/smalltalk discussed during these calls')
            product_selection = st.multiselect(
                'Products Discussed',
                ['Early Payment', 'Cash Flow Plus', 'Capitol Finance'],
                [])
        with tab2:
            st.text_area("Prospecting", key="Prospecting", value='Prospecting accounts, trying to ensure the right person is being sold the C2FO product', help='Prospecting accounts, trying to ensure the right person is being sold the C2FO product.')
            st.text_area("Discovery", key="Discovery", value='We are trying to determine the supplier\'s specific use case here.', help='We are trying to determine the supplier\'s specific use case here.')
            st.text_area("Present Solution", key="Present Solution", value='The supplier has been onboarded and has access to the product itself. We are showing them real-time examples of how to use the C2FO platform as they come in, to give a better idea of how to use it.', help='The supplier has been onboarded and has access to the product itself. We are showing them real-time examples of how to use the C2FO platform as they come in, to give a better idea of how to use it.')
            st.text_area("Consideration", key="Consideration", value='How would this be used? What kind of benefits could the C2FO platform give us?', help='How would this be used? What kind of benefits could the C2FO platform give us?')
            st.text_area("Participation", key="Participation", value='The supplier has begun using the C2FO platform actively.', help='The supplier has begun using the C2FO platform actively.')
            st.text_area("Repeat Use", key="Repeat Use", value='The supplier has begun using the C2FO platform actively.', help='The supplier is now a recurring user of the C2FO platform.')
            #for stage in sales_stages:
            #    st.text_area(stage, key=stage, help='Additional information to be provided to the model if the ' + stage + ' stage is selected.')         
        with tab3:
            st.text_area("Sun Spot", key="Sun Spot", help='This is a large company, selling large amounts of products to a large amount of customers')
            st.text_area("Sweet Spot", key="Sweet Spot", help='This is a medium-sized company, selling some products to a decent amount of customers without being overwhelming')
            st.text_area("Low Spot", key="Low Spot", help='This is a smaller company, potentially with a smaller amount of customers and sales over time')   
        st.button('Submit Request', 'submit', on_click=get_bedrock_response)
        
    with col2:
        tab1, tab2 = st.tabs(['Model Response', 'Complete Model Prompt'])
        with tab1:
            st.text_area(bedrock_response, key="bedrock_result",  height = 775, disabled=True, help='This is the response provided by the bedrock API after the model has been invoked')
            st.download_button('Download response', bedrock_response, "C2FO_Bedrock_Generated_Email")
        with tab2: 
            st.text_area(full_prompt, key="bedrock_prompt", height = 775, disabled=True, help='This is the prompt we use to invoke the model')