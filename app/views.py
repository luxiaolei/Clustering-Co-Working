from flask import redirect, request, render_template, url_for, session, g
from flask_wtf import Form
from wtforms import RadioField
from app import app
from werkzeug import secure_filename
import os
import json
import os.path as op
import pandas as pd
import cPickle as pkl

app.secret_key = 'F12Zr47j\3yX R~X@H!jmM]Lwf/,?KT'
ALLOWED_EXTENSIONS = set(['txt', 'csv'])


class selfgloablvars:
    def __init__(self):
        self.features = 1
        self.df = 1
        self.selected_feature = 1
        self.mappernew = 1

selfvars = selfgloablvars()


def allowed_file(filename):
    return '.' in filename and \
           filename.rsplit('.', 1)[1] in ALLOWED_EXTENSIONS


def recolor_mapperoutput(mapperjson):
    """
    set selfvars.mappernew to an altered mapper_ouput in json format
    the attartribut of vertices become the avg values of elements in the vertices
    """
    target = mapperjson

    for key, each_dic in enumerate(target['vertices']):
        elements_index = each_dic['members'] #list
        coresspoding_rows = selfvars.df.ix[elements_index, selfvars.selected_feature]
        average_value = np.average(coresspoding_rows)

        #reset the arrtribute
        target['vertices'][key]['attribute'] = average_value

    selfvars.mappernew =  target


@app.route('/', methods=['GET', 'POST'])
def upload_file():

    if request.method == 'POST':
        try:
        #file uploading
            file = request.files['file']
            if file and allowed_file(file.filename):
                filename = secure_filename(file.filename)
                file.save(os.path.join(app.config['UPLOAD_FOLDER'], filename))
                message = 'Successfully Uploaded!'
                session['filename'] = filename
                #retrive the column names and pass to /


                #pop index col
                FirstRowisIndex= True
                if FirstRowisIndex:
                    df = pd.read_csv('uploads/'+filename, index_col=0)
                else:
                    pass


                col = df.columns.values

                #store the col into selfvars obj
                selfvars.features = col
                selfvars.df = df

                return render_template('index.html', \
                message = message,  columns= col, submitflag= True)
            else:
                message = 'Failed upload! File type is not supported!'
                return render_template('index.html', message = message)
        except Exception:
            try:
                #feature selection
                selected_f = request.form['option']
                selfvars.selected_feature = selected_f

                data = selfvars.df[selected_f]
                minvalue = data.min()
                maxvalue = data.max()

                return render_template('index.html', columns= selfvars.features,\
                        submitflag=True, featureflag= True, selected_f= selfvars.selected_feature,\
                        minvalue= minvalue,\
                        maxvalue = maxvalue)
            except Exception:
                try:

                    inputrange = request.form['range']
                    inputrange = [float(i) for i in inputrange.split(',')]


                    df = selfvars.df
                    sf = selfvars.selected_feature
                    rangeindex = df.ix[(df[sf] >= inputrange[0]) & (df[sf] <= inputrange[-1])].index.values

                    with open('mapperoutput.pkl', 'rb') as f:
                        mapperoutput = pkl.load(f)

                    recolor_mapperoutput(mapperoutput)


                    return render_template('index.html', columns= selfvars.features,\
                            submitflag=True, featureflag= True, selected_f= selfvars.selected_feature,\
                            inputrange = inputrange, rangeindex = rangeindex)
                    #feture range selection
                    pass
                except Exception, e:
                    return render_template('index.html', error = str(e))
                    pass
    else: return render_template('index.html')


@app.route('/mapperjson')
def mapper_cluster():

    if selfvars.mappernew == 1:
        #first time initiate the graph

        with open('mapperoutput.pkl', 'rb') as f:
            G = pkl.load(f)
    else:
        G = selfvars.mappernew
    return json.dumps(G)
