<template>
    <div>
        <svg ref="svg" width="960" height="500"></svg>
    </div>
</template>

<script setup lang="ts">
import { ref, onMounted } from 'vue';
import * as d3 from 'd3';

const svg = ref<SVGSVGElement | null>(null);

interface Links {
    source: string; target: string
}

interface GraphNode extends d3.SimulationNodeDatum {
    id: string;
}

onMounted(() => {
    if (svg.value) {
        const nodes: GraphNode[] = [
            { id: 'A' },
            { id: 'B' },
            { id: 'C' },
            { id: 'D' }
        ];

        const links: Links[] = [
            { source: 'A', target: 'B' },
            { source: 'B', target: 'C' },
            { source: 'C', target: 'D' },
            { source: 'D', target: 'A' }
        ];

        const svgElement = d3.select(svg.value);

        const simulation = d3.forceSimulation<GraphNode>(nodes)
            .force('link', d3.forceLink<GraphNode, { source: string; target: string }>(links).id((d: any) => d.id))
            .force('charge', d3.forceManyBody())
            .force('center', d3.forceCenter(480, 250));

        const link = svgElement.selectAll('.link')
            .data(links)
            .enter().append('line')
            .attr('class', 'link')
            .attr('stroke', '#000')
            .attr('stroke-width', '2');

        const node = svgElement.selectAll('.node')
            .data(nodes)
            .enter().append('circle')
            .attr('class', 'node')
            .attr('r', 5)
            .attr('fill', '#ccc')
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
});
</script>

<style scoped>
.link {
    stroke: #000;
    stroke-width: 2px;
}

.node {
    cursor: pointer;
    fill: #ccc;
    stroke: #000;
    stroke-width: 1.5px;
}
</style>
