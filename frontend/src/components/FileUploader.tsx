import React, { useState, useRef } from 'react';
import { Upload, File } from 'lucide-react';
import { uploadFiles } from '../services/api';

interface FileUploaderProps {
  onUploadSuccess: (files: File[], errors: string[]) => void;
  setUploading: (isUploading: boolean) => void;
}

const FileUploader: React.FC<FileUploaderProps> = ({ onUploadSuccess, setUploading }) => {
  const [isDragging, setIsDragging] = useState(false);
  const fileInputRef = useRef<HTMLInputElement>(null);

  const handleDragEnter = (e: React.DragEvent<HTMLDivElement>) => {
    e.preventDefault();
    e.stopPropagation();
    setIsDragging(true);
  };

  const handleDragLeave = (e: React.DragEvent<HTMLDivElement>) => {
    e.preventDefault();
    e.stopPropagation();
    setIsDragging(false);
  };

  const handleDragOver = (e: React.DragEvent<HTMLDivElement>) => {
    e.preventDefault();
    e.stopPropagation();
    if (!isDragging) setIsDragging(true);
  };

  const handleDrop = async (e: React.DragEvent<HTMLDivElement>) => {
    e.preventDefault();
    e.stopPropagation();
    setIsDragging(false);
    
    if (e.dataTransfer.files && e.dataTransfer.files.length > 0) {
      await processFiles(Array.from(e.dataTransfer.files));
    }
  };

  const handleFileSelect = async (e: React.ChangeEvent<HTMLInputElement>) => {
    if (e.target.files && e.target.files.length > 0) {
      await processFiles(Array.from(e.target.files));
    }
  };

  const processFiles = async (files: File[]) => {
    // Filter out non-msg files but keep track of them for error reporting
    const msgFiles = files.filter(file => file.name.toLowerCase().endsWith('.msg'));
    const errorFiles = files.filter(file => !file.name.toLowerCase().endsWith('.msg'))
      .map(file => `Archivo ignorado: ${file.name}`);
    
    if (msgFiles.length === 0) {
      onUploadSuccess([], errorFiles);
      return;
    }
    
    setUploading(true);
    
    try {
      const result = await uploadFiles(msgFiles);
      onUploadSuccess(msgFiles, [...errorFiles, ...result.errores]);
    } catch (error) {
      console.error('Error uploading files:', error);
      onUploadSuccess([], ['Error al subir los archivos. Por favor, inténtelo de nuevo.']);
    } finally {
      setUploading(false);
    }
  };

  const handleButtonClick = () => {
    fileInputRef.current?.click();
  };

  return (
    <div
      onDragEnter={handleDragEnter}
      onDragLeave={handleDragLeave}
      onDragOver={handleDragOver}
      onDrop={handleDrop}
      className={`border-2 border-dashed rounded-lg p-6 
        flex flex-col items-center justify-center transition-colors duration-200 
        ${isDragging ? 'border-blue-500 bg-blue-50' : 'border-gray-300 hover:border-gray-400'}`}
    >
      <input
        type="file"
        ref={fileInputRef}
        onChange={handleFileSelect}
        multiple
        accept=".msg"
        className="hidden"
      />
      
      <div className="flex flex-col items-center text-center">
        <Upload 
          className={`h-12 w-12 mb-3 ${isDragging ? 'text-blue-500' : 'text-gray-400'}`} 
        />
        <h3 className="text-lg font-medium text-gray-900">
          {isDragging ? 'Suelta los archivos aquí' : 'Arrastra y suelta archivos .msg'}
        </h3>
        <p className="mt-1 text-sm text-gray-500">
          O haz clic para seleccionar archivos
        </p>
      </div>
      
      <button
        type="button"
        onClick={handleButtonClick}
        className="mt-4 inline-flex items-center px-4 py-2 border border-gray-300 rounded-md shadow-sm text-sm font-medium text-gray-700 bg-white hover:bg-gray-50 focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-blue-500"
      >
        <File className="-ml-1 mr-2 h-4 w-4 text-gray-400" />
        Seleccionar archivos
      </button>
      
      <p className="mt-3 text-xs text-gray-500">
        Solo se aceptan archivos con formato .msg
      </p>
    </div>
  );
};

export default FileUploader;