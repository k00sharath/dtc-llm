import openai
import streamlit as st
from elasticsearch import Elasticsearch



def search(query, coursefilter = "data-engineering-zoomcamp", index_name = "faq_search"):


    es_client = Elasticsearch("http://localhost:9200")
    
    search_settings =  {
        "size": 5,
        "query": {
            "bool": {
                "must": {
                    "multi_match": {
                        "query": query,
                        "fields": ["question", "text", "section"],
                        "type": "best_fields"
                    }
                },
                "filter": {
                    "term": {
                        "course": coursefilter
                    }
                }
            }
        }
    }

    response = es_client.search(index = index_name, body = search_settings)

    result_docs = []
   
    #print(response)
    for hit in response['hits']['hits']:

        result_docs.append(hit['_source'])
    
    return result_docs


def build_prompt(query, related_docs):

    

    prompt = """
    You are an assistant for teaching online courses answer the question based on the context provided.
    Only the information available in the provided context should be used strictly adhere to this
    
    question:{query}
    
    context:{context}
    
    
    """.strip()
    
    
    context = ""
    for doc in related_docs:
        
        context += f"section: {doc['section']}\nquestion: {doc['question']}\nanswer: {doc['text']} \n\n"
        
    print("context:",context)
    prompt = prompt.format(query = query, context = context).strip()
    
    return prompt

def chat(prompt, model = "phi3"):
   
    client = openai.OpenAI(
        base_url = "http://localhost:11434/v1/",
        
        api_key = "ollama"
    )
    
    response = client.chat.completions.create(
        model = model,
        messages = [{"role":"system", "content":"you are a faq assistant"},
                    {"role": "user", "content": prompt}]
    )
    
    print(response)
    
    return response.choices[0].message.content


def rag(query, model = "phi3"):

    results = search(query = query)
    prompt = build_prompt(query = query, related_docs = results)

    answer = chat(prompt, model = model)

    return answer


def main():
    st.title("RAG Function Invocation")

    user_input = st.text_input("Enter your input:")

    if st.button("Ask"):
        with st.spinner('Processing...'):
            output = rag(user_input)
            st.success("Completed!")
            st.write(output)

if __name__ == "__main__":
    main()