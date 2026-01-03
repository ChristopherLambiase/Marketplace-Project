import React, { useState } from 'react'

interface Props {
  isOpen: boolean;
  onClose: () => void;
  onCreated: () => void;
  sellerId: number;
}

const defaultListing = {
  title: '',
  description: '',
  price: '',
  category: '',
  condition: '',
  seller_id: 1,
  seller_name: '',
  location: '',
  images: ['']
}

const categories = ['Electronics', 'Books', 'Sports', 'Furniture']
const conditions = ['Excellent', 'Like New', 'Good', 'Fair']

const NewListingModal: React.FC<Props> = ({ isOpen, onClose, onCreated, sellerId }) => {
  const [form, setForm] = useState(defaultListing)
  const [loading, setLoading] = useState(false)
  const [error, setError] = useState<string | null>(null)

  const handleChange = (e: React.ChangeEvent<HTMLInputElement | HTMLSelectElement>) => {
    setForm({ ...form, [e.target.name]: e.target.value })
  }

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault()
    setLoading(true)
    setError(null)
    try {
      const res = await fetch('http://localhost:5001/post-listing', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
          ...form,
          price: parseFloat(form.price),
          images: form.images[0] ? [form.images[0]] : [],
          seller_id: sellerId
        })
      })
      if (!res.ok) {
        const data = await res.json()
        setError(data.error || 'Failed to create listing')
      } else {
        setForm(defaultListing)
        onCreated()
        onClose()
      }
    } catch {
      setError('Network error')
    } finally {
      setLoading(false)
    }
  }

  if (!isOpen) return null

  return (
    <div className="modal-overlay" onClick={onClose}>
      <div className="modal-content" onClick={e => e.stopPropagation()}>
        <h2>Create New Listing</h2>
        <form onSubmit={handleSubmit} className="modal-form">
          <input name="title" placeholder="Title" value={form.title} onChange={handleChange} required />
          <input name="description" placeholder="Description" value={form.description} onChange={handleChange} required />
          <input name="price" type="number" placeholder="Price" value={form.price} onChange={handleChange} required />
          <select name="category" value={form.category} onChange={handleChange} required>
            <option value="">Category</option>
            {categories.map(c => <option key={c} value={c}>{c}</option>)}
          </select>
          <select name="condition" value={form.condition} onChange={handleChange} required>
            <option value="">Condition</option>
            {conditions.map(c => <option key={c} value={c}>{c}</option>)}
          </select>
          <input name="seller_name" placeholder="Your Name" value={form.seller_name} onChange={handleChange} required />
          <input name="location" placeholder="Location" value={form.location} onChange={handleChange} required />
          <input name="images" placeholder="Image URL" value={form.images[0]} onChange={e => setForm({ ...form, images: [e.target.value] })} />
          {error && <div style={{ color: 'red', marginBottom: 8 }}>{error}</div>}
          <button type="submit" disabled={loading} className="mylistings-btn">
            {loading ? 'Creating...' : 'Create'}
          </button>
        </form>
        <button className="mylistings-btn" style={{ marginTop: 8 }} onClick={onClose}>Cancel</button>
      </div>
    </div>
  )
}

export default NewListingModal