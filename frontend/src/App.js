import React, { useState, useEffect } from 'react';
import './App.css';

const BACKEND_URL = process.env.REACT_APP_BACKEND_URL || 'http://localhost:8001';

function App() {
  const [activeTab, setActiveTab] = useState('optimize');
  const [selectedCategory, setSelectedCategory] = useState('');
  const [originalPrompt, setOriginalPrompt] = useState('');
  const [optimizedPrompt, setOptimizedPrompt] = useState('');
  const [isLoading, setIsLoading] = useState(false);
  const [history, setHistory] = useState([]);
  const [templates, setTemplates] = useState([]);
  const [categories, setCategories] = useState([]);
  const [selectedTemplate, setSelectedTemplate] = useState(null);

  useEffect(() => {
    fetchCategories();
    fetchHistory();
    fetchTemplates();
  }, []);

  const fetchCategories = async () => {
    try {
      const response = await fetch(`${BACKEND_URL}/api/categories`);
      const data = await response.json();
      setCategories(data.categories);
      if (data.categories.length > 0) {
        setSelectedCategory(data.categories[0].id);
      }
    } catch (error) {
      console.error('Error fetching categories:', error);
    }
  };

  const fetchHistory = async () => {
    try {
      const response = await fetch(`${BACKEND_URL}/api/history`);
      const data = await response.json();
      setHistory(data);
    } catch (error) {
      console.error('Error fetching history:', error);
    }
  };

  const fetchTemplates = async () => {
    try {
      const response = await fetch(`${BACKEND_URL}/api/templates`);
      const data = await response.json();
      setTemplates(data);
    } catch (error) {
      console.error('Error fetching templates:', error);
    }
  };

  const optimizePrompt = async () => {
    if (!originalPrompt.trim() || !selectedCategory) {
      alert('Please enter a prompt and select a category');
      return;
    }

    setIsLoading(true);
    try {
      const response = await fetch(`${BACKEND_URL}/api/optimize`, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({
          original_prompt: originalPrompt,
          category: selectedCategory
        })
      });

      const data = await response.json();
      setOptimizedPrompt(data.optimized_prompt);
      fetchHistory(); // Refresh history
    } catch (error) {
      console.error('Error optimizing prompt:', error);
      alert('Error optimizing prompt. Please try again.');
    } finally {
      setIsLoading(false);
    }
  };

  const copyToClipboard = (text) => {
    navigator.clipboard.writeText(text);
    // Simple feedback - could be enhanced with toast notifications
    const button = document.activeElement;
    const originalText = button.textContent;
    button.textContent = 'Copied!';
    setTimeout(() => {
      button.textContent = originalText;
    }, 2000);
  };

  const loadTemplate = (template) => {
    setOriginalPrompt(template.template);
    setSelectedTemplate(template);
    setActiveTab('optimize');
  };

  const loadFromHistory = (item) => {
    setOriginalPrompt(item.original_prompt);
    setOptimizedPrompt(item.optimized_prompt);
    setSelectedCategory(item.category);
    setActiveTab('optimize');
  };

  const deleteHistoryItem = async (id) => {
    try {
      await fetch(`${BACKEND_URL}/api/history/${id}`, { method: 'DELETE' });
      fetchHistory();
    } catch (error) {
      console.error('Error deleting history item:', error);
    }
  };

  return (
    <div className="min-h-screen bg-gray-900 text-white">
      {/* Header */}
      <header className="bg-gradient-to-r from-purple-900 to-blue-900 shadow-lg">
        <div className="max-w-7xl mx-auto px-4 py-6">
          <div className="flex items-center justify-between">
            <div className="flex items-center space-x-3">
              <div className="bg-white rounded-lg p-2">
                <span className="text-2xl">🧠</span>
              </div>
              <div>
                <h1 className="text-3xl font-bold">PromptMaster</h1>
                <p className="text-purple-200">AI-Powered Prompt Optimizer</p>
              </div>
            </div>
          </div>
        </div>
      </header>

      <div className="max-w-7xl mx-auto px-4 py-8">
        {/* Category Selection */}
        {activeTab === 'optimize' && (
          <div className="mb-8">
            <h2 className="text-xl font-semibold mb-4">Select Prompt Category</h2>
            <div className="grid grid-cols-2 md:grid-cols-3 lg:grid-cols-5 gap-3">
              {categories.map((category) => (
                <button
                  key={category.id}
                  onClick={() => setSelectedCategory(category.id)}
                  className={`p-4 rounded-lg border-2 transition-all duration-200 text-center ${
                    selectedCategory === category.id
                      ? 'border-purple-500 bg-purple-900/50 shadow-lg'
                      : 'border-gray-700 bg-gray-800 hover:border-purple-400 hover:bg-gray-700'
                  }`}
                >
                  <div className="text-2xl mb-2">{category.icon}</div>
                  <div className="text-sm font-medium">{category.name}</div>
                </button>
              ))}
            </div>
          </div>
        )}

        {/* Main Content Area */}
        <div className="grid grid-cols-1 lg:grid-cols-2 gap-8 mb-8">
          {/* Original Prompt */}
          {activeTab === 'optimize' && (
            <>
              <div>
                <div className="flex items-center justify-between mb-4">
                  <h3 className="text-lg font-semibold">Original Prompt</h3>
                  {selectedTemplate && (
                    <span className="text-sm text-purple-300">
                      Template: {selectedTemplate.title}
                    </span>
                  )}
                </div>
                <textarea
                  value={originalPrompt}
                  onChange={(e) => setOriginalPrompt(e.target.value)}
                  placeholder="Enter your prompt here..."
                  className="w-full h-64 p-4 bg-gray-800 border border-gray-700 rounded-lg resize-none focus:ring-2 focus:ring-purple-500 focus:border-transparent"
                />
                <div className="mt-4 flex gap-3">
                  <button
                    onClick={optimizePrompt}
                    disabled={isLoading || !originalPrompt.trim() || !selectedCategory}
                    className="bg-gradient-to-r from-purple-600 to-blue-600 hover:from-purple-700 hover:to-blue-700 disabled:from-gray-600 disabled:to-gray-600 px-6 py-2 rounded-lg font-medium transition-all duration-200 disabled:cursor-not-allowed"
                  >
                    {isLoading ? 'Optimizing...' : 'Optimize Prompt'}
                  </button>
                  <button
                    onClick={() => setOriginalPrompt('')}
                    className="bg-gray-700 hover:bg-gray-600 px-4 py-2 rounded-lg font-medium transition-colors"
                  >
                    Clear
                  </button>
                </div>
              </div>

              {/* Optimized Prompt */}
              <div>
                <div className="flex items-center justify-between mb-4">
                  <h3 className="text-lg font-semibold">Optimized Prompt</h3>
                  {optimizedPrompt && (
                    <button
                      onClick={() => copyToClipboard(optimizedPrompt)}
                      className="bg-green-600 hover:bg-green-700 px-4 py-2 rounded-lg text-sm font-medium transition-colors"
                    >
                      Copy Optimized
                    </button>
                  )}
                </div>
                <div className="w-full h-64 p-4 bg-gray-800 border border-gray-700 rounded-lg overflow-y-auto">
                  {optimizedPrompt ? (
                    <pre className="whitespace-pre-wrap text-sm">{optimizedPrompt}</pre>
                  ) : (
                    <p className="text-gray-400">Your optimized prompt will appear here...</p>
                  )}
                </div>
              </div>
            </>
          )}
        </div>

        {/* Tabs */}
        <div className="border-b border-gray-700 mb-6">
          <nav className="flex space-x-8">
            {['optimize', 'history', 'templates'].map((tab) => (
              <button
                key={tab}
                onClick={() => setActiveTab(tab)}
                className={`py-2 px-1 border-b-2 font-medium text-sm capitalize transition-colors ${
                  activeTab === tab
                    ? 'border-purple-500 text-purple-400'
                    : 'border-transparent text-gray-400 hover:text-gray-300 hover:border-gray-300'
                }`}
              >
                {tab}
              </button>
            ))}
          </nav>
        </div>

        {/* Tab Content */}
        {activeTab === 'history' && (
          <div>
            <h2 className="text-xl font-semibold mb-6">Optimization History</h2>
            <div className="space-y-4">
              {history.length === 0 ? (
                <p className="text-gray-400 text-center py-8">No optimization history yet.</p>
              ) : (
                history.map((item) => (
                  <div key={item.id} className="bg-gray-800 border border-gray-700 rounded-lg p-6">
                    <div className="flex items-center justify-between mb-4">
                      <div className="flex items-center space-x-3">
                        <span className="bg-purple-900 text-purple-200 px-3 py-1 rounded-full text-sm">
                          {categories.find(c => c.id === item.category)?.name || item.category}
                        </span>
                        <span className="text-gray-400 text-sm">
                          {new Date(item.timestamp).toLocaleDateString()}
                        </span>
                      </div>
                      <div className="flex space-x-2">
                        <button
                          onClick={() => loadFromHistory(item)}
                          className="bg-blue-600 hover:bg-blue-700 px-3 py-1 rounded text-sm transition-colors"
                        >
                          Load
                        </button>
                        <button
                          onClick={() => deleteHistoryItem(item.id)}
                          className="bg-red-600 hover:bg-red-700 px-3 py-1 rounded text-sm transition-colors"
                        >
                          Delete
                        </button>
                      </div>
                    </div>
                    <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
                      <div>
                        <h4 className="font-medium mb-2">Original:</h4>
                        <p className="text-gray-300 text-sm bg-gray-900 p-3 rounded">
                          {item.original_prompt}
                        </p>
                      </div>
                      <div>
                        <h4 className="font-medium mb-2">Optimized:</h4>
                        <div className="text-gray-300 text-sm bg-gray-900 p-3 rounded relative">
                          <pre className="whitespace-pre-wrap">{item.optimized_prompt}</pre>
                          <button
                            onClick={() => copyToClipboard(item.optimized_prompt)}
                            className="absolute top-2 right-2 bg-green-600 hover:bg-green-700 px-2 py-1 rounded text-xs transition-colors"
                          >
                            Copy
                          </button>
                        </div>
                      </div>
                    </div>
                  </div>
                ))
              )}
            </div>
          </div>
        )}

        {activeTab === 'templates' && (
          <div>
            <h2 className="text-xl font-semibold mb-6">Prompt Templates</h2>
            <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
              {templates.length === 0 ? (
                <p className="text-gray-400 text-center py-8 col-span-full">No templates available.</p>
              ) : (
                templates.map((template) => (
                  <div key={template.id} className="bg-gray-800 border border-gray-700 rounded-lg p-6">
                    <div className="flex items-center justify-between mb-4">
                      <h3 className="text-lg font-semibold">{template.title}</h3>
                      <span className="bg-purple-900 text-purple-200 px-3 py-1 rounded-full text-sm">
                        {categories.find(c => c.id === template.category)?.name || template.category}
                      </span>
                    </div>
                    <p className="text-gray-300 mb-4 text-sm">{template.description}</p>
                    <div className="bg-gray-900 p-3 rounded mb-4 max-h-40 overflow-y-auto">
                      <pre className="text-sm text-gray-300 whitespace-pre-wrap">{template.template}</pre>
                    </div>
                    <button
                      onClick={() => loadTemplate(template)}
                      className="bg-purple-600 hover:bg-purple-700 px-4 py-2 rounded-lg text-sm font-medium transition-colors w-full"
                    >
                      Use Template
                    </button>
                  </div>
                ))
              )}
            </div>
          </div>
        )}
      </div>
    </div>
  );
}

export default App;