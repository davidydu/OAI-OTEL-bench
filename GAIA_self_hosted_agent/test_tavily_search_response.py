from tavily import TavilyClient
import os

# Step 1. Instantiating your TavilyClient
tavily_client = TavilyClient(api_key=os.getenv("TAVILY_API_KEY"))

# Step 2. Executing a simple search query
# response = tavily_client.search("How many studio albums were published by Mercedes Sosa between 2000 and 2009 (included)? You can use the latest 2022 version of english wikipedia.")
"""
{'query': 'How many studio albums were published by Mercedes Sosa between 2000 and 2009 (included)? You can use the latest 2022 version of english wikipedia.', 'follow_up_questions': None, 'answer': None, 'images': [], 
'results': [{'url': 'https://en.wikipedia.org/wiki/Mercedes_Sosa', 'title': 'Mercedes Sosa - Wikipedia', 'content': 'Her career spanned four decades and she was the recipient of six Latin Grammy awards (2000, 2003, 2004, 2006, 2009, 2011), including a Latin Grammy Lifetime', 'score': 0.6551821, 'raw_content': None}, 
{'url': 'https://www.wikiwand.com/en/articles/Mercedes_Sosa', 'title': 'Mercedes Sosa - Wikiwand', 'content': 'Studio albums ; 1999, Misa Criolla. Label: Mercury ; 2005, Corazón Libre. Label: Edge ; 2009, Cantora 1 (w/various artists). Label: RCA ; 2009, Cantora 2 (w/various', 'score': 0.4497074, 'raw_content': None}, 
{'url': 'https://en.wikipedia.org/wiki/Cantora,_un_Viaje_%C3%8Dntimo', 'title': 'Cantora, un Viaje Íntimo - Wikipedia', 'content': 'Cantora, un Viaje Íntimo is a double album by Argentine singer Mercedes Sosa, released on 2009 through Sony Music Argentina. The album features Cantora 1', 'score': 0.3955783, 'raw_content': None}, 
{'url': 'https://en.wikipedia.org/wiki/Category:Mercedes_Sosa_albums', 'title': 'Category:Mercedes Sosa albums - Wikipedia', 'content': 'This category contains albums by Mercedes Sosa. Pages in category "Mercedes Sosa albums". The following 4 pages are in this category, out of 4 total', 'score': 0.34052956, 'raw_content': None}, 
{'url': 'https://www.discogs.com/artist/333361-Mercedes-Sosa?srsltid=AfmBOor3WUPOYx519c-Wmlso3F-Yp81BliF2IiMXEr04k7MqFiQ-oVQg', 'title': 'Mercedes Sosa Discography: Vinyl, CDs, & More | Discogs', 'content': "Explore Mercedes Sosa's biography, discography, and artist credits. Shop rare vinyl records, top albums, and more on Discogs.", 'score': 0.23004547, 'raw_content': None}], 'response_time': 1.82}
"""

# Step 2. Executing a context search query
response = tavily_client.get_search_context(query="How many studio albums were published by Mercedes Sosa between 2000 and 2009 (included)? You can use the latest 2022 version of english wikipedia.")

# Step 2. Executing a Q&A search query
# response = tavily_client.qna_search(query="How many studio albums were published by Mercedes Sosa between 2000 and 2009 (included)?")



# Step 3. That's it! You've done a Tavily Search!
print(response)