import React, { useState } from 'react';
import './ListingCard.css';

type Listing = {
  id: number;
  images?: string[];
  title: string;
  price: number | string;
  description?: string;
  category?: string;
  condition?: string;
  seller_name?: string;
  location?: string;
  date_posted?: string;
};

type ListingDetailsModalProps = {
  listing: Listing;
  onClose: () => void;
  onRequestBuy: (listingId: number, message: string) => void;
};

const IMAGE_BASE_URL = "http://localhost:5001";

const ListingDetailsModal: React.FC<ListingDetailsModalProps> = ({
  listing,
  onClose,
  onRequestBuy,
}) => {
  const [message, setMessage] = useState('');
  const [requestSent, setRequestSent] = useState(false);

  const getImageSrc = (imgPath?: string) => {
    if (!imgPath) return '';
    return imgPath.startsWith('/static')
      ? `${IMAGE_BASE_URL}${imgPath}`
      : imgPath;
  };

  const handleRequestBuy = () => {
    onRequestBuy(listing.id, message);
    setRequestSent(true);
  };

  return (
    <div className="listing-modal-overlay" onClick={onClose}>
      <div className="listing-modal" onClick={e => e.stopPropagation()}>
        <button className="close-btn" onClick={onClose}>×</button>
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
          <p><strong>Price:</strong> ${listing.price}</p>
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
              />
              <button className="request-buy-btn" onClick={handleRequestBuy}>
                Request to Buy
              </button>
            </div>
          ) : (
            <div className="request-sent-message">
              Request sent! The seller will contact you soon.
            </div>
          )}
        </div>
      </div>
    </div>
  );
};

export default ListingDetailsModal;