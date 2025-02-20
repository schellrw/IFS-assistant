// App.js - Main application component
import React, { useState, useEffect } from 'react';
import { BrowserRouter as Router, Routes, Route, Navigate } from 'react-router-dom';
import { 
  Dashboard,
  PartDetail, 
  SystemMap, 
  JournalPage,
  NewPartForm,
  Login,
  Settings
} from './pages';
import { Navbar, Sidebar } from './components';
import { IFSProvider } from './context/IFSContext';
import { AuthProvider, useAuth } from './context/AuthContext';
import './App.css';

const ProtectedRoute = ({ children }) => {
  const { currentUser, loading } = useAuth();
  
  if (loading) return <div className="loading-container">Loading...</div>;
  
  if (!currentUser) {
    return <Navigate to="/login" />;
  }
  
  return children;
};

function App() {
  return (
    <AuthProvider>
      <IFSProvider>
        <Router>
          <div className="app-container">
            <Routes>
              <Route path="/login" element={<Login />} />
              <Route path="/" element={
                <ProtectedRoute>
                  <Layout>
                    <Dashboard />
                  </Layout>
                </ProtectedRoute>
              } />
              <Route path="/parts/:partId" element={
                <ProtectedRoute>
                  <Layout>
                    <PartDetail />
                  </Layout>
                </ProtectedRoute>
              } />
              <Route path="/system-map" element={
                <ProtectedRoute>
                  <Layout>
                    <SystemMap />
                  </Layout>
                </ProtectedRoute>
              } />
              <Route path="/journal" element={
                <ProtectedRoute>
                  <Layout>
                    <JournalPage />
                  </Layout>
                </ProtectedRoute>
              } />
              <Route path="/new-part" element={
                <ProtectedRoute>
                  <Layout>
                    <NewPartForm />
                  </Layout>
                </ProtectedRoute>
              } />
              <Route path="/settings" element={
                <ProtectedRoute>
                  <Layout>
                    <Settings />
                  </Layout>
                </ProtectedRoute>
              } />
            </Routes>
          </div>
        </Router>
      </IFSProvider>
    </AuthProvider>
  );
}

const Layout = ({ children }) => {
  return (
    <>
      <Navbar />
      <div className="content-container">
        <Sidebar />
        <main className="main-content">
          {children}
        </main>
      </div>
    </>
  );
};

export default App;

// context/IFSContext.js - Context for IFS system data
import React, { createContext, useContext, useState, useEffect } from 'react';
import { useAuth } from './AuthContext';
import { db } from '../firebase';
import { doc, getDoc, setDoc, updateDoc } from 'firebase/firestore';

const IFSContext = createContext();

export const useIFS = () => useContext(IFSContext);

