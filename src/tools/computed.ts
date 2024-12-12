/*
 * @Description: K均值聚类算法实现，用于图像分割
 * @Author: 唐健峰
 * @Date: 2024-07-02 14:35:26
 * @LastEditors: ${author}
 * @LastEditTime: 2024-07-10 19:09:51
 */

/**
 * 计算两个 RGBA 数组之间的欧氏距离
 * @param rgba1 第一个 RGBA 数组
 * @param rgba2 第二个 RGBA 数组
 * @returns 欧氏距离
 */

function calculateDistance(rgba1: number[], rgba2: number[]): number {
    // 计算每个分量的平方差值并求和
    const squaredDist = rgba1.reduce((sum, value, index) => {
        return sum + Math.pow(value - rgba2[index], 2);
    }, 0);
    // 对平方和取平方根，得到欧氏距离
    return Math.sqrt(squaredDist);
}

function generateNormalRandom(mean: number, stdDev: number): number {
    let u = 0, v = 0;
    while (u === 0) u = Math.random(); // Converting [0,1) to (0,1)
    while (v === 0) v = Math.random();
    const normal = Math.sqrt(-2.0 * Math.log(u)) * Math.cos(2.0 * Math.PI * v);

    return mean + normal * stdDev;
}

export async function getCentroidsByNormalRandom(imageData: Uint8ClampedArray, iterations: number): Promise<number[][]> {
    const centroids: number[][] = [];
    for (let i = 0; i < iterations; i++) {
        const rgba: number[] = [];
        for (let j = 0; j < 4; j++) {
            let randomValue = generateNormalRandom(127.5, 63.75); // 使用正态分布随机数生成 RGBA 分量
            randomValue = Math.round(Math.min(Math.max(0, randomValue), 255)); // 确保值在 0 到 255 之间
            rgba.push(randomValue);
        }
        centroids.push(rgba);
    }
    return centroids
}

export async function getCentroidsByRandom(imageData: Uint8ClampedArray, iterations: number): Promise<number[][]> {
    const numPixels = imageData.length / 4; // 图像中像素的数量
    // 随机选择 'iterations' 个聚类中心
    const centroids: number[][] = [];
    for (let i = 0; i < iterations; i++) {
        const randomIndex = Math.floor(Math.random() * numPixels); // 随机选择一个像素索引
        // const randomIndex = Math.floor(generateNormalRandom(0, 1) * numPixels);
        const pixelIndex = randomIndex * 4; // 转换为 imageData 中 RGBA 数据的起始索引
        centroids.push([
            imageData[pixelIndex],
            imageData[pixelIndex + 1],
            imageData[pixelIndex + 2],
            imageData[pixelIndex + 3]
        ]);
    }
    return centroids
}

/**
 * K均值聚类算法，用于对图像数据进行分组
 * @param imageData 图像数据，Uint8ClampedArray 类型，包含每个像素的 RGBA 值
 * @param iterations 迭代次数，确定聚类中心的数量
 * @returns 返回每个聚类（cluster）中包含的像素索引的二维数组
 */
export async function KMeans(imageData: Uint8ClampedArray, iterations: number): Promise<number[][]> {
    const numPixels = imageData.length / 4; // 图像中像素的数量
    const pixelIndices = Array.from({ length: numPixels }, (_, index) => index); // 像素索引数组，从 0 到 numPixels-1
    const centroids = await getCentroidsByRandom(imageData, iterations)
    // 将每个像素分配到最近的聚类中心
    const clusters: number[][] = Array.from({ length: iterations }, () => []); // 创建一个包含 'iterations' 个空数组的数组

    pixelIndices.forEach((pixelIndex) => {
        const rgba = [
            imageData[pixelIndex * 4],         // Red
            imageData[pixelIndex * 4 + 1],     // Green
            imageData[pixelIndex * 4 + 2],     // Blue
            imageData[pixelIndex * 4 + 3]      // Alpha
        ];

        let minDistance = Number.MAX_VALUE; // 初始设定一个很大的距离值
        let clusterIndex = -1; // 初始化聚类索引为 -1

        centroids.forEach((centroid, index) => {
            const distance = calculateDistance(rgba, centroid); // 计算当前像素与每个聚类中心的距离
            if (distance < minDistance) {
                minDistance = distance; // 更新最小距离
                clusterIndex = index; // 更新最近的聚类索引
            }
        });

        clusters[clusterIndex].push(pixelIndex); // 将当前像素索引添加到对应的聚类中
    });

    return clusters; // 返回聚类结果，每个子数组包含属于同一聚类的像素索引
}

