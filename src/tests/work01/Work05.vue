<template>
    <div class="flex justify-evenly items-center">
        <!-- 力岛图 -->
        <svg class="bg-gray-200" ref="chart" width="960" :height="2 * height"></svg>
        <div class="overflow-auto w-[200px]" :style="{ height: height * 2 + 'px' }">
            <!-- 搜索框 -->
            <div class="m-auto my-2">
                <NDropdown trigger="hover" :options="searchOption" @select="handleSelect">
                    <NInput v-model:value="searchWords" placeholder="搜索框" />
                </NDropdown>
            </div>
            <!-- 搜索的结果列表 -->
            <div v-if="centerType == 'actor'">
                <ul class="divide-y divide-gray-200">
                    <li v-for="node in nodes.slice(1)" :key="node.id" class="p-2">
                        <div class="p-2 hover:bg-slate-200 rounded-xl" @mouseover="handleHoverToNode(undefined, node)"
                            @mouseout="handleIgnoreToNode(undefined, node)" @click="handleClickToNode(undefined, node)">
                            <font-awesome-icon :icon="['fas', 'film']" class="pr-2" />{{ node.id }}
                        </div>
                    </li>
                </ul>
            </div>
            <div v-else>
                <ul class="divide-y divide-gray-200">
                    <li v-for="node in nodes.slice(1)" :key="node.id" class="p-2">
                        <div class="p-2 hover:bg-slate-200 rounded-xl" @mouseover="handleHoverToNode(undefined, node)"
                            @mouseout="handleIgnoreToNode(undefined, node)" @click="handleClickToNode(undefined, node)">
                            <font-awesome-icon :icon="['fas', 'person']" class="pr-2" />{{ node.id }}
                        </div>
                    </li>
                </ul>
            </div>
        </div>
    </div>

</template>
<script setup lang="ts">
import { ref, onMounted, watch } from 'vue';
import { FontAwesomeIcon } from '@fortawesome/vue-fontawesome'
import { NInput, NDropdown } from 'naive-ui'
import * as d3 from 'd3';

interface AcActorData {
    name: string,
    list: Info[]
}

interface Info {
    ac: string,
    actor: string[]
}

interface Link {
    source: string,
    target: string,
    weight: number,
    character: string[]
}

/**
 * @type ["anime","actor"]
 */
interface GraphNode extends d3.SimulationNodeDatum {
    id: string;
    type: string;
    x?: number;
    y?: number;
}
interface SearchOption {
    label: string,
    key: string,
    disabled?: boolean | undefined,
    children?: SearchOption[] | undefined,
}

const acActorDataArray = ref<AcActorData[]>([]);
const chart = ref<SVGSVGElement | null>(null);
const svg = ref<d3.Selection<SVGGElement, unknown, HTMLElement, any>>(chart.value as any);
const centerType = ref<string>("actor");
const searchOption = ref<SearchOption[]>([])
const searchWords = ref<string>("")
const nodes = ref<GraphNode[]>([])
const links = ref<Link[]>([])

const width = ref<number>(600);
const height = ref<number>(400);

let timeoutId: NodeJS.Timeout | null = null;

// 监听 searchWords 变化，实现防抖操作
watch(searchWords, (newValue, oldValue) => {
    if (timeoutId) {
        clearTimeout(timeoutId);
        timeoutId = null;
    }
    // 设置新的 timeout
    timeoutId = setTimeout(() => {
        if (newValue != "") {
            searchFromWords()
        }
    }, 2000); // 2 秒后执行搜索操作
});

function handleSelect(key: string) {
    const [name, type] = key.split('@');
    if (type == "actor") {
        searchAcActorDataByActorName(name).then((graphResult) => {
            centerType.value = type
            renderChart();
        }).catch((error) => {
            console.error('Error fetching data:', error);
        });
    } else {
        searchAcActorDataByAnimeName(name).then((graphResult) => {
            centerType.value = type
            renderChart();
        }).catch((error) => {
            console.error('Error fetching data:', error);
        });
    }
}

