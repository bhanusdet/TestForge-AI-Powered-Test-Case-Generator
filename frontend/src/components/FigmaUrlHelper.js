import React, { useState } from 'react';
import { Check, X, Info } from 'lucide-react';

const FigmaUrlHelper = ({ onUrlSelect }) => {
  const [testUrl, setTestUrl] = useState('');
  const [isValid, setIsValid] = useState(null);

  const exampleUrls = [
    'https://www.figma.com/design/aajUyVRdgAsnnxSxTYQSHS/Merge-accounts?node-id=35-4577&t=hwbsktOIS5bQ5Ho0-0',
    'https://www.figma.com/file/ABC123456789/Login-Page-Design',
    'https://www.figma.com/design/XYZ987654321/Dashboard-Prototype?node-id=1-2'
  ];

  const validateUrl = (url) => {
    const figmaPatterns = [
      /^https:\/\/www\.figma\.com\/file\/[a-zA-Z0-9\-_]+\/[^?]*(\?[^#]*)?(#.*)?$/,
      /^https:\/\/www\.figma\.com\/design\/[a-zA-Z0-9\-_]+\/[^?]*(\?[^#]*)?(#.*)?$/,
      /^figma:\/\/file\/[a-zA-Z0-9\-_]+(#.*)?$/
    ];
    
    return figmaPatterns.some(pattern => pattern.test(url));
  };

  const handleTestUrl = (url) => {
    setTestUrl(url);
    const valid = validateUrl(url);
    setIsValid(valid);
    if (valid && onUrlSelect) {
      onUrlSelect(url);
    }
  };

  return (
    <div className="bg-purple-50 rounded-lg p-4 border border-purple-200">
      <div className="flex items-center space-x-2 mb-3">
        <Info className="w-4 h-4 text-purple-600" />
        <h4 className="font-medium text-purple-900">Figma URL Helper</h4>
      </div>
      
      <div className="space-y-3">
        <div>
          <label className="block text-sm text-purple-700 mb-1">Test a URL:</label>
          <div className="flex space-x-2">
            <input
              type="text"
              value={testUrl}
              onChange={(e) => handleTestUrl(e.target.value)}
              placeholder="Paste your Figma URL here..."
              className="flex-1 px-3 py-2 text-sm border border-purple-200 rounded focus:ring-2 focus:ring-purple-500 focus:border-transparent"
            />
            {isValid !== null && (
              <div className={`flex items-center px-2 ${isValid ? 'text-green-600' : 'text-red-600'}`}>
                {isValid ? <Check className="w-4 h-4" /> : <X className="w-4 h-4" />}
              </div>
            )}
          </div>
        </div>

        <div>
          <p className="text-sm text-purple-700 mb-2">Try these examples:</p>
          <div className="space-y-1">
            {exampleUrls.map((url, index) => (
              <button
                key={index}
                onClick={() => handleTestUrl(url)}
                className="block w-full text-left px-3 py-2 text-xs bg-white border border-purple-200 rounded hover:bg-purple-50 transition-colors"
              >
                <div className="truncate">{url}</div>
              </button>
            ))}
          </div>
        </div>

        <div className="text-xs text-purple-600 space-y-1">
          <p>💡 <strong>Tip:</strong> Use specific node IDs (node-id parameter) for better component extraction</p>
          <p>🔑 <strong>Setup:</strong> Make sure your backend has FIGMA_ACCESS_TOKEN configured</p>
        </div>
      </div>
    </div>
  );
};

export default FigmaUrlHelper;