export const IFSProvider = ({ children }) => {
  const { currentUser } = useAuth();
  const [system, setSystem] = useState(null);
  const [loading, setLoading] = useState(true);
  const [abstractionLevel, setAbstractionLevel] = useState('mixed');
  
  useEffect(() => {
    const loadSystem = async () => {
      if (!currentUser) {
        setSystem(null);
        setLoading(false);
        return;
      }
      
      try {
        const docRef = doc(db, "userSystems", currentUser.uid);
        const docSnap = await getDoc(docRef);
        
        if (docSnap.exists()) {
          const systemData = docSnap.data();
          setSystem(systemData);
          setAbstractionLevel(systemData.abstractionLevel || 'mixed');
        } else {
          // Create new system if none exists
          const newSystem = {
            userId: currentUser.uid,
            parts: {
              'self-part': {
                id: 'self-part',
                name: 'Self',
                role: 'Self',
                description: 'The compassionate core consciousness',
                feelings: ['calm', 'curious', 'compassionate'],
                beliefs: [],
                triggers: [],
                needs: [],
                createdAt: new Date().toISOString(),
                updatedAt: new Date().toISOString()
              }
            },
            relationships: {},
            journals: {},
            createdAt: new Date().toISOString(),
            abstractionLevel: 'mixed'
          };
          
          await setDoc(docRef, newSystem);
          setSystem(newSystem);
        }
      } catch (error) {
        console.error("Error loading system:", error);
      } finally {
        setLoading(false);
      }
    };
    
    loadSystem();
  }, [currentUser]);
  
  const addPart = async (part) => {
    if (!currentUser) return null;
    
    try {
      const docRef = doc(db, "userSystems", currentUser.uid);
      const updatedParts = { ...system.parts, [part.id]: part };
      
      await updateDoc(docRef, {
        parts: updatedParts
      });
      
      setSystem({
        ...system,
        parts: updatedParts
      });
      
      return part.id;
    } catch (error) {
      console.error("Error adding part:", error);
      return null;
    }
  };
  
  const updatePart = async (partId, updates) => {
    if (!currentUser || !system.parts[partId]) return false;
    
    try {
      const part = system.parts[partId];
      const updatedPart = {
        ...part,
        ...updates,
        updatedAt: new Date().toISOString()
      };
      
      const docRef = doc(db, "userSystems", currentUser.uid);
      await updateDoc(docRef, {
        [`parts.${partId}`]: updatedPart
      });
      
      setSystem({
        ...system,
        parts: {
          ...system.parts,
          [partId]: updatedPart
        }
      });
      
      return true;
    } catch (error) {
      console.error("Error updating part:", error);
      return false;
    }
  };
  
  const addRelationship = async (relationship) => {
    if (!currentUser) return null;
    
    try {
      const docRef = doc(db, "userSystems", currentUser.uid);
      const updatedRelationships = { 
        ...system.relationships, 
        [relationship.id]: relationship 
      };
      
      await updateDoc(docRef, {
        relationships: updatedRelationships
      });
      
      setSystem({
        ...system,
        relationships: updatedRelationships
      });
      
      return relationship.id;
    } catch (error) {
      console.error("Error adding relationship:", error);
      return null;
    }
  };
  
  const addJournal = async (journal) => {
    if (!currentUser) return null;
    
    try {
      const docRef = doc(db, "userSystems", currentUser.uid);
      const updatedJournals = { 
        ...system.journals, 
        [journal.id]: journal 
      };
      
      await updateDoc(docRef, {
        journals: updatedJournals
      });
      
      setSystem({
        ...system,
        journals: updatedJournals
      });
      
      return journal.id;
    } catch (error) {
      console.error("Error adding journal:", error);
      return null;
    }
  };
  
  const updateAbstractionLevel = async (level) => {
    if (!currentUser) return false;
    
    try {
      const docRef = doc(db, "userSystems", currentUser.uid);
      await updateDoc(docRef, {
        abstractionLevel: level
      });
      
      setSystem({
        ...system,
        abstractionLevel: level
      });
      
      setAbstractionLevel(level);
      return true;
    } catch (error) {
      console.error("Error updating abstraction level:", error);
      return false;
    }
  };
  
  const value = {
    system,
    loading,
    abstractionLevel,
    addPart,
    updatePart,
    addRelationship,
    addJournal,
    updateAbstractionLevel
  };
  
  return (
    <IFSContext.Provider value={value}>
      {children}
    </IFSContext.Provider>
  );
};

// components/SystemMapVisualization.js - D3-based visualization component
import React, { useEffect, useRef } from 'react';
import * as d3 from 'd3';
import { useIFS } from '../context/IFSContext';

