<template>
    <div class="flex flex-col items-center space-y-4 h-screen w-full py-20">
        <!-- d3图像 -->
        <div class="w-[800px] h-[500px]" ref="chartContainer"></div>
        <!-- 求平均的时间步长 -->
        <div>
            <NSpace vertical>
                <NSlider v-model:value="dayInterval" :step="1" :min="1" :max="100" />
                <NInputNumber v-model:value="dayInterval" size="small" />
            </NSpace>
        </div>
        <!-- 翻页 -->
        <div class="flex flex-row">
            <NButton class="mx-2" type="success" @click="handlePre">
                <FontAwesomeIcon :icon="['fas', 'arrow-left']" />
            </NButton>
            <NButton class="mx-2" type="success" @click="handleNext">
                <FontAwesomeIcon :icon="['fas', 'arrow-right']" />
            </NButton>
        </div>
    </div>
</template>

<script setup lang="ts">
import { ref, onMounted, computed, watch } from 'vue';
import { FontAwesomeIcon } from '@fortawesome/vue-fontawesome'
import { NButton, NSlider, NInputNumber, NSpace } from "naive-ui"
import * as d3 from 'd3';

interface CommentData {
    comments: string;
    point: number;
    date: Date;
}
interface ChartData {
    date: Date;
    value: number;
    activity: number;
}

const commentDataArray = ref<CommentData[]>([]);
const chartContainer = ref<HTMLElement | null>(null);
let fileNameIndex = ref<number>(2)
const fileName = ['鬼灭之刃 第三季(锻刀村篇)', '海贼王', '我推的孩子', '幸运星', 'Charlotte', '从Lv2开始开挂的原勇者候补悠闲的异世界生活']
const jsonPath = computed(() => `work/${fileName[fileNameIndex.value]}.json`);
const dayInterval = ref<number>(7)

async function handlePre() {
    fileNameIndex.value = (fileNameIndex.value - 1 + fileName.length) % fileName.length
    await getCommentDataArray()
    const newData = await calculateAveragePoints()
    renderChart(newData)
}

async function handleNext() {
    fileNameIndex.value = (fileNameIndex.value + 1) % fileName.length
    await getCommentDataArray()
    const newData = await calculateAveragePoints()
    renderChart(newData)
}

watch(dayInterval, async () => {
    await getCommentDataArray()
    const newData = await calculateAveragePoints()
    renderChart(newData)
});

