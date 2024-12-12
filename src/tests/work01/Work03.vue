<template>
    <div class="flex justify-center items-center h-screen" ref="colorChart"></div>
    <div class="h-screen flex flex-wrap"
        :style="{ width: 2 * imgAttribute.width + 'px,', height: 2 * imgAttribute.height + 'px' }">
        <div :style="{ width: imgAttribute.width + 'px' }">
            <canvas id="pc" :width="imgAttribute.width" :height="imgAttribute.height" style="border:1px solid #c3c3c3;">
                Your browser does not support the canvas element.
            </canvas>
            <canvas id="pc_k_means" :width="imgAttribute.width" :height="imgAttribute.height"
                style="border:1px solid #c3c3c3;">
                Your browser does not support the canvas element.
            </canvas>
        </div>
        <div>
            <svg ref="svg"
                :style="{ width: 2 * imgAttribute.width + 'px,', height: 2 * imgAttribute.height + 'px' }"></svg>
        </div>
    </div>
</template>

<script setup lang="ts">
import { ref, onMounted } from 'vue';
import * as d3 from 'd3';
import { PyLouvain, Edge, KMeansWithCentroids, KMeansWithConvergenceAndCentroids } from '@/tools/computed'

interface Point {
    w_index: number;
    h_index: number;
    x: number;
    y: number;
    r: number;
    g: number;
    b: number;
    color: string;
    visited?: boolean; // Add visited property
}
interface ImgAttribute {
    img: Uint8ClampedArray;
    width: number;
    height: number;
}
interface Links {
    source: string | number;
    target: string | number;
    weight: number;
}
interface GraphNode extends d3.SimulationNodeDatum {
    id: string | number;
    x?: number;
    y?: number;
    color: string;
}

const light = 1
const sample = 200
const width = 600;
const height = 600;
const threshold = 20
const lamda = 0.07
const radius = 3;
const sigma = 1.5;
const points: Point[] = [];

const colorChart = ref<HTMLElement | null>(null);
const imgAttribute = ref<ImgAttribute>({
    img: new Uint8ClampedArray(0),
    width: 0,
    height: 0
});
const svg = ref<SVGSVGElement | null>(null);

const img_path = ref<string>('02/images/08.jpg')

// Function: Convert HSL to RGB color
function hslToRgb(h: number, s: number, l: number): string {
    const hslColor = d3.hsl(h, s, l);
    return hslColor.toString();
}

// Function: Render color chart
function renderColorChart() {
    if (colorChart.value) {
        const radius = Math.min(width, height) / 3; // Radius
        const margin = { top: 20, right: 20, bottom: 30, left: 40 }; // Margin

        // Create SVG
        const svg = d3.select<SVGGElement, unknown>(colorChart.value as any)
            .append('svg')
            .attr('width', width + margin.left + margin.right)
            .attr('height', height + margin.top + margin.bottom)
            .append('g')
            .attr('transform', `translate(${(width + margin.left + margin.right) / 2},${(height + margin.top + margin.bottom) / 2})`);

        // Hue and saturation ranges
        const hueRange = [0, 360]; // Hue range
        const saturationRange = [0, 1]; // Saturation range

        // Create scales for angle and radius
        const angleScale = d3.scaleLinear()
            .domain(hueRange)
            .range([0, 2 * Math.PI]);

        const radiusScale = d3.scaleLinear()
            .domain(saturationRange)
            .range([radius, 0]);

        // Render gradient background
        for (let h = hueRange[0]; h <= hueRange[1]; h += 1) {
            for (let s = saturationRange[0]; s <= saturationRange[1]; s += 0.01) {
                const angle = angleScale(h);
                const r = radiusScale(s);
                const x = r * Math.cos(angle);
                const y = r * Math.sin(angle);

                // Adjust l value based on distance from center
                const distanceFromCenter = Math.sqrt(x * x + y * y);
                let l = light - light * 0.5 * Math.cbrt(distanceFromCenter / radius); // Adjust this formula as needed

                svg.append('circle')
                    .attr('cx', x)
                    .attr('cy', y)
                    .attr('r', radius / 100)
                    .attr('fill', hslToRgb(h, 1 - s, l));
            }
        }

        renderPoints(svg);

        // Add axes
        const hueAxis = svg.append('g')
            .attr('class', 'hue-axis')
            .selectAll('line')
            .data(d3.range(0, 360, 60))
            .enter().append('line')
            .attr('x1', d => 0)
            .attr('y1', 0)
            .attr('x2', d => radius * Math.cos(angleScale(d) - Math.PI / 2))
            .attr('y2', d => radius * Math.sin(angleScale(d) - Math.PI / 2))
            .attr('stroke', 'none');

        const saturationAxis = svg.append('g')
            .attr('class', 'saturation-axis')
            .selectAll('circle')
            .data(d3.range(0.1, 1.1, 0.1))
            .enter().append('circle')
            .attr('r', d => radiusScale(d))
            .attr('fill', 'none')
            .attr('stroke', 'none');
    }
}

