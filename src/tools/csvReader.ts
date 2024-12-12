/*
 * @Description: 
 * @Author: 唐健峰
 * @Date: 2024-07-01 16:30:00
 * @LastEditors: ${author}
 * @LastEditTime: 2024-07-01 19:29:54
 */
import * as d3 from 'd3-dsv';

export async function readFileAndProcessCSV(path: string): Promise<any[]> {
    try {
        const response = await fetch(path);
        const csvText = await response.text();
        const csvData = d3.csvParse(csvText);
        return csvData;
    } catch (error) {
        console.error("Error reading the CSV file:", error);
        throw error;
    }
}
