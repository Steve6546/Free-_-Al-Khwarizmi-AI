
import { useState, useEffect, useRef } from "react";
import { BrowserRouter, Routes, Route } from "react-router-dom";
import axios from "axios";
import { motion, AnimatePresence } from "framer-motion";
import { useTranslation, initReactI18next } from "react-i18next";
import i18n from "i18next";
import LanguageDetector from "i18next-browser-languagedetector";
import Lottie from "lottie-react";
import "./App.css";

// Arabic translations
const resources = {
  ar: {
    translation: {
      "app-title": "مُنشئ المواقع الذكي",
      "app-description": "أدخل فكرة موقعك، ودع الذكاء الاصطناعي يبنيه لك",
      "idea-placeholder": "أدخل فكرة موقعك هنا... مثال: أريد موقع لعرض المنتجات الحرفية",
      "api-key-placeholder": "أدخل مفتاح API الخاص بك هنا...",
      "api-key-info": "يتطلب استخدام مفتاح Gemini Pro API من Google",
      "start-button": "ابدأ الإنشاء",
      "reset-button": "إعادة ضبط",
      "thinker-title": "المُفكر",
      "planner-title": "المُخطط",
      "coder-title": "المُبرمج",
      "tester-title": "المُختبر",
      "deployer-title": "الناشر",
      "thinker-description": "يحلل فكرتك ويحدد متطلبات الموقع",
      "planner-description": "يضع خطة هيكلية للموقع ويختار التقنيات المناسبة",
      "coder-description": "يكتب كود الموقع بالكامل ويجهز الملفات",
      "tester-description": "يختبر الموقع ويتأكد من جودته وأدائه",
      "deployer-description": "يجهز الموقع للنشر ويوفر ملفات التنزيل",
      "download-button": "تنزيل الموقع",
      "preview-button": "معاينة الموقع",
      "thinking": "يفكر...",
      "planning": "يخطط...",
      "coding": "يكتب الكود...",
      "testing": "يختبر...",
      "deploying": "ينشر...",
      "waiting": "بانتظار الدور...",
      "completed": "اكتمل!",
      "api-key-button": "ضبط مفتاح API",
      "language-ar": "العربية",
      "language-en": "English",
      "generated-files": "الملفات المنشأة",
      "website-preview": "معاينة الموقع",
      "error-api-key": "مفتاح API مطلوب للمتابعة",
      "error-idea": "الرجاء إدخال فكرة الموقع للمتابعة",
      "loading": "جاري التحميل...",
      "file-structure": "بنية الملفات"
    }
  },
  en: {
    translation: {
      "app-title": "AI Website Builder",
      "app-description": "Enter your website idea, and let AI build it for you",
      "idea-placeholder": "Enter your website idea here... Example: I want a website to showcase handmade products",
      "api-key-placeholder": "Enter your API key here...",
      "api-key-info": "Requires Google's Gemini Pro API key",
      "start-button": "Start Building",
      "reset-button": "Reset",
      "thinker-title": "Thinker",
      "planner-title": "Planner",
      "coder-title": "Coder",
      "tester-title": "Tester",
      "deployer-title": "Deployer",
      "thinker-description": "Analyzes your idea and determines website requirements",
      "planner-description": "Creates website structure and selects appropriate technologies",
      "coder-description": "Writes the complete website code and prepares files",
      "tester-description": "Tests the website and ensures quality and performance",
      "deployer-description": "Prepares the website for deployment and provides download files",
      "download-button": "Download Website",
      "preview-button": "Preview Website",
      "thinking": "Thinking...",
      "planning": "Planning...",
      "coding": "Coding...",
      "testing": "Testing...",
      "deploying": "Deploying...",
      "waiting": "Waiting...",
      "completed": "Completed!",
      "api-key-button": "Set API Key",
      "language-ar": "العربية",
      "language-en": "English",
      "generated-files": "Generated Files",
      "website-preview": "Website Preview",
      "error-api-key": "API key is required to continue",
      "error-idea": "Please enter a website idea to continue",
      "loading": "Loading...",
      "file-structure": "File Structure"
    }
  }
};

// Initialize i18n
i18n
  .use(LanguageDetector)
  .use(initReactI18next)
  .init({
    resources,
    fallbackLng: "ar",
    detection: {
      order: ["localStorage", "navigator"],
      caches: ["localStorage"],
    },
    interpolation: {
      escapeValue: false
    }
  });

