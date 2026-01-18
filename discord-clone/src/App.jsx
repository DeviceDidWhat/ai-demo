import { useState } from 'react'
import './App.css'

function App() {
  const [servers, setServers] = useState([
    { id: 1, name: 'Server 1', initial: 'S1' },
    { id: 2, name: 'Server 2', initial: 'S2' },
    { id: 3, name: 'Server 3', initial: 'S3' },
  ])

  const [channels, setChannels] = useState([
    { id: 1, name: 'general', category: 'Text Channels' },
    { id: 2, name: 'random', category: 'Text Channels' },
    { id: 3, name: 'help', category: 'Text Channels' },
    { id: 4, name: 'General', category: 'Voice Channels' },
  ])

  const [messages, setMessages] = useState([
    { id: 1, username: 'User1', text: 'Hello everyone!', timestamp: '10:00 AM' },
    { id: 2, username: 'User2', text: 'Hi there! How are you?', timestamp: '10:05 AM' },
    { id: 3, username: 'User1', text: 'I am doing great! How about you?', timestamp: '10:10 AM' },
  ])

  const [currentChannel, setCurrentChannel] = useState('general')
  const [newMessage, setNewMessage] = useState('')

  const handleSendMessage = (e) => {
    e.preventDefault()
    if (newMessage.trim() === '') return
n
    const newMsg = {
      id: messages.length + 1,
      username: 'You',
      text: newMessage,
      timestamp: new Date().toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' })
    }

    setMessages([...messages, newMsg])
    setNewMessage('')
  }

  const getCategoryChannels = (category) => {
    return channels.filter(channel => channel.category === category)
  }

  return (
    <div className="app">
      {/* Server List */}
      <div className="server-list">
        {servers.map(server => (
          <div key={server.id} className="server-icon">
            {server.initial}
          </div>
        ))}
      </div>

      {/* Sidebar */}
      <div className="sidebar">
        <h2 style={{ color: 'white', marginBottom: '16px' }}>Discord Clone</h2>

        <div className="channel-list">
          {['Text Channels', 'Voice Channels'].map(category => (
            <div key={category} className="channel-category">
              <div className="channel-category-header">{category}</div>
              {getCategoryChannels(category).map(channel => (
                <div
                  key={channel.id}
                  className={`channel-item ${currentChannel === channel.name ? 'active' : ''}`}
                  onClick={() => setCurrentChannel(channel.name)}
                >
                  <div className="channel-icon">#</div>
                  <div>{channel.name}</div>
                </div>
              ))}
            </div>
          ))}
        </div>

        {/* User Info */}
        <div className="user-info">
          <div className="user-details">
            <div className="user-avatar"></div>
            <div className="user-name">Username</div>
            <div className="status-indicator"></div>
          </div>
        </div>
      </div>

      {/* Main Content */}
      <div className="main-content">
        {/* Header */}
        <div className="header">
          <div style={{ fontWeight: 'bold' }}>#{currentChannel}</div>
        </div>

        {/* Chat Area */}
        <div className="chat-area">
          {messages.map(message => (
            <div key={message.id} className="message">
              <div className="avatar"></div>
              <div className="message-content">
                <div className="message-header">
                  <span className="username">{message.username}</span>
                  <span className="timestamp">{message.timestamp}</span>
                </div>
                <div className="message-text">{message.text}</div>
              </div>
            </div>
          ))}
        </div>

        {/* Message Input */}
        <form onSubmit={handleSendMessage} className="message-input">
          <input
            type="text"
            value={newMessage}
            onChange={(e) => setNewMessage(e.target.value)}
            placeholder={`Message #${currentChannel}`}
          />
        </form>
      </div>
    </div>
  )
}

export default App