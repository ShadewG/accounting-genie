const { useState, useEffect } = React;

const db = firebase.firestore();
const storage = firebase.storage();

function App() {
  const [view, setView] = useState('dashboard');
  const [selectedId, setSelectedId] = useState(null);

  return (
    <div>
      {view === 'dashboard' && (
        <Dashboard onSelect={(id) => { setSelectedId(id); setView('detail'); }} />
      )}
      {view === 'detail' && (
        <ReceiptDetail receiptId={selectedId} onBack={() => setView('dashboard')} />
      )}
    </div>
  );
}

function Dashboard({ onSelect }) {
  const [receipts, setReceipts] = useState([]);

  useEffect(() => {
    const user = firebase.auth().currentUser;
    if (!user) return;
    const unsubscribe = db.collection('receipts')
      .where('userId', '==', user.uid)
      .onSnapshot((snap) => {
        const items = snap.docs.map((d) => ({ id: d.id, ...d.data() }));
        setReceipts(items);
      });
    return unsubscribe;
  }, []);

  return (
    <div>
      <h1 className="text-2xl font-bold mb-4">Dashboard</h1>
      <table className="min-w-full bg-white border">
        <thead>
          <tr>
            <th className="border px-2 py-1">Vendor</th>
            <th className="border px-2 py-1">Date</th>
            <th className="border px-2 py-1">Amount</th>
            <th className="border px-2 py-1">Status</th>
            <th className="border px-2 py-1"></th>
          </tr>
        </thead>
        <tbody>
          {receipts.map((r) => (
            <tr key={r.id}>
              <td className="border px-2 py-1">{r.vendor || '-'}</td>
              <td className="border px-2 py-1">
                {r.date ? new Date(r.date.seconds * 1000).toLocaleDateString() : '-'}
              </td>
              <td className="border px-2 py-1">{r.totalAmount || '-'}</td>
              <td className="border px-2 py-1">{r.status || '-'}</td>
              <td className="border px-2 py-1">
                <button className="text-blue-600 underline" onClick={() => onSelect(r.id)}>
                  View
                </button>
              </td>
            </tr>
          ))}
          {receipts.length === 0 && (
            <tr>
              <td colSpan="5" className="border px-2 py-1 text-center text-gray-500">
                No receipts found.
              </td>
            </tr>
          )}
        </tbody>
      </table>
    </div>
  );
}

function ReceiptDetail({ receiptId, onBack }) {
  const [receipt, setReceipt] = useState(null);
  const [imageUrl, setImageUrl] = useState('');
  const [form, setForm] = useState({ vendor: '', date: '', totalAmount: '' });
  const [posting, setPosting] = useState(false);

  useEffect(() => {
    if (!receiptId) return;
    const unsub = db.collection('receipts').doc(receiptId).onSnapshot(async (doc) => {
      const data = { id: doc.id, ...doc.data() };
      setReceipt(data);
      setForm({
        vendor: data.vendor || '',
        date: data.date ? new Date(data.date.seconds * 1000).toISOString().substr(0,10) : '',
        totalAmount: data.totalAmount || ''
      });
      if (data.filePath) {
        try {
          const url = await storage.ref(data.filePath).getDownloadURL();
          setImageUrl(url);
        } catch (e) {
          console.error('Failed to load image', e);
        }
      }
    });
    return unsub;
  }, [receiptId]);

  const updateForm = (e) => {
    const { name, value } = e.target;
    setForm((f) => ({ ...f, [name]: value }));
  };

  const postToFiken = async () => {
    setPosting(true);
    try {
      await db.collection('receipts').doc(receiptId).update({
        vendor: form.vendor,
        date: form.date ? new Date(form.date) : null,
        totalAmount: parseFloat(form.totalAmount) || null
      });
      await fetch(`/api/receipts/${receiptId}/post_to_fiken`, { method: 'POST' });
      alert('Posted to Fiken');
    } catch (err) {
      console.error(err);
      alert('Failed to post to Fiken');
    }
    setPosting(false);
  };

  if (!receipt) return <div>Loading...</div>;

  return (
    <div>
      <button className="text-blue-600 underline mb-4" onClick={onBack}>&larr; Back</button>
      <h2 className="text-xl font-semibold mb-2">Receipt Detail</h2>
      {imageUrl && <img src={imageUrl} alt="Receipt" className="mb-4 max-w-xs" />}
      <div className="space-y-2">
        <div>
          <label className="block">Vendor</label>
          <input type="text" name="vendor" value={form.vendor} onChange={updateForm} className="border p-1 w-full" />
        </div>
        <div>
          <label className="block">Date</label>
          <input type="date" name="date" value={form.date} onChange={updateForm} className="border p-1 w-full" />
        </div>
        <div>
          <label className="block">Total Amount</label>
          <input type="number" step="0.01" name="totalAmount" value={form.totalAmount} onChange={updateForm} className="border p-1 w-full" />
        </div>
        <button className="bg-green-600 text-white px-4 py-2 rounded" onClick={postToFiken} disabled={posting}>
          {posting ? 'Posting...' : 'Post to Fiken'}
        </button>
      </div>
    </div>
  );
}

ReactDOM.render(<App />, document.getElementById('root'));