const BACKEND_URL = process.env.REACT_APP_BACKEND_URL;
const API = `${BACKEND_URL}/api`;

// Agent images from Unsplash
const agentImages = {
  thinker: "https://images.unsplash.com/photo-1617791160536-598cf32026fb",
  planner: "https://images.unsplash.com/photo-1532178324009-6b6adeca1741",
  coder: "https://images.unsplash.com/photo-1488590528505-98d2b5aba04b",
  tester: "https://images.unsplash.com/photo-1581090464777-f3220bbe1b8b",
  deployer: "https://images.unsplash.com/photo-1597733336794-12d05021d510"
};

// Agent animation states
const agentStates = {
  WAITING: "waiting",
  WORKING: "working",
  COMPLETED: "completed"
};

// Agent component
const Agent = ({ type, name, description, status, isActive, isCompleted }) => {
  const { t } = useTranslation();
  
  return (
    <motion.div 
      className={`agent-card ${isActive ? 'active' : ''} ${isCompleted ? 'completed' : ''}`}
      initial={{ opacity: 0, y: 20 }}
      animate={{ opacity: 1, y: 0 }}
      transition={{ duration: 0.5 }}
    >
      <div className="agent-avatar">
        <motion.div
          className="agent-image-container"
          animate={{ 
            scale: isActive ? [1, 1.05, 1] : 1,
            rotate: isActive ? [0, 2, -2, 0] : 0
          }}
          transition={{ 
            repeat: isActive ? Infinity : 0, 
            duration: isActive ? 3 : 0.5 
          }}
        >
          <img src={agentImages[type]} alt={t(name)} className="agent-image" />
          {isActive && (
            <div className="pulse-overlay"></div>
          )}
        </motion.div>
      </div>
      <div className="agent-info">
        <h3>{t(name)}</h3>
        <p className="agent-description">{t(description)}</p>
        <div className="agent-status">
          {isActive ? (
            <motion.div 
              className="status-indicator active"
              animate={{ scale: [1, 1.2, 1] }}
              transition={{ repeat: Infinity, duration: 1.5 }}
            >
              <span>{t(status)}</span>
            </motion.div>
          ) : isCompleted ? (
            <motion.div 
              className="status-indicator completed"
              initial={{ scale: 0 }}
              animate={{ scale: 1 }}
              transition={{ type: "spring", stiffness: 300, damping: 15 }}
            >
              <span>{t('completed')}</span>
            </motion.div>
          ) : (
            <div className="status-indicator waiting">
              <span>{t('waiting')}</span>
            </div>
          )}
        </div>
      </div>
    </motion.div>
  );
};

// Preview component
const Preview = ({ files, loading }) => {
  const { t } = useTranslation();
  const [selectedFile, setSelectedFile] = useState(null);
  
  useEffect(() => {
    if (files && files.length > 0) {
      setSelectedFile(files[0]);
    }
  }, [files]);

  if (loading) {
    return (
      <div className="preview-loading">
        <motion.div
          animate={{ rotate: 360 }}
          transition={{ repeat: Infinity, duration: 2, ease: "linear" }}
          className="loading-circle"
        />
        <p>{t('loading')}</p>
      </div>
    );
  }

  if (!files || files.length === 0) {
    return (
      <div className="preview-placeholder">
        <p>{t('website-preview')}</p>
      </div>
    );
  }

  return (
    <div className="preview-container">
      <div className="file-list">
        <h3>{t('file-structure')}</h3>
        <div className="file-tree">
          {files.map((file, index) => (
            <div 
              key={index} 
              className={`file-item ${selectedFile && selectedFile.name === file.name ? 'selected' : ''}`}
              onClick={() => setSelectedFile(file)}
            >
              {file.name}
            </div>
          ))}
        </div>
      </div>
      <div className="file-preview">
        {selectedFile && (
          <div className="file-content">
            <h3>{selectedFile.name}</h3>
            <pre>{selectedFile.content}</pre>
          </div>
        )}
      </div>
    </div>
  );
};