function renderChart(data: ChartData[]) {
    // 示例数据
    // 创建 SVG 容器
    const margin = { top: 50, right: 50, bottom: 100, left: 50 };
    const width = 800 - margin.left - margin.right;
    const height = 500 - margin.top - margin.bottom;

    // 选择并清除之前的 SVG 容器中的所有元素
    const container = d3.select(chartContainer.value as any);
    if (container) {
        container.selectAll('*').remove();
    }

    const svg = d3.select(chartContainer.value)
        .append('svg')
        .attr('width', width + margin.left + margin.right)
        .attr('height', height + margin.top + margin.bottom)
        .style('border', '1px solid #ccc')  // 设置边框
        .style('background-color', '#f0f0f0')  // 设置背景色
        .append('g')
        .attr('transform', `translate(${margin.left},${margin.top})`);

    // 添加标题
    svg.append("text")
        .attr("x", (width / 2))
        .attr("y", -margin.top / 3)
        .attr("text-anchor", "middle")
        .style("font-size", "16px")
        .style("text-decoration", "underline")
        .text('<' + fileName[fileNameIndex.value] + '>' + '活跃度和评分变化图表');

    // X 轴比例尺
    const x = d3
        .scaleTime()
        .domain(d3.extent(data, d => d.date) as [Date, Date])
        .range([0, width])
        .nice();

    // Y 轴比例尺
    const y = d3
        .scaleLinear()
        .domain([0, 1])
        .nice()
        .range([height, 0]);

    // 计算矩形宽度
    const xDomain = x.domain();
    const totalDays = (xDomain[1].getTime() - xDomain[0].getTime()) / (1000 * 60 * 60 * 24);
    const rectWidth = (dayInterval.value / totalDays) * width;

    //活跃度
    const maxActivity = d3.max(data, d => d.activity)!;

    svg.selectAll('.rect')
        .data(data)
        .enter()
        .append('rect')
        .attr('class', 'rect')
        .attr('x', d => x(d.date)! - rectWidth / 2)
        .attr('y', 0)
        .attr('width', rectWidth)
        .attr('height', height)
        .attr('fill', d => {
            const opacity = d.activity / (maxActivity);
            return `rgba(50, 205, 50, ${opacity})`; // 绿色矩形，根据活跃度深浅
        })
        .on('mouseover', function (event, d) {
            const datum = d as ChartData
            d3.select(this)
                .attr('fill', d => {
                    const opacity = datum.activity / (maxActivity);
                    return `rgba(255, 165, 0, ${opacity})`; // 恢复绿色矩形
                });
            // 显示活动度 Tooltip
            const [xPos, yPos] = d3.pointer(event);
            svg.append('text')
                .attr('id', 'activity-tooltip')
                .attr('x', xPos)
                .attr('y', yPos - 10)
                .attr('text-anchor', 'middle')
                .text(`活跃度: ${d.activity}人 时间: ${d3.timeFormat('%m-%d')(d.date)}`)
                .style('fill', 'black')
                .style("font-size", "10px");
        })
        .on('mouseout', function (event, d) {
            const datum = d as ChartData
            d3.select(this)
                .attr('fill', d => {
                    const opacity = datum.activity / (maxActivity);
                    return `rgba(50, 205, 50, ${opacity})`; // 恢复绿色矩形
                });
            // 隐藏活动度 Tooltip
            svg.select('#activity-tooltip').remove();
        });

    // 折线生成器
    const line = d3.line<{ date: Date, value: number }>()
        .x(d => x(d.date)!)
        .y(d => y(d.value)!)
        .curve(d3.curveCatmullRom);
    // .curve(d3.curveBasis);


    // 添加折线路径
    svg.append('path')
        .datum(data)
        .attr('fill', 'none')
        .attr('stroke', 'steelblue')
        .attr('stroke-width', 1.5)
        .attr('d', line);

    // 添加数据点
    svg.selectAll('circle')
        .data(data)
        .enter()
        .append('circle')
        .attr('cx', d => x(d.date)!)
        .attr('cy', d => y(d.value)!)
        .attr('r', 4)
        .attr('fill', 'steelblue')
        .on('mouseover', function (event, d) {
            // 鼠标悬停时显示 Tooltip
            d3.select(this)
                .attr('r', 6) // 放大圆圈
                .style('fill', 'orange'); // 更改颜色
            // 显示 Tooltip
            svg.append('text')
                .attr('id', 'tooltip')
                .attr('x', x(d.date)!)
                .attr('y', y(d.value)!)
                .attr('dy', -10) // 调整位置
                .attr('text-anchor', 'middle')
                .text(d3.format('.2f')(d.value))
                .style('fill', 'orange')
                .style("font-size", "10px");
        })
        .on('mouseout', function (event, d) {
            // 鼠标移出时隐藏 Tooltip
            d3.select(this)
                .attr('r', 4) // 恢复原始大小
                .style('fill', 'steelblue'); // 恢复原始颜色
            svg.select('#tooltip').remove();
        });


    const xAxisFormat = d3.timeFormat('%Y-%m-%d');

    // 添加 X 轴
    svg.append('g')
        .attr('transform', `translate(0,${height})`)
        .call(d3.axisBottom(x)
            .tickFormat((value) => xAxisFormat(value as Date)))
        .selectAll("text")
        .style("font-size", "8px")
        .style("text-anchor", "start")
        .attr("transform", "rotate(15 -10 10)");

    // // 添加 X 轴辅助线
    // svg.append('g')
    //     .attr('class', 'grid')  // 添加 'grid' 类来区分主轴和辅助轴
    //     .call(d3.axisBottom(x)
    //         .tickSize(height)  // 设置辅助线的长度为图表的高度
    //         .tickFormat(() => '')
    //     )
    //     .selectAll('.tick line')
    //     .attr('stroke', '#ddd')  // 设置辅助线的颜色
    //     .attr('stroke-opacity', 0.7)  // 设置辅助线的透明度
    //     .attr('shape-rendering', 'crispEdges');  // 设置边缘渲染，以确保辅助线清晰显示


    // 添加 Y 轴
    svg.append('g')
        .call(d3.axisLeft(y));


    // 添加图例
    svg.append("text")
        .attr("x", width - 30)
        .attr("y", height + margin.top + 9)
        .style("text-anchor", "end")
        .style("font-size", "12px")
        .text("评分");

    // 添加图例标识线
    svg.append("line")
        .attr("x1", width - 20)
        .attr("y1", height + margin.top + 5)
        .attr("x2", width + 10)
        .attr("y2", height + margin.top + 5)
        .style("stroke", "steelblue")
        .style("stroke-width", 2);

    // 添加图例标识圆点
    svg.append("circle")
        .attr("cx", width - 5)
        .attr("cy", height + margin.top + 5)
        .attr("r", 4)
        .style("fill", "steelblue");

    // 活跃度图例
    svg.append("text")
        .attr("x", width - 30)
        .attr("y", height + margin.top + 29)
        .style("text-anchor", "end")
        .style("font-size", "12px")
        .text("活跃度");

    // 添加图例标识矩形
    svg.append("rect")
        .attr("x", width - 15)
        .attr("y", height + margin.top + 20)
        .attr("width", 20)
        .attr("height", 10)
        .style("fill", `rgba(50, 205, 50, 1)`); // 固定颜色的绿色矩形
}
async function calculateAveragePoints(): Promise<ChartData[]> {
    const sevenDaysMillis = dayInterval.value * 24 * 60 * 60 * 1000; // 七天的毫秒数
    let newData = [] as ChartData[]
    let startDate = commentDataArray.value[commentDataArray.value.length - 1].date;
    startDate.setHours(0, 0, 0, 0);
    for (let i = commentDataArray.value.length - 1; i >= 1;) {
        let nextDate = new Date(startDate.getTime());
        nextDate.setDate(nextDate.getDate() + dayInterval.value);
        let avgPoints = 0
        let activity = 0
        while (i > 0 && commentDataArray.value[i - 1].date.getTime() - startDate.getTime() < sevenDaysMillis) {
            avgPoints += commentDataArray.value[i - 1].point
            activity++
            i--
        }
        if (activity > 0) {
            avgPoints /= activity
            newData.push({ date: startDate, value: avgPoints, activity: activity } as ChartData)
        }
        i--
        if (i >= 0) {
            startDate = commentDataArray.value[i].date
            startDate.setHours(0, 0, 0, 0)
        }
    }
    return newData
}

