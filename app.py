import glob
import os
from PIL import Image
import xmltodict
import json

def get_bboxs(my_dict):
    objects = my_dict['annotation']['object']

    if isinstance(objects, dict):
        objects = [objects]

    bboxs = []
    category = []

    for o in objects:
       
        bndbox = o['bndbox']
        bbox = [   (int(bndbox['xmin']), int(bndbox['ymin'])), 
                    (int(bndbox['xmax']), int(bndbox['ymax']))
                ]
        bboxs.append(bbox)
        category.append(o['name'])

    return bboxs, category

def resize(img, my_dict, img_id, annotations, categories):
    w = img.size[0]
    h = img.size[1]

    ratio = min(800/w, 450/h)
    new_w = int(w*ratio)
    new_h = int(h*ratio)
    img = img.resize((new_w, new_h), Image.ANTIALIAS)

    bboxs, category = get_bboxs(my_dict)
    new_bboxs = []

    for i in range(len(bboxs)):
        bbox = bboxs[i]
        xmin = int(bbox[0][0] * ratio)
        ymin = int(bbox[0][1] * ratio)
        xmax = int(bbox[1][0] * ratio)
        ymax = int(bbox[1][1] * ratio)

        new_bbox = [(xmin, ymin), (xmax, ymax)]
        new_bboxs.append(new_bbox)

        ann_id = 0 if not annotations else max(x['id'] for x in annotations) +1

        annotations.append({
            "id": ann_id,
            "image_id": img_id,
            "category_id": next(x for x in categories if x["name"] == category[i])["id"],
            "bbox": [xmin, ymin, img.size[0], img.size[1]]
        }) 
        
    return img, annotations

def get_category(my_dict, categories):
    objects = my_dict['annotation']['object']

    if isinstance(objects, dict):
        objects = [objects]

    my_category = []

    for o in objects:
        category = o["name"]

        if not any(c['name'] == category for c in categories):
            if category == "cat" or category == "dog":
                supercategory = "animal"
            elif category == "bike" or category == "car":
                supercategory = "vehicle"
            elif category == "person":
                supercategory = "person"
            elif category == "ball":
                supercategory = "sports"

            cat_id = 0 if not categories else max(x['id'] for x in categories) +1

            categories.append({
                "id": cat_id,
                "name": category,
                "supercategory": supercategory
            })

            my_category.append({
                "id": cat_id,
                "name": category,
                "supercategory": supercategory
            })
    

    return categories, my_category
    


def execute_file(i, outputdir, categories, images, annotations):
    img = Image.open(imgs_list[i])

    with open(xmls_list[i], 'r', encoding='utf-8') as file:
        my_xml = file.read()
        my_dict = xmltodict.parse(my_xml)

        categories, my_category = get_category(my_dict, categories)
        img_id = 0 if not images else max(x['id'] for x in images) +1

        img, annotations = resize(img, my_dict, img_id, annotations, categories)
        
        images.append({
            "id": img_id,
            "width": img.size[0],
            "height": img.size[1],
            "file_name": my_dict["annotation"]["path"]
        })

        path =  f"{outputdir}/{img_id}.jpg"
        img.save(path)

    return categories, images, annotations
        

if __name__=='__main__':
    imagedir = "./images"
    xmldir = "./xmldata"
    outputdir = "./output"


    imgs_list = glob.glob(os.path.join(imagedir, "*.jpg"))
    xmls_list = glob.glob(os.path.join(xmldir, "*.xml"))

    categories = []
    images = []
    annotations = []

    for i in range(len(imgs_list)):
        categories, images, annotations = execute_file(i, outputdir, categories, images, annotations)

    res = {
        "categories": categories,
        "images": images,
        "annotations": annotations
    }

    path = outputdir + "/res.json"
    with open(path, "w") as  outpath:
        json.dump(res, outpath)

    