function searchFromWords() {
    searchOption.value = []
    // 遍历 acActorDataArray
    acActorDataArray.value.forEach((item) => {
        // 检查 name 是否包含搜索词
        if (item.name.includes(searchWords.value)) {
            // 添加一个 GraphNode，type 设置为 "anime"
            searchOption.value.push({ label: item.name, key: item.name + "@" + "anime" })
        }

        // 检查 list 中的每个 Info 对象
        item.list.forEach((info) => {
            // 检查 ac 是否包含搜索词
            if (info.ac.includes(searchWords.value)) {
                // 对于每个 actor 添加一个 GraphNode
                info.actor.forEach((actor) => {
                    searchOption.value.push({ label: info.ac + "(" + actor + ")", key: actor + "@" + "actor" })
                });
            }

            // 检查 actor 是否包含搜索词
            info.actor.forEach((actor) => {
                if (actor.includes(searchWords.value)) {
                    // 添加一个 GraphNode，type 设置为 "actor"
                    searchOption.value.push({ label: actor + "(" + info.ac + ")", key: actor + "@" + "actor" })
                }
            });
        });
    });
}

function handleHoverToNode(event: any | undefined, d: GraphNode) {
    let [xPos, yPos] = [0, 0]
    if (event) {
        [xPos, yPos] = d3.pointer(event);
    } else {
        xPos = d.x!;
        yPos = d.y!;
    }
    svg.value.selectAll('.node')
        .filter((nodeData: any) => nodeData === d && d.type != centerType.value)
        .attr('r', 10)
        .style('fill', 'darkblue');
    svg.value
        .append('text')
        .attr('id', 'node-id')
        .attr('x', xPos)
        .attr('y', yPos - 10)
        .attr('text-anchor', 'middle')
        .text(d.id)
        .style('fill', 'black')
        .style('font-size', '12px');
    if (d.type !== centerType.value) {
        svg.value.selectAll('.link')
            .filter((link: any) => link.source === d || link.target === d)
            .attr('stroke-width', (link: any) => {
                // 显示连接的字符信息
                svg.value.append('text')
                    .attr('id', 'link-text')
                    .attr('x', xPos)
                    .attr('y', yPos - 25) // 调整位置以避免重叠
                    .attr('text-anchor', 'middle')
                    .text("角色: " + link.character.join(', '))
                    .style('fill', 'black')
                    .style('font-size', '12px');

                return Math.cbrt(link.weight) + 2;
            });
    }
}

function handleIgnoreToNode(event: any | undefined, d: GraphNode) {
    svg.value.selectAll('.node')
        .filter((nodeData: any) => nodeData === d && d.type != centerType.value)
        .attr('r', 8)
        .style('fill', 'skyblue');
    svg.value.select('#node-id').remove();
    svg.value.select('#link-text').remove();
    svg.value.selectAll('.link')
        .attr('stroke-width', (link: any) => Math.cbrt(link.weight));
}

function handleClickToNode(event: any | undefined, d: GraphNode) {
    if (d.type !== centerType.value) {
        svg.value.select('#node-id').remove();
        svg.value.select('#link-text').remove();
        svg.value.selectAll('.link')
            .attr('stroke-width', (link: any) => Math.cbrt(link.weight));
        handleClickToChangeSvg(d.type, d.id)
    }
}

