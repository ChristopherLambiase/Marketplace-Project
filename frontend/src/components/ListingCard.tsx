import React, { useState } from 'react';
import './ListingCard.css';

type Listing = {
  id?: number;
  images?: string[];
  title: string;
  price: number | string;
  description?: string;
  category?: string;
  condition?: string;
  seller_name?: string;
  seller_id?: number;
  location?: string;
  date_posted?: string;
};

type ListingCardProps = {
  listing: Listing;
};

const formatPrice = (price: number | string) => {
  if (typeof price === 'number') {
    return price.toLocaleString('en-US', { style: 'currency', currency: 'USD' });
  }
  return `$${price}`;
};

const IMAGE_BASE_URL = "http://localhost:5001";
const API_BASE_URL = "http://localhost:5001";

const ListingCard: React.FC<ListingCardProps> = ({ listing }) => {
  const [showModal, setShowModal] = useState(false);
  const [message, setMessage] = useState('');
  const [requestSent, setRequestSent] = useState(false);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);

  const getImageSrc = (imgPath?: string) => {
    if (!imgPath) return '';
    return imgPath.startsWith('/static')
      ? `${IMAGE_BASE_URL}${imgPath}`
      : imgPath;
  };

  const handleRequestBuy = async () => {
    setLoading(true);
    setError(null);

    try {
      const buyerId = localStorage.getItem('user_id');
      
      if (!buyerId) {
        setError('You must be logged in to send a request');
        setLoading(false);
        return;
      }

      if (!listing.id || !listing.seller_id) {
        setError('Invalid listing information');
        setLoading(false);
        return;
      }

      const response = await fetch(`${API_BASE_URL}/send-request`, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({
          item_id: listing.id,
          buyer_id: parseInt(buyerId),
          message: message || '',
        }),
      });

      const data = await response.json();

      if (response.ok) {
        setRequestSent(true);
        setMessage('');
      } else {
        setError(data.message || 'Failed to send request');
      }
    } catch (err) {
      setError(err instanceof Error ? err.message : 'Failed to send request');
      console.error('Error sending request:', err);
    } finally {
      setLoading(false);
    }
  };

  return (
    <>
      <div className="listing-card" onClick={() => setShowModal(true)}>
        <div className="listing-image">
          {listing.images && listing.images.length > 0 ? (
            <img
              src={getImageSrc(listing.images[0])}
              alt={listing.title || 'Listing Image'}
              className="listing-img"
            />
          ) : (
            <div className="no-image">
              No Image Available
            </div>
          )}
        </div>
        <div className="listing-content">
          <h3 className="listing-title">
            {listing.title}
          </h3>
          <p className="listing-price">
            {formatPrice(listing.price)}
          </p>
          <p className="listing-description">
            {listing.description ? listing.description : <span style={{ color: '#aaa' }}>No description provided.</span>}
          </p>
        </div>
      </div>
      {showModal && (
        <div className="listing-modal-overlay" onClick={() => setShowModal(false)}>
          <div className="listing-modal" onClick={e => e.stopPropagation()}>
            <button className="close-btn" onClick={() => setShowModal(false)}>×</button>
            <div className="listing-modal-image">
              {listing.images && listing.images.length > 0 ? (
                <img
                  src={getImageSrc(listing.images[0])}
                  alt={listing.title || 'Listing Image'}
                  className="listing-img"
                />
              ) : (
                <div className="no-image">No Image Available</div>
              )}
            </div>
            <div className="listing-modal-content">
              <h2>{listing.title}</h2>
              <p><strong>Price:</strong> {formatPrice(listing.price)}</p>
              <p><strong>Description:</strong> {listing.description}</p>
              <p><strong>Category:</strong> {listing.category}</p>
              <p><strong>Condition:</strong> {listing.condition}</p>
              <p><strong>Seller:</strong> {listing.seller_name}</p>
              <p><strong>Location:</strong> {listing.location}</p>
              <p><strong>Date Posted:</strong> {listing.date_posted}</p>
              {!requestSent ? (
                <div className="request-buy-section">
                  <textarea
                    placeholder="Message to seller (optional)"
                    value={message}
                    onChange={e => setMessage(e.target.value)}
                    rows={3}
                    style={{ width: '100%', marginBottom: '1rem' }}
                    disabled={loading}
                  />
                  {error && (
                    <div style={{
                      color: '#d32f2f',
                      marginBottom: '1rem',
                      padding: '0.5rem',
                      backgroundColor: '#ffebee',
                      borderRadius: '4px'
                    }}>
                      {error}
                    </div>
                  )}
                  <button
                    className="request-buy-btn"
                    onClick={handleRequestBuy}
                    disabled={loading}
                    style={{ opacity: loading ? 0.6 : 1, cursor: loading ? 'not-allowed' : 'pointer' }}
                  >
                    {loading ? 'Sending...' : 'Request to Buy'}
                  </button>
                </div>
              ) : (
                <div className="request-sent-message">
                  ✓ Request sent! The seller will contact you soon.
                </div>
              )}
            </div>
          </div>
        </div>
      )}
    </>
  );
};

export default ListingCard;