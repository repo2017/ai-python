from fastapi import FastAPI
import requests
from bs4 import BeautifulSoup
from urllib.parse import urljoin, urlparse
import textwrap
from langchain.llms import OpenAI
import nltk
from unstructured.partition.html import partition_html
import pandas as pd
from langchain.text_splitter import CharacterTextSplitter
from langchain.embeddings.openai import OpenAIEmbeddings
from langchain.vectorstores import FAISS
from langchain.chains.qa_with_sources import load_qa_with_sources_chain
import os

app = FastAPI()

llm = OpenAI(model_name="gpt-3.5-turbo", temperature=0, openai_api_key=os.getenv("OPENAI_API_KEY"))

chain = load_qa_with_sources_chain(llm, chain_type="stuff")


# @app.post("/")
# async def ask_question():

#     return {"Hello": "World"}


@app.get("/")
async def read_root():
    scrape_docs_into_text('https://python.langchain.com/en/latest/index.html')
    return {"Hello": "World"}


def scrape_docs_into_text(url, level=0):

    # print("\n".join(textwrap.wrap(llm("What is LangChain?").strip())))

    toplevel = "https://langchain.readthedocs.io/en/latest"

    response = requests.get(toplevel)
    print(response.text)

    soup = BeautifulSoup(response.text, 'html.parser')
    print(soup.prettify())

    anchors_attrs = [anchor.attrs for anchor in soup.find_all('a')]

    paths = []
    for anchor_attrs in anchors_attrs:
        try:
            classes = anchor_attrs["class"]
            link = anchor_attrs["href"]
            if "reference" in classes:
                if "internal" in classes:
                    paths.append(link)
                elif "external" in classes:
                    if link.startswith("./"):
                        paths.append(link[len("./"):])
                    else:
                        pass  # not a link to docs
                else:
                    pass  # i didn't understand that reference
            else:
                pass  # not a reference
        except KeyError:
            print("no classes or no href:", anchor_attrs)

    paths = ["index.html"] + paths
    print(paths)
    pages = []
    for path in paths:
        try:
            url = "/".join([toplevel, path])
            resp = requests.get(url)
            resp.raise_for_status()
        except Exception:
            print(url)
        finally:
            pages.append({"content": resp.content, "url": url})

    parsed_docs = [partition_html(text=page["content"]) for page in pages]

    texts = []
    for doc in parsed_docs:
        texts.append("\n\n".join(
            [str(el).strip() for el in doc]).strip().replace("\\n", ""))

    print(*textwrap.wrap(texts[0]), sep="\n")

    for page, text in zip(pages, texts):
        page["text"] = text

    pages[0].keys()

    pd.DataFrame(pages).sample(10)

    text_splitter = CharacterTextSplitter.from_tiktoken_encoder(
        chunk_size=1024, chunk_overlap=128, separator=" ")
    documents = text_splitter.create_documents([page["text"] for page in pages], metadatas=[
                                               {"source": page["url"]} for page in pages])
    print(documents[0].metadata["source"], *
          textwrap.wrap(documents[0].page_content), sep="\n")

    embeddings = OpenAIEmbeddings()

    docsearch = FAISS.from_documents(documents, embeddings)
    query = "What is LangChain?"
    # query = "What is LangChainHub?"
    # query = "Does LangChain integrate with OpenAI? If so, how?"

    docs = docsearch.similarity_search(query)
    result = chain({"input_documents": docs, "question": query})

    text = "\n".join(textwrap.wrap(result["output_text"]))
    text = "\n\nSOURCES:\n".join(
        map(lambda s: s.strip(), text.split("SOURCES:")))

    print(text)
    print(chain.llm_chain.prompt.template)
    print(*textwrap.wrap(result["input_documents"][0].page_content), sep="\n")
