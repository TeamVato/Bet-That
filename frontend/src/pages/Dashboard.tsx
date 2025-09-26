import { useState } from 'react'
import { useOddsBest } from '@/hooks/useOdds'
import Skeleton from '@/components/Skeleton'
import { formatUTC } from '@/utils/format'

export default function Dashboard(){
  const [market,setMarket] = useState<string>('')
  const { data, isLoading, error, refetch, isFetching } = useOddsBest(market || undefined)

  return (
    <section className="space-y-4">
      <div className="flex items-center justify-between">
        <h1 className="text-xl font-semibold">Odds — Best Lines</h1>
        <div className="flex items-center gap-2">
          <select className="select" value={market} onChange={e=>setMarket(e.target.value)}>
            <option value="">All markets</option>
            <option value="spread">spread</option>
            <option value="total">total</option>
            <option value="moneyline">moneyline</option>
          </select>
          <button className="btn" onClick={()=>refetch()} disabled={isFetching}>Refresh</button>
        </div>
      </div>

      <div className="card p-4">
        {isLoading ? <Skeleton rows={6}/> :
          error ? <div className="text-red-600 text-sm">Failed to load odds.</div> :
          <div className="overflow-x-auto">
            <table className="w-full text-sm">
              <thead><tr className="text-left">
                <th className="py-2">Game</th>
                <th>Market</th>
                <th>Home</th>
                <th>Away</th>
                <th className="text-right">Timestamp <span className="badge border-gray-300 ml-1">UTC</span></th>
              </tr></thead>
              <tbody>
                {data.items.map((r:any, idx:number)=>(
                  <tr key={idx} className="border-t">
                    <td className="py-2">{r.game_id}</td>
                    <td>{r.market}</td>
                    <td>{r.price_home}</td>
                    <td>{r.price_away}</td>
                    <td className="text-right">{formatUTC(r.ts)}</td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
        }
      </div>
    </section>
  )
}