export async function KMeansWithCentroids(imageData: Uint8ClampedArray, centroids: number[][]): Promise<number[][]> {
    const numPixels = imageData.length / 4; // 图像中像素的数量
    const pixelIndices = Array.from({ length: numPixels }, (_, index) => index); // 像素索引数组，从 0 到 numPixels-1
    // 将每个像素分配到最近的聚类中心
    const clusters: number[][] = Array.from({ length: centroids.length }, () => []); // 创建一个包含 'iterations' 个空数组的数组

    pixelIndices.forEach((pixelIndex) => {
        const rgba = [
            imageData[pixelIndex * 4],         // Red
            imageData[pixelIndex * 4 + 1],     // Green
            imageData[pixelIndex * 4 + 2],     // Blue
            imageData[pixelIndex * 4 + 3]      // Alpha
        ];

        let minDistance = Number.MAX_VALUE; // 初始设定一个很大的距离值
        let clusterIndex = -1; // 初始化聚类索引为 -1

        centroids.forEach((centroid, index) => {
            const distance = calculateDistance(rgba, centroid); // 计算当前像素与每个聚类中心的距离
            if (distance < minDistance) {
                minDistance = distance; // 更新最小距离
                clusterIndex = index; // 更新最近的聚类索引
            }
        });

        clusters[clusterIndex].push(pixelIndex); // 将当前像素索引添加到对应的聚类中
    });

    return clusters; // 返回聚类结果，每个子数组包含属于同一聚类的像素索引
}

export async function KMeansWithConvergenceAndCentroids(imageData: Uint8ClampedArray, centroids: number[][], width: number, height: number, lambda: number, offset: number, maxDepth: number): Promise<number[][]> {
    const distancesToCentroids = calculateDistancesToCentroids(imageData, centroids, offset, width, height, lambda, maxDepth);

    // Rest of your clustering logic...
    const clusters: number[][] = Array.from({ length: centroids.length }, () => []);

    // Placeholder logic to demonstrate the usage
    for (let i = 0; i < distancesToCentroids.length; i++) {
        const pixelDistances = distancesToCentroids[i];
        const minDistance = Math.min(...pixelDistances);
        const clusterIndex = pixelDistances.indexOf(minDistance);

        clusters[clusterIndex].push(i); // Push pixel index to the appropriate cluster
    }

    return clusters;
}

function calculateAverageNeighborDistance(imageData: Uint8ClampedArray, pixelIndex: number, width: number, height: number): number {
    const rgba = [
        imageData[pixelIndex * 4],         // Red
        imageData[pixelIndex * 4 + 1],     // Green
        imageData[pixelIndex * 4 + 2],     // Blue
        imageData[pixelIndex * 4 + 3]      // Alpha
    ];

    const x = pixelIndex % width;
    const y = Math.floor(pixelIndex / width);

    const neighborOffsets = [
        [-1, 0], [1, 0], [0, -1], [0, 1]   // Left, Right, Up, Down
    ];

    const neighborDistances = neighborOffsets
        .map(([offsetX, offsetY]) => {
            const neighborX = x + offsetX;
            const neighborY = y + offsetY;

            if (neighborX >= 0 && neighborX < width && neighborY >= 0 && neighborY < height) {
                const neighborIndex = neighborY * width + neighborX;
                const neighborRgba = [
                    imageData[neighborIndex * 4],         // Red
                    imageData[neighborIndex * 4 + 1],     // Green
                    imageData[neighborIndex * 4 + 2],     // Blue
                    imageData[neighborIndex * 4 + 3]      // Alpha
                ];
                return calculateDistance(rgba, neighborRgba);
            } else {
                return 0;
            }
        })
        .filter(distance => distance !== 0);

    const averageDistance = neighborDistances.length > 0 ?
        neighborDistances.reduce((sum, distance) => sum + distance, 0) / neighborDistances.length :
        0;

    return averageDistance;
}

