export interface ResultsByDate {
  [date: string]: string[];
}

export interface ProcessingResult {
  resultados: ResultsByDate;
  errores: string[];
}