from flask import Flask,request, render_template, jsonify, Response, url_for
import os
from clarifai.rest import ClarifaiApp

app = Flask(__name__, static_folder="static", template_folder="template")
app.static_folder = 'static'


# compress = FlaskStaticCompress(app)

#print(os.environ["CLARIFAI_API_KEY"])
prog = ClarifaiApp(api_key= os.environ["CLARIFAI_API_KEY"]) # Use the api key provided by clarify for your application

UPLOAD_FOLDER = os.getcwd() + '/uploads'

@app.route("/")
def form():
    return render_template('index.html')

@app.route("/resultpage" , methods = ["POST","GET"] )
def result():
    if request.method == "POST":
        print("POST TRIGGERED!")

        img_file = request.files['file']
        #print(img_file)
        img_name = img_file.filename
        #print(img_name)
        img_file.save(os.path.join(UPLOAD_FOLDER, img_name))
        #print(os.path.join(UPLOAD_FOLDER, img_name))

        model = prog.models.get('Flowers') # For using custom model - replace "General" with "Flowers"
        resp = model.predict_by_filename(UPLOAD_FOLDER + '/' + img_name)
        img_path = UPLOAD_FOLDER + '/' + img_name
        print(resp)
        response = resp['outputs'][0]['data']['concepts'][0]
        print(response)

        os.remove(img_path)

        if 1 >= (resp['outputs'][0]['data']['concepts'][0]['value']) > 0.02:
            return jsonify({"recognised":True, 
            "payload":{
                "name":resp['outputs'][0]['data']['concepts'][0]['name'], 
                "value":resp['outputs'][0]['data']['concepts'][0]['value']}})
        else:
            return jsonify({"recognised" :False, "payload":None})

if __name__ == '__main__':
    port = int(os.environ.get('PORT', 3000))
    app.run(host='0.0.0.0', port=port, debug=True)

  # NOTE: While using host = 0.0.0.0 ; specify 0.0.0.0 as localhost in the url(i.e http://localhost:3000/)
