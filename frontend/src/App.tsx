import { useState } from 'react'
import Login from './Login'
import './App.css'
import Home from './home'
import MyListings from './MyListings'
import DMPage from './DMPage'
import UpcomingPickups from './upcoming_pickups'

export type PageType = 'login' | 'home' | 'myListings' | 'dm' | 'upcomingPickups'

function App() {
  const [currentPage, setCurrentPage] = useState<PageType>('login')

  const handleLogin = () => {
    setCurrentPage('home')
  }

  // Handler to go to DM page
  const goToDM = () => {
    setCurrentPage('dm')
  }

  if (currentPage === 'login') {
    return <Login onLogin={handleLogin} />
  }

  if (currentPage === 'home') {
    return (
      <div>
        <Home />
        <button onClick={goToDM}>Go to DM</button>
      </div>
    )
  }

  if (currentPage === 'myListings') {
    return <MyListings />
  }

  if (currentPage === 'dm') {
    return <DMPage />
  }

  if (currentPage === 'upcomingPickups') {
    return <UpcomingPickups />
  }

  return null
}

export default App