function renderChart() {
    if (chart.value) {
        const margin = { top: 0, right: 0, bottom: 0, left: 0 }; // Margin\

        svg.value = d3.select<SVGGElement, unknown>(chart.value as any)
            .attr('width', 2 * width.value)
            .attr('height', 2 * height.value);

        // 清除之前的节点和链接
        svg.value.selectAll('.link').remove();
        svg.value.selectAll('.node').remove();
        svg.value.select('.chart-title').remove();
        svg.value.select('.legend').remove();

        // 添加标题
        svg.value.append('text')
            .attr('class', 'chart-title')
            .attr('x', (2 * width.value + margin.left + margin.right) / 2)
            .attr('y', margin.top + 32)
            .attr('text-anchor', 'middle')
            .style('font-size', '16px')
            .style('font-weight', 'bold')
            .text(centerType.value + ": " + nodes.value[0].id);


        // 添加图例
        const legend = svg.value.append('g')
            .attr('class', 'legend')
            .attr('transform', `translate(${2 * width.value - 150}, ${margin.top + 10})`);

        const legendData = [
            { type: centerType.value, color: '#ffa500', text: centerType.value == "actor" ? "声优" : "动漫" },
            { type: 'other', color: 'skyblue', text: centerType.value == "actor" ? "动漫" : "声优" }
        ];

        const legendItem = legend.selectAll('.legend-item')
            .data(legendData)
            .enter().append('g')
            .attr('class', 'legend-item')
            .attr('transform', (d, i) => `translate(0, ${i * 20})`);

        legendItem.append('rect')
            .attr('width', 18)
            .attr('height', 18)
            .attr('fill', d => d.color);

        legendItem.append('text')
            .attr('x', 24)
            .attr('y', 9)
            .attr('dy', '0.35em')
            .text(d => d.text);


        const forceX = d3.forceX().x(width.value).strength(0.000001);
        const forceY = d3.forceY().y(height.value).strength(0.000001);
        const simulation = d3.forceSimulation<GraphNode>(nodes.value)
            .force('link', d3.forceLink<GraphNode, { source: string; target: string }>(links.value)
                .id((d: any) => d.id)
                .strength((link: any) => (Math.cbrt(link.weight) / 20)) // 根据边的权重来调整力场强度
            )
            .force('charge', d3.forceManyBody())
            .force('center', d3.forceCenter(width.value, height.value))
            .force('x', forceX)
            .force('y', forceY);

        const link = svg.value.selectAll('.link')
            .data(links.value)
            .enter().append('line')
            .attr('class', 'link')
            .attr('stroke', 'green')
            .attr('stroke-width', (d) => Math.cbrt(d.weight))
            .on('mouseover', function (event, d) {
                const [xPos, yPos] = d3.pointer(event);
                svg.value.append('text')
                    .attr('id', 'node-id')
                    .attr('x', xPos)
                    .attr('y', yPos - 10)
                    .attr('text-anchor', 'middle')
                    .text(d.character.join(', '))
                    .style('fill', 'black')
                    .style('font-size', '12px');
                d3.select(this)
                    .attr('stroke-width', (d: any) => Math.cbrt(d.weight) + 2); // 增加 2 个单位的宽度
            })
            .on('mouseout', function (event, d) {
                svg.value.select('#node-id').remove();
                d3.select(this)
                    .attr('stroke-width', (d: any) => { return Math.cbrt(d.weight) });
            });

        const node = svg.value.selectAll('.node')
            .data(nodes.value)
            .enter().append('circle')
            .attr('class', 'node')
            .attr('r', d => {
                // console.log("d.type: " + d.type)
                // console.log("centerType.type: " + centerType.value)
                return d.type === centerType.value ? 12 : 8;
            })
            .attr('fill', d => {
                return d.type === centerType.value ? '#ffa500' : 'skyblue';
            })
            .attr('stroke', '#000')
            .attr('stroke-width', '0.0')
            .on('mouseover', function (event, d) {
                handleHoverToNode(event, d)
            })
            .on('mouseout', function (event, d) {
                handleIgnoreToNode(event, d)
            })
            .on('click', function (event, d) {
                handleClickToNode(event, d)
            });


        simulation.on('tick', () => {
            link
                .attr('x1', (d: any) => d.source.x)
                .attr('y1', (d: any) => d.source.y)
                .attr('x2', (d: any) => d.target.x)
                .attr('y2', (d: any) => d.target.y);

            node
                .attr('cx', (d: any) => d.x)
                .attr('cy', (d: any) => d.y);
        })
    }
}

