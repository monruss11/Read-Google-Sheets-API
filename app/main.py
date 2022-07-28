from fastapi import FastAPI, Form, File, Depends
from fastapi.responses import HTMLResponse
from fastapi.templating import Jinja2Templates
from fastapi.staticfiles import StaticFiles
from  fastapi import Request
import uvicorn
import os
import gspread
from typing import Optional,Dict
import read_write_module as rw
from deta import Deta



app=FastAPI()
path=os.path.dirname(__file__)
templates = Jinja2Templates(directory=f'{path}/templates')
app.mount('/static', StaticFiles(directory='static'), name='static')

# 2) initialize with a project key
deta = Deta("b0mnv9cp_uRcyX9yEJn3soXQJYyadu3b3rQoprw2e")
# 3) create and use as many DBs as you want!
users = deta.Base("users")

@app.get('/', response_class=HTMLResponse)
async def home(request: Request ):
  global index; global check_count; global str_url; global url_googlesheet
  data_page = { 'title': 'Start page' }
  return templates.TemplateResponse('start_url.html', {'request': request, 'data_page': data_page})

@app.post('/',response_class=HTMLResponse)
async def res(request: Request, url_googlesheet:Optional[str]=Form(None),\
              language:Optional[str]=Form(None)):
  global check_count; global str_url; global row_count; global col_count
  global doc_lang
  
  data_page={ 'title':'Conditions Page', 'row_count':0, 'col_count':0 , 'doc_lang':None}
  if url_googlesheet!=None:
    str_url=url_googlesheet;
  else:
    data_page['title']='URL is empty! Input please URL'
    return templates.TemplateResponse('start_url.html',\
                        {'request': request, 'data_page': data_page})
  if language!=None:
    doc_lang=language
  else:
    data_page['title']='Choose language of document'
    return templates.TemplateResponse('start_url.html',\
                        {'request': request, 'data_page': data_page})
  if rw.make_googlesheets_client(str_url,doc_lang)!=False:
    row_count,col_count=rw.get_size_googlesheets()
    # data_page={ 'title':'Conditions Page', 'row_count':row_count, 'col_count':col_count }
    data_page['title']='Conditions Page';
    data_page['row_count']=row_count; data_page['col_count']=col_count
    return templates.TemplateResponse('start_conditions_run.html', \
                                    {'request': request,  'data_page': data_page })
  else:
    # data_page={ 'title':'URL Invalid. Please check URL', 'alert_':1 }
    data_page['title']='URL Invalid. Please check URL'
    return templates.TemplateResponse('start_url.html',\
                        {'request': request, 'data_page': data_page})

@app.post('/api/v1/result',response_class=HTMLResponse)
async def res(request: Request, row_num:Optional[int] = Form(None), \
              col_num:Optional[int]=Form(None)):
  global index; global check_count; global str_url; global col_count;  global row_count
  result=rw.read_from_googlesheets(row_num,col_num)[0]

  # print(result)
  data_page={ 'title':'Result Page','row_num':row_num, 'doc_lang':doc_lang, \
              'col_num':col_num, 'check_count':rw.read_from_googlesheets(row_num,col_num)[1]}
  print(doc_lang)
  print(type(doc_lang))
  # return index
  # return { 'cell vallue row='f'{row_num} ' 'column='f'{col_num}':result }
  return templates.TemplateResponse('result.html', \
                                    {'request': request, 'result': result, 'data_page': data_page })

if __name__=='__main__':
  ggl_wrksheet=''; index=[]; col_count=0; row_count=0
  check_count=0; str_url=''; url_googlesheet=''; doc_lang=''
  r_w=rw
  uvicorn.run('main:app', reload=True, port=8080)