async function getRGBAImageData(imageUrl: string) {
    try {
        // 使用 fetch 获取图像数据
        const response = await fetch(imageUrl);
        const blob = await response.blob();

        // 使用 createImageBitmap 转换为图像位图
        const bitmap = await createImageBitmap(blob);

        // 创建一个 OffscreenCanvas
        const offscreenCanvas = new OffscreenCanvas(bitmap.width, bitmap.height);
        const ctx = offscreenCanvas.getContext('2d');
        if (!ctx) {
            throw new Error('Unable to get 2D context');
        }

        // 在 OffscreenCanvas 上绘制图像位图
        ctx.drawImage(bitmap, 0, 0);

        // 获取图像的像素数据
        const imageData = ctx.getImageData(0, 0, offscreenCanvas.width, offscreenCanvas.height);
        // 更新 imgAttribute 对象的值
        imgAttribute.value = {
            img: imageData.data,
            width: offscreenCanvas.width,
            height: offscreenCanvas.height
        };
    } catch (error) {
        throw new Error('Error loading image:' + error);
    }
}

// Function: Render points from image data
async function renderPoints(svg: d3.Selection<SVGGElement, unknown, HTMLElement, any>) {
    const data = imgAttribute.value.img;
    const width = imgAttribute.value.width;
    const height = imgAttribute.value.height;

    // 获取数据
    for (let i = 0; i < sample; i++) {
        const index = Math.floor(Math.random() * (width * height)); // Random index within image data length
        const r = data[index * 4]; // Red value
        const g = data[index * 4 + 1]; // Green value
        const b = data[index * 4 + 2]; // Blue value
        const a = data[index * 4 + 3]; // Alpha value

        // Calculate coordinates based on color values
        const h = (r + g + b) / 3; // Hue
        const max = Math.max(r, g, b);
        const min = Math.min(r, g, b);

        let s = 0;
        if (max !== 0) {
            s = (max - min) / max;
        }
        const l = 0.5; // Lightness (adjust as needed)

        // Convert HSL to RGB color
        const color = hslToRgb(h, s, l);

        // Calculate position on the color chart
        const angle = (h / 360) * 2 * Math.PI;
        const saturation = s;
        const radius = Math.min(width, height) / 2;  // Use the existing radius scale from renderColorChart()

        const x = radius * saturation * Math.cos(angle);
        const y = radius * saturation * Math.sin(angle);
        const w_index = index % imgAttribute.value.width; // w = 10 % 5 = 0
        const h_index = Math.floor(index / imgAttribute.value.width);

        // Store point data
        points.push({ w_index, h_index, x, y, r, g, b, color });
    }

    // Define thresholds for community classification based on RGB
    const rgbThreshold = 50; // Adjust as needed

    // 存储社区的列表
    const communities = [];

    // 社区算法
    for (let i = 0; i < points.length; i++) {
        const point = points[i];

        // 如果点已经被访问过，则跳过
        if (point.visited) continue;

        // 创建一个新的社区，并将当前点加入到社区中
        const newCommunity = [point];
        communities.push(newCommunity);

        // 将当前点标记为已访问
        point.visited = true;

        // 检查与当前点相似的其他点
        for (let j = i + 1; j < points.length; j++) {
            const otherPoint = points[j];

            // 如果该点未访问且与当前点足够相似，则加入当前社区
            if (!otherPoint.visited) {
                const rgbDiff = Math.sqrt(
                    Math.pow(point.r - otherPoint.r, 2) +
                    Math.pow(point.g - otherPoint.g, 2) +
                    Math.pow(point.b - otherPoint.b, 2)
                );

                if (rgbDiff < rgbThreshold) {
                    newCommunity.push(otherPoint);
                    otherPoint.visited = true;
                }
            }
        }

        // 绘制多边形将同一社区的点连接起来
        const colors = ['#ff0000', '#00ff00', '#0000ff', '#ffff00', '#00ffff'];
        if (newCommunity.length > 1) {
            // 计算社区的平均坐标和最大半径
            let centerX = 0;
            let centerY = 0;
            let maxRadius = 0;

            newCommunity.forEach(p => {
                centerX += p.x;
                centerY += p.y;
            });

            centerX /= newCommunity.length;
            centerY /= newCommunity.length;

            newCommunity.forEach(p => {
                const distance = Math.sqrt(Math.pow(p.x - centerX, 2) + Math.pow(p.y - centerY, 2));
                if (distance > maxRadius) {
                    maxRadius = distance;
                }
            });

            // 选择颜色
            const colorIndex = communities.indexOf(newCommunity) % colors.length;
            const color = colors[colorIndex];

            // 绘制圆形
            svg.append('circle')
                .attr('cx', centerX)
                .attr('cy', centerY)
                .attr('r', maxRadius)
                .attr('fill', color)
                .attr('stroke', 'white')
                .attr('stroke-width', 2)
                .attr('opacity', 0.5);
        }
    }

    // hsl着点
    for (let i = 0; i < points.length; i++) {
        const point = points[i];

        const radius = Math.min(width, height) / 2;

        svg.append('circle')
            .attr('cx', point.x)
            .attr('cy', point.y)
            .attr('r', radius / 100) // Adjust the size of the circles as needed
            .attr('fill', point.color)
            .attr('opacity', 0.5); // Adjust opacity if necessary
    }
}

