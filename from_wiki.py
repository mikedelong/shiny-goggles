import wikipediaapi
import pandas as pd


# https://towardsdatascience.com/auto-generated-knowledge-graphs-92ca99a81121
def wiki_page(page_name):
    wiki_api = wikipediaapi.Wikipedia(language='en', extract_format=wikipediaapi.ExtractFormat.WIKI)
    page_name = wiki_api.page(page_name)
    if page_name.exists():
        return pd.DataFrame({'page': page_name, 'text': page_name.text, 'link': page_name.fullurl,
                             'categories': [[y[9:] for y in list(page_name.categories.keys())]]})
    else:
        return None
