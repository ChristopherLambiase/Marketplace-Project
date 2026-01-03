import React, { useState, useEffect } from 'react'

interface Listing {
  id: number;
  title: string;
  description: string;
  price: number;
  category: string;
  condition: string;
  images: string[];
  date_posted: string;
}

interface Request {
  id: number;
  requesterName: string;
  status: string;
  message: string;
}

interface Props {
  listings: Listing[];
}

type IncomingRequest = {
  id: number;
  item_id: number;
  requester: string;
  status: string;
  message: string;
}

const IMAGE_BASE_URL = "http://localhost:5001";

const getImageSrc = (imgPath?: string) => {
  if (!imgPath) return '';
  return imgPath.startsWith('/static')
    ? `${IMAGE_BASE_URL}${imgPath}`
    : imgPath;
};

const MyListingsTable: React.FC<Props> = ({ listings }) => {
  const [requestsByItem, setRequestsByItem] = useState<{ [itemId: number]: Request[] }>({});
  const [openListingId, setOpenListingId] = useState<number | null>(null);

  useEffect(() => {
    // Fetch incoming requests for this seller
    fetch('http://localhost:5001/get-incoming-requests')
      .then(res => res.json())
      .then((data: IncomingRequest[]) => {
        // Group requests by item id
        const grouped: { [itemId: number]: Request[] } = {};
        data.forEach(req => {
          if (!grouped[req.item_id]) grouped[req.item_id] = [];
          grouped[req.item_id].push({
            id: req.id,
            requesterName: req.requester,
            status: req.status,
            message: req.message,
          });
        });
        setRequestsByItem(grouped);
      });
  }, []);

  const getRequests = (listingId: number) => requestsByItem[listingId] || [];

  const handleRequestsClick = (listingId: number) => {
    setOpenListingId(openListingId === listingId ? null : listingId);
  };

  return (
    <table className="mylistings-table">
      <thead>
        <tr>
          <th>Item</th>
          <th>Price</th>
          <th>Requests</th>
        </tr>
      </thead>
      <tbody>
        {listings.map(listing => {
          const requests = getRequests(listing.id)
          return (
            <tr key={listing.id}>
              <td>
                <div style={{ display: 'flex', alignItems: 'center', gap: '10px' }}>
                  <div className="mylistings-image">
                    {listing.images && listing.images.length > 0 ? (
                      <img src={getImageSrc(listing.images[0])} alt={listing.title} style={{ width: '100%', height: '100%', objectFit: 'cover' }} />
                    ) : (
                      <span>📷</span>
                    )}
                  </div>
                  <div>
                    <div className="mylistings-item-title">
                      {listing.title}
                    </div>
                    <div className="mylistings-item-desc">
                      {listing.description.length > 60 ? listing.description.slice(0, 60) + '...' : listing.description}
                    </div>
                    <span className="mylistings-badge">{listing.category}</span>
                    <span className="mylistings-badge">{listing.condition}</span>
                  </div>
                </div>
              </td>
              <td>
                <div className="mylistings-price">${listing.price.toFixed(2)}</div>
              </td>
              <td>
                <div className="mylistings-requests">
                  <button
                    style={{ background: 'none', border: 'none', color: '#007bff', cursor: 'pointer', padding: 0 }}
                    onClick={() => handleRequestsClick(listing.id)}
                  >
                    {requests.length === 0
                      ? 'No requests'
                      : `${requests.length} request${requests.length > 1 ? 's' : ''}`}
                  </button>
                  {openListingId === listing.id && requests.length > 0 && (
                    <ul style={{ margin: '8px 0 0 0', paddingLeft: '1em', background: '#f9f9f9', borderRadius: '4px' }}>
                      {requests.map(req => (
                        <li key={req.id}>
                          {req.requesterName} ({req.status})
                          {req.status !== 'approved' && (
                            <input
                              type="checkbox"
                              style={{ marginLeft: '8px' }}
                              onChange={async (e) => {
                                if (e.target.checked) {
                                  // Replace with actual seller ID
                                  await fetch(`http://localhost:5001/update-request-status/${req.id}`, {
                                    method: 'POST',
                                    headers: { 'Content-Type': 'application/json' },
                                    body: JSON.stringify({ status: 'approved' }),
                                  });
                                  // Update UI
                                  setRequestsByItem(prev => {
                                    const updated = { ...prev };
                                    updated[listing.id] = updated[listing.id].map(r =>
                                      r.id === req.id ? { ...r, status: 'approved' } : r
                                    );
                                    return updated;
                                  });
                                }
                              }}
                            />
                          )}
                        </li>
                      ))}
                    </ul>
                  )}
                </div>
              </td>
            </tr>
          )
        })}
      </tbody>
    </table>
  );
}

export default MyListingsTable