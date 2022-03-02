from clarifai_grpc.grpc.api.status import status_code_pb2
from clarifai_grpc.grpc.api import service_pb2, resources_pb2
from flask import Flask, request, render_template, jsonify, Response, url_for
import os

from clarifai_grpc.channel.clarifai_channel import ClarifaiChannel
from clarifai_grpc.grpc.api import service_pb2_grpc

stub = service_pb2_grpc.V2Stub(ClarifaiChannel.get_grpc_channel())

apikey = os.environ["CLARIFAI_API_KEY"]
# This is how you authenticate.
metadata = (('authorization', 'Key '+apikey),) 

app = Flask(__name__, static_folder="static", template_folder="template")
app.static_folder = 'static'
# compress = FlaskStaticCompress(app)

UPLOAD_FOLDER = os.getcwd() + '/uploads'


@app.route("/")
def form():
    return render_template('index.html')


@app.route("/resultpage", methods=["POST", "GET"])
def result():
    if request.method == "POST":
        print("POST TRIGGERED!")

        img_file = request.files['file']
        # print(img_file)
        img_name = img_file.filename
        # print(img_name)
        img_file.save(os.path.join(UPLOAD_FOLDER, img_name))
        #print(os.path.join(UPLOAD_FOLDER, img_name))
        img_path = os.path.join(UPLOAD_FOLDER, img_name)

        with open(img_path, "rb") as f:
            file_bytes = f.read()

        post_model_outputs_response = stub.PostModelOutputs(
            service_pb2.PostModelOutputsRequest(
                model_id="Flowers",
                inputs=[
                    resources_pb2.Input(
                        data=resources_pb2.Data(
                            image=resources_pb2.Image(
                                base64=file_bytes
                            )
                        )
                    )
                ]
            ),
            metadata=metadata
        )

        if post_model_outputs_response.status.code != status_code_pb2.SUCCESS:
            print("There was an error with your request!")
            print("\tCode: {}".format(post_model_outputs_response.outputs[0].status.code))
            print("\tDescription: {}".format(post_model_outputs_response.outputs[0].status.description))
            print("\tDetails: {}".format(post_model_outputs_response.outputs[0].status.details))
            raise Exception("Post model outputs failed, status: " + post_model_outputs_response.status.description)

        # Since we have one input, one output will exist here.
        output = post_model_outputs_response.outputs[0]
        pred_class=[]
        pred_concepts=[]

        # print("Predicted concepts:")
        for concept in output.data.concepts:
            # print("%s %.2f" % (concept.name, concept.value))
            if 1>=concept.value>=0.05:
                pred_class.append(concept.value)
                pred_concepts.append(concept.name)
        if(len(pred_class)==0):
            prediction = "Undetermined"
            max_=None
        else:
            max_ = max(pred_class)
            prediction = pred_concepts[pred_class.index(max_)]

        try:
            os.remove(img_path)
        except:
            print("File Deletion Error")

        if max_!=None:
            return jsonify({"recognised": True,
                        "payload": {
                            "name": prediction,
                            "value": max_}})
        else:
            return jsonify({"recognised" :False, "payload":None})

if __name__ == '__main__':
    app.run(host="0.0.0.0", port=3000, debug=True)
