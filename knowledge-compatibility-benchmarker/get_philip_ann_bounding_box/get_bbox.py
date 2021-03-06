#!/usr/bin/python 
import sys
import cv2
import numpy as np
import json

def make_bw_img_for_one_class(class_id, ann):
    img = np.zeros((ann.shape[0],ann.shape[1],1), np.uint8)
    for row in range(ann.shape[0]):
        for col in range(ann.shape[1]):
            if ann[row][col]==class_id:
                img[row,col,0] = 255 # for the sake of BW image
    return img

def get_bbox(ann_filepath):
    #
    ann = np.genfromtxt(ann_filepath, delimiter=',')
    contained_classes = [int(i) for i in np.unique(ann).tolist()]
    # print contained_classes

    #
    contour_img = np.zeros((ann.shape[0],ann.shape[1],3), np.uint8)
    bbox_list = []
    rectangle = []
    for each_class in contained_classes:
        if each_class==0: #background
            continue

        # make BW image
        img = make_bw_img_for_one_class(each_class, ann)
        # cv2.imwrite(out_dir+'/noisy_bw_img_'+str(each_class)+'.png',img)

        # denoise, see http://docs.opencv.org/modules/photo/doc/denoising.html
        # TODO this denoising makes boundingRect become larger, may need to resize the (final) boundingRect
        mul = 1
        clean_img = cv2.fastNlMeansDenoising(img, None, h=1000,  templateWindowSize=7*mul, searchWindowSize=21*mul) 
        # cv2.imwrite(out_dir+'/bw_img_'+str(each_class)+'.png',img)
        
        # determine number of objects in this class, using contour
        noisy_contours, hierarchy = cv2.findContours(clean_img,cv2.RETR_EXTERNAL,cv2.CHAIN_APPROX_SIMPLE)

        # remove unreasonably small contours
        # TODO should we use cv2.contourArea(c)
        min_n_pixel = 75 # a magic number
        contours = [i for i in noisy_contours if i.shape[0]>=min_n_pixel]

        # get bbox for each contours
        local_bbox_list = []
        for c in contours:
            bbox = {}
            bbox['rectangle'] = cv2.boundingRect(c)
            bbox['contour'] = c
            local_bbox_list.append(bbox)
            
            #ian's code
            
            x,y,w,h = bbox['rectangle']
            coordinate = [x,y,x+w,y+h]
            xcenter = (coordinate[0] + coordinate[2]) / 2
            ycenter = (coordinate[1] + coordinate[3]) / 2
            center_rect_class = each_class
            rectangle.append([x,y,x+w,y+h,center_rect_class])
            
        bbox_list = bbox_list + local_bbox_list
    return bbox_list, rectangle
    #return bbox_list

#def write_bbox(bbox_list, png_ann_filepath, bbox_img_filepath):
def write_bbox(bbox_list, png_ann_filepath, bbox_img_filepath, rect_list, filename):
    
    out_filename = filename + ".json"
    keyval_for_json = {'pa_bbox' : rect_list}
    with open(out_filename, 'w') as f:
        json.dump(keyval_for_json, f)
    
    bbox_img = cv2.imread(png_ann_filepath)

    #
    red = (0,0,255)
    green = (0,255,0)
    for bbox in bbox_list:
        x,y,w,h = bbox['rectangle']
        cv2.rectangle(bbox_img, (x,y),(x+w,y+h), red, 3)

        cv2.drawContours(bbox_img, bbox['contour'], -1, green, 1)

    #
    cv2.imwrite(bbox_img_filepath,bbox_img)
    
def main(argv):
    #list_filepath = '/home/tor/sun4/xprmnt/bbox/meta/test.list'
    list_filepath = '/home/ian-djakman/Documents/data/output/knowledge-compatibility-benchmarker/meta/split-voc2010-ian/ann_img.list'
    #csv_ann_dir = '/home/tor/sun4/xprmnt/philipp-unary-voc2010/result/merged_test_csv'
    csv_ann_dir = '/home/ian-djakman/Documents/data/output/knowledge-compatibility-benchmarker/annotation/annotation-philippunary'
    #png_ann_dir = '/home/tor/sun4/xprmnt/philipp-unary-voc2010/result/merged_Test_cls'
    png_ann_dir = '/home/ian-djakman/Documents/data/output/knowledge-compatibility-benchmarker/annotation/annotation-philippunary'
    #out_dir = '/home/tor/sun4/xprmnt/bbox/bbox-overlayed'
    out_dir = '/home/ian-djakman/Documents/data/output/knowledge-compatibility-benchmarker/knowledge/philip_voc2010_boundingbox/boundingbox_data_tor'

    # read list
    with open(list_filepath) as f:
        ann_filename_list = f.readlines()
    ann_filename_list = [i.strip('\n') for i in ann_filename_list]

    #
    for i,ann_filename in enumerate(ann_filename_list):
        print('Processing %s (%i/%i)' % (ann_filename,i+1,len(ann_filename_list)))

        ann_filepath = csv_ann_dir + '/' + ann_filename + '.csv'
        bbox_list, rect_list = get_bbox(ann_filepath)

        png_ann_filepath = png_ann_dir + '/' + ann_filename + '.bmp'
        bbox_img_filepath = out_dir+'/bbox_img/' + ann_filename + '.bbox.png'
        filename = out_dir+'/' + ann_filename
        #write_bbox(bbox_list,png_ann_filepath,bbox_img_filepath)
        write_bbox(bbox_list,png_ann_filepath,bbox_img_filepath, rect_list, filename)

if __name__ == '__main__':
    main(sys.argv)