export async function KMeansWithPoints(imageData: Uint8ClampedArray, iterations: number, width: number, height: number, lambda: number): Promise<number[][]> {
    const numPixels = imageData.length / 4;
    const pixelIndices = Array.from({ length: numPixels }, (_, index) => index);

    const centroids = await getCentroidsByRandom(imageData, iterations);
    const clusters: number[][] = Array.from({ length: iterations }, () => []);

    pixelIndices.forEach((pixelIndex) => {
        const rgba = [
            imageData[pixelIndex * 4],         // Red
            imageData[pixelIndex * 4 + 1],     // Green
            imageData[pixelIndex * 4 + 2],     // Blue
            imageData[pixelIndex * 4 + 3]      // Alpha
        ];

        let minAdjustedDistance = Number.MAX_VALUE;
        let clusterIndex = -1;

        centroids.forEach((centroid, index) => {
            const distance = calculateDistance(rgba, centroid);
            const neighborDistance = calculateAverageNeighborDistance(imageData, pixelIndex, width, height);
            const adjustedDistance = (1 - lambda) * distance + lambda * neighborDistance;

            if (adjustedDistance < minAdjustedDistance) {
                minAdjustedDistance = adjustedDistance;
                clusterIndex = index;
            }
        });

        clusters[clusterIndex].push(pixelIndex);
    });

    return clusters;
}

function calculateDistancesToCentroids(imageData: Uint8ClampedArray, centroids: number[][], offset: number, width: number, height: number, lambda: number, maxDepth: number = 2): number[][] {
    const numPixels = imageData.length / 4;
    const distances: number[][] = [];

    for (let i = 0; i < numPixels; i++) {
        const rgba = [
            imageData[i * 4],         // Red
            imageData[i * 4 + 1],     // Green
            imageData[i * 4 + 2],     // Blue
            imageData[i * 4 + 3]      // Alpha
        ];

        const x = i % width;
        const y = Math.floor(i / width);

        const neighborOffsets = [
            [-Math.floor(offset * width), 0],
            [Math.floor(offset * width), 0],
            [0, -Math.floor(offset * height)],
            [0, Math.floor(offset * height)]
        ];

        const distancesToCentroids: number[] = centroids.map(centroid => {
            const distanceToCentroid = calculateDistance(rgba, centroid);

            let totalNeighborDistance = 0;
            let totalWeight = 0;

            function calculateNeighborDistance(currentX: number, currentY: number, currentDepth: number): void {
                if (currentDepth >= maxDepth) return;

                neighborOffsets.forEach(([offsetX, offsetY]) => {
                    const neighborX = currentX + offsetX;
                    const neighborY = currentY + offsetY;

                    if (neighborX >= 0 && neighborX < width && neighborY >= 0 && neighborY < height) {
                        const neighborIndex = neighborY * width + neighborX;
                        const neighborRgba = [
                            imageData[neighborIndex * 4],         // Red
                            imageData[neighborIndex * 4 + 1],     // Green
                            imageData[neighborIndex * 4 + 2],     // Blue
                            imageData[neighborIndex * 4 + 3]      // Alpha
                        ];

                        const neighborDistanceToCentroid = calculateDistance(neighborRgba, centroid);
                        const weight = Math.pow(lambda, currentDepth);
                        totalNeighborDistance += weight * neighborDistanceToCentroid;
                        totalWeight += weight;

                        calculateNeighborDistance(neighborX, neighborY, currentDepth + 1);
                    }
                });
            }

            calculateNeighborDistance(x, y, 0);

            const neighborDistanceToCentroid = totalWeight > 0 ? totalNeighborDistance / totalWeight : 0;
            return (1 - lambda) * distanceToCentroid + lambda * neighborDistanceToCentroid;
        });

        distances.push(distancesToCentroids);
    }

    return distances;
}

/**
 * KMeansWithConvergence:通过与四面偏移的点的迭代计算获得，具有模糊化，3渲2，线条化的效果
 * @param iterations 色块数,0以上的整数,越多分辨度越高
 * @param lambda 正则化向,0~1,越低色块越分散
 * @param offset 偏移量,0~1,Math.floor(offset * width)越高散光效果越强
 * @param maxDepth: 迭代次数,0以及以上的整数，越低边缘锐度越高
 * @returns number[][] [色块][index]
 */