// Home Component
const Home = () => {
  const { t, i18n } = useTranslation();
  const [idea, setIdea] = useState("");
  const [apiKey, setApiKey] = useState(localStorage.getItem('geminiApiKey') || "");
  const [showApiKeyModal, setShowApiKeyModal] = useState(false);
  const [agentsStatus, setAgentsStatus] = useState({
    thinker: agentStates.WAITING,
    planner: agentStates.WAITING,
    coder: agentStates.WAITING,
    tester: agentStates.WAITING,
    deployer: agentStates.WAITING
  });
  const [activeAgent, setActiveAgent] = useState(null);
  const [completedAgents, setCompletedAgents] = useState([]);
  const [generatedFiles, setGeneratedFiles] = useState([]);
  const [websitePreview, setWebsitePreview] = useState(null);
  const [isBuilding, setIsBuilding] = useState(false);
  const [error, setError] = useState(null);
  const [buildProgress, setBuildProgress] = useState(0);
  const [currentLanguage, setCurrentLanguage] = useState(i18n.language);
  
  // API key handling
  const saveApiKey = () => {
    localStorage.setItem('geminiApiKey', apiKey);
    setShowApiKeyModal(false);
  };

  // Language switching
  const changeLanguage = (lng) => {
    i18n.changeLanguage(lng);
    setCurrentLanguage(lng);
  };

  // Reset everything
  const resetBuilder = () => {
    setActiveAgent(null);
    setCompletedAgents([]);
    setGeneratedFiles([]);
    setWebsitePreview(null);
    setIsBuilding(false);
    setError(null);
    setBuildProgress(0);
    setAgentsStatus({
      thinker: agentStates.WAITING,
      planner: agentStates.WAITING,
      coder: agentStates.WAITING,
      tester: agentStates.WAITING,
      deployer: agentStates.WAITING
    });
  };

  // Simulate an agent working process
  const simulateAgentWork = async (agent, duration) => {
    return new Promise((resolve) => {
      setActiveAgent(agent);
      setAgentsStatus(prev => ({ ...prev, [agent]: agentStates.WORKING }));
      
      setTimeout(() => {
        setAgentsStatus(prev => ({ ...prev, [agent]: agentStates.COMPLETED }));
        setCompletedAgents(prev => [...prev, agent]);
        setActiveAgent(null);
        resolve();
      }, duration);
    });
  };

  // Start the build process
  const startBuild = async () => {
    // Validate inputs
    if (!apiKey) {
      setError(t('error-api-key'));
      setShowApiKeyModal(true);
      return;
    }
    
    if (!idea.trim()) {
      setError(t('error-idea'));
      return;
    }
    
    setError(null);
    setIsBuilding(true);
    setBuildProgress(0);
    
    try {
      // Simulate Thinker agent
      await simulateAgentWork('thinker', 3000);
      setBuildProgress(20);
      
      // Make actual API call to analyze idea
      const analyzeResponse = await axios.post(`${API}/analyze-idea`, { 
        idea,
        api_key: apiKey
      });
      
      // Simulate Planner agent
      await simulateAgentWork('planner', 3000);
      setBuildProgress(40);
      
      // Make actual API call to plan website
      const planResponse = await axios.post(`${API}/plan-website`, {
        idea,
        analysis: analyzeResponse.data.analysis,
        api_key: apiKey
      });
      
      // Simulate Coder agent
      await simulateAgentWork('coder', 5000);
      setBuildProgress(60);
      
      // Make actual API call to generate code
      const codeResponse = await axios.post(`${API}/generate-code`, {
        idea,
        plan: planResponse.data.plan,
        api_key: apiKey
      });
      
      // Update generated files
      setGeneratedFiles(codeResponse.data.files);
      
      // Simulate Tester agent
      await simulateAgentWork('tester', 3000);
      setBuildProgress(80);
      
      // Make actual API call to test website
      const testResponse = await axios.post(`${API}/test-website`, {
        files: codeResponse.data.files,
        api_key: apiKey
      });
      
      // Simulate Deployer agent
      await simulateAgentWork('deployer', 3000);
      setBuildProgress(100);
      
      // Make actual API call to prepare deployment
      const deployResponse = await axios.post(`${API}/prepare-deployment`, {
        files: codeResponse.data.files,
        test_results: testResponse.data.test_results,
        api_key: apiKey
      });
      
      // Set website preview URL if available
      if (deployResponse.data.preview_url) {
        setWebsitePreview(deployResponse.data.preview_url);
      }
      
    } catch (err) {
      console.error("Error in build process:", err);
      setError(err.response?.data?.message || "An error occurred during the build process");
    } finally {
      setIsBuilding(false);
    }
  };

  return (
    <div className={`app-container ${currentLanguage === 'ar' ? 'rtl' : 'ltr'}`}>
      <header className="app-header">
        <h1>{t('app-title')}</h1>
        <p>{t('app-description')}</p>
        
        <div className="language-selector">
          <button 
            onClick={() => changeLanguage('ar')} 
            className={currentLanguage === 'ar' ? 'active' : ''}
          >
            {t('language-ar')}
          </button>
          <button 
            onClick={() => changeLanguage('en')} 
            className={currentLanguage === 'en' ? 'active' : ''}
          >
            {t('language-en')}
          </button>
        </div>
      </header>
      
      <main className="app-main">
        <section className="idea-input-section">
          <div className="input-container">
            <textarea
              value={idea}
              onChange={(e) => setIdea(e.target.value)}
              placeholder={t('idea-placeholder')}
              disabled={isBuilding}
            />
            <div className="action-buttons">
              <button 
                className="api-key-button"
                onClick={() => setShowApiKeyModal(true)}
              >
                {t('api-key-button')}
              </button>
              <button 
                className="start-button"
                onClick={startBuild}
                disabled={isBuilding}
              >
                {t('start-button')}
              </button>
              <button 
                className="reset-button"
                onClick={resetBuilder}
                disabled={isBuilding}
              >
                {t('reset-button')}
              </button>
            </div>
            {error && <div className="error-message">{error}</div>}
          </div>
        </section>
        
        <section className="agents-section">
          <h2>AI Agents</h2>
          <div className="agents-container">
            <Agent 
              type="thinker"
              name="thinker-title"
              description="thinker-description"
              status="thinking"
              isActive={activeAgent === 'thinker'}
              isCompleted={completedAgents.includes('thinker')}
            />
            <Agent 
              type="planner"
              name="planner-title"
              description="planner-description"
              status="planning"
              isActive={activeAgent === 'planner'}
              isCompleted={completedAgents.includes('planner')}
            />
            <Agent 
              type="coder"
              name="coder-title"
              description="coder-description"
              status="coding"
              isActive={activeAgent === 'coder'}
              isCompleted={completedAgents.includes('coder')}
            />
            <Agent 
              type="tester"
              name="tester-title"
              description="tester-description"
              status="testing"
              isActive={activeAgent === 'tester'}
              isCompleted={completedAgents.includes('tester')}
            />
            <Agent 
              type="deployer"
              name="deployer-title"
              description="deployer-description"
              status="deploying"
              isActive={activeAgent === 'deployer'}
              isCompleted={completedAgents.includes('deployer')}
            />
          </div>
          
          {isBuilding && (
            <div className="progress-bar-container">
              <div 
                className="progress-bar" 
                style={{ width: `${buildProgress}%` }}
              ></div>
            </div>
          )}
        </section>
        
        <section className="preview-section">
          <h2>{t('generated-files')}</h2>
          <Preview files={generatedFiles} loading={isBuilding && completedAgents.includes('coder')} />
          
          {websitePreview && (
            <div className="website-preview-container">
              <h2>{t('website-preview')}</h2>
              <iframe 
                src={websitePreview} 
                title="Website Preview" 
                className="website-preview-iframe"
              />
            </div>
          )}
          
          {completedAgents.includes('deployer') && (
            <div className="download-section">
              <button className="download-button">
                {t('download-button')}
              </button>
            </div>
          )}
        </section>
      </main>
      
      {/* API Key Modal */}
      <AnimatePresence>
        {showApiKeyModal && (
          <motion.div 
            className="modal-overlay"
            initial={{ opacity: 0 }}
            animate={{ opacity: 1 }}
            exit={{ opacity: 0 }}
          >
            <motion.div 
              className="modal-content"
              initial={{ scale: 0.8, opacity: 0 }}
              animate={{ scale: 1, opacity: 1 }}
              exit={{ scale: 0.8, opacity: 0 }}
              transition={{ type: "spring", stiffness: 300, damping: 25 }}
            >
              <h2>{t('api-key-button')}</h2>
              <p>{t('api-key-info')}</p>
              <input 
                type="text" 
                value={apiKey} 
                onChange={(e) => setApiKey(e.target.value)}
                placeholder={t('api-key-placeholder')}
              />
              <div className="modal-buttons">
                <button onClick={() => setShowApiKeyModal(false)}>
                  {t('reset-button')}
                </button>
                <button onClick={saveApiKey} className="primary">
                  {t('api-key-button')}
                </button>
              </div>
            </motion.div>
          </motion.div>
        )}
      </AnimatePresence>
    </div>
  );
};

function App() {
  return (
    <BrowserRouter>
      <Routes>
        <Route path="/" element={<Home />} />
      </Routes>
    </BrowserRouter>
  );
}

export default App;
      