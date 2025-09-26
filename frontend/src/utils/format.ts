export function formatUTC(iso: string){
  try {
    const d = new Date(iso)
    return d.toISOString().replace('.000Z','Z')
  } catch { return iso }
}