// 构建点之间的边和权重
function buildEdges(points: Point[]): Edge[] {
    const edges: Edge[] = [];

    for (let i = 0; i < points.length; i++) {
        for (let j = i + 1; j < points.length; j++) {
            const distance = Math.sqrt((1 - lamda) *
                Math.pow(points[i].x - points[j].x, 2) +
                Math.pow(points[i].y - points[j].y, 2) +
                lamda *
                Math.pow(points[i].w_index - points[j].w_index, 2) +
                Math.pow(points[i].h_index - points[j].h_index, 2)
            );

            let weight: number;

            if (distance <= threshold) {
                weight = Math.ceil(threshold - distance); // 当距离大于临界值时，临界值 - distance 向上取整
                // 创建边对象并添加到数组中
                edges.push({ nodes: [i, j], weight });
            }
        }
    }

    return edges;
}


function test() {
    const edges = buildEdges(points)
    console.log(edges)
    const numNodes = points.length;

    // 创建 Louvain 算法实例
    const louvain = new PyLouvain(edges, numNodes);

    // 运行 Louvain 算法
    const communities = louvain.runLouvain();

    // 输出结果
    console.log('Final Communities:', communities);
}

async function renderSvg(edges: Edge[]) {
    if (svg.value) {
        const nodes: GraphNode[] = points.map((point, index) => ({
            id: index,
            x: point.x,
            y: point.y,
            color: `rgb(${point.r}, ${point.g}, ${point.b})`
        }));

        const links: Links[] = edges.map(edge => ({
            source: edge.nodes[0],
            target: edge.nodes[1],
            weight: edge.weight
        }));

        const svgElement = d3.select(svg.value)
            .attr('width', 2 * imgAttribute.value.width)
            .attr('height', 2 * imgAttribute.value.height);



        const forceX = d3.forceX().x(imgAttribute.value.width).strength(0.07);
        const forceY = d3.forceY().y(imgAttribute.value.height).strength(0.07);
        const simulation = d3.forceSimulation<GraphNode>(nodes)
            .force('link', d3.forceLink<GraphNode, { source: string | number; target: string | number }>(links)
                .id((d: any) => d.id)
                .strength((link: any) => Math.pow(link.weight / threshold, 2)) // 根据边的权重来调整力场强度
            )
            .force('charge', d3.forceManyBody())
            .force('center', d3.forceCenter(imgAttribute.value.width, imgAttribute.value.height))
            .force('x', forceX)
            .force('y', forceY);

        const link = svgElement.selectAll('.link')
            .data(links)
            .enter().append('line')
            .attr('class', 'link')
            .attr('stroke', '#000')
            .attr('stroke-width', (d) => Math.cbrt(d.weight) / 2);

        const node = svgElement.selectAll('.node')
            .data(nodes)
            .enter().append('circle')
            .attr('class', 'node')
            .attr('r', 5)
            .attr('fill', (d) => d.color)
            .attr('stroke', '#000')
            .attr('stroke-width', '1.5');


        simulation.on('tick', () => {
            link
                .attr('x1', (d: any) => d.source.x)
                .attr('y1', (d: any) => d.source.y)
                .attr('x2', (d: any) => d.target.x)
                .attr('y2', (d: any) => d.target.y);

            node
                .attr('cx', (d: any) => d.x)
                .attr('cy', (d: any) => d.y);
        });
    }
}

