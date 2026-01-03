import { useState, useEffect } from 'react'
import type { CSSProperties } from 'react'

type User = { id: number | string; name: string }
type Message = { from: string; to: string; text: string }

const CURRENT_USER_ID = 'yourUserId' 
const boxStyle: CSSProperties = {
  minHeight: '100vh',
  width: '100vw',
  background: '#f7f8fa',
  display: 'flex',
  flexDirection: 'column',
  alignItems: 'center',
  paddingTop: 40,
  color: '#222',
  fontFamily: 'Inter, Arial, sans-serif',
}

const messagesStyle: CSSProperties = {
  background: '#fff',
  borderRadius: 8,
  padding: 12,
  minHeight: 80,
  marginBottom: 16,
  maxHeight: 300,
  overflowY: 'auto',
  width: 360,
  boxShadow: '0 2px 8px #0001',
}

const messageStyle = (isMe: boolean): CSSProperties => ({
  margin: '6px 0',
  padding: '8px 12px',
  borderRadius: 6,
  background: isMe ? '#e3f2fd' : '#eee',
  color: '#222',
  textAlign: isMe ? 'right' : 'left',
  fontSize: 15,
})

const inputRowStyle = {
  display: 'flex',
  gap: 8,
  marginTop: 8,
  width: 360,
}

const inputStyle = {
  flex: 1,
  padding: '8px 12px',
  borderRadius: 6,
  border: '1px solid #ccc',
  fontSize: 15,
  background: '#fff',
  color: '#222',
}

function DMPage() {
  const [users, setUsers] = useState<User[]>([])
  const [selectedUser, setSelectedUser] = useState<User | null>(null)
  const [messages, setMessages] = useState<Message[]>([])
  const [input, setInput] = useState('')

  useEffect(() => {
    fetch('http://localhost:5001/users')
      .then(res => res.json())
      .then(setUsers)
  }, [])

  useEffect(() => {
    if (selectedUser) {
      fetch(`/api/messages?to=${selectedUser.id}`)
        .then(res => res.json())
        .then(setMessages)
    }
  }, [selectedUser])

  return (
    <div style={boxStyle}>
      <h2 style={{ marginBottom: 16, fontWeight: 600 }}>DM</h2>
      <div style={{ marginBottom: 12 }}>
        <select
          style={inputStyle}
          value={selectedUser?.id?.toString() || ''}
          onChange={e => {
            const user = users.find(u => u.id.toString() === e.target.value)
            setSelectedUser(user || null)
          }}
        >
          <option value="">Select user...</option>
          {users.map(u => (
            <option key={u.id} value={u.id}>{u.name}</option>
          ))}
        </select>
      </div>
      {selectedUser && (
        <>
          <div style={messagesStyle}>
            {messages.length === 0 && <div style={{ opacity: 0.5 }}>No messages yet.</div>}
            {messages.map((msg, idx) => (
              <div key={idx} style={messageStyle(msg.from === CURRENT_USER_ID)}>
                <span>{msg.text}</span>
              </div>
            ))}
          </div>
          <div style={inputRowStyle}>
            <input
              style={inputStyle}
              type="text"
              value={input}
              onChange={e => setInput(e.target.value)}
              placeholder="Type a message..."
            />
          </div>
        </>
      )}
    </div>
  )
}

export default DMPage