export default function Skeleton({ rows=3 }:{ rows?: number }){
  return (
    <div className="space-y-2">
      {Array.from({length:rows}).map((_,i)=>(
        <div key={i} className="h-4 bg-gray-200 rounded w-full animate-pulse" />
      ))}
    </div>
  )
}