function handleClickToChangeSvg(type: string, centerName: string) {
    if (type == "actor") {
        searchAcActorDataByActorName(centerName).then((graphResult) => {
            centerType.value = "actor"
            renderChart();
        }).catch((error) => {
            console.error('Error fetching data:', error);
        });
    } else {
        searchAcActorDataByAnimeName(centerName).then((graphResult) => {
            centerType.value = "anime"
            renderChart();
        }).catch((error) => {
            console.error('Error fetching data:', error);
        });
    }
}

async function searchAcActorDataByActorName(actorName: string) {
    nodes.value = []
    links.value = []
    nodes.value.push({
        id: actorName,
        type: "actor"
    });

    acActorDataArray.value.forEach((acActorData) => {
        acActorData.list.forEach((info, index) => {
            if (info.actor.includes(actorName)) {
                const weight = parseFloat(((acActorData.list.length - index) / acActorData.list.length).toFixed(4));
                const existingLink = links.value.find(link =>
                    link.source === acActorData.name && link.target === actorName
                );
                if (existingLink) {
                    // 如果已有 link 存在，更新 weight 和 character
                    if (weight > existingLink.weight) {
                        existingLink.weight = weight; // 取更大的 weight
                    }
                    existingLink.character.push(info.ac); // 追加 character
                } else {
                    // 否则，新增 link
                    links.value.push({
                        source: acActorData.name,
                        target: actorName,
                        weight: weight,
                        character: [info.ac]
                    });
                    nodes.value.push({
                        id: acActorData.name,
                        type: "anime"
                    });
                }
            }
        });
    });

    return { links, nodes };
}
async function searchAcActorDataByAnimeName(animeName: string) {
    nodes.value = []
    links.value = []
    nodes.value.push({
        id: animeName,
        type: "anime"
    });

    acActorDataArray.value.forEach((acActorData) => {
        if (acActorData.name == animeName) {
            // 使用Set去重
            const uniqueList = Array.from(new Set(acActorData.list.map(item => item.ac)))
                .map(ac => {
                    return acActorData.list.find(item => item.ac === ac);
                });
            uniqueList.forEach((itme, index) => {
                const weight = parseFloat(((uniqueList.length - index) / uniqueList.length).toFixed(4));
                itme?.actor.forEach((actorName) => {
                    const existingLink = links.value.find(link =>
                        link.source === actorName && link.target === animeName
                    )
                    if (existingLink) {
                        // 如果已有 link 存在，更新 weight 和 character
                        if (weight > existingLink.weight) {
                            existingLink.weight = weight; // 取更大的 weight
                        }
                        existingLink.character.push(itme.ac); // 追加 character
                    } else {
                        // 否则，新增 link
                        links.value.push({
                            source: actorName,
                            target: animeName,
                            weight: weight,
                            character: [itme.ac]
                        });
                        nodes.value.push({
                            id: actorName,
                            type: "actor"
                        });
                    }
                })
            })
        }
    });
}
async function getData(path: string): Promise<any[] | undefined> {
    try {
        const data = await d3.json(path) as any[];
        return data;
    } catch (error) {
        console.error('Error loading or validating data:', error);
        return undefined;
    }
}
onMounted(async () => {
    const data = await getData("work/ac_to_actor.json")
    const data02 = await getData("work/games_to_actors.json")
    const mergedData = data?.concat(data02);
    mergedData?.forEach((item: AcActorData, index) => {
        // 去除info.actor中重复爬取的数据
        item.list.forEach(info => {
            info.actor = Array.from(new Set(info.actor));
        });
        acActorDataArray.value[index] = item;
    });
    centerType.value = "anime"
    await searchAcActorDataByAnimeName("【我推的孩子】 第二季")
    renderChart()
})
</script>
<style>
.n-dropdown-menu {
    max-width: 150px;
    max-height: 200px;
    /* 设置最大高度 */
    overflow-y: auto;
    /* 超出部分滚动 */
}
</style>