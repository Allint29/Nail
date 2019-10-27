from flask import current_app
from elasticsearch.exceptions import ConnectionError as ElastConnect

def add_to_index(index, model):    
    if not current_app.elasticsearch:
        return
    try:
        payload = {}
        for field in model.__searchable__:
            payload[field] = getattr(model, field)
        current_app.elasticsearch.index(index=index, doc_type=index, id=model.id,
                                    body=payload)
    except ElastConnect as err:
        print ('My Error:', err)
    except Exception as err:
        print ('My Error:', err)
        return 0, 0
    except ConnectionRefusedError as err:
        print ('My Error:', err)
        return 0, 0
    except:
        pass
        

def remove_from_index(index, model):
    if not current_app.elasticsearch:
        return
    try:
        current_app.elasticsearch.delete(index=index, doc_type=index, id=model.id)
    except ElastConnect as err:
        print ('My Error:', err)
    except Exception as err:
        print ('My Error:', err)
        return 0, 0
    except ConnectionRefusedError as err:
        print ('My Error:', err)
        return 0, 0
    except:
        pass


def query_index(index, query, page, per_page):


    if not current_app.elasticsearch:
        return [], 0
    #здесь при испытании в питоне при указании doc_type - вызывал ошибку, а без него поиск работал
    try:
        search = current_app.elasticsearch.search(
            index=index, 
            body={'query': {'multi_match': {'query': query, 'fields': ['*']}},
                  'from': (page - 1) * per_page, 'size': per_page})    
        ids = [int(hit['_id']) for hit in search['hits']['hits']]
        return ids, search['hits']['total']
    except ElastConnect as err:
        print ('My Error:', err)
        return 0, 0
    except Exception as err:
        print ('My Error:', err)
        return 0, 0
    except ConnectionRefusedError as err:
        print ('My Error:', err)
        return 0, 0
    except:
        pass