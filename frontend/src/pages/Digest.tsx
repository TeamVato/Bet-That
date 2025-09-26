import { useState } from 'react'
import { api } from '@/utils/api'
import Toast from '@/components/Toast'

export default function Digest(){
  const [busy,setBusy] = useState(false)
  const [toast,setToast] = useState<{message:string,type:'success'|'error'}|null>(null)

  async function subscribe(){
    setBusy(true)
    try {
      const res = await api.subscribe()
      setToast({message: res.message || 'Subscribed', type:'success'})
    } catch(e:any){
      setToast({message: e?.message || 'Error', type:'error'})
    } finally {
      setBusy(false)
    }
  }

  return (
    <section className="space-y-4">
      <h1 className="text-xl font-semibold">Weekly Digest</h1>
      <div className="card p-4 flex items-center justify-between">
        <div className="text-sm text-gray-700">Subscribe your account to receive the weekly odds digest.</div>
        <button className="btn" onClick={subscribe} disabled={busy}>Subscribe</button>
      </div>
      {toast && <Toast message={toast.message} type={toast.type} onClose={()=>setToast(null)}/>}
    </section>
  )
}
