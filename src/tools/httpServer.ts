/*
 * @Description: 
 * @Author: 唐健峰
 * @Date: 2024-07-02 14:03:04
 * @LastEditors: ${author}
 * @LastEditTime: 2024-07-11 13:39:02
 */
import axios from 'axios';
//@ts-ignore
import { backendEndpoint } from '@/config/config'

const PYTHON_SERVER_URL = backendEndpoint;  // Python 服务器运行在本地的 5174 端口上

export async function sendRequestToPythonBackend(imageData: Uint8ClampedArray, iterations: number): Promise<number[][]> {
    try {
        // 将 Uint8ClampedArray 转换为普通数组
        const imageArray = Array.from(imageData);

        // 创建 JSON 对象
        const jsonData = {
            image: imageArray,
            iterations: iterations
        };

        // 发送 POST 请求
        const response = await axios.post(PYTHON_SERVER_URL + '/k_means', jsonData, {
            headers: {
                'Content-Type': 'application/json'  // 设置请求头为 application/json
            }
        });

        return response.data.clusters;
    } catch (error) {
        console.error('Failed to send request to Python backend:', error);
        throw error;
    }
}

export async function sendRequestToPythonBackend02(imageData: Uint8ClampedArray, iterations: number, width: number, height: number, lambda: number, offset: number, maxDepth: number): Promise<number[][]> {
    try {
        // 将 Uint8ClampedArray 转换为普通数组
        const imageArray = Array.from(imageData);

        // 创建 JSON 对象
        const jsonData = {
            image: imageArray,
            iterations: iterations,
            width: width,
            height: height,
            lambda_: lambda,
            offset: offset,
            max_depth: maxDepth
        };

        // 发送 POST 请求
        const response = await axios.post(PYTHON_SERVER_URL + '/k_means_with_convergence', jsonData, {
            headers: {
                'Content-Type': 'application/json'  // 设置请求头为 application/json
            },
            timeout: 600000
        });

        return response.data.clusters;
    } catch (error) {
        console.error('Failed to send request to Python backend:', error);
        throw error;
    }
}

export async function getWordFre(): Promise<any> {

    try {
        // 发送 POST 请求
        const response = await axios.post(PYTHON_SERVER_URL + '/ge_word_fre', {
            headers: {
                'Content-Type': 'application/json'  // 设置请求头为 application/json
            },
            timeout: 3600000
        });
        return response.data;
    } catch (error) {
        console.error('Failed to send request to Python backend:', error);
        throw error;
    }
}

interface VolumeResponse {
    volume: number;
}
export async function sendRequestToTest(x: number, y: number, z: number): Promise<VolumeResponse> {
    try {
        const jsonData = {
            x: x,
            y: y,
            z: z
        };

        // 发送 POST 请求
        const response = await axios.post(PYTHON_SERVER_URL + '/test', jsonData, {
            headers: {
                'Content-Type': 'application/json'  // 设置请求头为 application/json
            },
            timeout: 3600000
        });
        return response.data;
    } catch (error) {
        console.error('Failed to send request to Python backend:', error);
        throw error;
    }
}