const SystemMapVisualization = () => {
  const { system } = useIFS();
  const svgRef = useRef(null);
  
  useEffect(() => {
    if (!system || !svgRef.current) return;
    
    // Clear previous visualization
    d3.select(svgRef.current).selectAll("*").remove();
    
    // Convert system data to D3 format
    const nodes = Object.values(system.parts).map(part => ({
      id: part.id,
      name: part.name,
      role: part.role || 'Undefined',
      description: part.description
    }));
    
    const links = Object.values(system.relationships).map(rel => ({
      source: rel.sourceId,
      target: rel.targetId,
      type: rel.relationshipType,
      description: rel.description
    }));
    
    // Define color scheme
    const roleColors = {
      "Self": "#4CAF50",
      "Protector": "#2196F3",
      "Manager": "#9C27B0",
      "Firefighter": "#F44336",
      "Exile": "#FF9800",
      "Undefined": "#9E9E9E"
    };
    
    // Setup SVG
    const width = 800;
    const height = 600;
    const svg = d3.select(svgRef.current)
      .attr("viewBox", `0 0 ${width} ${height}`)
      .attr("width", "100%")
      .attr("height", "100%");
      
    // Create simulation
    const simulation = d3.forceSimulation(nodes)
      .force("link", d3.forceLink(links).id(d => d.id).distance(150))
      .force("charge", d3.forceManyBody().strength(-400))
      .force("center", d3.forceCenter(width / 2, height / 2))
      .force("collision", d3.forceCollide().radius(70));
    
    // Add links
    const link = svg.append("g")
      .selectAll("line")
      .data(links)
      .enter()
      .append("line")
      .attr("stroke", "#999")
      .attr("stroke-opacity", 0.6)
      .attr("stroke-width", 2);
      
    // Add link text
    const linkText = svg.append("g")
      .selectAll("text")
      .data(links)
      .enter()
      .append("text")
      .text(d => d.type)
      .attr("font-size", "10px")
      .attr("text-anchor", "middle")
      .attr("dy", -5);
      
    // Add nodes
    const node = svg.append("g")
      .selectAll("circle")
      .data(nodes)
      .enter()
      .append("circle")
      .attr("r", d => d.role === "Self" ? 30 : 20)
      .attr("fill", d => roleColors[d.role] || roleColors["Undefined"])
      .attr("stroke", "#fff")
      .attr("stroke-width", 2)
      .call(drag(simulation));
      
    // Add node labels
    const nodeText = svg.append("g")
      .selectAll("text")
      .data(nodes)
      .enter()
      .append("text")
      .text(d => d.name)
      .attr("font-size", "12px")
      .attr("text-anchor", "middle")
      .attr("dy", 30);
    
    // Add tooltips
    node.append("title")
      .text(d => `${d.name} (${d.role})\n${d.description}`);
    
    // Setup simulation tick
    simulation.on("tick", () => {
      // Update link positions
      link
        .attr("x1", d => d.source.x)
        .attr("y1", d => d.source.y)
        .attr("x2", d => d.target.x)
        .attr("y2", d => d.target.y);
      
      // Update link text positions
      linkText
        .attr("x", d => (d.source.x + d.target.x) / 2)
        .attr("y", d => (d.source.y + d.target.y) / 2);
      
      // Update node positions
      node
        .attr("cx", d => d.x = Math.max(30, Math.min(width - 30, d.x)))
        .attr("cy", d => d.y = Math.max(30, Math.min(height - 30, d.y)));
      
      // Update node text positions
      nodeText
        .attr("x", d => d.x)
        .attr("y", d => d.y);
    });
    
    // Drag functions
    function drag(simulation) {
      function dragstarted(event) {
        if (!event.active) simulation.alphaTarget(0.3).restart();
        event.subject.fx = event.subject.x;
        event.subject.fy = event.subject.y;
      }
      
      function dragged(event) {
        event.subject.fx = event.x;
        event.subject.fy = event.y;
      }
      
      function dragended(event) {
        if (!event.active) simulation.alphaTarget(0);
        event.subject.fx = null;
        event.subject.fy = null;
      }
      
      return d3.drag()
        .on("start", dragstarted)
        .on("drag", dragged)
        .on("end", dragended);
    }
    
    // Add legend
    const legend = svg.append("g")
      .attr("transform", `translate(${width - 150}, 20)`);
      
    Object.entries(roleColors).forEach(([role, color], i) => {
      legend.append("circle")
        .attr("cx", 10)
        .attr("cy", i * 25 + 10)
        .attr("r", 7)
        .attr("fill", color);
        
      legend.append("text")
        .attr("x", 25)
        .attr("y", i * 25 + 15)
        .text(role)
        .attr("font-size", "12px");
    });
    
    // Cleanup
    return () => {
      simulation.stop();
    };
  }, [system]);
  
  return (
    <div className="system-map-container">
      <svg ref={svgRef} className="system-map-svg"></svg>
    </div>
  );
};

export default SystemMapVisualization;

// pages/JournalPage.js - Journal page with sentiment analysis
import React, { useState } from 'react';
import { useIFS } from '../context/IFSContext';
import { v4 as uuidv4 } from 'uuid';
import { EmotionPicker, PartSelector, ReflectivePrompt } from '../components';

