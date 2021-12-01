from flask import Flask, render_template, request, redirect, url_for, current_app, send_from_directory
import os
import pandas as pd
import lemmaSynys as les
from os.path import join, dirname, realpath

app = Flask(__name__,template_folder='template')

# enable debugging mode
app.config["DEBUG"] = False

# Upload folder
UPLOAD_FOLDER = 'RDAsheet'
app.config['UPLOAD_FOLDER'] =  UPLOAD_FOLDER


# Root URL
@app.route('/')
def index():
     # Set The upload HTML template '\templates\index.html'
    return render_template('index.html')

@app.route('/syns', methods=['GET', 'POST'])
def syns():
    # if uploaded_file.filename != '':
    #     file_path = os.path.join(app.config['UPLOAD_FOLDER'], uploaded_file.filename)
    #     # set the file path and save the file
    #     uploaded_file.save(file_path)
    #     df = pd.read_csv(file_path,encoding='iso-8859-1')
    #     html=les.generate_csv_output(df)
    #     file =open("template/csvtoht1.html","w",encoding="utf8", errors='ignore')
    #     file.write(html)
    #     file.close()
    if request.method == 'POST':
        text = request.form['message']
        act_terms=les.deal_with_input(text)
        print(act_terms)
        synset=les.get_syns_set(act_terms)
        for i in act_terms:
            synset.append(i)
    return render_template("syns.html",synset=synset)

@app.route('/inflect', methods=['POST'])
def inflect():
    text = request.form['inf']
    print(text)
    infl=les.inflect_generator(text)
    return render_template("syns.html",infl=infl)

@app.route('/upload', methods=[ 'POST'])
def uploads():
    uploaded_file = request.files['file']
    if uploaded_file.filename != '':
        file_path = os.path.join(app.config['UPLOAD_FOLDER'], uploaded_file.filename)
        # set the file path and save the file
        uploaded_file.save(file_path)
        df = pd.read_csv(file_path)
        return redirect(url_for('index'))
def main():
    app.run(port=5000)

if (__name__ == "__main__"):
     main()