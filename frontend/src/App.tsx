import React, { useState } from 'react';
import { Upload, AlertCircle, FileText, CheckCircle, Loader2 } from 'lucide-react';
import FileUploader from './components/FileUploader';
import ResultsPanel from './components/ResultsPanel';
import ErrorPanel from './components/ErrorPanel';
import { processMails, resetUploads } from './services/api';
import { ResultsByDate } from './types';

function App() {
  const [uploadedFiles, setUploadedFiles] = useState<File[]>([]);
  const [uploading, setUploading] = useState(false);
  const [processing, setProcessing] = useState(false);
  const [results, setResults] = useState<ResultsByDate>({});
  const [errors, setErrors] = useState<string[]>([]);
  const [uploadSuccess, setUploadSuccess] = useState(false);
  const [uploadErrors, setUploadErrors] = useState<string[]>([]);

  const handleUploadSuccess = (files: File[], uploadErrors: string[]) => {
    setUploadedFiles(files);
    setUploadSuccess(true);
    setUploadErrors(uploadErrors);
  };

  const handleProcessMails = async () => {
    if (uploadedFiles.length === 0) return;
    
    setProcessing(true);
    try {
      const data = await processMails();
      setResults(data.resultados);
      setErrors(data.errores);
    } catch (error) {
      setErrors(['Error al procesar los correos. Por favor, inténtelo de nuevo.']);
    } finally {
      setProcessing(false);
    }
  };

  const handleReset = async () => {
    setUploadedFiles([]);
    setResults({});
    setErrors([]);
    setUploadSuccess(false);
    setUploadErrors([]);
    
    try {
      await resetUploads();
    } catch (error) {
      console.error('Error al restablecer:', error);
    }
  };

  return (
    <div className="min-h-screen bg-gray-50">
      <header className="bg-white shadow-sm">
        <div className="max-w-7xl mx-auto py-6 px-4 sm:px-6 lg:px-8">
          <h1 className="text-3xl font-bold text-gray-900">Procesador de Correos</h1>
        </div>
      </header>
      
      <main className="max-w-7xl mx-auto py-6 sm:px-6 lg:px-8">
        <div className="px-4 py-6 sm:px-0">
          {/* Upload Section */}
          <div className="bg-white shadow rounded-lg mb-6 overflow-hidden">
            <div className="px-6 py-5 border-b border-gray-200">
              <div className="flex items-center">
                <Upload className="h-5 w-5 text-blue-500 mr-2" />
                <h2 className="text-lg font-medium text-gray-900">Subir Archivos</h2>
              </div>
            </div>
            <div className="px-6 py-6">
              <FileUploader 
                onUploadSuccess={handleUploadSuccess} 
                setUploading={setUploading}
              />
              
              {uploadSuccess && (
                <div className="mt-4 p-3 bg-green-50 rounded-md flex items-start">
                  <CheckCircle className="h-5 w-5 text-green-500 mr-2 mt-0.5" />
                  <div>
                    <p className="text-sm font-medium text-green-800">
                      {uploadedFiles.length} archivo{uploadedFiles.length !== 1 ? 's' : ''} subido{uploadedFiles.length !== 1 ? 's' : ''} correctamente
                    </p>
                    {uploadErrors.length > 0 && (
                      <p className="text-sm text-green-700 mt-1">
                        {uploadErrors.length} archivo{uploadErrors.length !== 1 ? 's' : ''} ignorado{uploadErrors.length !== 1 ? 's' : ''} (no son archivos .msg)
                      </p>
                    )}
                  </div>
                </div>
              )}

              {/* Action Buttons */}
              <div className="mt-6 flex space-x-3">
                <button
                  onClick={handleProcessMails}
                  disabled={uploadedFiles.length === 0 || processing || uploading}
                  className={`inline-flex items-center px-4 py-2 border border-transparent rounded-md shadow-sm text-sm font-medium text-white 
                    ${uploadedFiles.length === 0 || processing || uploading ? 
                      'bg-blue-300 cursor-not-allowed' : 
                      'bg-blue-600 hover:bg-blue-700 focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-blue-500'}`}
                >
                  {processing ? (
                    <>
                      <Loader2 className="animate-spin -ml-1 mr-2 h-4 w-4" />
                      Procesando...
                    </>
                  ) : (
                    <>
                      <FileText className="-ml-1 mr-2 h-4 w-4" />
                      Procesar Correos
                    </>
                  )}
                </button>
                
                <button
                  onClick={handleReset}
                  disabled={uploading || processing}
                  className={`inline-flex items-center px-4 py-2 border border-gray-300 rounded-md shadow-sm text-sm font-medium text-gray-700 
                    ${uploading || processing ? 
                      'bg-gray-100 cursor-not-allowed' : 
                      'bg-white hover:bg-gray-50 focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-blue-500'}`}
                >
                  Restablecer
                </button>
              </div>
            </div>
          </div>

          {/* Results and Errors Section */}
          {(Object.keys(results).length > 0 || errors.length > 0) && (
            <div className="space-y-6">
              {Object.keys(results).length > 0 && (
                <div className="bg-white shadow rounded-lg overflow-hidden">
                  <div className="px-6 py-5 border-b border-gray-200">
                    <div className="flex items-center">
                      <CheckCircle className="h-5 w-5 text-green-500 mr-2" />
                      <h2 className="text-lg font-medium text-gray-900">Resultados</h2>
                    </div>
                  </div>
                  <div className="px-2 py-4">
                    <ResultsPanel results={results} />
                  </div>
                </div>
              )}
              
              {errors.length > 0 && (
                <div className="bg-white shadow rounded-lg overflow-hidden">
                  <div className="px-6 py-5 border-b border-gray-200">
                    <div className="flex items-center">
                      <AlertCircle className="h-5 w-5 text-amber-500 mr-2" />
                      <h2 className="text-lg font-medium text-gray-900">Errores</h2>
                    </div>
                  </div>
                  <div className="px-6 py-4">
                    <ErrorPanel errors={errors} />
                  </div>
                </div>
              )}
            </div>
          )}
        </div>
      </main>
    </div>
  );
}

export default App;
