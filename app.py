import os
from tqdm.notebook import tqdm
import numpy as np
from flask import Flask, request, jsonify, render_template
from tensorflow.keras.applications.vgg16 import VGG16, preprocess_input
from tensorflow.keras.preprocessing.image import load_img, img_to_array
from tensorflow.keras.preprocessing.text import Tokenizer
from tensorflow.keras.preprocessing.sequence import pad_sequences
from tensorflow.keras.models import Model, load_model
from deep_translator import GoogleTranslator

app = Flask(__name__)


model_path = os.path.join('Output', 'best_model(25).h5')
model = load_model(model_path)


BASE_DIR = os.path.join('Dataset', 'flickr8k')
WORKING_DIR = os.path.join('Output')


with open(os.path.join(BASE_DIR, 'captions.txt'), 'r') as f:
    next(f)
    captions_doc = f.read()


# create mapping of image to captions
mapping = {}
# process lines
for line in tqdm(captions_doc.split('\n')):
    # split the line by comma(,)
    tokens = line.split(',')
    if len(line) < 2:
        continue
    image_id, caption = tokens[0], tokens[1:]
    # remove extension from image ID
    image_id = image_id.split('.')[0]
    # convert caption list to string
    caption = " ".join(caption)
    # create list if needed
    if image_id not in mapping:
        mapping[image_id] = []
    # store the caption
    mapping[image_id].append(caption)


def clean(mapping):
    for key, captions in mapping.items():
        for i in range(len(captions)):
            # take one caption at a time
            caption = captions[i]
            # preprocessing steps
            # convert to lowercase
            caption = caption.lower()
            # delete digits, special chars, etc.,
            caption = caption.replace('[^A-Za-z]', '')
            # delete additional spaces
            caption = caption.replace('\s+', ' ')
            # add start and end tags to the caption
            caption = 'startseq ' + " ".join([word for word in caption.split() if len(word)>1]) + ' endseq'
            captions[i] = caption


clean(mapping)


all_captions = []
for key in mapping:
    for caption in mapping[key]:
        all_captions.append(caption)



# tokenize the text
tokenizer = Tokenizer()
tokenizer.fit_on_texts(all_captions)



max_length = max(len(caption.split()) for caption in all_captions)



vgg_model = VGG16()
# restructure the model
vgg_model = Model(inputs=vgg_model.inputs, outputs=vgg_model.layers[-2].output)


def idx_to_word(integer, tokenizer1):
    for word, index in tokenizer1.word_index.items():
        if index == integer:
            return word
    return None


# generate caption for an image
def predict_caption(model1, image, tokenizer1, max_length1):
    # add start tag for generation process
    in_text = 'startseq'
    # iterate over the max length of sequence
    for i in range(max_length1):
        # encode input sequence
        sequence = tokenizer1.texts_to_sequences([in_text])[0]
        # pad the sequence
        sequence = pad_sequences([sequence], max_length1)
        # predict next word
        yhat = model1.predict([image, sequence], verbose=0)
        # get index with high probability
        yhat = np.argmax(yhat)
        # convert index to word
        word = idx_to_word(yhat, tokenizer1)
        # stop if word not found
        if word is None:
            break
        # append word as input for generating next word
        in_text += " " + word
        # stop if we reach end tag
        if word == 'endseq':
            break

    return in_text


# Define a route to handle image captioning
@app.route('/predict', methods=['POST'])
def predict():
    try:
        image_path = request.json.get('image_path')
        # load image
        image = load_img(image_path, target_size=(224, 224))
        # convert image pixels to numpy array
        image = img_to_array(image)
        # reshape data for model
        image = image.reshape((1, image.shape[0], image.shape[1], image.shape[2]))
        # preprocess image for vgg
        image = preprocess_input(image)
        # extract features
        feature = vgg_model.predict(image, verbose=0)
        # predict from the trained model
        result = predict_caption(model, feature, tokenizer, max_length)
        # Return the caption in the response
        return jsonify({'caption': result})

    except Exception as e:
        return jsonify({'error': str(e)})


@app.route('/translate', methods=['POST'])
def translate():
    try:
        s1 = request.json.get('s1')
        lang = request.json.get('lang')
        to_translate = s1
        result = GoogleTranslator(source='auto', target=lang).translate(to_translate)
        # Return the caption in the response
        return jsonify({'caption': result})

    except Exception as e:
        return jsonify({'error': str(e)})



@app.route('/index')
def home():
    return render_template('index.html')

if __name__ == '__main__':
    app.run(debug=True)
