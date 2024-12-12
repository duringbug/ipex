<template>
    <canvas id="my-canvas" width="800" height="800">
        Your browser does not support the HTML5 canvas element.
    </canvas>
</template>

<script setup lang="ts">
import { onMounted } from 'vue';

const num = 6
let gl: WebGLRenderingContext | null = null;
let canvas: HTMLCanvasElement | null = null;
let glProgram: WebGLProgram | null = null;
let fragmentShader: WebGLShader | null = null;
let vertexShader: WebGLShader | null = null;

let vertexPositionAttribute: number | null = null;
let trianglesVerticeBuffer: WebGLBuffer | null = null;

function initWebGL() {
    canvas = document.getElementById("my-canvas") as HTMLCanvasElement;
    gl = canvas.getContext("experimental-webgl") as WebGLRenderingContext;

    if (gl) {
        setupWebGL();
        initBuffers();
        initShaders();
        drawScene();
    } else {
        alert("Error: Your browser does not appear to support WebGL.");
    }
}

function setupWebGL() {
    gl?.clearColor(0.1, 0.5, 0.1, 1.0);
    gl?.clear(gl.COLOR_BUFFER_BIT);
}

function initShaders() {
    if (gl) {
        let fs_source = `
        void main(void) {
          gl_FragColor = vec4(1.0, 1.0, 1.0, 1.0);
        }
      `;
        let vs_source = `
        attribute vec3 aVertexPosition;
        void main(void) {
          gl_Position = vec4(aVertexPosition, 1.0);
        }
      `;

        vertexShader = makeShader(vs_source, gl.VERTEX_SHADER) as WebGLShader | null;
        fragmentShader = makeShader(fs_source, gl.FRAGMENT_SHADER) as WebGLShader | null;

        glProgram = gl.createProgram();

        gl.attachShader(glProgram as any, vertexShader as any);
        gl.attachShader(glProgram as any, fragmentShader as any);
        gl.linkProgram(glProgram as any);

        if (!gl.getProgramParameter(glProgram as any, gl.LINK_STATUS)) {
            alert("Unable to initialize the shader program.");
        }

        gl.useProgram(glProgram);
    }
}

function makeShader(src: string, type: number) {
    if (gl) {
        let shader = gl.createShader(type);
        gl.shaderSource(shader as any, src);
        gl.compileShader(shader as any);

        if (!gl.getShaderParameter(shader as any, gl.COMPILE_STATUS)) {
            alert("Error compiling shader: " + gl.getShaderInfoLog(shader as any));
        }

        return shader;
    }
}

function initBuffers() {
    let side_length = 0.3;
    let offset = side_length;
    let height = (Math.sqrt(3) / 2) * side_length;

    let triangleVertices = [];
    for (let i = 0; i < num; i++) {
        let xOffset = i * offset;
        triangleVertices.push(
            -side_length / 2 + xOffset - 0.8, 0.0, 0.0,
            0.0 + xOffset - 0.8, height, 0.0,
            side_length / 2 + xOffset - 0.8, 0.0, 0.0
        );
    }

    if (gl) {
        trianglesVerticeBuffer = gl.createBuffer();
        gl.bindBuffer(gl.ARRAY_BUFFER, trianglesVerticeBuffer);
        gl.bufferData(gl.ARRAY_BUFFER, new Float32Array(triangleVertices), gl.STATIC_DRAW);
    }
}

function drawScene() {
    if (gl) {
        vertexPositionAttribute = gl.getAttribLocation(glProgram as any, "aVertexPosition");
        gl.enableVertexAttribArray(vertexPositionAttribute);
        gl.bindBuffer(gl.ARRAY_BUFFER, trianglesVerticeBuffer);
        gl.vertexAttribPointer(vertexPositionAttribute, 3, gl.FLOAT, false, 0, 0);
        gl.drawArrays(gl.TRIANGLES, 0, num * 3);
    }
}

onMounted(() => {
    initWebGL();
});
</script>

<style scoped>
body {
    background-color: grey;
}

canvas {
    background-color: white;
}
</style>