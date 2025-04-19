import React, { useState } from 'react';
import { Calendar } from 'lucide-react';
import { ResultsByDate } from '../types';

interface ResultsPanelProps {
  results: ResultsByDate;
}

const ResultsPanel: React.FC<ResultsPanelProps> = ({ results }) => {
  const dates = Object.keys(results);
  const [activeTab, setActiveTab] = useState(dates.length > 0 ? dates[0] : '');

  if (dates.length === 0) {
    return <p className="text-gray-500 p-4">No hay resultados para mostrar.</p>;
  }

  const formatDate = (dateStr: string) => {
    try {
      const date = new Date(dateStr);
      return new Intl.DateTimeFormat('es-ES', { 
        day: '2-digit', 
        month: '2-digit', 
        year: 'numeric' 
      }).format(date);
    } catch (e) {
      return dateStr;
    }
  };

  return (
    <div>
      <div className="border-b border-gray-200">
        <nav className="-mb-px flex overflow-x-auto" aria-label="Tabs">
          {dates.map((date) => (
            <button
              key={date}
              onClick={() => setActiveTab(date)}
              className={`whitespace-nowrap py-3 px-4 border-b-2 font-medium text-sm ${
                activeTab === date
                  ? 'border-blue-500 text-blue-600'
                  : 'border-transparent text-gray-500 hover:text-gray-700 hover:border-gray-300'
              }`}
              aria-current={activeTab === date ? 'page' : undefined}
            >
              <div className="flex items-center">
                <Calendar className="h-4 w-4 mr-2" />
                {formatDate(date)}
              </div>
            </button>
          ))}
        </nav>
      </div>
      
      <div className="mt-4 px-4">
        {activeTab && (
          <div>
            <h3 className="text-sm font-medium text-gray-500 mb-2">
              {results[activeTab].length} correo{results[activeTab].length !== 1 ? 's' : ''} encontrado{results[activeTab].length !== 1 ? 's' : ''}
            </h3>
            <ul className="divide-y divide-gray-200">
              {results[activeTab].map((item, index) => (
                <li key={index} className="py-3">
                  <div className="flex items-start">
                    <div className="ml-1">
                      <p className="text-sm font-medium text-gray-900">{item}</p>
                    </div>
                  </div>
                </li>
              ))}
            </ul>
          </div>
        )}
      </div>
    </div>
  );
};

export default ResultsPanel;