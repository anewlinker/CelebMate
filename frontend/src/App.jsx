import { useState, useEffect, useRef } from 'react'
import './index.css'

const API_URL = 'http://localhost:8000'

function App() {
  const [events, setEvents] = useState({ birthdays: [], promotions: [] })
  const [loading, setLoading] = useState(true)
  const [generating, setGenerating] = useState({}) // object for multiple queue
  const [resultImages, setResultImages] = useState({})
  const [messages, setMessages] = useState({})
  const [eventTypes, setEventTypes] = useState({})
  const [customEventTypes, setCustomEventTypes] = useState({})
  
  // Settings
  const [apiKey, setApiKey] = useState(localStorage.getItem('openai_api_key') || '')
  const [showSettings, setShowSettings] = useState(false)
  const [activeInfo, setActiveInfo] = useState(null)
  
  // Refs for file uploads
  const rosterRef = useRef(null)
  const photoRef = useRef(null)

  useEffect(() => {
    fetchEvents()
  }, [])

  const fetchEvents = async () => {
    try {
      const res = await fetch(`${API_URL}/api/events`)
      const data = await res.json()
      setEvents(data)
      setLoading(false)
      const initialMsgs = {}
      const initialTypes = {}
      if (data.all_members) {
        data.all_members.forEach(e => {
            if (e.defaultType === '생일') {
                initialMsgs[e['성명']] = `${e['성명']}님, 생일을 진심으로 축하합니다!\n오늘 하루 세상에서 가장 행복하게 보내세요 🎉`
                initialTypes[e['성명']] = '생일'
            } else if (e.defaultType === '승진') {
                initialMsgs[e['성명']] = `${e['성명']}님, 승진을 축하드립니다!\n앞으로의 멋진 활약을 기대하고 응원합니다 ✨`
                initialTypes[e['성명']] = '승진'
            } else {
                initialMsgs[e['성명']] = `${e['성명']}님, 기념일을 축하합니다!`
                initialTypes[e['성명']] = e.defaultType || '생일'
            }
        })
      }
      setMessages(initialMsgs)
      setEventTypes(initialTypes)
    } catch (err) {
      console.error("Failed to fetch events", err)
      setLoading(false)
    }
  }

  const handleGenerate = async (memberName, memberRank) => {
    setGenerating(prev => ({...prev, [memberName]: '생성중...'}))
    
    // Fallback if message is empty
    const currentEvent = eventTypes[memberName] || '생일'
    const fallbackMessage = `${memberName}님, ${currentEvent}을 진심으로 축하합니다!`
    
    try {
      const res = await fetch(`${API_URL}/api/generate`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
          member_name: memberName,
          member_rank: memberRank,
          message: messages[memberName] || fallbackMessage,
          event_type: currentEvent === 'custom' ? '축하' : currentEvent
        })
      })
      const data = await res.json()
      if (data.success) {
        setResultImages(prev => ({
          ...prev, 
          [memberName]: data.filenames.map(fn => `${API_URL}/images/${fn}?t=${new Date().getTime()}`)
        }))
      } else {
        alert(`[${memberName}] 포스터 생성 실패 (백엔드 에러)`)
      }
    } catch (err) {
      console.error("Failed to generate", err)
      alert(`[${memberName}] 포스터 생성에 실패했습니다.`)
    }
    setGenerating(prev => {
      const next = {...prev}
      delete next[memberName]
      return next
    })
  }

  const handleGenerateAll = async () => {
    if (allEvents.length === 0) return
    
    // Set all to queued
    const queued = {}
    allEvents.forEach(e => { queued[e['성명']] = '대기중...' })
    setGenerating(queued)
    
    for (const ev of allEvents) {
      await handleGenerate(ev['성명'], ev['직급'])
    }
  }

  const handleGenerateAIMessage = async (memberName, memberRank, overrideEventType = null) => {
    if (!apiKey) {
      alert("설정(⚙️)에서 OpenAI API Key를 먼저 입력해주세요!")
      return
    }
    
    // Set a temporary loading message
    setMessages(prev => ({ ...prev, [memberName]: "AI가 센스있는 멘트를 고민 중입니다... 💭" }))
    
    const currentType = overrideEventType || eventTypes[memberName] || '생일'
    const finalType = currentType === 'custom' ? '특별한 이벤트' : currentType
    
    try {
      const res = await fetch(`${API_URL}/api/generate_message`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
          member_name: memberName,
          member_rank: memberRank,
          event_type: finalType,
          custom_prompt: currentType === 'custom' ? customEventTypes[memberName] : '',
          api_key: apiKey
        })
      })
      const data = await res.json()
      if (data.success) {
        setMessages(prev => ({ ...prev, [memberName]: data.message }))
      } else {
        setMessages(prev => ({ ...prev, [memberName]: "생성 실패. 직접 입력해주세요." }))
      }
    } catch (err) {
      console.error("Failed to get AI message", err)
      setMessages(prev => ({ ...prev, [memberName]: "네트워크 오류 발생." }))
    }
  }

  const handleUploadRoster = async (e) => {
    const file = e.target.files[0]
    if (!file) return
    const formData = new FormData()
    formData.append('file', file)
    
    try {
      const res = await fetch(`${API_URL}/api/upload/roster`, {
        method: 'POST',
        body: formData
      })
      const data = await res.json()
      if (data.success) {
        alert(data.message)
        fetchEvents() // Reload events
      }
    } catch (err) {
      alert("명부 업로드 실패")
    }
  }

  const handleUploadPhotos = async (e) => {
    const files = e.target.files
    if (!files || files.length === 0) return
    const formData = new FormData()
    for (let i = 0; i < files.length; i++) {
        formData.append('files', files[i])
    }
    
    try {
      const res = await fetch(`${API_URL}/api/upload/photos`, {
        method: 'POST',
        body: formData
      })
      const data = await res.json()
      if (data.success) {
        alert(data.message)
        if (photoRef.current) photoRef.current.value = ''
      }
    } catch (err) {
      alert("사진 업로드 실패")
    }
  }

  const saveApiKey = (key) => {
    setApiKey(key)
    localStorage.setItem('openai_api_key', key)
  }

  const allEvents = events.all_members || []

  return (
    <div className="app-container">
      <header>
        <div style={{display: 'flex', justifyContent: 'flex-end', width: '100%'}}>
          <button className="settings-btn" onClick={() => setShowSettings(!showSettings)}>⚙️ 설정 및 업로드</button>
        </div>
        <h1>CelebMate V2</h1>
        <p>상반신 누끼 합성과 AI 자동 멘트가 지원되는 프리미엄 포스터 메이커</p>
      </header>

      {showSettings && (
        <div className="glass-panel settings-panel">
          <div className="panel-title">환경 설정 및 데이터 업로드</div>
          
          <div className="settings-grid">
            <div className="setting-item">
              <label>OpenAI API Key (AI 멘트 자동 생성용)</label>
              <input 
                type="password" 
                value={apiKey} 
                onChange={(e) => saveApiKey(e.target.value)} 
                placeholder="sk-..." 
              />
              <small>키는 브라우저에만 안전하게 저장됩니다.</small>
            </div>
            
            <div className="setting-item">
              <label>엑셀 명부 업로드 (.xlsx)</label>
              <input type="file" accept=".xlsx" ref={rosterRef} onChange={handleUploadRoster} />
              <small>'성명', '생년월일', '현직급 임용일' 열이 포함되어야 합니다.</small>
            </div>
            
            <div className="setting-item">
              <label>구성원 다중 사진 업로드</label>
              <div style={{display: 'flex', gap: '10px'}}>
                <input type="file" accept="image/*" multiple ref={photoRef} onChange={handleUploadPhotos} />
              </div>
              <small>파일 이름을 '이름.jpg' 또는 '이름.png'로 하여 여러 장을 한 번에 업로드하세요.</small>
            </div>
          </div>
        </div>
      )}

      <div className="main-content">
        <div className="glass-panel">
          <div className="panel-title" style={{display: 'flex', justifyContent: 'space-between', alignItems: 'center'}}>
            <span>다가오는 이벤트 대상자</span>
            {allEvents.length > 0 && (
              <button onClick={handleGenerateAll} disabled={generating !== null}>
                전체 일괄 합성 🚀
              </button>
            )}
          </div>
          
          {loading ? (
            <div style={{textAlign: 'center', padding: '40px'}}><div className="loader"></div></div>
          ) : (
            <div className="event-list">
              {allEvents.length === 0 ? (
                <div className="preview-empty" style={{minHeight: '200px'}}>이번 달은 축하할 이벤트가 없습니다.</div>
              ) : (
                allEvents.map((ev, idx) => (
                  <div className="event-item" key={idx} style={{display: 'flex', flexDirection: 'column', gap: '15px', padding: '20px', background: 'white', borderRadius: '12px', boxShadow: '0 4px 15px rgba(0,0,0,0.05)'}}>
                    
                    {/* Single Line Input Area */}
                    <div style={{display: 'flex', flexDirection: 'row', alignItems: 'center', gap: '15px', width: '100%'}}>
                      <div className="event-info" style={{minWidth: '150px'}}>
                        <h3 style={{margin: '0 0 5px 0'}}>{ev['성명']} <span className="text-muted" style={{fontSize: '0.9rem'}}>{ev['직급']}</span></h3>
                        <div className="event-meta" style={{fontSize: '0.85rem'}}>D-{ev['D-Day']}</div>
                      </div>
                      
                      <div style={{display: 'flex', gap: '8px', minWidth: '130px'}}>
                        <select 
                          value={eventTypes[ev['성명']] || ev.defaultType}
                          onChange={(e) => {
                            const newType = e.target.value;
                            setEventTypes(prev => ({...prev, [ev['성명']]: newType}));
                            if (newType !== 'custom' && apiKey) {
                              handleGenerateAIMessage(ev['성명'], ev['직급'], newType);
                            }
                          }}
                          style={{padding: '8px', borderRadius: '6px', border: '1px solid #ddd'}}
                        >
                          <option value="생일">🎂 생일</option>
                          <option value="승진">📈 승진</option>
                          <option value="수상">🏆 수상</option>
                          <option value="환영">👋 환영</option>
                          <option value="custom">✏️ 직접 입력</option>
                        </select>
                        {(eventTypes[ev['성명']] === 'custom') && (
                          <input
                            type="text"
                            value={customEventTypes[ev['성명']] || ''}
                            onChange={(e) => setCustomEventTypes(prev => ({ ...prev, [ev['성명']]: e.target.value }))}
                            placeholder="이벤트명 (예: 결혼)"
                            style={{width: '100px', padding: '8px', borderRadius: '6px', border: '1px solid #ddd'}}
                          />
                        )}
                      </div>

                      <div style={{display: 'flex', flexDirection: 'row', flex: 1, gap: '10px', alignItems: 'center'}}>
                          <button className="ai-btn" onClick={() => handleGenerateAIMessage(ev['성명'], ev['직급'])} style={{padding: '8px 12px', whiteSpace: 'nowrap'}}>🪄 AI 멘트</button>
                          <input 
                            type="text"
                            value={messages[ev['성명']] || ''} 
                            onChange={(e) => setMessages(prev => ({ ...prev, [ev['성명']]: e.target.value }))}
                            placeholder="축하 멘트를 입력하세요 (1줄 권장)"
                            style={{flex: 1, padding: '10px', borderRadius: '6px', border: '1px solid #ddd'}}
                          />
                      </div>
                      
                      <div>
                          <button 
                            onClick={() => handleGenerate(ev['성명'], ev['직급'])}
                            disabled={!!generating[ev['성명']]}
                            style={{padding: '10px 20px', whiteSpace: 'nowrap', fontWeight: 'bold'}}
                          >
                            {generating[ev['성명']] ? generating[ev['성명']] : '🎨 4종 포스터 생성'}
                          </button>
                      </div>
                    </div>

                    {/* 3 Images Preview Area */}
                    {resultImages[ev['성명']] && resultImages[ev['성명']].length > 0 && (
                      <div style={{display: 'flex', flexDirection: 'row', gap: '15px', marginTop: '10px', overflowX: 'auto', padding: '15px', background: '#f8f9fa', borderRadius: '10px'}}>
                        {resultImages[ev['성명']].map((imgUrl, i) => (
                           <div key={i} style={{flex: 1, display: 'flex', flexDirection: 'column', alignItems: 'center', gap: '10px'}}>
                             <img src={imgUrl} style={{width: '100%', maxHeight: '350px', objectFit: 'contain', borderRadius: '8px', border: '1px solid #eaeaea', boxShadow: '0 4px 12px rgba(0,0,0,0.08)'}} alt={`Style ${i+1}`} />
                             <button 
                               className="download-btn"
                               style={{width: '100%', padding: '8px', fontSize: '0.9rem'}}
                               onClick={() => {
                                 const a = document.createElement('a');
                                 a.href = imgUrl;
                                 a.download = `${ev['성명']}_${ev['직급']}_포스터_스타일${i+1}_${new Date().getTime()}.png`;
                                 a.click();
                               }}
                             >
                               스타일 {i+1} 다운로드 ⬇️
                             </button>
                           </div>
                        ))}
                      </div>
                    )}
                  </div>
                ))
              )}
            </div>
          )}
        </div>
      </div>
    </div>
  )
}

export default App