// 根据 edges 和 points 构建每个孤岛的点集
function findIslands(points: Point[], edges: Edge[]): Point[][] {
    const visited: boolean[] = new Array(points.length).fill(false);
    const islands: Point[][] = [];

    function dfs(node: number, island: number[]) {
        visited[node] = true;
        island.push(node);
        for (const edge of edges) {
            if (edge.nodes[0] === node && !visited[edge.nodes[1]]) {
                dfs(edge.nodes[1], island);
            }
            if (edge.nodes[1] === node && !visited[edge.nodes[0]]) {
                dfs(edge.nodes[0], island);
            }
        }
    }

    for (let i = 0; i < points.length; i++) {
        if (!visited[i]) {
            const island: number[] = [];
            dfs(i, island);
            islands.push(island.map(index => points[index]));
        }
    }

    return islands;
}

// 计算每个孤岛的平均值
function calculateIslandsAverage(islands: Point[][]): Point[] {
    const islandsAverage: Point[] = [];

    for (const island of islands) {
        const averagePoint: Point = {
            w_index: 0,
            h_index: 0,
            x: 0,
            y: 0,
            r: 0,
            g: 0,
            b: 0,
            color: `rgb(${255}, ${255}, ${255})`
        };

        for (const point of island) {
            averagePoint.w_index += point.w_index;
            averagePoint.h_index += point.h_index;
            averagePoint.r += point.r;
            averagePoint.g += point.g;
            averagePoint.b += point.b;
        }

        averagePoint.w_index /= island.length;
        averagePoint.h_index /= island.length;
        averagePoint.r /= island.length;
        averagePoint.g /= island.length;
        averagePoint.b /= island.length;
        averagePoint.color = `rgb(${averagePoint.r}, ${averagePoint.g}, ${averagePoint.b})`

        islandsAverage.push(averagePoint);
    }

    return islandsAverage;
}

function calculateIslandsMedian(islands: Point[][]): Point[] {
    const islandsMedian: Point[] = [];

    for (const island of islands) {
        // 按照每个属性创建临时数组以便计算中位数
        const sortedByWIndex = island.slice().sort((a, b) => a.w_index - b.w_index);
        const sortedByHIndex = island.slice().sort((a, b) => a.h_index - b.h_index);
        const sortedByR = island.slice().sort((a, b) => a.r - b.r);
        const sortedByG = island.slice().sort((a, b) => a.g - b.g);
        const sortedByB = island.slice().sort((a, b) => a.b - b.b);

        // 计算中位数
        const medianPoint: Point = {
            w_index: median(sortedByWIndex.map(point => point.w_index)),
            h_index: median(sortedByHIndex.map(point => point.h_index)),
            x: 0,
            y: 0,
            r: median(sortedByR.map(point => point.r)),
            g: median(sortedByG.map(point => point.g)),
            b: median(sortedByB.map(point => point.b)),
            color: ""
        };

        medianPoint.color = `rgb(${medianPoint.r}, ${medianPoint.g}, ${medianPoint.b})`;

        islandsMedian.push(medianPoint);
    }

    return islandsMedian;
}

function median(values: number[]): number {
    if (values.length === 0) return 0;

    const half = Math.floor(values.length / 2);
    if (values.length % 2 === 0) {
        return (values[half - 1] + values[half]) / 2;
    } else {
        return values[half];
    }
}

async function renderPc(img: Uint8ClampedArray, id: string) {
    const canvas = document.getElementById(id) as HTMLCanvasElement;
    const context = canvas.getContext('2d');

    if (context) {
        const width = canvas.width;
        const height = canvas.height;

        // 创建 ImageData 对象
        const imageData = new ImageData(img, width, height);

        // 清空 canvas
        context.clearRect(0, 0, width, height);

        // 将图像数据绘制到 canvas 上
        context.putImageData(imageData, 0, 0);
    } else {
        console.error('Unable to get 2D context for canvas');
    }
}

