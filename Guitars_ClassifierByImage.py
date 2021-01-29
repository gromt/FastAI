# -*- coding: utf-8 -*-
"""Guitars classifier by image.

Automatically generated by Colaboratory.

Original file is located at
    https://colab.research.google.com/drive/1gWWkzFoLse7PYLP4cmjrta0WmuWtnvAr
"""

!pip install -Uqq fastbook
import fastbook
fastbook.setup_book()

from fastbook import *
from fastai.vision.widgets import *

key = os.environ.get('AZURE_SEARCH_KEY', '*YOUR_KEY*')
key

guitars_types = 'ibanez','gibson','fender', 'yamaha', 'musicman'
path = Path('guitars')
guitars_types

if not path.exists():
    path.mkdir()
    for o in guitars_types:
        dest = (path/o)
        dest.mkdir(exist_ok=True)
        results = search_images_bing(key, f'{o} guitar')
        download_images(dest, urls=results.attrgot('contentUrl'))

from google.colab import drive
drive.mount('/content/drive')

fns = get_image_files(path)
fns

failed = verify_images(fns)
failed

failed.map(Path.unlink)

guitars = DataBlock(
    blocks=(ImageBlock, CategoryBlock), 
    get_items=get_image_files, 
    splitter=RandomSplitter(valid_pct=0.2, seed=42),
    get_y=parent_label,
    item_tfms=Resize(512))

dls = guitars.dataloaders(path)

guitars = guitars.new(item_tfms=RandomResizedCrop(512, min_scale=0.2))
dls = guitars.dataloaders(path)
dls.train.show_batch(max_n=4, nrows=1, unique=True)

doc(cnn_learner)

learn = cnn_learner(dls, resnet34, metrics=error_rate)
learn.fine_tune(10)

interp = ClassificationInterpretation.from_learner(learn)
interp.plot_confusion_matrix()

interp.plot_top_losses(5, nrows=1)

learn.export()
path = Path()
path.ls(file_exts='.pkl')
learn_inf = load_learner(path/'export.pkl')
learn_inf.dls.vocab

btn_upload = widgets.FileUpload()
btn_run = widgets.Button(description='Classify')
lbl_pred = widgets.Label()
out_pl = widgets.Output()

def on_click_classify(change):
    img = PILImage.create(btn_upload.data[-1])
    out_pl.clear_output()
    with out_pl: display(img.to_thumb(128,128))
    pred,pred_idx,probs = learn_inf.predict(img)
    lbl_pred.value = f'Prediction: {pred}; Probability: {probs[pred_idx]:.04f}'

btn_run.on_click(on_click_classify)

VBox([widgets.Label('Select your guitar!'), 
      btn_upload, btn_run, out_pl, lbl_pred])