from langchain_openai import ChatOpenAI  
import os  
import httpx  
client = httpx.Client(verify=False) 
llm = ChatOpenAI( 
base_url="https://genailab.tcs.in" ,
model = "gemini-2.5-pro", 
api_key="sk-Xnp0YZBIyM-bn3hobXm8EA", 
http_client = client 
) 
response = llm.invoke("Hi")

print(response)
print("----------------------")
print(response.content)