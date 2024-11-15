from rufus import RufusClient

client = RufusClient(api_key="your_api_key")
instructions = "tell me about the FAQs and the product differentiator for Delve"
results = client.scrape("https://www.getdelve.com/", instructions)
