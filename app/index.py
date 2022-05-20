#from asyncio.windows_events import NULL
from flask import Flask, render_template, redirect, url_for, request
import os
import subprocess
import sys

app = Flask(__name__)

def RunCommand(command):
    result = os.popen(command).read();
    return result

@app.route("/")
def index():
    return render_template('index.html')

# add deploy new app
@app.route('/deploy_option', methods=['POST','GET'])
def app_deployment():
    if request.method == 'POST':
        # if form has data then
        if request.form['application'] is not None:
            # get app name
            my_app = request.form['application']
            # deploy string
            deploy_str = 'helm install {} bitnami/{}'.format(my_app, my_app)
            #print(deploy_str)
            output = os.popen(deploy_str).readlines()
            output = " ".join(output)
            return render_template('detail.html', mydata = output)
    else:
        return render_template('index.html')

# modify app   
@app.route('/deploy_modify', methods=['POST','GET'])
def app_deployment():
    if request.method == 'POST':
        # if form has data then
        # get app name
        my_app = request.args.get('app')
        # deploy string
        status_str = 'helm status {} '.format(my_app)
        list = os.popen('kubectl get rs').readlines()
        for i in list:
            print(i)
        output = os.popen(status_str).readlines()
        output = " ".join(output)
        return render_template('detail.html', mydata = output)
    else:
        return render_template('index.html')
# add delete app
@app.route('/delete_deploy', methods=['POST','GET'])
def delete_deployment():
    name_app = request.args.get('app')
    output = os.system("helm delete {}".format(name_app))
    print(output)
    return render_template('deployment.html')


#delete all deployment
@app.route('/delete_all', methods=['POST','GET'])
def delete_all_deployment():
    output = os.system("")
    print(output)
    return render_template('deployment.html')


@app.route('/deploy_apps', methods=['POST','GET'])
def vmd_app():
    if request.method == 'POST':
        if request.form['submit_button'] == 'Start cluster':
            #output = os.system('minikube start')
            return render_template('deployment.html')
        elif request.form['submit_button'] == 'Stop cluster':
            #output = os.system('minikube stop')
            return render_template('index.html')
        elif request.form['submit_button'] == 'Delete cluster':
            #output = os.system('minikube delete')
            return render_template('index.html')
    else:
        return render_template('index.html')

@app.route('/show_all_deploy', methods=['POST','GET'])
def show_all_deployment():
    if request.method == 'POST':
        if request.form['submit_button'] == 'Show all applications':
            #output = os.system('helm repo add bitnami https://charts.bitnami.com/bitnami')
            list = os.popen('helm ls').readlines()
            matrix = []
            for i in list:
                ls  = i.replace(" ", "").split('\t')
                ls[len(ls)-1] = ls[len(ls)-1][-2]
                matrix.append(ls)
            #print(matrix)
            return render_template('deploy.html', mydata = matrix[1:len(matrix)])
        elif request.form['submit_button'] == 'Delete all applications':
            #output = os.system('helm delete redis')
            return render_template('deployment.html')
    else:
        return render_template('deployment.html')



if __name__ == "__main__":
    app.run(debug=True,host='0.0.0.0',port=5000)