export async function KMeansWithConvergence(imageData: Uint8ClampedArray, iterations: number, width: number, height: number, lambda: number, offset: number, maxDepth: number): Promise<number[][]> {
    const centroids = await getCentroidsByRandom(imageData, iterations);
    const distancesToCentroids = calculateDistancesToCentroids(imageData, centroids, offset, width, height, lambda, maxDepth);

    // Rest of your clustering logic...
    const clusters: number[][] = Array.from({ length: iterations }, () => []);

    // Placeholder logic to demonstrate the usage
    for (let i = 0; i < distancesToCentroids.length; i++) {
        const pixelDistances = distancesToCentroids[i];
        const minDistance = Math.min(...pixelDistances);
        const clusterIndex = pixelDistances.indexOf(minDistance);

        clusters[clusterIndex].push(i); // Push pixel index to the appropriate cluster
    }

    return clusters;
}

export interface Edge {
    nodes: [number, number];
    weight: number;
}

// 定义 Louvain 算法类
export class PyLouvain {
    private edges: Edge[];
    private numNodes: number;
    private communities: number[];

    constructor(edges: Edge[], numNodes: number) {
        this.edges = edges;
        this.numNodes = numNodes;
        this.communities = Array.from({ length: numNodes }, (_, i) => i);
    }

    // 计算初始的每个节点的社区
    private initializeCommunities(): number[] {
        return Array.from({ length: this.numNodes }, (_, i) => i);
    }

    // 计算社区内的度
    private computeDegree(node: number, community: number): number {
        return this.edges
            .filter(edge => edge.nodes.includes(node) && this.communities[edge.nodes[0]] === community)
            .reduce((acc, edge) => acc + edge.weight, 0);
    }

    // 计算社区内的总权重
    private computeCommunityWeight(community: number): number {
        return this.edges
            .filter(edge => this.communities[edge.nodes[0]] === community)
            .reduce((acc, edge) => acc + edge.weight, 0);
    }

    // 计算节点移动后的模块度增量
    private computeModularityGain(node: number, community: number): number {
        const m = this.edges.reduce((acc, edge) => acc + edge.weight, 0);
        const degreeIn = this.computeDegree(node, community);
        const degreeTot = this.computeDegree(node, community) + this.computeCommunityWeight(community);
        return (degreeIn - (degreeTot * degreeIn) / (2 * m)) / (2 * m);
    }

    // Louvain 算法的主函数，进行迭代优化
    public runLouvain(): number[] {
        let currentCommunities = this.initializeCommunities();
        let modularity = this.calculateModularity(currentCommunities);

        let improvement = true;
        while (improvement) {
            improvement = false;
            for (let node = 0; node < this.numNodes; node++) {
                const initialCommunity = currentCommunities[node];
                let bestCommunity = initialCommunity;
                let bestGain = 0;

                // 遍历所有可能的社区
                for (let community = 0; community < this.numNodes; community++) {
                    const gain = this.computeModularityGain(node, community);
                    if (gain > bestGain) {
                        bestCommunity = community;
                        bestGain = gain;
                    }
                }

                // 如果找到了更好的社区，则移动节点
                if (bestCommunity !== initialCommunity) {
                    currentCommunities[node] = bestCommunity;
                    improvement = true;
                }
            }
        }

        return currentCommunities;
    }

    // 计算模块度
    private calculateModularity(communities: number[]): number {
        const m = this.edges.reduce((acc, edge) => acc + edge.weight, 0);
        let modularity = 0;

        for (let community = 0; community < this.numNodes; community++) {
            const communityNodes = communities.reduce<number[]>((acc, comm, node) => (comm === community ? [...acc, node] : acc), []);
            const communityEdges = this.edges.filter(edge => communityNodes.includes(edge.nodes[0]) && communityNodes.includes(edge.nodes[1]));
            const sumA = communityNodes.reduce((acc, node) => acc + this.computeDegree(node, community), 0);
            const sumB = communityEdges.reduce((acc, edge) => acc + edge.weight, 0);
            modularity += sumB / (2 * m) - Math.pow(sumA / (2 * m), 2);
        }

        return modularity;
    }
}




