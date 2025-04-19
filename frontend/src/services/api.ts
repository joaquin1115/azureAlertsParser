// URL base del backend
const API_BASE_URL = 'http://localhost:5000';

/**
 * Sube archivos al servidor
 */
export const uploadFiles = async (files: File[]) => {
  const formData = new FormData();
  
  files.forEach(file => {
    formData.append('archivos', file);
  });
  
  const response = await fetch(`${API_BASE_URL}/subir-archivos`, {
    method: 'POST',
    body: formData,
    credentials: 'include' // importante para incluir cookies de sesión
  });
  
  if (!response.ok) {
    throw new Error('Error al subir los archivos');
  }
  
  return await response.json();
};

/**
 * Procesa los correos previamente subidos
 */
export const processMails = async () => {
  const response = await fetch(`${API_BASE_URL}/procesar-correos`, {
    method: 'POST',
    credentials: 'include',
    headers: {
      'Content-Type': 'application/json'
    }
  });
  
  if (!response.ok) {
    throw new Error('Error al procesar los correos');
  }
  
  return await response.json();
};

/**
 * Restablece la subida de archivos
 */
export const resetUploads = async () => {
  const response = await fetch(`${API_BASE_URL}/restablecer`, {
    method: 'POST',
    credentials: 'include',
    headers: {
      'Content-Type': 'application/json'
    }
  });
  
  if (!response.ok) {
    throw new Error('Error al restablecer');
  }
  
  return await response.json();
};