async function getCommentDataArray() {
    commentDataArray.value = []
    try {
        const response = await fetch(jsonPath.value);
        if (!response.ok) {
            throw new Error(`HTTP error! status: ${response.status}`);
        }
        const jsonData = await response.json();
        // 处理日期字符串，并创建 CommentData 对象数组
        commentDataArray.value = jsonData.comments.map((comment: string, index: number) => ({
            comments: comment,
            point: jsonData.point[index],
            date: parseDate(jsonData.date[index])
        }));

    } catch (error) {
        console.error('Error fetching or processing the JSON file:', error);
    }
}

onMounted(async () => {
    await getCommentDataArray()
    const newData = await calculateAveragePoints()
    renderChart(newData)
});

// 辅助函数：解析日期字符串为 Date 对象
function parseDate(dateStr: string): Date | null {
    // 去除括号和空格
    const cleanedDateString = dateStr.replace(/[（）]/g, '').trim();
    // 分割日期和时间部分
    const [datePart, timePart] = cleanedDateString.split(' ');
    // 分割日期部分的年、月、日
    const [year, month, day] = datePart.split('-').map(Number);
    // 分割时间部分的时、分、秒
    const [hours, minutes, seconds] = timePart.split(':').map(Number);
    // 创建 Date 对象
    const dateObject = new Date(year, month - 1, day, hours, minutes, seconds);
    // 检查 Date 对象是否有效
    if (isNaN(dateObject.getTime())) {
        return null; // 如果日期无效，返回 null
    }
    return dateObject;
}
</script>

<style scoped></style>