const JournalPage = () => {
  const { system, addJournal } = useIFS();
  const [content, setContent] = useState('');
  const [selectedEmotions, setSelectedEmotions] = useState([]);
  const [selectedParts, setSelectedParts] = useState([]);
  const [insights, setInsights] = useState([]);
  const [analysis, setAnalysis] = useState(null);
  const [usePrompt, setUsePrompt] = useState(false);
  const [currentPrompt, setCurrentPrompt] = useState('');
  
  const commonEmotions = [
    { id: 'angry', label: 'Angry', color: '#F44336' },
    { id: 'sad', label: 'Sad', color: '#2196F3' },
    { id: 'afraid', label: 'Afraid', color: '#FFC107' },
    { id: 'ashamed', label: 'Ashamed', color: '#9C27B0' },
    { id: 'peaceful', label: 'Peaceful', color: '#4CAF50' },
    { id: 'joyful', label: 'Joyful', color: '#FF9800' },
    { id: 'anxious', label: 'Anxious', color: '#795548' },
    { id: 'curious', label: 'Curious', color: '#607D8B' },
    { id: 'confused', label: 'Confused', color: '#9E9E9E' },
    { id: 'overwhelmed', label: 'Overwhelmed', color: '#FF5722' }
  ];
  
  const reflectivePrompts = [
    "How are you feeling in your body right now?",
    "What parts of you are most active today?",
    "When you sit with this feeling, what images or memories arise?",
    "If this emotion had a voice, what would it say?",
    "What does this part of you need right now?",
    "How would your Self view this situation?",
    "Is there a part that feels reluctant to be seen or heard?"
  ];
  
  const handleNewPrompt = () => {
    const randomPrompt = reflectivePrompts[Math.floor(Math.random() * reflectivePrompts.length)];
    setCurrentPrompt(randomPrompt);
    setUsePrompt(true);
  };
  
  const handleSkipPrompt = () => {
    setUsePrompt(false);
    setCurrentPrompt('');
  };
  
  const handleAnalyzeJournal = async () => {
    // In a real implementation, this would call your backend API with LLM integration
    // For now, we'll simulate a simple analysis
    
    const simulatedAnalysis = {
      identifiedEmotions: selectedEmotions,
      potentialParts: selectedParts,
      insights: []
    };
    
    // Simple pattern matching
    const patterns = [
      { regex: /part of me feels (\w+)/i, label: "Potential part feeling" },
      { regex: /I notice ([\w\s]+) inside/i, label: "Internal experience" },
      { regex: /whenever I ([\w\s]+), I feel ([\w\s]+)/i, label: "Trigger pattern" }
    ];
    
    patterns.forEach(pattern => {
      const matches = [...content.matchAll(pattern.regex)];
      matches.forEach(match => {
        simulatedAnalysis.insights.push({
          type: pattern.label,
          text: match[0],
          excerpt: match[1]
        });
      });
    });
    
    setAnalysis(simulatedAnalysis);
  };
  
  const handleSaveJournal = async () => {
    if (!content.trim()) return;
    
    const newJournal = {
      id: uuidv4(),
      content,
      partsPresent: selectedParts,
      emotions: selectedEmotions,
      insights: insights.filter(i => i.trim() !== ''),
      createdAt: new Date().toISOString()
    };
    
    await addJournal(newJournal);
    
    // Reset form
    setContent('');
    setSelectedEmotions([]);
    setSelectedParts([]);
    setInsights([]);
    setAnalysis(null);
    setUsePrompt(false);
    setCurrentPrompt('');
  };
  
  const handleAddInsight = (e) => {
    if (e.key === 'Enter' && e.target.value.trim() !== '') {
      setInsights([...insights, e.target.value]);
      e.target.value = '';
    }
  };
  
  return (
    <div className="journal-page">
      <h1>Journal Entry</h1>
      
      {!usePrompt ? (
        <div className="prompt-controls">
          <button onClick={handleNewPrompt} className="prompt-button">
            Use a reflective prompt
          </button>
        </div>
      ) : (
        <div className="active-prompt">
          <ReflectivePrompt text={currentPrompt} />
          <button onClick={handleSkipPrompt} className="skip-prompt">
            Skip prompt
          </button>
        </div>
      )}
      
      <div className="journal-editor">
        <textarea
          value={content}
          onChange={(e) => setContent(e.target.value)}
          placeholder={usePrompt ? "Reflect on the prompt above..." : "Write your journal entry here..."}
          rows={10}
          className="journal-textarea"
        />
      </div>
      
      <div className="journal-metadata">
        <div className="emotion-section">
          <h3>How are you feeling?</h3>
          <EmotionPicker
            emotions={commonEmotions}
            selectedEmotions={selectedEmotions}
            onChange={setSelectedEmotions}
          />
        </div>
        
        <div className="parts-section">
          <h3>Parts present</h3>
          <PartSelector
            parts={Object.values(system?.parts || {})}
            selectedParts={selectedParts}
            onChange={setSelectedParts}
          />
        </div>
      </div>
      
      <div className="journal-actions">
        <button onClick={handleAnalyzeJournal} className="analyze-button">
          Analyze Entry
        </button>
        <button onClick={handleSaveJournal} className="save-button">
          Save Journal
        </button>
      </div>
      
      {analysis && (
        <div className="journal-analysis">
          <h3>Journal Analysis</h3>
          
          {analysis.insights.length > 0 && (
            <div className="analysis-insights">
              <h4>Potential Insights</h4>
              <ul>
                {analysis.insights.map((insight, index) => (
                  <li key={index} className="insight-item">
                    <strong>{insight.type}:</strong> {insight.text}
                  </li>
                ))}
              </ul>
            </div>
          )}
          
          <div className="your-insights">
            <h4>Add your own insights</h4>
            <input
              type="text"
              placeholder="Type an insight and press Enter"
              onKeyDown={handleAddInsight}
              className="insight-input"
            />
            
            {insights.length > 0 && (
              <ul className="insights-list">
                {insights.map((insight, index) => (
                  <li key={index}>{insight}</li>
                ))}
              </ul>
            )}
          </div>
        </div>
      )}
    </div>
  );
};

