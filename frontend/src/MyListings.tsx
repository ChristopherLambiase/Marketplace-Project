import { useState, useEffect, useCallback } from 'react'
import './MyListings.css'
import MyListingsTable from './components/MyListingsTable.tsx'
import NewListingModal from './components/NewListingModal'

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

function MyListings() {
  const [myListings, setMyListings] = useState<Listing[]>([])
  const [loading, setLoading] = useState(false)
  const [error, setError] = useState<string | null>(null)
  const [showModal, setShowModal] = useState(false)

  const userId = Number(localStorage.getItem('user_id'))

  const fetchMyListings = useCallback(async () => {
    setLoading(true)
    setError(null)
    try {
      const response = await fetch(`http://localhost:5001/get-my-listings?user_id=${userId}`)
      const data = await response.json()
      setMyListings(data.user_listings || [])
    } catch (err) {
      setError('Failed to fetch your listings: ' + (err instanceof Error ? err.message : 'Unknown error'))
    } finally {
      setLoading(false)
    }
  }, [userId])

  useEffect(() => { fetchMyListings() }, [fetchMyListings])

  return (
    <div className="mylistings-container">
      <div className="mylistings-title">My Listings</div>
      <button className="mylistings-btn" style={{ marginBottom: 16 }} onClick={() => setShowModal(true)}>
        + Create New Listing
      </button>
      <NewListingModal
        isOpen={showModal}
        onClose={() => setShowModal(false)}
        onCreated={fetchMyListings}
        sellerId={userId}
      />

      {error && (
        <div className="mylistings-error">
          <div>Error: {error}</div>
          <button className="mylistings-btn" onClick={fetchMyListings}>Retry</button>
        </div>
      )}

      {loading && <div>Loading...</div>}

      {!loading && !error && myListings.length > 0 && (
        <MyListingsTable
          listings={myListings}
        />
      )}

      {!loading && myListings.length === 0 && !error && (
        <div className="mylistings-empty">
          <div style={{ fontSize: '2.5rem', marginBottom: '12px' }}>📦</div>
          <div>No listings found</div>
          <div style={{ color: '#888', fontSize: '1rem', marginTop: '8px' }}>You haven't created any listings yet.</div>
        </div>
      )}
    </div>
  )
}

export default MyListings