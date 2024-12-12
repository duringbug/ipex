/*
 * @Description: 
 * @Author: 唐健峰
 * @Date: 2024-07-01 15:01:18
 * @LastEditors: ${author}
 * @LastEditTime: 2024-07-01 15:20:57
 */
import * as XLSX from 'xlsx';

export async function readFileAndProcessExcel(path: string): Promise<any[]> {
    try {
        const response = await fetch(path);
        const data = await response.arrayBuffer();
        const workbook = XLSX.read(data, { type: 'array' });
        const firstSheetName = workbook.SheetNames[0];
        const worksheet = workbook.Sheets[firstSheetName];
        const excelData = XLSX.utils.sheet_to_json(worksheet);
        return excelData;
    } catch (error) {
        console.error("Error reading the Excel file:", error);
        throw error;
    }
}