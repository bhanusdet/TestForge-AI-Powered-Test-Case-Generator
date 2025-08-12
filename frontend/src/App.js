import React from 'react';
import { BrowserRouter as Router, Routes, Route } from 'react-router-dom';
import { ToastContainer } from 'react-toastify';
import 'react-toastify/dist/ReactToastify.css';
import Header from './components/Header';
import Footer from './components/Footer';
import Home from './pages/Home';
import TestCaseGenerator from './components/TestCaseGenerator';
import Analytics from './pages/Analytics';
import Documentation from './pages/Documentation';

function App() {
  return (
    <Router>
      <div className="min-h-screen bg-gray-50 flex flex-col">
        <Header />
        <main className="flex-grow">
          <Routes>
            <Route path="/" element={<Home />} />
            <Route path="/generate" element={<TestCaseGenerator />} />
            <Route path="/analytics" element={<Analytics />} />
            <Route path="/docs" element={<Documentation />} />
          </Routes>
        </main>
        <Footer />
        <ToastContainer 
          position="top-right"
          autoClose={4000}
        />
      </div>
    </Router>
  );
}

export default App;