export default JournalPage;

// components/NewPartForm.js - Form for creating a new part with guided experience
import React, { useState } from 'react';
import { useNavigate } from 'react-router-dom';
import { useIFS } from '../context/IFSContext';
import { v4 as uuidv4 } from 'uuid';
import { InputField, TextArea, RoleSelector, FeelingsInput } from './FormComponents';

const NewPartForm = () => {
  const { abstractionLevel, addPart } = useIFS();
  const navigate = useNavigate();
  
  const [step, setStep] = useState(1);
  const [partData, setPartData] = useState({
    id: uuidv4(),
    name: '',
    role: '',
    description: '',
    feelings: [],
    beliefs: [],
    triggers: [],
    needs: [],
    createdAt: new Date().toISOString(),
    updatedAt: new Date().toISOString()
  });
  
  const handleInputChange = (field, value) => {
    setPartData({
      ...partData,
      [field]: value
    });
  };
  
  const getPromptText = (field) => {
    // Adapt language based on user's conceptual understanding
    if (abstractionLevel === 'abstract') {
      switch (field) {
        case 'name':
          return "What would you call this aspect of yourself?";
        case 'description':
          return "How would you describe what this aspect represents in your life?";
        case 'role':
          return "If you had to categorize this aspect, what might fit best?";
        case 'feelings':
          return "What emotions or sensations are associated with this aspect?";
        case 'beliefs':
          return "What core beliefs might this aspect hold?";
        case 'triggers':
          return "What situations tend to activate this aspect of yourself?";
        case 'needs':
          return "What might this aspect be seeking or needing?";
        default:
          return "";
      }
    } else if (abstractionLevel === 'concrete') {
      switch (field) {
        case 'name':
          return "What name would you give this part?";
        case 'description':
          return "What does this part look like? How does it feel in your body?";
        case 'role':
          return "What role does this part have in your system?";
        case 'feelings':
          return "What specific emotions does this part carry?";
        case 'beliefs':
          return "What does this part believe about you or the world?";
        case 'triggers':
          return "What situations cause this part to get activated?";
        case 'needs':
          return "What does this part need to feel safe?";
        default:
          return "";
      }
    } else {
      // Mixed/balanced approach
      switch (field) {
        case 'name':
          return "What would you like to call this part?";
        case 'description':
          return "Tell me about this part - what it feels like, what it cares about:";
        case 'role':
          return "What role might this part have in your system?";
        case 'feelings':
          return "What emotions or feelings does this part carry?";
        case 'beliefs':
          return "What beliefs or thoughts are associated with this part?";
        case 'triggers':
          return "When does this part tend to show up?";
        case 'needs':
          return "What might this part need from you?";
        default:
          return "";
      }
    }
  };
  
  const handleNext = () => {
    if (step < 4) {
      setStep(step + 1);
    } else {
      handleSubmit();
    }
  };
  
  const handleBack = () => {
    if (step > 1) {
      setStep(step - 1);
    }
  };
  
  const handleSubmit = async () => {
    await addPart(partData);
    navigate(`/parts/${partData.id}`);
  };
  
  const roleOptions = [
    { value: 'Manager', label: 'Manager', description: 'Proactive protector that tries to keep the system functioning' },
    { value: 'Firefighter', label: 'Firefighter', description: 'Reactive protector that activates when exiles are triggered' },
    { value: 'Exile', label: 'Exile', description: 'Carries pain, trauma, or vulnerability' },
    { value: 'Protector', label: 'Protector', description: 'General protective part' },
    { value: 'Other', label: 'Other', description: 'Another type of part' }
  ];
  
  return (
    <div className="new-part-form">
      <h2>Create New Part</h2>
      
      <div className="form-progress">
        <div className={`progress-step ${step >= 1 ? 'active' : ''}`}>1</div>
        <div className="progress-line"></div>
        <div className={`progress-step ${step >= 2 ? 'active' : ''}`}>2</div>
        <div className="progress-line"></div>
        <div className={`progress-step ${step >= 3 ? 'active' : ''}`}>3</div>
        <div className="progress-line"></div>
        <div className={`progress-step ${step >= 4 ? 'active' : ''}`}>4</div>
      </div>
      
      {step === 1 && (
        <div className="form-step">
          <h3>Identity</h3>
          
          <InputField
            label={getPromptText('name')}
            value={partData.name}
            onChange={(value) => handleInputChange('name', value)}
            required
          />
          
          <TextArea
            label={getPromptText('description')}
            value={partData.description}
            onChange={(value) => handleInputChange('description', value)}
            rows={4}
          />
          
          <RoleSelector
            label={getPromptText('role')}
            options={roleOptions}
            value={partData.role}
            onChange={(value) => handleInputChange('role', value)}
            abstractionLevel={abstractionLevel}
          />
        </div>
      )}
      
      {step === 2 && (
        <div className="form-step">
          <h3>Emotional Experience</h3>
          
          <FeelingsInput
            label={getPromptText('feelings')}
            value={partData.feelings}
            onChange={(value) => handleInputChange('feelings', value)}
          />
          
          <div className="guided-experience">
            <h4>Connecting with this part</h4>
            <p>Take a moment to close your eyes and try to sense this part in your body. Where do you feel it? What sensations arise?</p>
            
            <TextArea
              label="What do you notice in your body? (optional)"
              value={partData.bodyExperience || ''}
              onChange={(value) => handleInputChange('bodyExperience', value)}
              rows={3}
            />
          </div>
        </div>
      )}
      
      {step === 3 && (
        <div className="form-step">
          <h3>Beliefs & Triggers</h3>
          
          <TextArea
            label={getPromptText('beliefs')}
            value={partData.beliefs.join('\n')}
            onChange={(value) => handleInputChange('beliefs', value.split('\n').filter(b => b.trim() !== ''))}
            placeholder="Enter one belief per line"
            rows={4}
          />
          
          <TextArea
            label={getPromptText('triggers')}
            value={partData.triggers.join('\n')}
            onChange={(value) => handleInputChange('triggers', value.split('\n').filter(t => t.trim() !== ''))}
            placeholder="Enter one trigger per line"
            rows={4}
          />
        </div>
      )}
      
      {step === 4 && (
        <div className="form-step">
          <h3>Needs & Connection</h3>
          
          <TextArea
            label={getPromptText('needs')}
            value={partData.needs.join('\n')}
            onChange={(value) => handleInputChange('needs', value.split('\n').filter(n => n.trim() !== ''))}