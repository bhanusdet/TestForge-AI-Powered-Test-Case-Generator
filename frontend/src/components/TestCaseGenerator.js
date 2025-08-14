import React, { useState } from 'react';
import axios from 'axios';
import { toast } from 'react-toastify';
import { motion } from 'framer-motion';
import { 
  FileText, 
  Upload, 
  Loader2, 
  CheckCircle, 
  Download,
  Copy,
  Star,
  Sparkles,
  X,
  Brain
} from 'lucide-react';

export default function TestCaseGenerator() {
  const [userStory, setUserStory] = useState('');
  const [attachments, setAttachments] = useState([]);
  const [testCases, setTestCases] = useState([]);
  const [metadata, setMetadata] = useState(null);
  const [loading, setLoading] = useState(false);
  const [showFeedback, setShowFeedback] = useState(false);
  const [feedbackRating, setFeedbackRating] = useState(5);
  const [feedbackComment, setFeedbackComment] = useState('');
  const [feedbackCategories, setFeedbackCategories] = useState([]);
  const [missingScenarios, setMissingScenarios] = useState('');
  const [improvedTestCases, setImprovedTestCases] = useState([]);

  const API_BASE = process.env.NODE_ENV === 'production' 
    ? '/api/v1' 
    : 'http://127.0.0.1:8000/api/v1';

  const handleFileUpload = (e) => {
    const files = Array.from(e.target.files).slice(0, 5);
    setAttachments(files);
  };

  const removeFile = (index) => {
    setAttachments(prev => prev.filter((_, i) => i !== index));
  };

  const handleGenerate = async () => {
    if (!userStory.trim() && attachments.length === 0) {
      toast.error("❌ Please enter a story or upload files");
      return;
    }

    setLoading(true);
    try {
      const formData = new FormData();
      formData.append('story', userStory);

      // Add all uploaded files (PDFs + images)
      attachments.forEach(file => {
        formData.append('attachments', file);
      });

      const response = await axios.post(
        `${API_BASE}/generate-test-cases`,
        formData,
        { headers: { 'Content-Type': 'multipart/form-data' } }
      );

      console.log("Raw API response:", response.data);

      // Handle enhanced response format
      setTestCases(response.data.test_cases || []);
      setMetadata(response.data.metadata || null);
      toast.success("✅ Test cases generated!");
    } catch (error) {
      console.error(error);
      toast.error("❌ Failed to generate test cases");
    } finally {
      setLoading(false);
    }
  };

  const submitFeedback = async () => {
    if (!metadata?.story_id) return;

    try {
      const feedbackData = {
        story_id: metadata.story_id,
        quality_score: feedbackRating,
        feedback: feedbackComment,
        feedback_categories: feedbackCategories,
        missing_scenarios: missingScenarios ? missingScenarios.split(',').map(s => s.trim()) : [],
        improved_testcases: improvedTestCases.length > 0 ? improvedTestCases : null
      };

      await axios.post(`${API_BASE}/feedback`, feedbackData);
      toast.success("🙏 Thank you for your detailed feedback! This helps improve our AI.");
      setShowFeedback(false);
      
      // Reset all feedback states
      setFeedbackComment('');
      setFeedbackRating(5);
      setFeedbackCategories([]);
      setMissingScenarios('');
      setImprovedTestCases([]);
    } catch (error) {
      toast.error("❌ Failed to submit feedback");
      console.error('Feedback submission error:', error);
    }
  };

  const toggleFeedbackCategory = (category) => {
    setFeedbackCategories(prev => 
      prev.includes(category) 
        ? prev.filter(c => c !== category)
        : [...prev, category]
    );
  };

  const addImprovedTestCase = () => {
    const newTestCase = {
      id: `improved_${improvedTestCases.length + 1}`,
      title: '',
      preconditions: '',
      steps: '',
      expected: '',
      priority: 'Medium'
    };
    setImprovedTestCases([...improvedTestCases, newTestCase]);
  };

  const updateImprovedTestCase = (index, field, value) => {
    const updated = [...improvedTestCases];
    updated[index][field] = value;
    setImprovedTestCases(updated);
  };

  const removeImprovedTestCase = (index) => {
    setImprovedTestCases(prev => prev.filter((_, i) => i !== index));
  };

  const exportCSV = () => {
    const headers = [
      'Test Case ID',
      'Title',
      'Preconditions',
      'Test Steps',
      'Expected Result',
      'Priority',
    ];
    const rows = testCases.map(tc => [
      tc.id, tc.title, tc.preconditions, tc.steps, tc.expected, tc.priority
    ]);
    const csvContent = [headers, ...rows]
      .map(e => e.map(f => `"${f || ''}"`).join(","))
      .join("\n");

    // Create meaningful filename from user story or uploaded file
    const generateFilename = () => {
      const timestamp = new Date().toISOString().slice(0, 10); // YYYY-MM-DD
      
      // If PDF/file uploaded, use the filename
      if (attachments.length > 0) {
        const firstFile = attachments[0];
        const fileNameWithoutExt = firstFile.name.replace(/\.[^/.]+$/, ""); // Remove extension
        const cleanFileName = fileNameWithoutExt
          .replace(/[^a-zA-Z0-9\s-_]/g, '') // Keep alphanumeric, spaces, hyphens, underscores
          .replace(/\s+/g, '_') // Replace spaces with underscores
          .toLowerCase();
        return `testcases_${cleanFileName}_${timestamp}.csv`;
      }
      
      // Extract meaningful business terms from user story
      if (userStory.trim()) {
        // Common stop words to ignore
        const stopWords = new Set([
          'as', 'a', 'an', 'the', 'i', 'want', 'to', 'so', 'that', 'can', 'will', 'be', 'is', 'are',
          'user', 'customer', 'admin', 'system', 'should', 'able', 'have', 'get', 'see', 'view',
          'for', 'in', 'on', 'at', 'by', 'with', 'from', 'up', 'about', 'into', 'through', 'during',
          'before', 'after', 'above', 'below', 'to', 'from', 'up', 'down', 'in', 'out', 'on', 'off',
          'over', 'under', 'again', 'further', 'then', 'once', 'my', 'me', 'myself', 'we', 'our',
          'ours', 'ourselves', 'you', 'your', 'yours', 'yourself', 'yourselves', 'he', 'him', 'his',
          'himself', 'she', 'her', 'hers', 'herself', 'it', 'its', 'itself', 'they', 'them', 'their',
          'theirs', 'themselves', 'what', 'which', 'who', 'whom', 'this', 'that', 'these', 'those'
        ]);
        
        const meaningfulWords = userStory
          .toLowerCase()
          .replace(/[^a-z0-9\s]/g, '') // Remove special characters
          .split(/\s+/)
          .filter(word => 
            word.length > 2 && 
            !stopWords.has(word) &&
            !word.includes('test') && // Remove test-related words
            !word.includes('case')
          )
          .slice(0, 3) // Take first 3 meaningful words
          .join('_');
        
        if (meaningfulWords) {
          return `testcases_${meaningfulWords}_${timestamp}.csv`;
        }
      }
      
      // Fallback to story ID or timestamp
      return `testcases_${metadata?.story_id || 'generated'}_${timestamp}.csv`;
    };

    const blob = new Blob([csvContent], { type: 'text/csv' });
    const url = URL.createObjectURL(blob);
    const a = document.createElement('a');
    a.href = url;
    a.download = generateFilename();
    a.click();
    URL.revokeObjectURL(url);
  };

  const copyToClipboard = () => {
    const text = JSON.stringify(testCases, null, 2);
    navigator.clipboard.writeText(text);
    toast.success("📋 Test cases copied to clipboard!");
  };

  return (
    <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-8">
      {/* Header */}
      <motion.div 
        initial={{ opacity: 0, y: 20 }}
        animate={{ opacity: 1, y: 0 }}
        className="text-center mb-8"
      >
        <div className="flex justify-center mb-4">
          <div className="p-3 bg-gradient-to-r from-blue-500 to-purple-600 rounded-xl">
            <Brain className="w-8 h-8 text-white" />
          </div>
        </div>
        <h1 className="text-3xl md:text-4xl font-bold text-gray-900 mb-2">
          AI Test Case Generator
        </h1>
        <p className="text-lg text-gray-600">
          Transform your user stories into comprehensive test cases
        </p>
      </motion.div>

      <div className="grid grid-cols-1 lg:grid-cols-2 gap-8">
        {/* Input Section */}
        <motion.div 
          initial={{ opacity: 0, x: -20 }}
          animate={{ opacity: 1, x: 0 }}
          className="space-y-6"
        >
          {/* User Story Input */}
          <div>
            <label className="block text-sm font-medium text-gray-700 mb-2">
              User Story
            </label>
            <textarea
              rows="8"
              className="w-full px-4 py-3 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent resize-none"
              value={userStory}
              onChange={(e) => setUserStory(e.target.value)}
              placeholder="Enter your user story here..."
            />
          </div>

          {/* File Upload */}
          <div>
            <label className="block text-sm font-medium text-gray-700 mb-2">
              Upload Files (PDF or Image)
            </label>
            <input
              type="file"
              multiple
              accept="image/*,application/pdf"
              onChange={handleFileUpload}
              className="mt-1 block w-full text-sm text-gray-500
                file:mr-4 file:py-2 file:px-4 file:rounded-full
                file:border-0 file:text-sm file:font-semibold
                file:bg-blue-50 file:text-blue-700
                hover:file:bg-blue-100"
            />

            {/* File List */}
            {attachments.length > 0 && (
              <div className="mt-4 space-y-2">
                {attachments.map((file, index) => (
                  <div key={index} className="flex items-center justify-between p-3 bg-gray-50 rounded-lg">
                    <div className="flex items-center space-x-2">
                      <FileText className="w-5 h-5 text-gray-500" />
                      <span className="text-sm text-gray-700">{file.name}</span>
                      <span className="text-xs text-gray-500">
                        ({(file.size / 1024 / 1024).toFixed(1)} MB)
                      </span>
                    </div>
                    <button
                      onClick={() => removeFile(index)}
                      className="text-red-500 hover:text-red-700 p-1"
                    >
                      <X className="w-4 h-4" />
                    </button>
                  </div>
                ))}
              </div>
            )}
          </div>

          {/* Generate Button */}
          <button
            onClick={handleGenerate}
            className="w-full bg-blue-600 text-white py-3 px-6 rounded-lg font-semibold hover:bg-blue-700 disabled:bg-gray-400 disabled:cursor-not-allowed transition-colors flex items-center justify-center space-x-2"
            disabled={loading}
          >
            {loading ? (
              <>
                <Loader2 className="w-5 h-5 animate-spin" />
                <span>Generating Test Cases...</span>
              </>
            ) : (
              <>
                <Sparkles className="w-5 h-5" />
                <span>Generate Test Cases</span>
              </>
            )}
          </button>
        </motion.div>

        {/* Results Section */}
        <motion.div 
          initial={{ opacity: 0, x: 20 }}
          animate={{ opacity: 1, x: 0 }}
          className="space-y-6"
        >
          {testCases.length > 0 && (
            <div className="bg-white border border-gray-200 rounded-lg p-6">
              {/* Results Header */}
              <div className="flex items-center justify-between mb-6">
                <div className="flex items-center space-x-2">
                  <CheckCircle className="w-6 h-6 text-green-500" />
                  <h3 className="text-xl font-semibold text-gray-900">
                    Generated Test Cases
                  </h3>
                </div>
                <div className="flex items-center space-x-2">
                  <button
                    onClick={copyToClipboard}
                    className="p-2 text-gray-500 hover:text-gray-700 rounded-lg hover:bg-gray-100 transition-colors"
                    title="Copy to clipboard"
                  >
                    <Copy className="w-5 h-5" />
                  </button>
                  <button
                    onClick={exportCSV}
                    className="p-2 text-gray-500 hover:text-gray-700 rounded-lg hover:bg-gray-100 transition-colors"
                    title="Export CSV"
                  >
                    <Download className="w-5 h-5" />
                  </button>
                  {metadata?.story_id && (
                    <button
                      onClick={() => setShowFeedback(true)}
                      className="flex items-center space-x-1 px-3 py-2 bg-yellow-100 text-yellow-800 rounded-lg hover:bg-yellow-200 transition-colors"
                    >
                      <Star className="w-4 h-4" />
                      <span className="text-sm">Rate</span>
                    </button>
                  )}
                </div>
              </div>

              {/* Enhanced Metadata */}
              {metadata && (
                <div className="bg-gradient-to-r from-blue-50 to-purple-50 rounded-lg p-4 mb-6">
                  <h4 className="font-medium text-gray-900 mb-2 flex items-center">
                    <Brain className="w-4 h-4 mr-2 text-blue-600" />
                    AI Generation Info
                  </h4>
                  <div className="grid grid-cols-2 md:grid-cols-3 gap-4 text-sm">
                    <div>
                      <span className="text-gray-500">Generated: </span>
                      <span className="text-gray-900 font-medium">{metadata.generated_count} test cases</span>
                    </div>
                    {metadata.similar_examples_used && (
                      <div>
                        <span className="text-gray-500">Learning: </span>
                        <span className="text-green-600 font-medium">{metadata.similar_examples_used} examples used</span>
                      </div>
                    )}
                    {metadata.enhanced_rag && (
                      <div>
                        <span className="text-gray-500">AI Mode: </span>
                        <span className="text-purple-600 font-medium">Enhanced RAG</span>
                      </div>
                    )}
                  </div>
                </div>
              )}

              {/* Test Cases - Card Layout (Better for readability) */}
              <div className="space-y-4">
                {testCases.map((tc, idx) => (
                  <div key={idx} className="border border-gray-200 rounded-lg p-4 hover:shadow-md transition-shadow">
                    <div className="flex items-start justify-between mb-3">
                      <div className="flex items-center space-x-3">
                        <span className="bg-blue-100 text-blue-800 px-2 py-1 rounded text-sm font-medium">
                          {tc.id}
                        </span>
                        <span className={`px-2 py-1 rounded-full text-xs font-medium ${
                          tc.priority === 'High' ? 'bg-red-100 text-red-800' :
                          tc.priority === 'Medium' ? 'bg-yellow-100 text-yellow-800' :
                          'bg-green-100 text-green-800'
                        }`}>
                          {tc.priority}
                        </span>
                      </div>
                    </div>
                    
                    <h4 className="font-semibold text-gray-900 mb-3">{tc.title}</h4>
                    
                    <div className="grid grid-cols-1 md:grid-cols-3 gap-4 text-sm">
                      <div>
                        <span className="font-medium text-gray-700 block mb-1">Preconditions:</span>
                        <p className="text-gray-600 whitespace-pre-line">{tc.preconditions || 'None'}</p>
                      </div>
                      
                      <div>
                        <span className="font-medium text-gray-700 block mb-1">Test Steps:</span>
                        <p className="text-gray-600 whitespace-pre-line">{tc.steps}</p>
                      </div>
                      
                      <div>
                        <span className="font-medium text-gray-700 block mb-1">Expected Result:</span>
                        <p className="text-gray-600 whitespace-pre-line">{tc.expected}</p>
                      </div>
                    </div>
                  </div>
                ))}
              </div>
            </div>
          )}
        </motion.div>
      </div>
        {/* Enhanced Feedback Modal */}
        {showFeedback && (
          <div className="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center p-4 z-50">
            <motion.div
              initial={{ opacity: 0, scale: 0.95 }}
              animate={{ opacity: 1, scale: 1 }}
              className="bg-white rounded-xl p-6 w-full max-w-2xl max-h-[90vh] overflow-y-auto"
            >
              <div className="flex items-center justify-between mb-6">
                <h3 className="text-xl font-semibold text-gray-900">🎯 Help Us Improve!</h3>
                <button
                  onClick={() => setShowFeedback(false)}
                  className="text-gray-400 hover:text-gray-600"
                >
                  <X className="w-5 h-5" />
                </button>
              </div>

              {/* Quality Rating */}
              <div className="mb-6">
                <label className="block text-sm font-medium text-gray-700 mb-3">
                  Overall Quality Rating ⭐
                </label>
                <div className="flex space-x-2 mb-2">
                  {[1, 2, 3, 4, 5].map(rating => (
                    <button
                      key={rating}
                      onClick={() => setFeedbackRating(rating)}
                      className={`p-2 rounded transition-colors ${
                        feedbackRating >= rating ? 'text-yellow-500' : 'text-gray-300'
                      }`}
                    >
                      <Star className="w-8 h-8 fill-current" />
                    </button>
                  ))}
                </div>
                <div className="text-sm text-gray-500">
                  {feedbackRating === 1 && "😞 Poor - Needs major improvement"}
                  {feedbackRating === 2 && "😐 Below Average - Several issues"}
                  {feedbackRating === 3 && "🙂 Average - Good but could be better"}
                  {feedbackRating === 4 && "😊 Good - Minor improvements needed"}
                  {feedbackRating === 5 && "🤩 Excellent - Very satisfied!"}
                </div>
              </div>

              {/* Feedback Categories */}
              <div className="mb-6">
                <label className="block text-sm font-medium text-gray-700 mb-3">
                  What aspects need improvement? (Select all that apply)
                </label>
                <div className="grid grid-cols-2 gap-2">
                  {[
                    'Coverage', 'Edge Cases', 'Clarity', 'Completeness', 
                    'Relevance', 'Priority', 'Steps Detail', 'Expected Results'
                  ].map(category => (
                    <button
                      key={category}
                      onClick={() => toggleFeedbackCategory(category)}
                      className={`px-3 py-2 rounded-lg text-sm border transition-colors ${
                        feedbackCategories.includes(category)
                          ? 'bg-blue-100 border-blue-300 text-blue-700'
                          : 'bg-gray-50 border-gray-200 text-gray-600 hover:bg-gray-100'
                      }`}
                    >
                      {category}
                    </button>
                  ))}
                </div>
              </div>

              {/* Missing Scenarios */}
              <div className="mb-6">
                <label className="block text-sm font-medium text-gray-700 mb-2">
                  Missing Scenarios (comma-separated)
                </label>
                <input
                  type="text"
                  value={missingScenarios}
                  onChange={(e) => setMissingScenarios(e.target.value)}
                  className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent"
                  placeholder="e.g., mobile view, accessibility, performance"
                />
              </div>

              {/* Comments */}
              <div className="mb-6">
                <label className="block text-sm font-medium text-gray-700 mb-2">
                  Detailed Comments
                </label>
                <textarea
                  value={feedbackComment}
                  onChange={(e) => setFeedbackComment(e.target.value)}
                  rows="4"
                  className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent"
                  placeholder="Share specific feedback to help our AI learn better..."
                />
              </div>

              {/* Improved Test Cases Section */}
              <div className="mb-6">
                <div className="flex items-center justify-between mb-3">
                  <label className="block text-sm font-medium text-gray-700">
                    💡 Add Your Improved Test Cases (Optional)
                  </label>
                  <button
                    onClick={addImprovedTestCase}
                    className="text-sm bg-green-100 text-green-700 px-3 py-1 rounded hover:bg-green-200"
                  >
                    + Add Test Case
                  </button>
                </div>
                
                {improvedTestCases.map((testCase, index) => (
                  <div key={index} className="border border-gray-200 rounded-lg p-4 mb-3 bg-gray-50">
                    <div className="flex justify-between items-center mb-2">
                      <h4 className="font-medium text-gray-700">Test Case {index + 1}</h4>
                      <button
                        onClick={() => removeImprovedTestCase(index)}
                        className="text-red-500 hover:text-red-700"
                      >
                        <X className="w-4 h-4" />
                      </button>
                    </div>
                    
                    <div className="grid grid-cols-1 gap-3">
                      <input
                        type="text"
                        placeholder="Test Case Title"
                        value={testCase.title}
                        onChange={(e) => updateImprovedTestCase(index, 'title', e.target.value)}
                        className="w-full px-2 py-1 text-sm border border-gray-300 rounded"
                      />
                      <input
                        type="text"
                        placeholder="Preconditions"
                        value={testCase.preconditions}
                        onChange={(e) => updateImprovedTestCase(index, 'preconditions', e.target.value)}
                        className="w-full px-2 py-1 text-sm border border-gray-300 rounded"
                      />
                      <textarea
                        placeholder="Test Steps"
                        value={testCase.steps}
                        onChange={(e) => updateImprovedTestCase(index, 'steps', e.target.value)}
                        rows="2"
                        className="w-full px-2 py-1 text-sm border border-gray-300 rounded"
                      />
                      <textarea
                        placeholder="Expected Result"
                        value={testCase.expected}
                        onChange={(e) => updateImprovedTestCase(index, 'expected', e.target.value)}
                        rows="2"
                        className="w-full px-2 py-1 text-sm border border-gray-300 rounded"
                      />
                    </div>
                  </div>
                ))}
              </div>

              {/* Action Buttons */}
              <div className="flex space-x-3">
                <button
                  onClick={submitFeedback}
                  className="flex-1 bg-gradient-to-r from-blue-600 to-purple-600 text-white py-3 px-4 rounded-lg hover:from-blue-700 hover:to-purple-700 transition-all font-medium"
                >
                  🚀 Submit Enhanced Feedback
                </button>
                <button
                  onClick={() => setShowFeedback(false)}
                  className="flex-1 border border-gray-300 text-gray-700 py-3 px-4 rounded-lg hover:bg-gray-50 transition-colors"
                >
                  Cancel
                </button>
              </div>
              
              <p className="text-xs text-gray-500 mt-3 text-center">
                Your feedback directly improves our AI's ability to generate better test cases! 🙏
              </p>
            </motion.div>
          </div>
        )}
    </div>
  );
}