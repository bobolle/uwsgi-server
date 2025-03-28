import json
import time
import os
import sys

sys.path.append(os.path.abspath('src'))
from template import BoTemplate 

#component_all_data = [['ALL', [{"device_id": "pico_w", "data": 10}, {"device_id": "pico_w", "data": 20}]]]
component_all_data = []
component_all_index = 0

def master(env, sr):
    global component_all_index
    path = env['PATH_INFO']
    request = env['REQUEST_METHOD']
    data = env['wsgi.input'].read()

    # GET
    if request == 'GET':
        if path == '/':
            return response(sr, '200 OK', None, 'base.html')

        if path == '/monitor':
            # get some data for components
            # 'component' [{}]
            if component_all_data:
                component_all_index = len(component_all_data[0][1])
            return response(sr, '200 OK', None, 'monitor.html', component_all_data)
        
        if path == '/stream':
            headers = [('Content-Type', 'text/event-stream')]
            sr('200 OK', headers)

            # will be routed to offload
            return b''

        return response(sr, '404 Not Found', None, 'base.html')

    # PUT 
    if request == 'PUT':
        return response(sr, '404 Not Found', None, 'base.html')

    # POST
    if request == 'POST':
        if path == '/api/data':
            # right now the only things we're doing is storing in a global variable
            # should be stored in a db but right now im too lazy
            # I will have refactor/recreate this
            json_data = json.loads(data.decode())
            if component_all_data:
                component_all_data[0][1].append(json_data)
            else:
                component_all_data.append(['ALL', [json_data]])
            return response(sr, '200 OK')

        return response(sr, '404 Not Found', None, 'base.html')

    return response(sr, '404 Not Found', None, 'base.html')

def response(start_response, status_code, headers=None, template_name=None, data=None, body=b''):
    # handle status code, headers, template, data and content
    # working pretty well as it is right now

    if headers is None:
        headers = [('Content-Type', 'text/html')]

    template = None
    if template_name:
        templateHandler = BoTemplate(template_name)
        templateHandler.parse()
        if data:
            templateHandler.add_data(data)

        template = templateHandler.get()
        headers.append(('Content-Length', str(len(template))))
        start_response(status_code, headers)

        return [template]

    else:
        headers.append(('Content-Length', str(len(body))))
        start_response(status_code, headers)
        return [body]
