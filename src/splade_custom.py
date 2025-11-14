import json
from splade.models.transformer_rep import Splade
from langchain_core.documents import Document
import numpy as np
import torch
from transformers import AutoModelForMaskedLM, AutoTokenizer
from langchain_core.retrievers import BaseRetriever
from langchain_core.callbacks.manager import (
        AsyncCallbackManagerForRetrieverRun,
        CallbackManagerForRetrieverRun,
        Callbacks,
    )
from langchain_core.runnables import (
    Runnable,
    RunnableConfig,
    RunnableSerializable,
    ensure_config,
)
from typing import List, Optional, Any
from langchain_chroma import Chroma


from langchain_community.embeddings import SentenceTransformerEmbeddings
from langchain_chroma import Chroma
from uuid import uuid4
import os
embeddings = SentenceTransformerEmbeddings(model_name="Alibaba-NLP/gte-base-en-v1.5",model_kwargs={"trust_remote_code": True})

def create_documents(path=rf'{os.environ['PATH_TO_SCRAPED_DATA']}'):
    if path is None:
        path=os.environ['PATH_TO_SCRAPED_DATA']
    with open(path, 'rb') as file:
            data = file.read()
    parsed_data = json.loads(data)
    parsed_data_org = parsed_data

    c = 0
    for c, i in enumerate(parsed_data):
        if c==0:
            continue
        index = parsed_data[i].find('\n\nWe are a team of high-performing')
        parsed_data[i] = parsed_data[i][:index]

    # for i in parsed_data:
    #     parsed_data[i] = i + ' ' + parsed_data[i]
    doc = []
    for i, key in enumerate(parsed_data):
        #print(i, key)
        doc.append(Document(page_content=parsed_data[key], metadata={'source':key}, id=i))

    return doc


class Retriever(BaseRetriever):
    
    def _get_relevant_documents(
        self, query: str, *, run_manager: CallbackManagerForRetrieverRun
    ) -> List[Document]:
        model_id = 'naver/splade-cocondenser-ensembledistil'
        tokenizer = AutoTokenizer.from_pretrained(model_id)
        model = AutoModelForMaskedLM.from_pretrained(model_id)
        doc = create_documents()
        query = query
        temp = -1
        val = -999999
        pq = []
        diction = {}
        vec_store = Chroma(persist_directory='vectorstore', embedding_function=embeddings, collection_name='example1')
        ret = vec_store.as_retriever(search_kwargs = {'k':15})
        docu = ret.invoke(query)
        for i, document in enumerate(docu):
            texts = [query, docu[i].page_content]
            tokens = tokenizer(
            texts, return_tensors='pt',
            padding=True, truncation=True
            )
            output = model(**tokens)
            # aggregate the token-level vecs and transform to sparse
            vecs = torch.max(
                torch.log(1 + torch.relu(output.logits)) * tokens.attention_mask.unsqueeze(-1), dim=1
            )[0].squeeze().detach().cpu().numpy()
            # vecs.shape
            sim = np.zeros((vecs.shape[0], vecs.shape[0]))

            for j, vec in enumerate(vecs):
                sim[j,:] = np.dot(vec, vecs.T) / (
                    np.linalg.norm(vec) * np.linalg.norm(vecs, axis=1)
                )
            
            document.metadata['score'] = sim[0][1]
            # print(sim[0][1], doc[i].metadata)
            diction[sim[0][1]] = i
            pq.append(sim[0][1])
            if sim[0][1]>val:
                val=sim[0][1]
                temp = i

        pq.sort(reverse=True)
        res = []
        for i, n in enumerate(pq):
            if i==6:
                break
            res.append(docu[diction[n]])
            # print('score: ', n , doc[diction[n]].metadata)
        #print(doc[temp])
        return res
        # pass

    async def _aget_relevant_documents(
        self, query: str, *, run_manager: AsyncCallbackManagerForRetrieverRun
    ) -> List[Document]:
        # Your implementation here
        pass

    def invoke(
        self, input: str, config: Optional[RunnableConfig] = None, **kwargs: Any
    ) -> list[Document]:

        from langchain_core.callbacks.manager import CallbackManager

        config = ensure_config(config)
        inheritable_metadata = {
            **(config.get("metadata") or {}),
            **self._get_ls_params(**kwargs),
        }
        callback_manager = CallbackManager.configure(
            config.get("callbacks"),
            None,
            verbose=kwargs.get("verbose", False),
            inheritable_tags=config.get("tags"),
            local_tags=self.tags,
            inheritable_metadata=inheritable_metadata,
            local_metadata=self.metadata,
        )
        run_manager = callback_manager.on_retriever_start(
            None,
            input,
            name=config.get("run_name") or self.get_name(),
            run_id=kwargs.pop("run_id", None),
        )
        try:
            _kwargs = kwargs if self._expects_other_args else {}
            if self._new_arg_supported:
                result = self._get_relevant_documents(
                    input, run_manager=run_manager, **_kwargs
                )
            else:
                result = self._get_relevant_documents(input, **_kwargs)
        except Exception as e:
            run_manager.on_retriever_error(e)
            raise
        else:
            run_manager.on_retriever_end(
                result,
            )
            return result