async function normalImageData(imageData: Uint8ClampedArray, clusters: number[][]): Promise<Uint8ClampedArray> {
    clusters.forEach((cluster: number[]) => {
        if (cluster.length === 0) {
            return;
        }
        let totalR = 0, totalG = 0, totalB = 0, totalA = 0;
        cluster.forEach((index: number) => {
            totalR += imageData[4 * index];
            totalG += imageData[4 * index + 1];
            totalB += imageData[4 * index + 2];
            totalA += imageData[4 * index + 3];
        });
        const numPixels = cluster.length;
        const avgR = Math.round(totalR / numPixels);
        const avgG = Math.round(totalG / numPixels);
        const avgB = Math.round(totalB / numPixels);
        const avgA = Math.round(totalA / numPixels);
        console.log(`Cluster average RGBA: (${avgR}, ${avgG}, ${avgB}, ${avgA})`);
        cluster.forEach((index: number) => {
            imageData[4 * index] = avgR;
            imageData[4 * index + 1] = avgG;
            imageData[4 * index + 2] = avgB;
            imageData[4 * index + 3] = avgA;
        });
    });
    return imageData;
}


function applyGaussianBlur(imgAttribute: ImgAttribute, radius: number, sigma: number): Uint8ClampedArray {
    const { img, width, height } = imgAttribute;
    const blurredImg = new Uint8ClampedArray(img.length);


    // Calculate the size of the kernel
    const kernelSize = 2 * radius + 1;
    const kernel: number[] = [];
    let kernelSum = 0;

    // Generate a 1-dimensional Gaussian kernel
    console.log('Generate a 1-dimensional Gaussian kernel')
    for (let i = -radius; i <= radius; i++) {
        const weight = Math.exp(-(i * i) / (2 * sigma * sigma)) / (Math.sqrt(2 * Math.PI) * sigma);
        kernel.push(weight);
        kernelSum += weight;
    }

    // Normalize the kernel
    console.log('Normalize the kernel')
    for (let i = 0; i < kernel.length; i++) {
        kernel[i] /= kernelSum;
    }

    // Apply horizontal blur
    console.log('Apply horizontal blur')
    for (let y = 0; y < height; y++) {
        for (let x = 0; x < width; x++) {
            let r = 0, g = 0, b = 0, a = 0;
            for (let i = -radius; i <= radius; i++) {
                const xPos = Math.min(Math.max(x + i, 0), width - 1);
                const pixelIndex = (y * width + xPos) * 4;
                const weight = kernel[i + radius];

                r += img[pixelIndex] * weight;
                g += img[pixelIndex + 1] * weight;
                b += img[pixelIndex + 2] * weight;
                a += img[pixelIndex + 3] * weight;
            }
            const index = (y * width + x) * 4;
            blurredImg[index] = r;
            blurredImg[index + 1] = g;
            blurredImg[index + 2] = b;
            blurredImg[index + 3] = a;
        }
    }

    // Apply vertical blur
    console.log('Apply vertical blur')
    const tempImg = new Uint8ClampedArray(img.length);
    for (let y = 0; y < height; y++) {
        for (let x = 0; x < width; x++) {
            let r = 0, g = 0, b = 0, a = 0;
            for (let i = -radius; i <= radius; i++) {
                const yPos = Math.min(Math.max(y + i, 0), height - 1);
                const pixelIndex = (yPos * width + x) * 4;
                const weight = kernel[i + radius];

                r += blurredImg[pixelIndex] * weight;
                g += blurredImg[pixelIndex + 1] * weight;
                b += blurredImg[pixelIndex + 2] * weight;
                a += blurredImg[pixelIndex + 3] * weight;
            }
            const index = (y * width + x) * 4;
            tempImg[index] = r;
            tempImg[index + 1] = g;
            tempImg[index + 2] = b;
            tempImg[index + 3] = a;
        }
    }

    return tempImg;
}

// Execute renderColorChart function after component mounted
onMounted(async () => {
    await getRGBAImageData(img_path.value)
    renderColorChart();
    renderPc(imgAttribute.value.img, "pc");
    const edges = buildEdges(points)
    renderSvg(edges)
    const islands = findIslands(points, edges)
    const islandsAverage = calculateIslandsMedian(islands)
    const centroids: number[][] = islandsAverage.map(point => [point.r, point.g, point.b, 255]);
    // const clusters = await KMeansWithCentroids(imgAttribute.value.img, centroids);
    const clusters = await KMeansWithConvergenceAndCentroids(imgAttribute.value.img, centroids, imgAttribute.value.width, imgAttribute.value.height, 0.98, 0.005, 2);
    const normalImageDataArray = await normalImageData(imgAttribute.value.img, clusters);
    // const normalImageAttribute = {
    //     img: normalImageDataArray,
    //     width: imgAttribute.value.width,
    //     height: imgAttribute.value.height,
    // }
    // const blurredImageData = applyGaussianBlur(normalImageAttribute, radius, sigma);
    renderPc(normalImageDataArray, "pc_k_means");
    // test()
});
</script>

<style scoped>
/* Add styles here */
</style>
