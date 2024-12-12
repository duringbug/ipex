'''
Description: 
Author: 唐健峰
Date: 2024-07-02 13:53:24
LastEditors: ${author}
LastEditTime: 2024-07-11 13:45:33
'''
from flask import Flask, request, jsonify
from flask_cors import CORS
import numpy as np

from tools.computed import k_means,k_means_with_convergence
from tools.crawlser import prc02

app = Flask(__name__)
CORS(app) 



@app.route('/k_means', methods=['POST'])
def k_means_endpoint():
    data = request.json
    image_data = data['image']
    iterations = data['iterations']
    
    # 将图像数据转换为一维数组
    image_data_flat = np.array(image_data).flatten()

    clusters = k_means(image_data_flat, iterations)

    return jsonify({'clusters': clusters})

@app.route('/k_means_with_convergence', methods=['POST'])
def k_means_with_convergence_endpoint():
    data = request.json
    image_data = data['image']
    iterations = data['iterations']
    width = data['width']
    height = data['height']
    lambda_ = data['lambda_']
    offset = data['offset']
    max_depth = data['max_depth']
    
    # 将图像数据转换为一维数组
    image_data_flat = np.array(image_data).flatten()

    clusters = k_means_with_convergence(image_data_flat, iterations, width, height, lambda_, offset, max_depth)

    return jsonify({'clusters': clusters})

@app.route('/ge_word_fre', methods=['POST', 'OPTIONS'])
def get_word_fre():
    if request.method == 'OPTIONS':
        return jsonify({'Allow': 'POST'}), 200
    elif request.method == 'POST':
        data = prc02()
        return jsonify({'data': data})

@app.route('/test', methods=['POST', 'OPTIONS'])
def test():
    if request.method == 'OPTIONS':
        return jsonify({'Allow': 'POST'}), 200
    elif request.method == 'POST':
        data = request.json
        x = data['x']
        y = data['y']
        z = data['z']
        return jsonify({'volume': x * y * z})

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5174)