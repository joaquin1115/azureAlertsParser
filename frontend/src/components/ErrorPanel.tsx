import React from 'react';
import { XCircle } from 'lucide-react';

interface ErrorPanelProps {
  errors: string[];
}

const ErrorPanel: React.FC<ErrorPanelProps> = ({ errors }) => {
  if (errors.length === 0) {
    return <p className="text-gray-500">No hay errores para mostrar.</p>;
  }

  return (
    <div>
      <h3 className="text-sm font-medium text-gray-500 mb-2">
        {errors.length} error{errors.length !== 1 ? 'es' : ''} encontrado{errors.length !== 1 ? 's' : ''}
      </h3>
      <ul className="divide-y divide-gray-200 mt-2">
        {errors.map((error, index) => (
          <li key={index} className="py-3 flex items-start">
            <XCircle className="h-5 w-5 text-red-400 mr-2 mt-0.5 flex-shrink-0" />
            <p className="text-sm text-gray-800">{error}</p>
          </li>
        ))}
      </ul>
    </div>
  );
};

export default ErrorPanel;