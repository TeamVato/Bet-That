export default function Footer({ disclaimer }:{ disclaimer: string }){
  return (
    <footer className="border-t bg-white mt-10">
      <div className="container py-4 text-xs text-gray-600">
        <div>{disclaimer}</div>
      </div>
    </footer>
  )
}
