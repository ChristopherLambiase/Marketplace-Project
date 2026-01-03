import { useState, useEffect } from 'react'
import './App.css'
import './Home.css'
import ListingCard from './components/ListingCard'
import MyListings from './MyListings'

interface Listing {
  id: number;
  title: string;
  description: string;
  price: number;
  category: string;
  condition: string;
  seller_id: number;
  seller_name: string;
  location: string;
  date_posted: string;
  status: string;
  images: string[];
}

function Home() {
  const [listings, setListings] = useState<Listing[]>([])
  const [loading, setLoading] = useState(false)
  const [error, setError] = useState<string | null>(null)
  const [isMenuOpen, setIsMenuOpen] = useState(false)
  const [currentView, setCurrentView] = useState('home')

  // Fetch listings from API
  const fetchListings = async () => {
    setLoading(true)
    setError(null)
    try {
      const response = await fetch('http://localhost:5001/get-all-listings')
      if (!response.ok) {
        throw new Error(`HTTP error! status: ${response.status}`)
      }
      const data = await response.json()
      setListings(data.listings)
    } catch (err) {
      setError(err instanceof Error ? err.message : 'Failed to fetch listings')
      console.error('Error fetching listings:', err)
    } finally {
      setLoading(false)
    }
  }

  useEffect(() => {
    fetchListings()
  }, [])

  const menuItems = [
    { 
      label: 'My Listings', 
      onClick: () => {
        setCurrentView('my-listings')
        setIsMenuOpen(false)
      }
    },
    { label: 'Upcoming Pickups', onClick: () => console.log('Navigate to Upcoming Pickups') },
    {
      label: 'Logout',
      onClick: () => {
        localStorage.clear()
        sessionStorage.clear()
        setCurrentView('home')
        setIsMenuOpen(false)
        window.location.reload()
      }
    }
  ]

  // Show My Listings component if selected
  if (currentView === 'my-listings') {
    return (
      <>
        <button className="menu-btn" onClick={() => setIsMenuOpen(!isMenuOpen)}>
          ☰ Menu
        </button>
        <button className="back-btn" onClick={() => {
          setCurrentView('home')
          fetchListings()
        }}>
          ← Back to Home
        </button>
        {isMenuOpen && <div className="overlay" onClick={() => setIsMenuOpen(false)} />}
        <div className={`side-menu${isMenuOpen ? ' open' : ''}`}>
          <div className="side-menu-content">
            <h2 className="side-menu-title">Navigation</h2>
            <button
              className="side-menu-item"
              onClick={() => {
                setCurrentView('home')
                fetchListings()
                setIsMenuOpen(false)
              }}
            >
              Home
            </button>
            {menuItems.map((item, index) => (
              <button
                key={index}
                className="side-menu-item"
                onClick={() => {
                  item.onClick()
                  setIsMenuOpen(false)
                }}
              >
                {item.label}
              </button>
            ))}
          </div>
        </div>
        <MyListings />
      </>
    )
  }

  return (
    <div className="home-container">
      <button className="menu-btn" onClick={() => setIsMenuOpen(!isMenuOpen)}>
        ☰ Menu
      </button>
      {isMenuOpen && <div className="overlay" onClick={() => setIsMenuOpen(false)} />}
      <div className={`side-menu${isMenuOpen ? ' open' : ''}`}>
        <div className="side-menu-content">
          <h2 className="side-menu-title">Navigation</h2>
          {menuItems.map((item, index) => (
            <button
              key={index}
              className="side-menu-item"
              onClick={() => {
                item.onClick()
                setIsMenuOpen(false)
              }}
            >
              {item.label}
            </button>
          ))}
        </div>
      </div>
      <h1 className="home-title">Marketplace Listings</h1>
      {error && (
        <div className="error-message">
          <p>Error: {error}</p>
          <button onClick={fetchListings}>Retry</button>
        </div>
      )}
      <div>
        <div className="listings-grid">
          {listings.map((listing) => (
            <ListingCard key={listing.id} listing={listing} />
          ))}
        </div>
        {!loading && listings.length === 0 && !error && (
          <p className="no-listings-message">No listings available at the moment.</p>
        )}
      </div>
    </div>
  )
}

export default Home